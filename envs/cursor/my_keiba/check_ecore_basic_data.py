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

class CheckEcoreBasicData:
    """ecore.dbから基本データ確認"""
    
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
    
    def check_ecore_tables(self):
        """ecore.dbのテーブル確認"""
        print("=== ecore.dbのテーブル確認 ===")
        
        try:
            # テーブル一覧取得
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f"ecore.dbのテーブル一覧: {tables}")
            
            return tables
            
        except Exception as e:
            print(f"ecore.dbのテーブル確認エラー: {e}")
            return None
    
    def check_race_results(self):
        """レース結果データ確認"""
        print("=== レース結果データ確認 ===")
        
        try:
            # レース結果テーブルの確認
            query = """
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT JyoCD) as unique_courses,
                COUNT(DISTINCT RaceNum) as unique_races,
                COUNT(DISTINCT KettoNum) as unique_horses,
                COUNT(DISTINCT ChokyosiRyakusyo) as unique_trainers
            FROM N_UMA_RACE
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("レース結果データ:")
            print(f"  総レコード数: {result.iloc[0]['total_records']}")
            print(f"  ユニーク場数: {result.iloc[0]['unique_courses']}")
            print(f"  ユニークレース数: {result.iloc[0]['unique_races']}")
            print(f"  ユニーク馬数: {result.iloc[0]['unique_horses']}")
            print(f"  ユニーク調教師数: {result.iloc[0]['unique_trainers']}")
            
            return result
            
        except Exception as e:
            print(f"レース結果データ確認エラー: {e}")
            return None
    
    def check_odds_data(self):
        """オッズデータ確認"""
        print("=== オッズデータ確認 ===")
        
        try:
            # オッズデータの確認
            query = """
            SELECT 
                COUNT(*) as total_records,
                COUNT(TanshoOdds) as tansho_count,
                COUNT(FukushoOdds) as fukusho_count,
                AVG(CAST(TanshoOdds AS REAL)) as tansho_avg,
                AVG(CAST(FukushoOdds AS REAL)) as fukusho_avg,
                MIN(CAST(TanshoOdds AS REAL)) as tansho_min,
                MAX(CAST(TanshoOdds AS REAL)) as tansho_max
            FROM N_UMA_RACE
            WHERE TanshoOdds IS NOT NULL OR FukushoOdds IS NOT NULL
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("オッズデータ:")
            print(f"  総レコード数: {result.iloc[0]['total_records']}")
            print(f"  単勝オッズ数: {result.iloc[0]['tansho_count']}")
            print(f"  複勝オッズ数: {result.iloc[0]['fukusho_count']}")
            print(f"  単勝オッズ平均: {result.iloc[0]['tansho_avg']:.2f}")
            print(f"  複勝オッズ平均: {result.iloc[0]['fukusho_avg']:.2f}")
            print(f"  単勝オッズ範囲: {result.iloc[0]['tansho_min']:.2f} - {result.iloc[0]['tansho_max']:.2f}")
            
            return result
            
        except Exception as e:
            print(f"オッズデータ確認エラー: {e}")
            return None
    
    def show_sample_race_data(self):
        """サンプルレースデータ表示"""
        print("=== サンプルレースデータ表示 ===")
        
        try:
            # サンプルレースデータ表示
            query = """
            SELECT 
                JyoCD,
                RaceNum,
                KettoNum,
                Bamei,
                ChokyosiRyakusyo,
                KakuteiJyuni,
                TanshoOdds,
                FukushoOdds
            FROM N_UMA_RACE
            WHERE TanshoOdds IS NOT NULL
            ORDER BY JyoCD, RaceNum, KettoNum
            LIMIT 20
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("サンプルレースデータ（20件）:")
            print(result.to_string(index=False))
            
            return result
            
        except Exception as e:
            print(f"サンプルレースデータ表示エラー: {e}")
            return None
    
    def run_check(self):
        """確認実行"""
        print("=== ecore.db基本データ確認実行 ===")
        
        try:
            # 1) ecore.dbのテーブル確認
            tables = self.check_ecore_tables()
            if tables is None:
                return False
            
            # 2) レース結果データ確認
            race_result = self.check_race_results()
            if race_result is None:
                return False
            
            # 3) オッズデータ確認
            odds_result = self.check_odds_data()
            if odds_result is None:
                return False
            
            # 4) サンプルレースデータ表示
            sample_result = self.show_sample_race_data()
            if sample_result is None:
                return False
            
            print("✅ ecore.db基本データ確認完了")
            return True
            
        except Exception as e:
            print(f"ecore.db基本データ確認実行エラー: {e}")
            return False

def main():
    checker = CheckEcoreBasicData()
    success = checker.run_check()
    
    if success:
        print("\n✅ ecore.db基本データ確認成功")
    else:
        print("\n❌ ecore.db基本データ確認失敗")

if __name__ == "__main__":
    main()




