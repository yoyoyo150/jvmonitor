#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
excel_data.dbの構造分析スクリプト
お客様の加工データの構造を理解する
"""
import sqlite3
import pandas as pd
import sys

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def analyze_excel_data_structure():
    """excel_data.dbの構造を分析"""
    print("=== excel_data.db の構造分析開始 ===")
    
    try:
        conn = sqlite3.connect('trainer_prediction_system/excel_data.db')
        
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
        main_tables = ['excel_marks']
        
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
        
        # 6. 独自変数関連のカラムを探す
        print("\n--- 独自変数関連のカラム検索 ---")
        for table in df_tables['name']:
            query_schema = f"PRAGMA table_info({table})"
            df_schema = pd.read_sql_query(query_schema, conn)
            
            # 独自変数関連のカラムを検索
            custom_columns = df_schema[df_schema['name'].str.contains('Mark|ZI|ZM|Index', case=False, na=False)]
            if not custom_columns.empty:
                print(f"\n{table} の独自変数関連カラム:")
                for _, row in custom_columns.iterrows():
                    print(f"  {row['name']}: {row['type']}")
        
        # 7. データの日付範囲を確認
        print("\n--- データの日付範囲確認 ---")
        for table in df_tables['name']:
            if 'SourceDate' in [col['name'] for col in pd.read_sql_query(f"PRAGMA table_info({table})", conn).to_dict('records')]:
                query_date_range = f"""
                SELECT 
                    MIN(SourceDate) as min_date,
                    MAX(SourceDate) as max_date,
                    COUNT(DISTINCT SourceDate) as unique_dates,
                    COUNT(*) as total_records
                FROM {table}
                """
                try:
                    df_date_range = pd.read_sql_query(query_date_range, conn)
                    print(f"\n{table} の日付範囲:")
                    print(f"  最小日付: {df_date_range['min_date'].iloc[0]}")
                    print(f"  最大日付: {df_date_range['max_date'].iloc[0]}")
                    print(f"  ユニーク日付数: {df_date_range['unique_dates'].iloc[0]}")
                    print(f"  総レコード数: {df_date_range['total_records'].iloc[0]}")
                except Exception as e:
                    print(f"エラー: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    analyze_excel_data_structure()




