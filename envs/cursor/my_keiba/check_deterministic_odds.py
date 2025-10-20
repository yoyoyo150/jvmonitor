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

class CheckDeterministicOdds:
    """確定オッズ認識チェック"""
    
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
    
    def check_odds_columns(self):
        """オッズ列の確認"""
        print("=== オッズ列の確認 ===")
        
        try:
            # オッズ関連列の確認
            query_odds = """
            SELECT 
                COUNT(*) as total_records,
                COUNT(Tansho_Odds) as tansho_odds_count,
                COUNT(Fukusho_Odds) as fukusho_odds_count,
                COUNT(Tan_Odds) as tan_odds_count,
                COUNT(Fukusho_Odds_Lower) as fukusho_lower_count,
                COUNT(Fukusho_Odds_Upper) as fukusho_upper_count,
                AVG(CAST(Tansho_Odds AS REAL)) as tansho_avg,
                AVG(CAST(Fukusho_Odds AS REAL)) as fukusho_avg,
                AVG(CAST(Tan_Odds AS REAL)) as tan_avg
            FROM SE_FE
            WHERE Tansho_Odds IS NOT NULL OR Fukusho_Odds IS NOT NULL OR Tan_Odds IS NOT NULL
            """
            result_odds = pd.read_sql_query(query_odds, self.conn)
            
            print("オッズ列状況:")
            print(f"  総レコード数: {result_odds.iloc[0]['total_records']}")
            print(f"  Tansho_Odds列数: {result_odds.iloc[0]['tansho_odds_count']}")
            print(f"  Fukusho_Odds列数: {result_odds.iloc[0]['fukusho_odds_count']}")
            print(f"  Tan_Odds列数: {result_odds.iloc[0]['tan_odds_count']}")
            print(f"  Fukusho_Odds_Lower列数: {result_odds.iloc[0]['fukusho_lower_count']}")
            print(f"  Fukusho_Odds_Upper列数: {result_odds.iloc[0]['fukusho_upper_count']}")
            print(f"  Tansho_Odds平均: {result_odds.iloc[0]['tansho_avg']:.2f}")
            print(f"  Fukusho_Odds平均: {result_odds.iloc[0]['fukusho_avg']:.2f}")
            print(f"  Tan_Odds平均: {result_odds.iloc[0]['tan_avg']:.2f}")
            
            return result_odds
            
        except Exception as e:
            print(f"オッズ列確認エラー: {e}")
            return None
    
    def check_winning_horses_odds(self):
        """1着馬のオッズ確認"""
        print("=== 1着馬のオッズ確認 ===")
        
        try:
            # 1着馬のオッズ確認
            query_winning = """
            SELECT 
                SourceDate,
                HorseNameS,
                Chaku,
                Tansho_Odds,
                Fukusho_Odds,
                Tan_Odds,
                Fukusho_Odds_Lower,
                Fukusho_Odds_Upper
            FROM SE_FE
            WHERE CAST(Chaku AS INTEGER) = 1
            AND (Tansho_Odds IS NOT NULL OR Fukusho_Odds IS NOT NULL OR Tan_Odds IS NOT NULL)
            ORDER BY SourceDate DESC
            LIMIT 10
            """
            result_winning = pd.read_sql_query(query_winning, self.conn)
            
            print("1着馬のオッズサンプル（10件）:")
            print(result_winning.to_string(index=False))
            
            return result_winning
            
        except Exception as e:
            print(f"1着馬のオッズ確認エラー: {e}")
            return None
    
    def calculate_correct_roi(self):
        """正しいROI計算（確定オッズ使用）"""
        print("=== 正しいROI計算（確定オッズ使用） ===")
        
        try:
            # 単勝ROI計算（1着の単勝オッズを掛ける）
            query_tansho = """
            SELECT
                'tansho' AS bettype,
                COUNT(*) AS bets,
                COUNT(*) * 100 AS stake_yen,
                SUM(CASE 
                    WHEN CAST(Chaku AS INTEGER) = 1 AND Tansho_Odds IS NOT NULL 
                    THEN CAST(Tansho_Odds AS REAL) * 100 
                    ELSE 0 
                END) AS payoff_yen,
                ROUND(100.0 * SUM(CASE 
                    WHEN CAST(Chaku AS INTEGER) = 1 AND Tansho_Odds IS NOT NULL 
                    THEN CAST(Tansho_Odds AS REAL) * 100 
                    ELSE 0 
                END) / NULLIF(COUNT(*) * 100.0, 0), 2) AS roi_pct
            FROM SE_FE
            WHERE Tansho_Odds IS NOT NULL
            """
            result_tansho = pd.read_sql_query(query_tansho, self.conn)
            
            # 複勝ROI計算（1-3着の複勝オッズを掛ける）
            query_fukusho = """
            SELECT
                'fukusho' AS bettype,
                COUNT(*) AS bets,
                COUNT(*) * 100 AS stake_yen,
                SUM(CASE 
                    WHEN CAST(Chaku AS INTEGER) BETWEEN 1 AND 3 AND Fukusho_Odds_Lower IS NOT NULL 
                    THEN CAST(Fukusho_Odds_Lower AS REAL) * 100 
                    ELSE 0 
                END) AS payoff_yen,
                ROUND(100.0 * SUM(CASE 
                    WHEN CAST(Chaku AS INTEGER) BETWEEN 1 AND 3 AND Fukusho_Odds_Lower IS NOT NULL 
                    THEN CAST(Fukusho_Odds_Lower AS REAL) * 100 
                    ELSE 0 
                END) / NULLIF(COUNT(*) * 100.0, 0), 2) AS roi_pct
            FROM SE_FE
            WHERE Fukusho_Odds_Lower IS NOT NULL
            """
            result_fukusho = pd.read_sql_query(query_fukusho, self.conn)
            
            # 結果を結合
            kpi_results = pd.concat([result_tansho, result_fukusho], ignore_index=True)
            
            print("正しいROI計算結果（確定オッズ使用）:")
            print(kpi_results.to_string(index=False))
            
            return kpi_results
            
        except Exception as e:
            print(f"正しいROI計算エラー: {e}")
            return None
    
    def run_deterministic_odds_check(self):
        """確定オッズ認識チェック実行"""
        print("=== 確定オッズ認識チェック実行 ===")
        
        try:
            # 1) オッズ列の確認
            odds_result = self.check_odds_columns()
            if odds_result is None:
                return False
            
            # 2) 1着馬のオッズ確認
            winning_result = self.check_winning_horses_odds()
            if winning_result is None:
                return False
            
            # 3) 正しいROI計算
            roi_result = self.calculate_correct_roi()
            if roi_result is None:
                return False
            
            print("✅ 確定オッズ認識チェック完了")
            return True
            
        except Exception as e:
            print(f"確定オッズ認識チェック実行エラー: {e}")
            return False

def main():
    checker = CheckDeterministicOdds()
    success = checker.run_deterministic_odds_check()
    
    if success:
        print("\n✅ 確定オッズ認識チェック成功")
    else:
        print("\n❌ 確定オッズ認識チェック失敗")

if __name__ == "__main__":
    main()




