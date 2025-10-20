import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
import sys

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class EvaluationPanelEnhanced:
    """拡張評価パネル - 期間評価と品質出力"""
    
    def __init__(self, db_path="trainer_prediction_system/excel_data.db"):
        self.db_path = db_path
        self.conn = None
        self.connect()
    
    def connect(self):
        """データベース接続"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            print("データベース接続成功")
        except Exception as e:
            print(f"データベース接続エラー: {e}")
            return False
        return True
    
    def check_column_coverage(self):
        """列検出カバレッジ確認"""
        print("=== 列検出カバレッジ確認 ===")
        
        try:
            # 列の存在確認
            query_columns = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='SE_FE'
            """
            result = pd.read_sql_query(query_columns, self.conn)
            
            if result.empty:
                print("❌ SE_FEテーブルが存在しません")
                return False
            
            # SE_FEの列一覧
            query_schema = """
            PRAGMA table_info(SE_FE)
            """
            schema_result = pd.read_sql_query(query_schema, self.conn)
            
            print("SE_FEテーブルの列一覧:")
            for _, row in schema_result.iterrows():
                print(f"  {row['name']} ({row['type']})")
            
            # 新規追加列の確認
            new_columns = [
                'race_id', 'distance_num', 'r_zi_gap_num', 'r_zm_gap_num', 'takeuchi_prev23_cnt',
                'super_fav_flag', 'late_ZI_candidate', 'no_bet_flag', 'low_confidence_flag',
                'smart_tag_A', 'smart_tag_B', 'smart_tag_C', 'speed_rank', 'spirit_rank',
                'mark5_score_raw', 'mark6_score_raw', 'mark5_low_conf_flag', 'mark6_low_conf_flag',
                'zm_score', 'prev_ninki_rank', 'zm_odds_pred', 'style_front', 'style_mid', 'style_back',
                'accel_score', 'original_score', 'race_roughness_idx'
            ]
            
            existing_columns = schema_result['name'].tolist()
            found_columns = [col for col in new_columns if col in existing_columns]
            missing_columns = [col for col in new_columns if col not in existing_columns]
            
            print(f"\n新規追加列の検出結果:")
            print(f"  検出済み: {len(found_columns)}/{len(new_columns)}")
            print(f"  未検出: {missing_columns}")
            
            return True
            
        except Exception as e:
            print(f"列検出カバレッジ確認エラー: {e}")
            return False
    
    def check_data_quality(self):
        """データ品質確認"""
        print("=== データ品質確認 ===")
        
        try:
            # 基本統計
            query_stats = """
            SELECT 
                COUNT(*) as total_records,
                COUNT(CASE WHEN horse_id IS NOT NULL THEN 1 END) as horse_id_count,
                COUNT(CASE WHEN umaban IS NOT NULL THEN 1 END) as umaban_count,
                COUNT(CASE WHEN race_roughness_idx IS NOT NULL THEN 1 END) as roughness_count,
                COUNT(CASE WHEN super_fav_flag = 1 THEN 1 END) as super_fav_count,
                COUNT(CASE WHEN no_bet_flag = 1 THEN 1 END) as no_bet_count
            FROM SE_FE
            """
            result = pd.read_sql_query(query_stats, self.conn)
            
            print("データ品質統計:")
            print(f"  総レコード数: {result.iloc[0]['total_records']}")
            print(f"  馬ID数: {result.iloc[0]['horse_id_count']}")
            print(f"  馬番数: {result.iloc[0]['umaban_count']}")
            print(f"  荒れ度指数数: {result.iloc[0]['roughness_count']}")
            print(f"  超堅フラグ数: {result.iloc[0]['super_fav_count']}")
            print(f"  無投票フラグ数: {result.iloc[0]['no_bet_count']}")
            
            # 欠損率計算
            total_records = result.iloc[0]['total_records']
            horse_id_missing_rate = (total_records - result.iloc[0]['horse_id_count']) / total_records * 100
            umaban_missing_rate = (total_records - result.iloc[0]['umaban_count']) / total_records * 100
            
            print(f"\n欠損率:")
            print(f"  馬ID欠損率: {horse_id_missing_rate:.2f}%")
            print(f"  馬番欠損率: {umaban_missing_rate:.2f}%")
            
            return True
            
        except Exception as e:
            print(f"データ品質確認エラー: {e}")
            return False
    
    def analyze_roughness_distribution(self):
        """荒れ度分布分析"""
        print("=== 荒れ度分布分析 ===")
        
        try:
            # 荒れ度分布
            query_roughness = """
            SELECT 
                race_roughness_idx,
                COUNT(*) as count,
                AVG(CASE WHEN finish = 1 THEN 1.0 ELSE 0.0 END) as win_rate,
                AVG(CASE WHEN finish BETWEEN 1 AND 3 THEN 1.0 ELSE 0.0 END) as place_rate
            FROM SE_FE
            WHERE race_roughness_idx IS NOT NULL
            GROUP BY race_roughness_idx
            ORDER BY race_roughness_idx
            """
            result = pd.read_sql_query(query_roughness, self.conn)
            
            print("荒れ度分布:")
            print(result.to_string(index=False))
            
            # 堅いレース vs 荒れレース
            query_comparison = """
            WITH race_roughness AS (
                SELECT 
                    race_id,
                    AVG(race_roughness_idx) as avg_roughness
                FROM SE_FE
                WHERE race_roughness_idx IS NOT NULL
                GROUP BY race_id
            ),
            race_classification AS (
                SELECT 
                    se.*,
                    CASE 
                        WHEN rr.avg_roughness < -0.5 THEN '堅い'
                        WHEN rr.avg_roughness > 0.5 THEN '荒れ'
                        ELSE '普通'
                    END as race_type
                FROM SE_FE se
                JOIN race_roughness rr ON se.race_id = rr.race_id
            )
            SELECT 
                race_type,
                COUNT(*) as total_bets,
                AVG(CASE WHEN finish = 1 THEN 1.0 ELSE 0.0 END) as win_rate,
                AVG(CASE WHEN finish BETWEEN 1 AND 3 THEN 1.0 ELSE 0.0 END) as place_rate,
                COUNT(CASE WHEN super_fav_flag = 1 THEN 1 END) as super_fav_count,
                COUNT(CASE WHEN no_bet_flag = 1 THEN 1 END) as no_bet_count
            FROM race_classification
            GROUP BY race_type
            ORDER BY race_type
            """
            comparison_result = pd.read_sql_query(query_comparison, self.conn)
            
            print("\nレースタイプ別分析:")
            print(comparison_result.to_string(index=False))
            
            return True
            
        except Exception as e:
            print(f"荒れ度分布分析エラー: {e}")
            return False
    
    def run_period_evaluation(self, start_date="2024-05-01", end_date="2025-09-28"):
        """期間評価実行"""
        print("=== 期間評価実行 ===")
        
        try:
            start_date_norm = start_date.replace('-', '')
            end_date_norm = end_date.replace('-', '')
            
            # 期間評価クエリ
            query_evaluation = """
            SELECT 
                '期間評価' as evaluation_type,
                COUNT(*) as total_bets,
                COUNT(*) * 100 as total_stake,
                SUM(CASE WHEN finish = 1 AND win_pay_yen IS NOT NULL THEN win_pay_yen ELSE 0 END) as tansho_payoff,
                SUM(CASE WHEN finish BETWEEN 1 AND 3 AND plc_pay_yen_low IS NOT NULL THEN plc_pay_yen_low ELSE 0 END) as fukusho_payoff,
                ROUND(100.0 * SUM(CASE WHEN finish = 1 AND win_pay_yen IS NOT NULL THEN win_pay_yen ELSE 0 END) / NULLIF(COUNT(*) * 100.0, 0), 2) as tansho_roi,
                ROUND(100.0 * SUM(CASE WHEN finish BETWEEN 1 AND 3 AND plc_pay_yen_low IS NOT NULL THEN plc_pay_yen_low ELSE 0 END) / NULLIF(COUNT(*) * 100.0, 0), 2) as fukusho_roi
            FROM SE_FE
            WHERE SourceDate >= ? AND SourceDate <= ?
            AND win_pay_yen IS NOT NULL AND plc_pay_yen_low IS NOT NULL
            """
            result = pd.read_sql_query(query_evaluation, self.conn, params=[start_date_norm, end_date_norm])
            
            print("期間評価結果:")
            print(result.to_string(index=False))
            
            return result
            
        except Exception as e:
            print(f"期間評価実行エラー: {e}")
            return None
    
    def run_enhanced_evaluation(self):
        """拡張評価実行"""
        print("=== 拡張評価実行 ===")
        
        try:
            # 1) 列検出カバレッジ確認
            if not self.check_column_coverage():
                return False
            
            # 2) データ品質確認
            if not self.check_data_quality():
                return False
            
            # 3) 荒れ度分布分析
            if not self.analyze_roughness_distribution():
                return False
            
            # 4) 期間評価実行
            evaluation_result = self.run_period_evaluation()
            if evaluation_result is None:
                return False
            
            print("✅ 拡張評価完了")
            return True
            
        except Exception as e:
            print(f"拡張評価実行エラー: {e}")
            return False

def main():
    evaluator = EvaluationPanelEnhanced()
    success = evaluator.run_enhanced_evaluation()
    
    if success:
        print("\n✅ 拡張評価成功")
    else:
        print("\n❌ 拡張評価失敗")

if __name__ == "__main__":
    main()




