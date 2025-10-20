#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データベースのテーブルとスキーマを確認するスクリプト
"""

import sqlite3
import os

def check_db_schema(db_path):
    if not os.path.exists(db_path):
        print(f"[ERROR] データベースが見つかりません: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"=== {db_path} のテーブル一覧 ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    if tables:
        for table in tables:
            table_name = table[0]
            print(f"  テーブル名: {table_name}")
            
            cursor.execute(f'PRAGMA table_info({table_name})')
            columns = cursor.fetchall()
            print(f"    カラム:")
            for col in columns:
                print(f"      - {col[1]} ({col[2]})")
    else:
        print("  テーブルがありません")
    
    conn.close()

if __name__ == '__main__':
    check_db_schema('predictions.db')
    print()
    check_db_schema('ecore.db')

