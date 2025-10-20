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

class CheckEcoreColumns:
    """ecore.dbの列構造確認"""
    
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
    
    def check_n_uma_race_columns(self):
        """N_UMA_RACEテーブルの列構造確認"""
        print("=== N_UMA_RACEテーブルの列構造確認 ===")
        
        try:
            # 列構造確認
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(N_UMA_RACE)")
            columns_info = cursor.fetchall()
            
            print("N_UMA_RACEテーブルの列構造:")
            for col in columns_info:
                print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL OK'}")
            
            # 列名リスト
            column_names = [col[1] for col in columns_info]
            print(f"\n列名リスト: {column_names}")
            
            return column_names
            
        except Exception as e:
            print(f"N_UMA_RACEテーブルの列構造確認エラー: {e}")
            return None
    
    def check_odds_columns(self, column_names):
        """オッズ関連列の確認"""
        print("=== オッズ関連列の確認 ===")
        
        try:
            # オッズ関連列の検索
            odds_columns = []
            for col in column_names:
                if 'odds' in col.lower() or 'tansho' in col.lower() or 'fukusho' in col.lower():
                    odds_columns.append(col)
            
            print(f"オッズ関連列: {odds_columns}")
            
            return odds_columns
            
        except Exception as e:
            print(f"オッズ関連列の確認エラー: {e}")
            return None
    
    def show_sample_data(self):
        """サンプルデータ表示"""
        print("=== サンプルデータ表示 ===")
        
        try:
            # サンプルデータ表示
            query = """
            SELECT *
            FROM N_UMA_RACE
            ORDER BY JyoCD, RaceNum, KettoNum
            LIMIT 5
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("N_UMA_RACEサンプルデータ（5件）:")
            print(result.to_string(index=False))
            
            return result
            
        except Exception as e:
            print(f"サンプルデータ表示エラー: {e}")
            return None
    
    def run_check(self):
        """確認実行"""
        print("=== ecore.db列構造確認実行 ===")
        
        try:
            # 1) N_UMA_RACEテーブルの列構造確認
            columns = self.check_n_uma_race_columns()
            if columns is None:
                return False
            
            # 2) オッズ関連列の確認
            odds_columns = self.check_odds_columns(columns)
            if odds_columns is None:
                return False
            
            # 3) サンプルデータ表示
            sample_result = self.show_sample_data()
            if sample_result is None:
                return False
            
            print("✅ ecore.db列構造確認完了")
            return True
            
        except Exception as e:
            print(f"ecore.db列構造確認実行エラー: {e}")
            return False

def main():
    checker = CheckEcoreColumns()
    success = checker.run_check()
    
    if success:
        print("\n✅ ecore.db列構造確認成功")
    else:
        print("\n❌ ecore.db列構造確認失敗")

if __name__ == "__main__":
    main()




