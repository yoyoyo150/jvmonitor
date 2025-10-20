#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データベースの最新性と文字化け問題をチェックするスクリプト
"""

import sqlite3
import os
from datetime import datetime, date

def check_database_status(db_path, db_name):
    """データベースの状態をチェック"""
    print(f"\n=== {db_name} 状態チェック ===")
    print(f"パス: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"エラー: データベースが見つかりません")
        return
    
    try:
        # UTF-8エンコーディングで接続
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA encoding = 'UTF-8'")
        cursor = conn.cursor()
        
        # テーブル一覧取得
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"テーブル数: {len(tables)}")
        
        # 各テーブルの最新データをチェック
        for table in tables:
            table_name = table[0]
            print(f"\n--- {table_name} ---")
            
            # レコード数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"レコード数: {count:,}")
            
            if count == 0:
                print("データなし")
                continue
            
            # テーブル構造確認
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # 日付関連のカラムを探す
            date_columns = []
            for col in columns:
                col_name = col[1].lower()
                if any(keyword in col_name for keyword in ['date', '日付', 'year', 'month', 'day']):
                    date_columns.append(col[1])
            
            if date_columns:
                print(f"日付関連カラム: {date_columns}")
                
                # 最新の日付を取得
                for date_col in date_columns:
                    try:
                        cursor.execute(f"SELECT MAX({date_col}) FROM {table_name} WHERE {date_col} IS NOT NULL;")
                        max_date = cursor.fetchone()[0]
                        if max_date:
                            print(f"最新{date_col}: {max_date}")
                    except Exception as e:
                        print(f"{date_col}の取得エラー: {e}")
            
            # サンプルデータで文字化けチェック
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 2;")
            samples = cursor.fetchall()
            
            print("サンプルデータ（文字化けチェック）:")
            for i, sample in enumerate(samples, 1):
                print(f"  {i}: {sample}")
                
                # 日本語文字の確認
                for j, field in enumerate(sample):
                    if isinstance(field, str):
                        try:
                            # UTF-8として正しくデコードできるかチェック
                            field.encode('utf-8').decode('utf-8')
                        except UnicodeError:
                            print(f"    文字化け検出: カラム{j} = {field}")
        
        conn.close()
        
    except Exception as e:
        print(f"エラー: {e}")

def main():
    """メイン処理"""
    print("データベース状態チェック")
    print("=" * 50)
    
    # データベースパス
    base_path = r"C:\my_project_folder\envs\cursor\my_keiba"
    ecore_db = os.path.join(base_path, "ecore.db")
    excel_db = os.path.join(base_path, "excel_data.db")
    
    # 各データベースをチェック
    check_database_status(ecore_db, "ecore.db (JRA-VANデータ)")
    check_database_status(excel_db, "excel_data.db (エクセルデータ)")
    
    print("\nチェック完了")

if __name__ == "__main__":
    main()


