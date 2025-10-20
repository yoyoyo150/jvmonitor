#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データベース構造分析スクリプト
ecore.db（JRA-VANデータ）とexcel_data.db（エクセルデータ）の構造を分析
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path

def analyze_database(db_path, db_name):
    """データベースの構造を分析"""
    print(f"\n=== {db_name} 分析 ===")
    print(f"パス: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"エラー: データベースが見つかりません: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # テーブル一覧取得
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"テーブル数: {len(tables)}")
        print("テーブル一覧:")
        
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
            
            # テーブル構造取得
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print(f"    カラム数: {len(columns)}")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                print(f"      {col_id}: {col_name} ({col_type})")
            
            # レコード数取得
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"    レコード数: {count:,}")
            
            # サンプルデータ表示（最初の3件）
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                samples = cursor.fetchall()
                print(f"    サンプルデータ:")
                for i, sample in enumerate(samples, 1):
                    print(f"      {i}: {sample}")
            
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"エラー: {e}")

def main():
    """メイン処理"""
    print("競馬データベース構造分析")
    print("=" * 50)
    
    # データベースパス
    base_path = r"C:\my_project_folder\envs\cursor\my_keiba"
    ecore_db = os.path.join(base_path, "ecore.db")
    excel_db = os.path.join(base_path, "excel_data.db")
    
    # 各データベースを分析
    analyze_database(ecore_db, "ecore.db (JRA-VANデータ)")
    analyze_database(excel_db, "excel_data.db (エクセルデータ)")
    
    print("\n分析完了")

if __name__ == "__main__":
    main()
