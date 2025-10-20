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

class FinalStablePatch:
    """最終安定パッチ - 無限ループを物理的に止める"""
    
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
    
    def create_roi_lock(self):
        """1) 列ロック（SQLite）"""
        print("=== 列ロック作成 ===")
        
        try:
            cursor = self.conn.cursor()
            
            # ROI対象フラグを追加
            try:
                cursor.execute("ALTER TABLE SE_FE ADD COLUMN roi_lock INTEGER")
                print("roi_lock列追加")
            except:
                print("roi_lock列は既に存在")
            
            # 全件にROI対象フラグを設定
            cursor.execute("UPDATE SE_FE SET roi_lock = 1")
            print("ROI対象フラグ設定完了")
            
            # ROI計算用ビューを作成（ZI/ZM完全遮断）
            cursor.execute("""
            DROP VIEW IF EXISTS V_ROI_INPUT
            """)
            
            cursor.execute("""
            CREATE VIEW V_ROI_INPUT AS
            SELECT
              SourceDate as race_id,
              HorseNameS as horse_id,
              CAST(Chaku AS INTEGER) as finish,
              win_pay_yen,
              plc_pay_yen_low,
              roi_lock
            FROM SE_FE
            WHERE roi_lock = 1
            """)
            print("V_ROI_INPUTビュー作成完了")
            
            self.conn.commit()
            print("列ロック作成完了")
            
            return True
            
        except Exception as e:
            print(f"列ロック作成エラー: {e}")
            return False
    
    def calculate_roi_fixed(self, start_date="2024-11-02", end_date="2025-09-28"):
        """2) ROI計算（円ベースのみ／ZI・ZM完全遮断）"""
        print("=== ROI計算（固定列のみ） ===")
        
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
            FROM V_ROI_INPUT
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
            FROM V_ROI_INPUT
            WHERE race_id >= ? AND race_id <= ?
            AND plc_pay_yen_low IS NOT NULL
            """
            result_fukusho = pd.read_sql_query(query_fukusho, self.conn, params=[start_date_norm, end_date_norm])
            
            # 結果を結合
            kpi_results = pd.concat([result_tansho, result_fukusho], ignore_index=True)
            
            print("固定列ROI計算結果:")
            print(kpi_results.to_string(index=False))
            
            return kpi_results
            
        except Exception as e:
            print(f"固定列ROI計算エラー: {e}")
            return None
    
    def check_plausible_range(self, kpi_results):
        """3) 常識レンジで強制ブレーキ"""
        print("=== 常識レンジ監査 ===")
        
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
            print(f"常識レンジ監査エラー: {e}")
            return False
    
    def run_unit_tests(self):
        """4) ユニットテスト"""
        print("=== ユニットテスト ===")
        
        try:
            # テスト1: 払戻列は整数（円）であるべき
            query_test1 = """
            SELECT CASE WHEN SUM(CASE WHEN win_pay_yen = CAST(win_pay_yen AS INTEGER) THEN 0 ELSE 1 END) > 0
              THEN 'FAIL: win_pay_yen has non-integer values'
              ELSE 'PASS: win_pay_yen is integer'
            END as test1_result
            FROM V_ROI_INPUT
            WHERE win_pay_yen IS NOT NULL
            """
            result_test1 = pd.read_sql_query(query_test1, self.conn)
            print(f"テスト1: {result_test1.iloc[0]['test1_result']}")
            
            # テスト2: 代表日を1日選び、理論上の上限/下限で暴れないこと
            query_test2 = """
            SELECT 
              MAX(win_pay_yen) as max_win_pay,
              MIN(CASE WHEN finish = 1 THEN win_pay_yen END) as min_win_pay
            FROM V_ROI_INPUT
            WHERE race_id = '20250928'
            AND win_pay_yen IS NOT NULL
            """
            result_test2 = pd.read_sql_query(query_test2, self.conn)
            
            max_win_pay = result_test2.iloc[0]['max_win_pay']
            min_win_pay = result_test2.iloc[0]['min_win_pay']
            
            print(f"テスト2: 最大払戻={max_win_pay}, 最小払戻={min_win_pay}")
            
            if max_win_pay > 30000:
                print("❌ テスト2失敗: win_pay_yen too large")
                return False
            
            if min_win_pay < 100:
                print("❌ テスト2失敗: win_pay_yen too small")
                return False
            
            print("✅ ユニットテスト完了")
            return True
            
        except Exception as e:
            print(f"ユニットテストエラー: {e}")
            return False
    
    def show_sample_data(self):
        """5) サンプルデータ表示"""
        print("=== サンプルデータ表示 ===")
        
        try:
            # V_ROI_INPUTの小さなサンプル（10行）
            query_sample = """
            SELECT 
              race_id,
              horse_id,
              finish,
              win_pay_yen,
              plc_pay_yen_low
            FROM V_ROI_INPUT
            WHERE win_pay_yen IS NOT NULL
            ORDER BY race_id DESC
            LIMIT 10
            """
            result_sample = pd.read_sql_query(query_sample, self.conn)
            
            print("V_ROI_INPUTサンプル（10行）:")
            print(result_sample.to_string(index=False))
            
            return result_sample
            
        except Exception as e:
            print(f"サンプルデータ表示エラー: {e}")
            return None
    
    def run_final_stable_patch(self, start_date="2024-11-02", end_date="2025-09-28"):
        """最終安定パッチ実行"""
        print("=== 最終安定パッチ実行 ===")
        
        try:
            # 1) 列ロック作成
            if not self.create_roi_lock():
                return False
            
            # 2) ROI計算（固定列のみ）
            kpi_results = self.calculate_roi_fixed(start_date, end_date)
            if kpi_results is None:
                return False
            
            # 3) 常識レンジ監査
            if not self.check_plausible_range(kpi_results):
                print("❌ 常識レンジ外のため停止")
                return False
            
            # 4) ユニットテスト
            if not self.run_unit_tests():
                return False
            
            # 5) サンプルデータ表示
            self.show_sample_data()
            
            print("✅ 最終安定パッチ完了")
            return True
            
        except Exception as e:
            print(f"最終安定パッチエラー: {e}")
            return False

def main():
    patch = FinalStablePatch()
    success = patch.run_final_stable_patch()
    
    if success:
        print("\n✅ 最終安定パッチ成功")
    else:
        print("\n❌ 最終安定パッチ失敗")

if __name__ == "__main__":
    main()




