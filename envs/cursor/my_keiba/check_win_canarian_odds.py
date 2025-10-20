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

class CheckWinCanarianOdds:
    """ウインカーネリアンのTansho_Odds確認"""
    
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
    
    def check_win_canarian_odds(self):
        """ウインカーネリアンのTansho_Odds確認"""
        print("=== ウインカーネリアンのTansho_Odds確認 ===")
        
        try:
            # ウインカーネリアンのTansho_Odds確認
            query = """
            SELECT 
                SourceDate,
                HorseNameS,
                Chaku,
                Tansho_Odds,
                Fukusho_Odds,
                Tan_Odds,
                Fukusho_Odds_Lower,
                Fukusho_Odds_Upper,
                win_pay_yen,
                plc_pay_yen_low
            FROM SE_FE
            WHERE HorseNameS LIKE '%ウインカーネリアン%'
            ORDER BY SourceDate DESC
            LIMIT 10
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("ウインカーネリアンのTansho_Odds確認:")
            print(result.to_string(index=False))
            
            return result
            
        except Exception as e:
            print(f"ウインカーネリアンのTansho_Odds確認エラー: {e}")
            return None
    
    def check_odds_distribution(self):
        """Tansho_Odds分布確認"""
        print("=== Tansho_Odds分布確認 ===")
        
        try:
            # Tansho_Odds分布確認
            query = """
            SELECT 
                COUNT(*) as total_count,
                AVG(CAST(Tansho_Odds AS REAL)) as avg_value,
                MIN(CAST(Tansho_Odds AS REAL)) as min_value,
                MAX(CAST(Tansho_Odds AS REAL)) as max_value,
                COUNT(CASE WHEN CAST(Tansho_Odds AS REAL) < 10 THEN 1 END) as under_10_count,
                COUNT(CASE WHEN CAST(Tansho_Odds AS REAL) BETWEEN 10 AND 100 THEN 1 END) as between_10_100_count,
                COUNT(CASE WHEN CAST(Tansho_Odds AS REAL) > 100 THEN 1 END) as over_100_count
            FROM SE_FE
            WHERE Tansho_Odds IS NOT NULL
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("Tansho_Odds分布:")
            print(f"  総件数: {result.iloc[0]['total_count']}")
            print(f"  平均値: {result.iloc[0]['avg_value']:.2f}")
            print(f"  最小値: {result.iloc[0]['min_value']:.2f}")
            print(f"  最大値: {result.iloc[0]['max_value']:.2f}")
            print(f"  10未満: {result.iloc[0]['under_10_count']}")
            print(f"  10-100: {result.iloc[0]['between_10_100_count']}")
            print(f"  100超: {result.iloc[0]['over_100_count']}")
            
            return result
            
        except Exception as e:
            print(f"Tansho_Odds分布確認エラー: {e}")
            return None
    
    def show_sample_odds(self):
        """サンプルオッズ表示"""
        print("=== サンプルオッズ表示 ===")
        
        try:
            # サンプルオッズ表示
            query = """
            SELECT 
                SourceDate,
                HorseNameS,
                Chaku,
                Tansho_Odds,
                Fukusho_Odds,
                Tan_Odds
            FROM SE_FE
            WHERE Tansho_Odds IS NOT NULL
            ORDER BY SourceDate DESC
            LIMIT 20
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("サンプルオッズ表示（20件）:")
            print(result.to_string(index=False))
            
            return result
            
        except Exception as e:
            print(f"サンプルオッズ表示エラー: {e}")
            return None
    
    def run_check(self):
        """確認実行"""
        print("=== ウインカーネリアンのTansho_Odds確認実行 ===")
        
        try:
            # 1) ウインカーネリアンのTansho_Odds確認
            win_result = self.check_win_canarian_odds()
            if win_result is None:
                return False
            
            # 2) Tansho_Odds分布確認
            odds_result = self.check_odds_distribution()
            if odds_result is None:
                return False
            
            # 3) サンプルオッズ表示
            sample_result = self.show_sample_odds()
            if sample_result is None:
                return False
            
            print("✅ ウインカーネリアンのTansho_Odds確認完了")
            return True
            
        except Exception as e:
            print(f"ウインカーネリアンのTansho_Odds確認実行エラー: {e}")
            return False

def main():
    checker = CheckWinCanarianOdds()
    success = checker.run_check()
    
    if success:
        print("\n✅ ウインカーネリアンのTansho_Odds確認成功")
    else:
        print("\n❌ ウインカーネリアンのTansho_Odds確認失敗")

if __name__ == "__main__":
    main()




