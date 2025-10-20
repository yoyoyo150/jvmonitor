#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ecore.dbの構造分析スクリプト
JRAVANデータの構造を理解する
"""
import sqlite3
import pandas as pd
import sys

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def analyze_ecore_structure():
    """ecore.dbの構造を分析"""
    print("=== ecore.db の構造分析開始 ===")
    
    try:
        conn = sqlite3.connect('ecore.db')
        
        # 1. テーブル一覧の取得
        print("\n--- テーブル一覧 ---")
        query_tables = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        df_tables = pd.read_sql_query(query_tables, conn)
        print(f"テーブル数: {len(df_tables)}")
        for table in df_tables['name']:
            print(f"  - {table}")
        
        # 2. 各テーブルのスキーマ確認
        print("\n--- 各テーブルのスキーマ ---")
        for table in df_tables['name']:
            print(f"\n### {table} ###")
            query_schema = f"PRAGMA table_info({table})"
            df_schema = pd.read_sql_query(query_schema, conn)
            print(f"カラム数: {len(df_schema)}")
            for _, row in df_schema.iterrows():
                print(f"  {row['name']}: {row['type']} {'(PK)' if row['pk'] else ''}")
        
        # 3. 主要テーブルのサンプルデータ確認
        print("\n--- 主要テーブルのサンプルデータ ---")
        main_tables = ['N_UMA_RACE', 'HORSE_MARKS', 'N_ODDS_TANPUKU']
        
        for table in main_tables:
            if table in df_tables['name'].values:
                print(f"\n### {table} のサンプルデータ ###")
                query_sample = f"SELECT * FROM {table} LIMIT 3"
                try:
                    df_sample = pd.read_sql_query(query_sample, conn)
                    print(f"レコード数: {len(df_sample)}")
                    print(df_sample.to_string(index=False))
                except Exception as e:
                    print(f"エラー: {e}")
        
        # 4. 血統番号関連のカラムを探す
        print("\n--- 血統番号関連のカラム検索 ---")
        for table in df_tables['name']:
            query_schema = f"PRAGMA table_info({table})"
            df_schema = pd.read_sql_query(query_schema, conn)
            
            # 血統番号関連のカラムを検索
            ketto_columns = df_schema[df_schema['name'].str.contains('ketto|Ketto|KETTO', case=False, na=False)]
            if not ketto_columns.empty:
                print(f"\n{table} の血統番号関連カラム:")
                for _, row in ketto_columns.iterrows():
                    print(f"  {row['name']}: {row['type']}")
        
        # 5. 馬名関連のカラムを探す
        print("\n--- 馬名関連のカラム検索 ---")
        for table in df_tables['name']:
            query_schema = f"PRAGMA table_info({table})"
            df_schema = pd.read_sql_query(query_schema, conn)
            
            # 馬名関連のカラムを検索
            horse_columns = df_schema[df_schema['name'].str.contains('horse|Horse|HORSE|bamei|Bamei|BAMEI', case=False, na=False)]
            if not horse_columns.empty:
                print(f"\n{table} の馬名関連カラム:")
                for _, row in horse_columns.iterrows():
                    print(f"  {row['name']}: {row['type']}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    analyze_ecore_structure()




