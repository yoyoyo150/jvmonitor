#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データベース内のMark5/Mark6関連カラム検索スクリプト
"""
import sqlite3
import pandas as pd
import sys

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def search_mark_columns(db_path="ecore.db"):
    """データベース内の全テーブルからMark5/Mark6関連カラムを検索"""
    print("=== Mark5/Mark6関連カラムのデータベース検索を開始します ===")
    
    try:
        conn = sqlite3.connect(db_path)
        print("データベース接続成功")
        
        # 全テーブル名を取得
        query_tables = "SELECT name FROM sqlite_master WHERE type='table'"
        df_tables = pd.read_sql_query(query_tables, conn)
        
        found_columns = {}
        
        if not df_tables.empty:
            for table_name in df_tables['name']:
                print(f"\n--- テーブル: {table_name} のカラムを確認中 ---")
                query_schema = f"PRAGMA table_info({table_name})"
                df_schema = pd.read_sql_query(query_schema, conn)
                
                if not df_schema.empty:
                    for _, row in df_schema.iterrows():
                        col_name = row['name']
                        # Mark5, Mark6, またはそれに関連するキーワードを検索
                        if "Mark5" in col_name or "Mark6" in col_name or "MARK5" in col_name or "MARK6" in col_name:
                            if table_name not in found_columns:
                                found_columns[table_name] = []
                            found_columns[table_name].append(col_name)
                            print(f"  -> 検出: {col_name}")
                else:
                    print(f"  テーブル {table_name} のスキーマ情報が見つかりません。")
        else:
            print("データベースにテーブルが見つかりません。")
            
        conn.close()
        
        print("\n=== Mark5/Mark6関連カラムのデータベース検索結果 ===")
        if found_columns:
            for table, cols in found_columns.items():
                print(f"テーブル '{table}': {", ".join(cols)}")
        else:
            print("Mark5/Mark6に関連するカラムは見つかりませんでした。")
            
        print("\n=== データベース検索完了 ===")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    search_mark_columns()




