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

class ValidationChecks:
    """TARGET frontier基準の検証可能な入力チェック"""
    
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
    
    def check_input_coverage(self):
        """1) 入力カバレッジ（Excel→標準スキーマに何列入った？）"""
        print("=== 入力カバレッジチェック ===")
        
        try:
            query = """
            SELECT 'mark5_imp' AS col, ROUND(100.0*AVG(CASE WHEN mark5_imp IS NOT NULL THEN 1 ELSE 0 END),2) AS filled_pct FROM SE_FE
            UNION ALL SELECT 'mark6_imp', ROUND(100.0*AVG(CASE WHEN mark6_imp IS NOT NULL THEN 1 ELSE 0 END),2) FROM SE_FE
            UNION ALL SELECT 'zm_odds_pred',ROUND(100.0*AVG(CASE WHEN zm_odds_pred IS NOT NULL THEN 1 ELSE 0 END),2) FROM SE_FE
            UNION ALL SELECT 'speed_rank',  ROUND(100.0*AVG(CASE WHEN speed_rank IS NOT NULL THEN 1 ELSE 0 END),2) FROM SE_FE
            UNION ALL SELECT 'race_roughness_idx', ROUND(100.0*AVG(CASE WHEN race_roughness_idx IS NOT NULL THEN 1 ELSE 0 END),2) FROM SE_FE
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("入力カバレッジ結果:")
            print(result.to_string(index=False))
            
            # 0%の列を特定
            zero_pct_cols = result[result['filled_pct'] == 0.0]['col'].tolist()
            if zero_pct_cols:
                print(f"\n❌ 0%の列（Excelに載ってない or 見出しが違う）: {zero_pct_cols}")
                print("→ alias_config.jsonに追記すれば埋まる")
            else:
                print("\n✅ 全列にデータが入っています")
            
            return result
            
        except Exception as e:
            print(f"入力カバレッジチェックエラー: {e}")
            return None
    
    def check_minimum_requirements(self):
        """2) 最小要件が揃ってるか（これが揃えばROIは出せる）"""
        print("=== 最小要件チェック ===")
        
        try:
            # RA(date,race_id) が期間内で埋まる
            query_ra = """
            SELECT 
                COUNT(*) as ra_count,
                MIN(date) as min_date,
                MAX(date) as max_date
            FROM RA
            WHERE date >= '2024-11-02' AND date <= '2025-09-28'
            """
            ra_result = pd.read_sql_query(query_ra, self.conn)
            
            print("RAテーブル確認:")
            print(f"  レース数: {ra_result.iloc[0]['ra_count']}")
            print(f"  期間: {ra_result.iloc[0]['min_date']} ～ {ra_result.iloc[0]['max_date']}")
            
            # SE_FE(race_id, horse_id, finish, win_pay_yen, plc_pay_yen_low) がNULLでも動く形
            query_se = """
            SELECT 
                COUNT(*) as total_records,
                COUNT(CASE WHEN race_id IS NOT NULL THEN 1 END) as race_id_count,
                COUNT(CASE WHEN horse_id IS NOT NULL THEN 1 END) as horse_id_count,
                COUNT(CASE WHEN finish IS NOT NULL THEN 1 END) as finish_count,
                COUNT(CASE WHEN win_pay_yen IS NOT NULL THEN 1 END) as win_pay_count,
                COUNT(CASE WHEN plc_pay_yen_low IS NOT NULL THEN 1 END) as plc_pay_count
            FROM SE_FE
            """
            se_result = pd.read_sql_query(query_se, self.conn)
            
            print("\nSE_FEテーブル確認:")
            print(f"  総レコード数: {se_result.iloc[0]['total_records']}")
            print(f"  race_id: {se_result.iloc[0]['race_id_count']}")
            print(f"  horse_id: {se_result.iloc[0]['horse_id_count']}")
            print(f"  finish: {se_result.iloc[0]['finish_count']}")
            print(f"  win_pay_yen: {se_result.iloc[0]['win_pay_count']}")
            print(f"  plc_pay_yen_low: {se_result.iloc[0]['plc_pay_count']}")
            
            # finishは必須
            if se_result.iloc[0]['finish_count'] == 0:
                print("❌ finish列が必須ですが存在しません")
                return False
            
            print("\n✅ 最小要件は揃っています")
            return True
            
        except Exception as e:
            print(f"最小要件チェックエラー: {e}")
            return False
    
    def check_reality_range(self, test_date="2024-11-02"):
        """3) 現実レンジ（1日だけ canary）"""
        print(f"=== 現実レンジチェック（{test_date}） ===")
        
        try:
            query = f"""
            WITH D AS (
              SELECT se.*, ra.date
              FROM V_ROI_INPUT_FINAL se 
              JOIN RA ra ON ra.race_id = se.race_id
              WHERE ra.date='{test_date}'
            )
            SELECT
              'tansho' AS bet, COUNT(*) bets, COUNT(*)*100 stake,
              SUM(CASE WHEN finish=1 THEN win_pay_yen ELSE 0 END) payoff,
              ROUND(100.0*SUM(CASE WHEN finish=1 THEN win_pay_yen ELSE 0 END)/NULLIF(COUNT(*)*100.0,0),2) roi_pct
            FROM D
            UNION ALL
            SELECT
              'fukusho', COUNT(*), COUNT(*)*100,
              SUM(CASE WHEN finish BETWEEN 1 AND 3 THEN plc_pay_yen_low ELSE 0 END),
              ROUND(100.0*SUM(CASE WHEN finish BETWEEN 1 AND 3 THEN plc_pay_yen_low ELSE 0 END)/NULLIF(COUNT(*)*100.0,0),2)
            FROM D
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("現実レンジチェック結果:")
            print(result.to_string(index=False))
            
            # 常識圏チェック
            tansho_roi = result[result['bet'] == 'tansho']['roi_pct'].iloc[0]
            fukusho_roi = result[result['bet'] == 'fukusho']['roi_pct'].iloc[0]
            
            print(f"\n常識圏チェック:")
            print(f"  単勝ROI: {tansho_roi}% (目安: 70-95%)")
            print(f"  複勝ROI: {fukusho_roi}% (目安: 80-100%)")
            
            if 70 <= tansho_roi <= 95 and 80 <= fukusho_roi <= 100:
                print("✅ 現実レンジ内")
                return True
            else:
                print("❌ 現実レンジ外")
                return False
            
        except Exception as e:
            print(f"現実レンジチェックエラー: {e}")
            return False
    
    def check_se_fe_sample(self):
        """SE_FEの中身を10行見る"""
        print("=== SE_FEサンプル（10行） ===")
        
        try:
            query = """
            SELECT 
              race_id, horse_id, finish, win_pay_yen, plc_pay_yen_low,
              mark5_imp, mark6_imp, zm_odds_pred, speed_rank, race_roughness_idx
            FROM SE_FE
            WHERE finish IS NOT NULL
            ORDER BY race_id DESC
            LIMIT 10
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("SE_FEサンプル:")
            print(result.to_string(index=False))
            
            return result
            
        except Exception as e:
            print(f"SE_FEサンプル表示エラー: {e}")
            return None
    
    def check_v_roi_input_sample(self):
        """V_ROI_INPUTから同じ10行を見る"""
        print("=== V_ROI_INPUT_FINALサンプル（10行） ===")
        
        try:
            query = """
            SELECT 
              race_id, horse_id, finish, win_pay_yen, plc_pay_yen_low
            FROM V_ROI_INPUT_FINAL
            WHERE finish IS NOT NULL
            ORDER BY race_id DESC
            LIMIT 10
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("V_ROI_INPUT_FINALサンプル:")
            print(result.to_string(index=False))
            
            return result
            
        except Exception as e:
            print(f"V_ROI_INPUT_FINALサンプル表示エラー: {e}")
            return None
    
    def run_validation_checks(self):
        """検証チェック実行"""
        print("=== TARGET frontier基準の検証チェック実行 ===")
        
        try:
            # 1) 入力カバレッジ
            coverage_result = self.check_input_coverage()
            if coverage_result is None:
                return False
            
            # 2) 最小要件
            if not self.check_minimum_requirements():
                return False
            
            # 3) 現実レンジ
            if not self.check_reality_range():
                return False
            
            # 4) SE_FEサンプル
            self.check_se_fe_sample()
            
            # 5) V_ROI_INPUTサンプル
            self.check_v_roi_input_sample()
            
            print("\n✅ 全チェック完了")
            return True
            
        except Exception as e:
            print(f"検証チェック実行エラー: {e}")
            return False

def main():
    validator = ValidationChecks()
    success = validator.run_validation_checks()
    
    if success:
        print("\n✅ 検証チェック成功")
    else:
        print("\n❌ 検証チェック失敗")

if __name__ == "__main__":
    main()




