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

class FixOddsNormalization:
    """確定オッズの表記ゆれ（3方式）を正しく円に直す"""
    
    def __init__(self, db_path="ecore.db"):
        self.db_path = db_path
        self.conn = None
        self.connect()
    
    def connect(self):
        """データベース接続"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            print("ecore.db接続成功")
        except Exception as e:
            print(f"ecore.db接続エラー: {e}")
            return False
        return True
    
    def normalize_odds_to_yen(self):
        """勝者の確定オッズ→払戻(円) に正規化（レース単位で自動判別）"""
        print("=== 勝者の確定オッズ→払戻(円) に正規化 ===")
        
        try:
            cursor = self.conn.cursor()
            
            # 勝者の生オッズをレース単位で取得（同着があっても最大値で代表）
            cursor.execute("""
            CREATE TEMP TABLE winners_raw AS
            SELECT
              Year || MonthDay as race_id,
              MAX(CASE WHEN CAST(KakuteiJyuni AS INTEGER) = 1 THEN CAST(Odds AS REAL) END) AS W
            FROM N_UMA_RACE
            WHERE Odds IS NOT NULL AND Odds != '0000'
            GROUP BY Year || MonthDay
            """)
            
            # ルール判定と払戻計算
            cursor.execute("""
            CREATE TEMP TABLE winners_pay AS
            SELECT
              r.race_id,
              CASE
                WHEN r.W IS NULL THEN NULL
                WHEN r.W >= 100 AND r.W = CAST(r.W AS INTEGER) AND (CAST(r.W AS INTEGER) % 10 = 0)
                  THEN CAST(r.W AS INTEGER)                                         -- R1: 円
                WHEN r.W < 100 AND ABS(r.W - CAST(r.W AS INTEGER)) > 0.0
                  THEN CAST(ROUND(r.W * 100) AS INTEGER)                             -- R2: 倍率(小数)
                WHEN r.W < 1000 AND r.W = CAST(r.W AS INTEGER) AND (CAST(r.W AS INTEGER) % 10 <> 0)
                  THEN CAST(CAST(r.W AS INTEGER) * 10 AS INTEGER)                    -- R3: 圧縮整数
                ELSE NULL                                                            -- 不明表記は除外
              END AS win_pay_yen_winner,
              CASE
                WHEN r.W IS NULL THEN 'MISS'
                WHEN r.W >= 100 AND r.W = CAST(r.W AS INTEGER) AND (CAST(r.W AS INTEGER) % 10 = 0) THEN 'R1_YEN'
                WHEN r.W < 100 AND ABS(r.W - CAST(r.W AS INTEGER)) > 0.0 THEN 'R2_DEC'
                WHEN r.W < 1000 AND r.W = CAST(r.W AS INTEGER) AND (CAST(r.W AS INTEGER) % 10 <> 0) THEN 'R3_PACK10'
                ELSE 'MISS'
              END AS rule_applied,
              r.W AS winner_odds_raw
            FROM winners_raw r
            """)
            
            # 有効レース集合
            cursor.execute("""
            CREATE TEMP TABLE valid_races AS
            SELECT race_id, win_pay_yen_winner
            FROM winners_pay
            WHERE win_pay_yen_winner IS NOT NULL
            """)
            
            # 診断（今どう判定されたか確認）
            query_diagnosis = """
            SELECT
              COUNT(*) AS total_races,
              SUM(CASE WHEN rule_applied='R1_YEN'   THEN 1 ELSE 0 END) AS r1_yen_races,
              SUM(CASE WHEN rule_applied='R2_DEC'   THEN 1 ELSE 0 END) AS r2_dec_races,
              SUM(CASE WHEN rule_applied='R3_PACK10'THEN 1 ELSE 0 END) AS r3_pack10_races,
              SUM(CASE WHEN rule_applied='MISS'     THEN 1 ELSE 0 END) AS miss_races,
              MIN(win_pay_yen_winner) AS min_winner_pay,
              MAX(win_pay_yen_winner) AS max_winner_pay
            FROM winners_pay
            """
            result_diagnosis = pd.read_sql_query(query_diagnosis, self.conn)
            
            print("診断結果:")
            print(f"  総レース数: {result_diagnosis.iloc[0]['total_races']}")
            print(f"  R1_YEN（円）: {result_diagnosis.iloc[0]['r1_yen_races']}")
            print(f"  R2_DEC（倍率小数）: {result_diagnosis.iloc[0]['r2_dec_races']}")
            print(f"  R3_PACK10（×10圧縮）: {result_diagnosis.iloc[0]['r3_pack10_races']}")
            print(f"  MISS（不明）: {result_diagnosis.iloc[0]['miss_races']}")
            print(f"  最小勝者払戻: {result_diagnosis.iloc[0]['min_winner_pay']}円")
            print(f"  最大勝者払戻: {result_diagnosis.iloc[0]['max_winner_pay']}円")
            
            # サニティチェック
            min_winner_pay = result_diagnosis.iloc[0]['min_winner_pay']
            max_winner_pay = result_diagnosis.iloc[0]['max_winner_pay']
            
            if min_winner_pay >= 100 and max_winner_pay <= 1000000:
                print("✅ サニティチェック通過")
                return True
            else:
                print("❌ サニティチェック失敗")
                return False
            
        except Exception as e:
            print(f"勝者の確定オッズ→払戻(円) 正規化エラー: {e}")
            return False
    
    def calculate_roi_valid_races_only(self, start_date="2024-11-02", end_date="2025-09-28"):
        """ROI（有効レースだけで計算）"""
        print("=== ROI（有効レースだけで計算） ===")
        
        try:
            start_date_norm = start_date.replace('-', '')
            end_date_norm = end_date.replace('-', '')
            
            # 期間を絞ってまず1日テスト
            query = f"""
            WITH scope AS (
              SELECT 
                Year || MonthDay as race_id,
                KettoNum as horse_id,
                CAST(KakuteiJyuni AS INTEGER) as finish,
                Odds
              FROM N_UMA_RACE
              WHERE Year || MonthDay >= '{start_date_norm[:8]}' AND Year || MonthDay <= '{end_date_norm[:8]}'
            ),
            valid_scope AS (
              SELECT s.*
              FROM scope s
              JOIN valid_races v ON v.race_id = s.race_id
            ),
            stake AS (
              SELECT COUNT(*)*100 AS stake_yen FROM valid_scope
            ),
            tansho_pay AS (
              SELECT SUM(CASE WHEN finish = 1 THEN v.win_pay_yen_winner ELSE 0 END) AS payoff_yen
              FROM valid_scope s
              JOIN valid_races v ON v.race_id = s.race_id
            ),
            KPI AS (
              SELECT
                'tansho' AS bettype,
                (SELECT stake_yen FROM stake) AS stake_yen,
                (SELECT payoff_yen FROM tansho_pay) AS payoff_yen,
                ROUND(100.0 * (SELECT payoff_yen FROM tansho_pay) / NULLIF((SELECT stake_yen FROM stake)*1.0,0), 2) AS roi_pct
            )
            SELECT * FROM KPI
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("ROI結果（有効レースのみ）:")
            print(result.to_string(index=False))
            
            return result
            
        except Exception as e:
            print(f"ROI計算エラー: {e}")
            return None
    
    def show_abnormal_races(self):
        """異常レース上位（最大払戻が大きいor小さい）"""
        print("=== 異常レース上位 ===")
        
        try:
            query = """
            SELECT *
            FROM winners_pay
            WHERE win_pay_yen_winner IS NOT NULL
            ORDER BY win_pay_yen_winner DESC
            LIMIT 10
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("異常レース上位（10件）:")
            print(result.to_string(index=False))
            
            return result
            
        except Exception as e:
            print(f"異常レース上位表示エラー: {e}")
            return None
    
    def show_winner_details(self, sample_day="20241102"):
        """有効レースの"勝者行"だけ一覧（当日の検証）"""
        print(f"=== 有効レースの勝者行一覧（{sample_day}） ===")
        
        try:
            query = f"""
            WITH scope AS (
              SELECT 
                Year || MonthDay as race_id,
                KettoNum as horse_id,
                CAST(KakuteiJyuni AS INTEGER) as finish,
                Odds
              FROM N_UMA_RACE
              WHERE Year || MonthDay = '{sample_day}'
            ),
            v AS (SELECT * FROM valid_races)
            SELECT s.race_id, s.horse_id, s.finish, s.Odds AS odds_raw,
                   v.win_pay_yen_winner
            FROM scope s JOIN v ON v.race_id=s.race_id
            WHERE s.finish=1
            ORDER BY s.race_id
            LIMIT 50
            """
            result = pd.read_sql_query(query, self.conn)
            
            print(f"有効レースの勝者行一覧（{sample_day}）:")
            print(result.to_string(index=False))
            
            return result
            
        except Exception as e:
            print(f"有効レースの勝者行一覧表示エラー: {e}")
            return None
    
    def run_fix_odds_normalization(self, start_date="2024-11-02", end_date="2025-09-28"):
        """確定オッズの表記ゆれ修正実行"""
        print("=== 確定オッズの表記ゆれ修正実行 ===")
        
        try:
            # 1) 勝者の確定オッズ→払戻(円) に正規化
            if not self.normalize_odds_to_yen():
                return False
            
            # 2) ROI（有効レースだけで計算）
            roi_result = self.calculate_roi_valid_races_only(start_date, end_date)
            if roi_result is None:
                return False
            
            # 3) 異常レース上位表示
            self.show_abnormal_races()
            
            # 4) 有効レースの勝者行一覧
            self.show_winner_details()
            
            print("✅ 確定オッズの表記ゆれ修正完了")
            return True
            
        except Exception as e:
            print(f"確定オッズの表記ゆれ修正実行エラー: {e}")
            return False

def main():
    fixer = FixOddsNormalization()
    success = fixer.run_fix_odds_normalization()
    
    if success:
        print("\n✅ 確定オッズの表記ゆれ修正成功")
    else:
        print("\n❌ 確定オッズの表記ゆれ修正失敗")

if __name__ == "__main__":
    main()




