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

class ShowSpecificWinnerData:
    """具体的な勝者データの表示"""
    
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
    
    def show_specific_winners(self):
        """具体的な勝者データの表示"""
        print("=== 具体的な勝者データの表示 ===")
        
        try:
            # 具体的な勝者データ（日付、レース、馬名、オッズ、払い戻し）
            query = """
            WITH scope AS (
              SELECT 
                Year || MonthDay as race_id,
                JyoCD,
                RaceNum,
                KettoNum,
                Bamei,
                CAST(KakuteiJyuni AS INTEGER) as finish,
                Odds
              FROM N_UMA_RACE
              WHERE Year || MonthDay = '20241102'
            ),
            v AS (SELECT * FROM valid_races)
            SELECT 
              s.race_id,
              s.JyoCD,
              s.RaceNum,
              s.KettoNum,
              s.Bamei,
              s.finish,
              s.Odds AS odds_raw,
              v.win_pay_yen_winner
            FROM scope s JOIN v ON v.race_id=s.race_id
            WHERE s.finish=1
            ORDER BY s.race_id, s.RaceNum
            LIMIT 20
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("具体的な勝者データ（2024年11月2日）:")
            print("日付 | 場 | R | 血統番号 | 馬名 | 着順 | オッズ | 払い戻し")
            print("-" * 80)
            
            for _, row in result.iterrows():
                print(f"{row['race_id']} | {row['JyoCD']} | {row['RaceNum']}R | {row['KettoNum']} | {row['Bamei']} | {row['finish']}着 | {row['odds_raw']} | {row['win_pay_yen_winner']}円")
            
            return result
            
        except Exception as e:
            print(f"具体的な勝者データ表示エラー: {e}")
            return None
    
    def show_odds_distribution(self):
        """オッズ分布の表示"""
        print("=== オッズ分布の表示 ===")
        
        try:
            # オッズ分布の確認
            query = """
            SELECT 
              Odds,
              COUNT(*) as count,
              MIN(Odds) as min_odds,
              MAX(Odds) as max_odds,
              AVG(CAST(Odds AS REAL)) as avg_odds
            FROM N_UMA_RACE
            WHERE Year || MonthDay = '20241102'
            AND Odds IS NOT NULL AND Odds != '0000'
            GROUP BY Odds
            ORDER BY CAST(Odds AS REAL)
            LIMIT 20
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("オッズ分布（2024年11月2日）:")
            print("オッズ | 件数 | 最小 | 最大 | 平均")
            print("-" * 50)
            
            for _, row in result.iterrows():
                print(f"{row['Odds']} | {row['count']} | {row['min_odds']} | {row['max_odds']} | {row['avg_odds']:.2f}")
            
            return result
            
        except Exception as e:
            print(f"オッズ分布表示エラー: {e}")
            return None
    
    def show_winner_odds_details(self):
        """勝者のオッズ詳細表示"""
        print("=== 勝者のオッズ詳細表示 ===")
        
        try:
            # 勝者のオッズ詳細
            query = """
            SELECT 
              Year || MonthDay as race_id,
              JyoCD,
              RaceNum,
              KettoNum,
              Bamei,
              Odds,
              CASE
                WHEN CAST(Odds AS REAL) >= 100 AND CAST(Odds AS REAL) = CAST(CAST(Odds AS REAL) AS INTEGER) AND (CAST(CAST(Odds AS REAL) AS INTEGER) % 10 = 0)
                  THEN 'R1_YEN'
                WHEN CAST(Odds AS REAL) < 100 AND ABS(CAST(Odds AS REAL) - CAST(CAST(Odds AS REAL) AS INTEGER)) > 0.0
                  THEN 'R2_DEC'
                WHEN CAST(Odds AS REAL) < 1000 AND CAST(Odds AS REAL) = CAST(CAST(Odds AS REAL) AS INTEGER) AND (CAST(CAST(Odds AS REAL) AS INTEGER) % 10 <> 0)
                  THEN 'R3_PACK10'
                ELSE 'MISS'
              END AS rule_applied
            FROM N_UMA_RACE
            WHERE Year || MonthDay = '20241102'
            AND CAST(KakuteiJyuni AS INTEGER) = 1
            ORDER BY race_id, RaceNum
            LIMIT 20
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("勝者のオッズ詳細（2024年11月2日）:")
            print("日付 | 場 | R | 血統番号 | 馬名 | オッズ | ルール")
            print("-" * 80)
            
            for _, row in result.iterrows():
                print(f"{row['race_id']} | {row['JyoCD']} | {row['RaceNum']}R | {row['KettoNum']} | {row['Bamei']} | {row['Odds']} | {row['rule_applied']}")
            
            return result
            
        except Exception as e:
            print(f"勝者のオッズ詳細表示エラー: {e}")
            return None
    
    def run_show_specific_data(self):
        """具体的なデータ表示実行"""
        print("=== 具体的なデータ表示実行 ===")
        
        try:
            # 1) 具体的な勝者データの表示
            winners = self.show_specific_winners()
            if winners is None:
                return False
            
            # 2) オッズ分布の表示
            odds_dist = self.show_odds_distribution()
            if odds_dist is None:
                return False
            
            # 3) 勝者のオッズ詳細表示
            winner_details = self.show_winner_odds_details()
            if winner_details is None:
                return False
            
            print("✅ 具体的なデータ表示完了")
            return True
            
        except Exception as e:
            print(f"具体的なデータ表示実行エラー: {e}")
            return False

def main():
    shower = ShowSpecificWinnerData()
    success = shower.run_show_specific_data()
    
    if success:
        print("\n✅ 具体的なデータ表示成功")
    else:
        print("\n❌ 具体的なデータ表示失敗")

if __name__ == "__main__":
    main()




