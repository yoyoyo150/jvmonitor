#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check ecore.db structure
ecore.dbの構造を確認して正しいカラム名を調べる
"""

import sqlite3
import pandas as pd

def check_ecore_structure():
    """ecore.dbの構造を確認"""
    
    print("=== ecore.db Structure Check ===")
    print()
    
    try:
        conn = sqlite3.connect('ecore.db')
        cursor = conn.cursor()
        
        # 1. N_UMA_RACEテーブルの構造
        print("1. N_UMA_RACEテーブルの構造")
        print("=" * 50)
        cursor.execute("PRAGMA table_info(N_UMA_RACE);")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
        
        print()
        
        # 2. 日付関連のカラムを探す
        print("2. 日付関連のカラム")
        print("=" * 50)
        date_columns = [col for col in columns if 'date' in col[1].lower() or 'kai' in col[1].lower()]
        for col in date_columns:
            print(f"- {col[1]} ({col[2]})")
        
        print()
        
        # 3. サンプルデータで日付形式を確認
        print("3. サンプルデータで日付形式を確認")
        print("=" * 50)
        
        # 最新のデータを取得
        cursor.execute("SELECT * FROM N_UMA_RACE LIMIT 5;")
        sample_data = cursor.fetchall()
        
        if sample_data:
            # カラム名を取得
            column_names = [description[0] for description in cursor.description]
            print("カラム名:", column_names)
            print()
            
            for i, row in enumerate(sample_data):
                print(f"サンプル {i+1}:")
                for j, value in enumerate(row):
                    if column_names[j].lower().find('date') != -1 or column_names[j].lower().find('kai') != -1:
                        print(f"  {column_names[j]}: {value}")
                print()
        
        # 4. 2025年10月のデータがあるか確認
        print("4. 2025年10月のデータ確認")
        print("=" * 50)
        
        # 日付カラムを特定
        date_col = None
        for col in columns:
            if 'date' in col[1].lower() or 'kai' in col[1].lower():
                date_col = col[1]
                break
        
        if date_col:
            print(f"日付カラム: {date_col}")
            
            # 2025年10月のデータを検索
            cursor.execute(f"SELECT COUNT(*) FROM N_UMA_RACE WHERE {date_col} LIKE '202510%';")
            oct_2025_count = cursor.fetchone()[0]
            print(f"2025年10月のデータ: {oct_2025_count}件")
            
            if oct_2025_count > 0:
                # サンプルデータを取得
                cursor.execute(f"SELECT {date_col}, JyoCD, RaceNum, Umaban, KakuteiJyuni FROM N_UMA_RACE WHERE {date_col} LIKE '202510%' LIMIT 5;")
                oct_samples = cursor.fetchall()
                print("2025年10月のサンプル:")
                for sample in oct_samples:
                    print(f"  {sample}")
        
        conn.close()
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_ecore_structure()