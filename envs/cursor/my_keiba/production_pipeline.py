import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
import sys
import csv

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class ProductionPipeline:
    """本番用の配管 - 壊れない本番分析システム"""
    
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
    
    def assert_fe_gate(self, start_date="2024-11-02", end_date="2025-09-28"):
        """DQゲート（派生側NULLゼロを必須、Raw未知率はWARN）"""
        print("=== DQゲート実行 ===")
        
        try:
            start_date_norm = start_date.replace('-', '')
            end_date_norm = end_date.replace('-', '')
            
            # SE_FEのNULL確認
            query_fe = """
            SELECT SUM(CASE WHEN mark5_imp IS NULL OR mark6_imp IS NULL THEN 1 ELSE 0 END) as fe_nulls
            FROM SE_FE
            WHERE SourceDate >= ? AND SourceDate <= ?
            """
            result_fe = pd.read_sql_query(query_fe, self.conn, params=[start_date_norm, end_date_norm])
            fe_nulls = result_fe.iloc[0]['fe_nulls']
            
            if fe_nulls > 0:
                raise Exception(f"SE_FEにNULLが残っています: {fe_nulls}")
            
            print("✅ SE_FE NULL確認完了")
            
            # Raw未知率はログに出力（停止はしない）
            query_raw = """
            SELECT
                ROUND(100.0 * SUM(CASE WHEN mark5_num IS NULL AND TRIM(COALESCE(Mark5,'')) <> '' THEN 1 ELSE 0 END) /
                      NULLIF(SUM(CASE WHEN TRIM(COALESCE(Mark5,'')) <> '' THEN 1 ELSE 0 END),0), 2) as m5_unknown_pct,
                ROUND(100.0 * SUM(CASE WHEN mark6_num IS NULL AND TRIM(COALESCE(Mark6,'')) <> '' THEN 1 ELSE 0 END) /
                      NULLIF(SUM(CASE WHEN TRIM(COALESCE(Mark6,'')) <> '' THEN 1 ELSE 0 END),0), 2) as m6_unknown_pct
            FROM excel_marks
            WHERE SourceDate >= ? AND SourceDate <= ?
            """
            result_raw = pd.read_sql_query(query_raw, self.conn, params=[start_date_norm, end_date_norm])
            m5_unknown_pct = result_raw.iloc[0]['m5_unknown_pct']
            m6_unknown_pct = result_raw.iloc[0]['m6_unknown_pct']
            
            print(f"⚠️ Raw未知率: Mark5={m5_unknown_pct}% Mark6={m6_unknown_pct}%")
            
            # Raw未知率が60%超の場合は停止
            if m5_unknown_pct > 60 or m6_unknown_pct > 60:
                raise Exception(f"Raw未知率が60%超: Mark5={m5_unknown_pct}% Mark6={m6_unknown_pct}%")
            
            return True
            
        except Exception as e:
            print(f"DQゲートエラー: {e}")
            return False
    
    def calculate_kpi(self, start_date="2024-11-02", end_date="2025-09-28"):
        """集計SQL（本番用：単勝/複勝の基礎KPI）"""
        print("=== KPI計算実行 ===")
        
        try:
            start_date_norm = start_date.replace('-', '')
            end_date_norm = end_date.replace('-', '')
            
            # 単勝KPI
            query_tansho = """
            SELECT
                'tansho' AS bettype,
                COUNT(*) AS bets,
                COUNT(*)*100 AS stake,
                SUM(CASE WHEN CAST(Chaku AS INTEGER) = 1 AND ZI_Index > 1.0 THEN CAST(ROUND(ZI_Index*100) AS INTEGER) ELSE 0 END) AS payoff,
                ROUND(100.0 * SUM(CASE WHEN CAST(Chaku AS INTEGER) = 1 AND ZI_Index > 1.0 THEN ROUND(ZI_Index*100) ELSE 0 END) / (COUNT(*)*100.0), 2) AS roi_pct,
                ROUND(AVG(mark5_missing_flag)*100.0,2) AS m5_missing_rate_pct,
                ROUND(AVG(mark6_missing_flag)*100.0,2) AS m6_missing_rate_pct
            FROM SE_FE
            WHERE SourceDate >= ? AND SourceDate <= ?
            AND ZI_Index IS NOT NULL AND ZI_Index > 1.0
            """
            result_tansho = pd.read_sql_query(query_tansho, self.conn, params=[start_date_norm, end_date_norm])
            
            # 複勝KPI
            query_fukusho = """
            SELECT
                'fukusho' AS bettype,
                COUNT(*) AS bets,
                COUNT(*)*100 AS stake,
                SUM(CASE WHEN CAST(Chaku AS INTEGER) BETWEEN 1 AND 3 AND ZM_Value > 1.0 THEN CAST(ROUND(ZM_Value*100) AS INTEGER) ELSE 0 END) AS payoff,
                ROUND(100.0 * SUM(CASE WHEN CAST(Chaku AS INTEGER) BETWEEN 1 AND 3 AND ZM_Value > 1.0 THEN ROUND(ZM_Value*100) ELSE 0 END) / (COUNT(*)*100.0), 2) AS roi_pct,
                ROUND(AVG(mark5_missing_flag)*100.0,2) AS m5_missing_rate_pct,
                ROUND(AVG(mark6_missing_flag)*100.0,2) AS m6_missing_rate_pct
            FROM SE_FE
            WHERE SourceDate >= ? AND SourceDate <= ?
            AND ZM_Value IS NOT NULL AND ZM_Value > 1.0
            """
            result_fukusho = pd.read_sql_query(query_fukusho, self.conn, params=[start_date_norm, end_date_norm])
            
            # 結果を結合
            kpi_results = pd.concat([result_tansho, result_fukusho], ignore_index=True)
            
            print("KPI計算結果:")
            print(kpi_results.to_string(index=False))
            
            return kpi_results
            
        except Exception as e:
            print(f"KPI計算エラー: {e}")
            return None
    
    def generate_audit_log(self, start_date, end_date, kpi_results):
        """監査ログ生成"""
        print("=== 監査ログ生成 ===")
        
        try:
            # 監査ログの内容
            audit_log = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'kpi_results': kpi_results.to_dict('records') if kpi_results is not None else [],
                'data_quality': {
                    'se_fe_nulls': 0,  # DQゲートで確認済み
                    'raw_unknown_rate': 'WARNレベル'  # DQゲートで確認済み
                }
            }
            
            # 監査ログ保存
            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            audit_file = f"{output_dir}/audit_log_{timestamp}.json"
            
            with open(audit_file, 'w', encoding='utf-8') as f:
                json.dump(audit_log, f, ensure_ascii=False, indent=2)
            
            print(f"監査ログ保存完了: {audit_file}")
            
            return audit_file
            
        except Exception as e:
            print(f"監査ログ生成エラー: {e}")
            return None
    
    def save_kpi_csv(self, kpi_results, start_date, end_date):
        """KPI結果をCSV保存"""
        print("=== KPI結果CSV保存 ===")
        
        try:
            if kpi_results is None or kpi_results.empty:
                print("KPI結果が空です")
                return None
            
            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_file = f"{output_dir}/kpi_results_{start_date}_{end_date}_{timestamp}.csv"
            
            kpi_results.to_csv(csv_file, index=False, encoding='utf-8-sig')
            
            print(f"KPI結果CSV保存完了: {csv_file}")
            
            return csv_file
            
        except Exception as e:
            print(f"KPI結果CSV保存エラー: {e}")
            return None
    
    def run_production_pipeline(self, start_date="2024-11-02", end_date="2025-09-28"):
        """本番パイプライン実行"""
        print("=== 本番パイプライン実行 ===")
        
        try:
            # 1) DQゲート
            if not self.assert_fe_gate(start_date, end_date):
                return False
            
            # 2) KPI計算
            kpi_results = self.calculate_kpi(start_date, end_date)
            if kpi_results is None:
                return False
            
            # 3) 監査ログ生成
            audit_file = self.generate_audit_log(start_date, end_date, kpi_results)
            
            # 4) KPI結果CSV保存
            csv_file = self.save_kpi_csv(kpi_results, start_date, end_date)
            
            print("\n✅ 本番パイプライン完了")
            print(f"監査ログ: {audit_file}")
            print(f"KPI結果: {csv_file}")
            
            return True
            
        except Exception as e:
            print(f"本番パイプラインエラー: {e}")
            return False

def main():
    pipeline = ProductionPipeline()
    success = pipeline.run_production_pipeline()
    
    if success:
        print("\n🎉 本番パイプライン成功 - 分析完了！")
    else:
        print("\n❌ 本番パイプライン失敗")

if __name__ == "__main__":
    main()




