#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
20250913ra.xlsx専用インポートスクリプト
"""
import sqlite3
import pandas as pd

def safe_column_name(col_name):
    """カラム名をSQLite安全な形式に変換"""
    if not col_name or pd.isna(col_name):
        return "UNKNOWN_COL"
    
    col_str = str(col_name).strip()
    
    # 特殊文字を置換
    replacements = {
        ' ': '_', '　': '_', '(': '_', ')': '_', 
        '[': '_', ']': '_', '{': '_', '}': '_',
        '-': '_', '－': '_', '+': '_', '＋': '_',
        '.': '_', '．': '_', ',': '_', '，': '_',
        '/': '_', '／': '_', '\\': '_', '￥': '_',
        ':': '_', '：': '_', ';': '_', '；': '_',
        '?': '_', '？': '_', '!': '_', '！': '_',
        '@': '_', '＠': '_', '#': '_', '＃': '_',
        '$': '_', '＄': '_', '%': '_', '％': '_',
        '^': '_', '&': '_', '＆': '_', '*': '_',
        '＊': '_', '=': '_', '＝': '_', '|': '_',
        '｜': '_', '~': '_', '～': '_', '`': '_',
        "'": '_', '"': '_', '<': '_', '>': '_',
        '＜': '_', '＞': '_'
    }
    
    for old, new in replacements.items():
        col_str = col_str.replace(old, new)
    
    # 数字で始まる場合はCOL_を前置
    if col_str and col_str[0].isdigit():
        col_str = f"COL_{col_str}"
    
    # 空文字列の場合はデフォルト名
    if not col_str:
        col_str = "UNKNOWN_COL"
    
    return col_str

def main():
    print("=== 20250913ra.xlsx 専用インポート ===")
    
    # ファイル読み込み
    df = pd.read_excel('yDate/20250913ra.xlsx', engine='openpyxl')
    print(f"読み込み: {len(df)}行, {len(df.columns)}列")
    
    # カラム名変換
    safe_columns = {}
    for col in df.columns:
        safe_col = safe_column_name(col)
        safe_columns[col] = safe_col
    
    # データベース処理
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    table_name = "EXCEL_DATA_20250913"
    
    # 既存テーブル削除
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    print(f"🗑️  既存テーブル削除: {table_name}")
    
    # テーブル作成
    columns_def = [f"{safe_col} TEXT" for safe_col in safe_columns.values()]
    create_sql = f"""
        CREATE TABLE {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {', '.join(columns_def)}
        )
    """
    cursor.execute(create_sql)
    print(f"✅ テーブル作成: {table_name}")
    
    # データ挿入
    insert_columns = list(safe_columns.values())
    placeholders = ', '.join(['?' for _ in insert_columns])
    insert_sql = f"INSERT INTO {table_name} ({', '.join(insert_columns)}) VALUES ({placeholders})"
    
    inserted_count = 0
    for _, row in df.iterrows():
        values = []
        for original_col in safe_columns.keys():
            value = row[original_col]
            if pd.isna(value):
                values.append(None)
            else:
                values.append(str(value))
        
        cursor.execute(insert_sql, values)
        inserted_count += 1
    
    conn.commit()
    print(f"✅ データ挿入: {inserted_count}件")
    
    # 確認
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"📊 最終確認: {count}件")
    
    # サンプルデータ確認
    try:
        cursor.execute(f"SELECT 馬名S, 馬印1, 馬印2 FROM {table_name} LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            print(f"サンプル: {sample[0]} - 馬印1:{sample[1]}, 馬印2:{sample[2]}")
    except Exception as e:
        print(f"サンプルデータ取得エラー: {e}")
    
    conn.close()
    print("✅ インポート完了")

if __name__ == "__main__":
    main()
