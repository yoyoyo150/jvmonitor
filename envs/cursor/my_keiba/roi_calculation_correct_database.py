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

class ROICalculationCorrectDatabase:
    """正しいデータベース（race.db）でのROI計算"""
    
    def __init__(self, db_path="C:/JVLinkToSQLite/JVLinkToSQLiteArtifact/race.db"):
        self.db_path = db_path
        self.conn = None
        self.connect()
    
    def connect(self):
        """データベース接続"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            print("race.db接続成功")
        except Exception as e:
            print(f"race.db接続エラー: {e}")
            return False
        return True
    
    def check_database_structure(self):
        """データベース構造確認"""
        print("=== データベース構造確認 ===")
        
        try:
            # テーブル一覧取得
            query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            result = pd.read_sql_query(query, self.conn)
            
            print("テーブル一覧:")
            for _, row in result.iterrows():
                print(f"- {row['name']}")
            
            return result
            
        except Exception as e:
            print(f"データベース構造確認エラー: {e}")
            return None
    
    def check_race_data(self):
        """レースデータ確認"""
        print("=== レースデータ確認 ===")
        
        try:
            # レースデータ確認
            query = """
            SELECT 
              COUNT(*) as total_races,
              MIN(Year || MonthDay) as min_date,
              MAX(Year || MonthDay) as max_date
            FROM NL_RA_RACE
            WHERE Year || MonthDay = '20241102'
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("レースデータ確認（2024年11月2日）:")
            print("総レース数 | 最小日付 | 最大日付")
            print("-" * 50)
            
            for _, row in result.iterrows():
                print(f"{row['total_races']} | {row['min_date']} | {row['max_date']}")
            
            return result
            
        except Exception as e:
            print(f"レースデータ確認エラー: {e}")
            return None
    
    def check_odds_data(self):
        """オッズデータ確認"""
        print("=== オッズデータ確認 ===")
        
        try:
            # オッズデータ確認
            query = """
            SELECT 
              COUNT(*) as total_odds,
              MIN(Year || MonthDay) as min_date,
              MAX(Year || MonthDay) as max_date
            FROM NL_O1_ODDS_TANFUKUWAKU
            WHERE Year || MonthDay = '20241102'
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("オッズデータ確認（2024年11月2日）:")
            print("総オッズ数 | 最小日付 | 最大日付")
            print("-" * 50)
            
            for _, row in result.iterrows():
                print(f"{row['total_odds']} | {row['min_date']} | {row['max_date']}")
            
            return result
            
        except Exception as e:
            print(f"オッズデータ確認エラー: {e}")
            return None
    
    def calculate_roi_correct_database(self):
        """正しいデータベースでのROI計算"""
        print("=== 正しいデータベースでのROI計算 ===")
        
        try:
            # 正しいデータベースでのROI計算
            query = """
            WITH race_data AS (
              SELECT 
                r.Year || r.MonthDay as race_id,
                r.JyoCD,
                r.RaceNum,
                s.KettoNum,
                s.Umaban,
                s.Bamei,
                s.KakuteiJyuni,
                o.TansyoOdds,
                o.FukusyoOdds
              FROM NL_RA_RACE r
              JOIN NL_SE_RACE_UMA s ON s.Year = r.Year AND s.MonthDay = r.MonthDay 
                AND s.JyoCD = r.JyoCD AND s.RaceNum = r.RaceNum
              LEFT JOIN NL_O1_ODDS_TANFUKUWAKU o ON o.Year = r.Year AND o.MonthDay = r.MonthDay 
                AND o.JyoCD = r.JyoCD AND o.RaceNum = r.RaceNum AND o.Umaban = s.Umaban
              WHERE r.Year || r.MonthDay = '20241102'
              AND s.KakuteiJyuni IS NOT NULL 
              AND s.KakuteiJyuni != ''
            )
            SELECT
              'tansho' AS bettype,
              COUNT(*) AS bets,
              COUNT(*) * 100 AS stake_yen,
              SUM(CASE WHEN CAST(KakuteiJyuni AS INTEGER) = 1 AND TansyoOdds IS NOT NULL 
                THEN CAST(TansyoOdds AS INTEGER) * 100 ELSE 0 END) AS payoff_yen,
              ROUND(100.0 * SUM(CASE WHEN CAST(KakuteiJyuni AS INTEGER) = 1 AND TansyoOdds IS NOT NULL 
                THEN CAST(TansyoOdds AS INTEGER) * 100 ELSE 0 END) / NULLIF(COUNT(*) * 100.0, 0), 2) AS roi_pct
            FROM race_data
            UNION ALL
            SELECT
              'fukusho' AS bettype,
              COUNT(*) AS bets,
              COUNT(*) * 100 AS stake_yen,
              SUM(CASE WHEN CAST(KakuteiJyuni AS INTEGER) BETWEEN 1 AND 3 AND FukusyoOdds IS NOT NULL 
                THEN CAST(FukusyoOdds AS INTEGER) * 100 ELSE 0 END) AS payoff_yen,
              ROUND(100.0 * SUM(CASE WHEN CAST(KakuteiJyuni AS INTEGER) BETWEEN 1 AND 3 AND FukusyoOdds IS NOT NULL 
                THEN CAST(FukusyoOdds AS INTEGER) * 100 ELSE 0 END) / NULLIF(COUNT(*) * 100.0, 0), 2) AS roi_pct
            FROM race_data;
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("正しいデータベースでのROI計算結果（2024年11月2日）:")
            print("賭け種 | 賭け数 | 購入額 | 払戻額 | 回収率")
            print("-" * 60)
            
            for _, row in result.iterrows():
                print(f"{row['bettype']} | {row['bets']} | {row['stake_yen']}円 | {row['payoff_yen']}円 | {row['roi_pct']}%")
            
            return result
            
        except Exception as e:
            print(f"正しいデータベースでのROI計算エラー: {e}")
            return None
    
    def run_roi_calculation_correct(self):
        """正しいデータベースでのROI計算実行"""
        print("=== 正しいデータベースでのROI計算実行 ===")
        
        try:
            # 1) データベース構造確認
            structure = self.check_database_structure()
            if structure is None:
                return False
            
            # 2) レースデータ確認
            race_data = self.check_race_data()
            if race_data is None:
                return False
            
            # 3) オッズデータ確認
            odds_data = self.check_odds_data()
            if odds_data is None:
                return False
            
            # 4) 正しいデータベースでのROI計算
            roi_result = self.calculate_roi_correct_database()
            if roi_result is None:
                return False
            
            print("✅ 正しいデータベースでのROI計算完了")
            return True
            
        except Exception as e:
            print(f"正しいデータベースでのROI計算実行エラー: {e}")
            return False

def main():
    calculator = ROICalculationCorrectDatabase()
    success = calculator.run_roi_calculation_correct()
    
    if success:
        print("\n✅ 正しいデータベースでのROI計算成功")
    else:
        print("\n❌ 正しいデータベースでのROI計算失敗")

if __name__ == "__main__":
    main()




