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

class ROICalculationFixed:
    """ROI計算固定版 - 列固定で事故防止"""
    
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
    
    def create_roi_lock_final(self):
        """最終ROIロック作成"""
        print("=== 最終ROIロック作成 ===")
        
        try:
            cursor = self.conn.cursor()
            
            # ROI対象フラグを追加
            try:
                cursor.execute("ALTER TABLE SE_FE ADD COLUMN roi_lock_final INTEGER")
                print("roi_lock_final列追加")
            except:
                print("roi_lock_final列は既に存在")
            
            # 全件にROI対象フラグを設定
            cursor.execute("UPDATE SE_FE SET roi_lock_final = 1")
            print("ROI対象フラグ設定完了")
            
            # ROI計算用ビューを作成（ZI/ZM完全遮断）
            cursor.execute("""
            DROP VIEW IF EXISTS V_ROI_INPUT_FINAL
            """)
            
            cursor.execute("""
            CREATE VIEW V_ROI_INPUT_FINAL AS
            SELECT
              SourceDate as race_id,
              HorseNameS as horse_id,
              CAST(Chaku AS INTEGER) as finish,
              win_pay_yen,
              plc_pay_yen_low,
              roi_lock_final
            FROM SE_FE
            WHERE roi_lock_final = 1
            """)
            print("V_ROI_INPUT_FINALビュー作成完了")
            
            self.conn.commit()
            print("最終ROIロック作成完了")
            
            return True
            
        except Exception as e:
            print(f"最終ROIロック作成エラー: {e}")
            return False
    
    def calculate_roi_fixed_final(self, start_date="2024-11-02", end_date="2025-09-28"):
        """最終ROI計算（列固定）"""
        print("=== 最終ROI計算（列固定） ===")
        
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
            FROM V_ROI_INPUT_FINAL
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
            FROM V_ROI_INPUT_FINAL
            WHERE race_id >= ? AND race_id <= ?
            AND plc_pay_yen_low IS NOT NULL
            """
            result_fukusho = pd.read_sql_query(query_fukusho, self.conn, params=[start_date_norm, end_date_norm])
            
            # 結果を結合
            kpi_results = pd.concat([result_tansho, result_fukusho], ignore_index=True)
            
            print("最終ROI計算結果（列固定）:")
            print(kpi_results.to_string(index=False))
            
            return kpi_results
            
        except Exception as e:
            print(f"最終ROI計算エラー: {e}")
            return None
    
    def check_plausible_range_final(self, kpi_results):
        """最終常識レンジ監査"""
        print("=== 最終常識レンジ監査 ===")
        
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
            print(f"最終常識レンジ監査エラー: {e}")
            return False
    
    def show_sample_data_final(self):
        """最終サンプルデータ表示"""
        print("=== 最終サンプルデータ表示 ===")
        
        try:
            # V_ROI_INPUT_FINALの小さなサンプル（10行）
            query_sample = """
            SELECT 
              race_id,
              horse_id,
              finish,
              win_pay_yen,
              plc_pay_yen_low
            FROM V_ROI_INPUT_FINAL
            WHERE win_pay_yen IS NOT NULL
            ORDER BY race_id DESC
            LIMIT 10
            """
            result_sample = pd.read_sql_query(query_sample, self.conn)
            
            print("V_ROI_INPUT_FINALサンプル（10行）:")
            print(result_sample.to_string(index=False))
            
            return result_sample
            
        except Exception as e:
            print(f"最終サンプルデータ表示エラー: {e}")
            return None
    
    def run_roi_calculation_fixed(self, start_date="2024-11-02", end_date="2025-09-28"):
        """最終ROI計算実行"""
        print("=== 最終ROI計算実行 ===")
        
        try:
            # 1) 最終ROIロック作成
            if not self.create_roi_lock_final():
                return False
            
            # 2) 最終ROI計算（列固定）
            kpi_results = self.calculate_roi_fixed_final(start_date, end_date)
            if kpi_results is None:
                return False
            
            # 3) 最終常識レンジ監査
            if not self.check_plausible_range_final(kpi_results):
                print("❌ 常識レンジ外のため停止")
                return False
            
            # 4) 最終サンプルデータ表示
            self.show_sample_data_final()
            
            print("✅ 最終ROI計算完了")
            return True
            
        except Exception as e:
            print(f"最終ROI計算実行エラー: {e}")
            return False

def main():
    calculator = ROICalculationFixed()
    success = calculator.run_roi_calculation_fixed()
    
    if success:
        print("\n✅ 最終ROI計算成功")
    else:
        print("\n❌ 最終ROI計算失敗")

if __name__ == "__main__":
    main()




