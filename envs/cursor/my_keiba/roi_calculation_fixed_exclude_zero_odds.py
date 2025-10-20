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

class ROICalculationFixedExcludeZeroOdds:
    """オッズが0のレースを除外したROI計算"""
    
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
    
    def calculate_roi_exclude_zero_odds(self):
        """オッズが0のレースを除外したROI計算"""
        print("=== オッズが0のレースを除外したROI計算 ===")
        
        try:
            # オッズが0のレースを除外したROI計算
            query = """
            WITH valid_races AS (
              SELECT DISTINCT
                Year || MonthDay as race_id,
                JyoCD,
                RaceNum
              FROM N_UMA_RACE
              WHERE Year || MonthDay = '20241102'
              AND Odds IS NOT NULL 
              AND Odds != '0000'
              AND Odds != ''
            ),
            valid_horses AS (
              SELECT 
                n.Year || n.MonthDay as race_id,
                n.KettoNum as horse_id,
                CAST(n.KakuteiJyuni AS INTEGER) as finish,
                n.Odds,
                CASE
                  WHEN CAST(n.Odds AS REAL) >= 100 AND CAST(n.Odds AS REAL) = CAST(CAST(n.Odds AS REAL) AS INTEGER) AND (CAST(CAST(n.Odds AS REAL) AS INTEGER) % 10 = 0)
                    THEN CAST(n.Odds AS INTEGER)
                  WHEN CAST(n.Odds AS REAL) < 100 AND ABS(CAST(n.Odds AS REAL) - CAST(CAST(n.Odds AS REAL) AS INTEGER)) > 0.0
                    THEN CAST(ROUND(CAST(n.Odds AS REAL) * 100) AS INTEGER)
                  WHEN CAST(n.Odds AS REAL) < 1000 AND CAST(n.Odds AS REAL) = CAST(CAST(n.Odds AS REAL) AS INTEGER) AND (CAST(CAST(n.Odds AS REAL) AS INTEGER) % 10 <> 0)
                    THEN CAST(CAST(n.Odds AS INTEGER) * 10 AS INTEGER)
                  ELSE NULL
                END AS win_pay_yen_winner
              FROM N_UMA_RACE n
              JOIN valid_races v ON v.race_id = n.Year || n.MonthDay 
                AND v.JyoCD = n.JyoCD 
                AND v.RaceNum = n.RaceNum
              WHERE n.Year || n.MonthDay = '20241102'
              AND n.KakuteiJyuni IS NOT NULL 
              AND n.KakuteiJyuni != ''
            )
            SELECT
              'tansho' AS bettype,
              COUNT(*) AS bets,
              COUNT(*) * 100 AS stake_yen,
              SUM(CASE WHEN finish = 1 AND win_pay_yen_winner IS NOT NULL THEN win_pay_yen_winner ELSE 0 END) AS payoff_yen,
              ROUND(100.0 * SUM(CASE WHEN finish = 1 AND win_pay_yen_winner IS NOT NULL THEN win_pay_yen_winner ELSE 0 END)
                           / NULLIF(COUNT(*) * 100.0, 0), 2) AS roi_pct
            FROM valid_horses
            UNION ALL
            SELECT
              'fukusho' AS bettype,
              COUNT(*) AS bets,
              COUNT(*) * 100 AS stake_yen,
              SUM(CASE WHEN finish BETWEEN 1 AND 3 AND win_pay_yen_winner IS NOT NULL THEN win_pay_yen_winner ELSE 0 END) AS payoff_yen,
              ROUND(100.0 * SUM(CASE WHEN finish BETWEEN 1 AND 3 AND win_pay_yen_winner IS NOT NULL THEN win_pay_yen_winner ELSE 0 END)
                           / NULLIF(COUNT(*) * 100.0, 0), 2) AS roi_pct
            FROM valid_horses;
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("オッズが0のレースを除外したROI計算結果（2024年11月2日）:")
            print("賭け種 | 賭け数 | 購入額 | 払戻額 | 回収率")
            print("-" * 60)
            
            for _, row in result.iterrows():
                print(f"{row['bettype']} | {row['bets']} | {row['stake_yen']}円 | {row['payoff_yen']}円 | {row['roi_pct']}%")
            
            return result
            
        except Exception as e:
            print(f"オッズが0のレースを除外したROI計算エラー: {e}")
            return None
    
    def check_valid_races_count(self):
        """有効レース数の確認"""
        print("=== 有効レース数の確認 ===")
        
        try:
            # 有効レース数の確認
            query = """
            WITH all_races AS (
              SELECT DISTINCT
                Year || MonthDay as race_id,
                JyoCD,
                RaceNum
              FROM N_UMA_RACE
              WHERE Year || MonthDay = '20241102'
            ),
            valid_races AS (
              SELECT DISTINCT
                Year || MonthDay as race_id,
                JyoCD,
                RaceNum
              FROM N_UMA_RACE
              WHERE Year || MonthDay = '20241102'
              AND Odds IS NOT NULL 
              AND Odds != '0000'
              AND Odds != ''
            )
            SELECT 
              (SELECT COUNT(*) FROM all_races) as total_races,
              (SELECT COUNT(*) FROM valid_races) as valid_races,
              (SELECT COUNT(*) FROM all_races) - (SELECT COUNT(*) FROM valid_races) as excluded_races
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("有効レース数の確認（2024年11月2日）:")
            print("総レース数 | 有効レース数 | 除外レース数")
            print("-" * 50)
            
            for _, row in result.iterrows():
                print(f"{row['total_races']} | {row['valid_races']} | {row['excluded_races']}")
            
            return result
            
        except Exception as e:
            print(f"有効レース数の確認エラー: {e}")
            return None
    
    def run_roi_calculation_fixed(self):
        """オッズが0のレースを除外したROI計算実行"""
        print("=== オッズが0のレースを除外したROI計算実行 ===")
        
        try:
            # 1) 有効レース数の確認
            race_count = self.check_valid_races_count()
            if race_count is None:
                return False
            
            # 2) オッズが0のレースを除外したROI計算
            roi_result = self.calculate_roi_exclude_zero_odds()
            if roi_result is None:
                return False
            
            print("✅ オッズが0のレースを除外したROI計算完了")
            return True
            
        except Exception as e:
            print(f"オッズが0のレースを除外したROI計算実行エラー: {e}")
            return False

def main():
    calculator = ROICalculationFixedExcludeZeroOdds()
    success = calculator.run_roi_calculation_fixed()
    
    if success:
        print("\n✅ オッズが0のレースを除外したROI計算成功")
    else:
        print("\n❌ オッズが0のレースを除外したROI計算失敗")

if __name__ == "__main__":
    main()




