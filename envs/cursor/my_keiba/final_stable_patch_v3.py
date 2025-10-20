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

class FinalStablePatchV3:
    """最終安定パッチ v3 - 無限ループを物理的に止める"""
    
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
    
    def create_roi_lock_v3(self):
        """1) 列ロック v3（SQLite）"""
        print("=== 列ロック v3作成 ===")
        
        try:
            cursor = self.conn.cursor()
            
            # ROI対象フラグを追加
            try:
                cursor.execute("ALTER TABLE SE_FE ADD COLUMN roi_lock_v3 INTEGER")
                print("roi_lock_v3列追加")
            except:
                print("roi_lock_v3列は既に存在")
            
            # 全件にROI対象フラグを設定
            cursor.execute("UPDATE SE_FE SET roi_lock_v3 = 1")
            print("ROI対象フラグ設定完了")
            
            # ROI計算用ビューを作成（ZI/ZM完全遮断）
            cursor.execute("""
            DROP VIEW IF EXISTS V_ROI_INPUT_V3
            """)
            
            cursor.execute("""
            CREATE VIEW V_ROI_INPUT_V3 AS
            SELECT
              SourceDate as race_id,
              HorseNameS as horse_id,
              CAST(Chaku AS INTEGER) as finish,
              win_pay_yen,
              plc_pay_yen_low,
              roi_lock_v3
            FROM SE_FE
            WHERE roi_lock_v3 = 1
            """)
            print("V_ROI_INPUT_V3ビュー作成完了")
            
            self.conn.commit()
            print("列ロック v3作成完了")
            
            return True
            
        except Exception as e:
            print(f"列ロック v3作成エラー: {e}")
            return False
    
    def calculate_roi_fixed_v3(self, start_date="2024-11-02", end_date="2025-09-28"):
        """2) ROI計算 v3（円ベースのみ／ZI・ZM完全遮断）"""
        print("=== ROI計算 v3（固定列のみ） ===")
        
        try:
            start_date_norm = start_date.replace('-', '')
            end_date_norm = end_date.replace('-', '')
            
            # 単勝KPI（固定列のみ）
            query_tansho = """
            SELECT
                'tansho' AS bettype,
                COUNT(*) AS bets,
                COUNT(*) * 100 AS stake_yen,
                SUM(CASE WHEN finish = 1 AND win_pay_yen IS NOT NULL THEN win_pay_yen ELSE 0 END) AS payoff_yen,
                ROUND(100.0 * SUM(CASE WHEN finish = 1 AND win_pay_yen IS NOT NULL THEN win_pay_yen ELSE 0 END)
                      / NULLIF(COUNT(*) * 100.0, 0), 2) AS roi_pct
            FROM V_ROI_INPUT_V3
            WHERE race_id >= ? AND race_id <= ?
            AND win_pay_yen IS NOT NULL
            """
            result_tansho = pd.read_sql_query(query_tansho, self.conn, params=[start_date_norm, end_date_norm])
            
            # 複勝KPI（固定列のみ）
            query_fukusho = """
            SELECT
                'fukusho' AS bettype,
                COUNT(*) AS bets,
                COUNT(*) * 100 AS stake_yen,
                SUM(CASE WHEN finish BETWEEN 1 AND 3 AND plc_pay_yen_low IS NOT NULL THEN plc_pay_yen_low ELSE 0 END) AS payoff_yen,
                ROUND(100.0 * SUM(CASE WHEN finish BETWEEN 1 AND 3 AND plc_pay_yen_low IS NOT NULL THEN plc_pay_yen_low ELSE 0 END)
                      / NULLIF(COUNT(*) * 100.0, 0), 2) AS roi_pct
            FROM V_ROI_INPUT_V3
            WHERE race_id >= ? AND race_id <= ?
            AND plc_pay_yen_low IS NOT NULL
            """
            result_fukusho = pd.read_sql_query(query_fukusho, self.conn, params=[start_date_norm, end_date_norm])
            
            # 結果を結合
            kpi_results = pd.concat([result_tansho, result_fukusho], ignore_index=True)
            
            print("固定列ROI計算結果 v3:")
            print(kpi_results.to_string(index=False))
            
            return kpi_results
            
        except Exception as e:
            print(f"固定列ROI計算エラー v3: {e}")
            return None
    
    def check_plausible_range_v3(self, kpi_results):
        """3) 常識レンジで強制ブレーキ v3"""
        print("=== 常識レンジ監査 v3 ===")
        
        try:
            if kpi_results is None or kpi_results.empty:
                print("KPI結果が空です")
                return False
            
            # 単勝・複勝のROIを取得
            tansho_roi = kpi_results[kpi_results['bettype'] == 'tansho']['roi_pct'].iloc[0]
            fukusho_roi = kpi_results[kpi_results['bettype'] == 'fukusho']['roi_pct'].iloc[0]
            
            print(f"単勝ROI: {tansho_roi}%")
            print(f"複勝ROI: {fukusho_roi}%")
            
            # 常識レンジチェック
            if tansho_roi < 30.0 or tansho_roi > 130.0:
                print(f"❌ 単勝ROIが常識レンジ外: {tansho_roi}% (30-130%)")
                return False
            
            if fukusho_roi < 40.0 or fukusho_roi > 160.0:
                print(f"❌ 複勝ROIが常識レンジ外: {fukusho_roi}% (40-160%)")
                return False
            
            print("✅ ROIが常識レンジ内")
            return True
            
        except Exception as e:
            print(f"常識レンジ監査エラー v3: {e}")
            return False
    
    def show_sample_data_v3(self):
        """4) サンプルデータ表示 v3"""
        print("=== サンプルデータ表示 v3 ===")
        
        try:
            # V_ROI_INPUT_V3の小さなサンプル（10行）
            query_sample = """
            SELECT 
              race_id,
              horse_id,
              finish,
              win_pay_yen,
              plc_pay_yen_low
            FROM V_ROI_INPUT_V3
            WHERE win_pay_yen IS NOT NULL
            ORDER BY race_id DESC
            LIMIT 10
            """
            result_sample = pd.read_sql_query(query_sample, self.conn)
            
            print("V_ROI_INPUT_V3サンプル（10行）:")
            print(result_sample.to_string(index=False))
            
            return result_sample
            
        except Exception as e:
            print(f"サンプルデータ表示エラー v3: {e}")
            return None
    
    def run_final_stable_patch_v3(self, start_date="2024-11-02", end_date="2025-09-28"):
        """最終安定パッチ v3実行"""
        print("=== 最終安定パッチ v3実行 ===")
        
        try:
            # 1) 列ロック v3作成
            if not self.create_roi_lock_v3():
                return False
            
            # 2) ROI計算 v3（固定列のみ）
            kpi_results = self.calculate_roi_fixed_v3(start_date, end_date)
            if kpi_results is None:
                return False
            
            # 3) 常識レンジ監査 v3
            if not self.check_plausible_range_v3(kpi_results):
                print("❌ 常識レンジ外のため停止")
                return False
            
            # 4) サンプルデータ表示 v3
            self.show_sample_data_v3()
            
            print("✅ 最終安定パッチ v3完了")
            return True
            
        except Exception as e:
            print(f"最終安定パッチ v3エラー: {e}")
            return False

def main():
    patch = FinalStablePatchV3()
    success = patch.run_final_stable_patch_v3()
    
    if success:
        print("\n✅ 最終安定パッチ v3成功")
    else:
        print("\n❌ 最終安定パッチ v3失敗")

if __name__ == "__main__":
    main()




