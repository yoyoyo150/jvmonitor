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

class CheckOddsZeroCause:
    """オッズが0の原因確認"""
    
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
    
    def check_odds_zero_races(self):
        """オッズが0のレース確認"""
        print("=== オッズが0のレース確認 ===")
        
        try:
            # オッズが0のレースの詳細確認
            query = """
            SELECT 
              Year || MonthDay as race_id,
              JyoCD,
              RaceNum,
              KettoNum,
              Bamei,
              CAST(KakuteiJyuni AS INTEGER) as finish,
              Odds,
              Honsyokin,
              Fukasyokin
            FROM N_UMA_RACE
            WHERE Year || MonthDay = '20241102'
            AND Odds = '0000'
            ORDER BY race_id, RaceNum
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("オッズが0のレース詳細（2024年11月2日）:")
            print("日付 | 場 | R | 血統番号 | 馬名 | 着順 | オッズ | 本賞金 | 複勝賞金")
            print("-" * 100)
            
            for _, row in result.iterrows():
                print(f"{row['race_id']} | {row['JyoCD']} | {row['RaceNum']}R | {row['KettoNum']} | {row['Bamei']} | {row['finish']}着 | {row['Odds']} | {row['Honsyokin']} | {row['Fukasyokin']}")
            
            return result
            
        except Exception as e:
            print(f"オッズが0のレース確認エラー: {e}")
            return None
    
    def check_race_completeness(self):
        """レースの完全性確認"""
        print("=== レースの完全性確認 ===")
        
        try:
            # レースの完全性確認
            query = """
            SELECT 
              Year || MonthDay as race_id,
              JyoCD,
              RaceNum,
              COUNT(*) as horse_count,
              SUM(CASE WHEN Odds = '0000' THEN 1 ELSE 0 END) as zero_odds_count,
              SUM(CASE WHEN Odds IS NULL OR Odds = '' THEN 1 ELSE 0 END) as null_odds_count,
              SUM(CASE WHEN CAST(KakuteiJyuni AS INTEGER) = 1 THEN 1 ELSE 0 END) as winner_count
            FROM N_UMA_RACE
            WHERE Year || MonthDay = '20241102'
            GROUP BY Year || MonthDay, JyoCD, RaceNum
            ORDER BY JyoCD, RaceNum
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("レースの完全性確認（2024年11月2日）:")
            print("日付 | 場 | R | 頭数 | オッズ0頭数 | オッズNULL頭数 | 1着頭数")
            print("-" * 80)
            
            for _, row in result.iterrows():
                print(f"{row['race_id']} | {row['JyoCD']} | {row['RaceNum']}R | {row['horse_count']} | {row['zero_odds_count']} | {row['null_odds_count']} | {row['winner_count']}")
            
            return result
            
        except Exception as e:
            print(f"レースの完全性確認エラー: {e}")
            return None
    
    def check_odds_distribution_by_race(self):
        """レース別オッズ分布確認"""
        print("=== レース別オッズ分布確認 ===")
        
        try:
            # レース別オッズ分布確認
            query = """
            SELECT 
              Year || MonthDay as race_id,
              JyoCD,
              RaceNum,
              Odds,
              COUNT(*) as count
            FROM N_UMA_RACE
            WHERE Year || MonthDay = '20241102'
            AND Odds IS NOT NULL
            GROUP BY Year || MonthDay, JyoCD, RaceNum, Odds
            ORDER BY JyoCD, RaceNum, CAST(Odds AS REAL)
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("レース別オッズ分布確認（2024年11月2日）:")
            print("日付 | 場 | R | オッズ | 件数")
            print("-" * 60)
            
            for _, row in result.iterrows():
                print(f"{row['race_id']} | {row['JyoCD']} | {row['RaceNum']}R | {row['Odds']} | {row['count']}")
            
            return result
            
        except Exception as e:
            print(f"レース別オッズ分布確認エラー: {e}")
            return None
    
    def run_check_odds_zero_cause(self):
        """オッズが0の原因確認実行"""
        print("=== オッズが0の原因確認実行 ===")
        
        try:
            # 1) オッズが0のレース確認
            zero_odds = self.check_odds_zero_races()
            if zero_odds is None:
                return False
            
            # 2) レースの完全性確認
            completeness = self.check_race_completeness()
            if completeness is None:
                return False
            
            # 3) レース別オッズ分布確認
            distribution = self.check_odds_distribution_by_race()
            if distribution is None:
                return False
            
            print("✅ オッズが0の原因確認完了")
            return True
            
        except Exception as e:
            print(f"オッズが0の原因確認実行エラー: {e}")
            return False

def main():
    checker = CheckOddsZeroCause()
    success = checker.run_check_odds_zero_cause()
    
    if success:
        print("\n✅ オッズが0の原因確認成功")
    else:
        print("\n❌ オッズが0の原因確認失敗")

if __name__ == "__main__":
    main()




