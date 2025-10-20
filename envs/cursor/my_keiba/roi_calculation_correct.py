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

class ROICalculationCorrect:
    """正しいROI計算（3列固定）"""
    
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
    
    def create_roi_input_correct(self):
        """正しいROI入力ビュー作成（3列固定）"""
        print("=== 正しいROI入力ビュー作成（3列固定） ===")
        
        try:
            cursor = self.conn.cursor()
            
            # ROI計算用ビューを作成（3列固定）
            cursor.execute("""
            DROP VIEW IF EXISTS V_ROI_INPUT_CORRECT
            """)
            
            cursor.execute("""
            CREATE VIEW V_ROI_INPUT_CORRECT AS
            SELECT
              SourceDate as race_id,
              HorseNameS as horse_id,
              CAST(Chaku AS INTEGER) as finish,
              win_pay_yen,
              plc_pay_yen_low
            FROM SE_FE
            WHERE Chaku IS NOT NULL
            """)
            print("V_ROI_INPUT_CORRECTビュー作成完了")
            
            self.conn.commit()
            print("正しいROI入力ビュー作成完了")
            
            return True
            
        except Exception as e:
            print(f"正しいROI入力ビュー作成エラー: {e}")
            return False
    
    def calculate_roi_correct(self, start_date="2024-11-02", end_date="2025-09-28"):
        """正しいROI計算（3列固定）"""
        print("=== 正しいROI計算（3列固定） ===")
        
        try:
            start_date_norm = start_date.replace('-', '')
            end_date_norm = end_date.replace('-', '')
            
            # 単勝KPI（3列固定）
            query_tansho = """
            SELECT
                'tansho' AS bettype,
                COUNT(*) AS bets,
                COUNT(*) * 100 AS stake_yen,
                SUM(CASE WHEN finish = 1 AND win_pay_yen IS NOT NULL THEN win_pay_yen ELSE 0 END) AS payoff_yen,
                ROUND(100.0 * SUM(CASE WHEN finish = 1 AND win_pay_yen IS NOT NULL THEN win_pay_yen ELSE 0 END)
                      / NULLIF(COUNT(*) * 100.0, 0), 2) AS roi_pct
            FROM V_ROI_INPUT_CORRECT
            WHERE race_id >= ? AND race_id <= ?
            AND win_pay_yen IS NOT NULL
            """
            result_tansho = pd.read_sql_query(query_tansho, self.conn, params=[start_date_norm, end_date_norm])
            
            # 複勝KPI（3列固定）
            query_fukusho = """
            SELECT
                'fukusho' AS bettype,
                COUNT(*) AS bets,
                COUNT(*) * 100 AS stake_yen,
                SUM(CASE WHEN finish BETWEEN 1 AND 3 AND plc_pay_yen_low IS NOT NULL THEN plc_pay_yen_low ELSE 0 END) AS payoff_yen,
                ROUND(100.0 * SUM(CASE WHEN finish BETWEEN 1 AND 3 AND plc_pay_yen_low IS NOT NULL THEN plc_pay_yen_low ELSE 0 END)
                      / NULLIF(COUNT(*) * 100.0, 0), 2) AS roi_pct
            FROM V_ROI_INPUT_CORRECT
            WHERE race_id >= ? AND race_id <= ?
            AND plc_pay_yen_low IS NOT NULL
            """
            result_fukusho = pd.read_sql_query(query_fukusho, self.conn, params=[start_date_norm, end_date_norm])
            
            # 結果を結合
            kpi_results = pd.concat([result_tansho, result_fukusho], ignore_index=True)
            
            print("正しいROI計算結果（3列固定）:")
            print(kpi_results.to_string(index=False))
            
            return kpi_results
            
        except Exception as e:
            print(f"正しいROI計算エラー: {e}")
            return None
    
    def check_sanity_range(self, kpi_results):
        """サニティレンジチェック"""
        print("=== サニティレンジチェック ===")
        
        try:
            if kpi_results is None or kpi_results.empty:
                print("KPI結果が空です")
                return False
            
            # 単勝・複勝のROIを取得
            tansho_roi = kpi_results[kpi_results['bettype'] == 'tansho']['roi_pct'].iloc[0]
            fukusho_roi = kpi_results[kpi_results['bettype'] == 'fukusho']['roi_pct'].iloc[0]
            
            print(f"単勝ROI: {tansho_roi}%")
            print(f"複勝ROI: {fukusho_roi}%")
            
            # サニティレンジチェック
            if tansho_roi < 30.0 or tansho_roi > 130.0:
                print(f"❌ 単勝ROIが異常範囲外: {tansho_roi}% (30-130%)")
                return False
            
            if fukusho_roi < 40.0 or fukusho_roi > 160.0:
                print(f"❌ 複勝ROIが異常範囲外: {fukusho_roi}% (40-160%)")
                return False
            
            print("✅ サニティレンジ内")
            return True
            
        except Exception as e:
            print(f"サニティレンジチェックエラー: {e}")
            return False
    
    def show_sample_data(self):
        """サンプルデータ表示"""
        print("=== サンプルデータ表示 ===")
        
        try:
            # V_ROI_INPUT_CORRECTの小さなサンプル（10行）
            query_sample = """
            SELECT 
              race_id,
              horse_id,
              finish,
              win_pay_yen,
              plc_pay_yen_low
            FROM V_ROI_INPUT_CORRECT
            WHERE finish IS NOT NULL
            ORDER BY race_id DESC
            LIMIT 10
            """
            result_sample = pd.read_sql_query(query_sample, self.conn)
            
            print("V_ROI_INPUT_CORRECTサンプル（10行）:")
            print(result_sample.to_string(index=False))
            
            return result_sample
            
        except Exception as e:
            print(f"サンプルデータ表示エラー: {e}")
            return None
    
    def log_audit_info(self, kpi_results):
        """監査ログ記録"""
        print("=== 監査ログ記録 ===")
        
        try:
            audit_log = {
                "timestamp": datetime.now().isoformat(),
                "used_columns": ["Chaku", "win_pay_yen", "plc_pay_yen_low"],
                "calculation_method": "3列固定（正しい実装）",
                "kpi_results": kpi_results.to_dict('records') if kpi_results is not None else None,
                "sanity_check": "passed" if self.check_sanity_range(kpi_results) else "failed"
            }
            
            # 監査ログをJSONファイルに保存
            with open("audit_log_correct.json", "w", encoding="utf-8") as f:
                json.dump(audit_log, f, ensure_ascii=False, indent=2)
            
            print("監査ログ記録完了")
            return True
            
        except Exception as e:
            print(f"監査ログ記録エラー: {e}")
            return False
    
    def run_roi_calculation_correct(self, start_date="2024-11-02", end_date="2025-09-28"):
        """正しいROI計算実行"""
        print("=== 正しいROI計算実行 ===")
        
        try:
            # 1) 正しいROI入力ビュー作成
            if not self.create_roi_input_correct():
                return False
            
            # 2) 正しいROI計算（3列固定）
            kpi_results = self.calculate_roi_correct(start_date, end_date)
            if kpi_results is None:
                return False
            
            # 3) サニティレンジチェック
            if not self.check_sanity_range(kpi_results):
                print("❌ サニティレンジ外のため停止")
                return False
            
            # 4) サンプルデータ表示
            self.show_sample_data()
            
            # 5) 監査ログ記録
            self.log_audit_info(kpi_results)
            
            print("✅ 正しいROI計算完了")
            return True
            
        except Exception as e:
            print(f"正しいROI計算実行エラー: {e}")
            return False

def main():
    calculator = ROICalculationCorrect()
    success = calculator.run_roi_calculation_correct()
    
    if success:
        print("\n✅ 正しいROI計算成功")
    else:
        print("\n❌ 正しいROI計算失敗")

if __name__ == "__main__":
    main()




