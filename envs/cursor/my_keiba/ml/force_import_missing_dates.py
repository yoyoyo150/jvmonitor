#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
欠損日付の強制インポートシステム
指定された日付のエクセルファイルを強制的にDBに登録
"""
import os
import sqlite3
import pandas as pd
from datetime import datetime
import sys

def safe_column_name(col_name):
    """カラム名をSQLite安全な形式に変換"""
    if not col_name or pd.isna(col_name):
        return "UNKNOWN_COL"
    
    # 文字列に変換
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

def force_import_single_file(file_path, target_date):
    """単一ファイルを強制インポート"""
    print(f"\n=== {target_date} ファイル強制インポート ===")
    print(f"ファイル: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ ファイルが存在しません: {file_path}")
        return False
    
    try:
        # エクセルファイル読み込み
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path, engine='openpyxl')
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='utf-8')
        else:
            print(f"❌ サポートされていないファイル形式: {file_path}")
            return False
        
        print(f"📊 読み込み行数: {len(df)}")
        print(f"📊 読み込み列数: {len(df.columns)}")
        
        # カラム名を安全な形式に変換
        safe_columns = {}
        for i, col in enumerate(df.columns):
            safe_col = safe_column_name(col)
            safe_columns[col] = safe_col
            if i < 10:  # 最初の10列のみ表示
                print(f"  列{i+1}: '{col}' -> '{safe_col}'")
        
        # データベース接続
        conn = sqlite3.connect('excel_data.db')
        cursor = conn.cursor()
        
        # テーブル名
        table_name = f"EXCEL_DATA_{target_date}"
        
        # 既存テーブルを削除
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        print(f"🗑️  既存テーブル削除: {table_name}")
        
        # 新しいテーブル作成
        columns_def = []
        for original_col, safe_col in safe_columns.items():
            columns_def.append(f"{safe_col} TEXT")
        
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
        
        # データを行ごとに挿入
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
        conn.close()
        
        print(f"✅ データ挿入完了: {inserted_count}件")
        return True
        
    except Exception as e:
        print(f"❌ インポートエラー: {e}")
        return False

def force_import_missing_dates():
    """欠損日付の強制インポート"""
    print("🔄 欠損日付強制インポートシステム")
    print("=" * 50)
    
    # 問題の日付とファイル
    target_files = [
        ('20240810', 'yDate/20240810.xlsx'),
        ('20240913', None),  # ファイルなし
        ('20240914', 'yDate/20240914.xlsx'),
        ('20240922', 'yDate/20240922.xlsx')
    ]
    
    success_count = 0
    total_count = 0
    
    for date, file_path in target_files:
        total_count += 1
        
        if file_path is None:
            print(f"\n❌ {date}: yDateファイルが存在しません")
            continue
        
        if force_import_single_file(file_path, date):
            success_count += 1
        else:
            print(f"❌ {date}: インポート失敗")
    
    print(f"\n📊 結果: {success_count}/{total_count} 件成功")
    
    # 結果確認
    print("\n=== インポート結果確認 ===")
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    for date, _ in target_files:
        table_name = f"EXCEL_DATA_{date}"
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"✅ {table_name}: {count}件")
            
            # サンプルデータ確認
            try:
                cursor.execute(f"SELECT 馬名S, 馬印1, 馬印2 FROM {table_name} LIMIT 1")
                sample = cursor.fetchone()
                if sample:
                    print(f"    例: {sample[0]} - 馬印1:{sample[1]}, 馬印2:{sample[2]}")
            except:
                print(f"    サンプルデータ取得失敗")
        else:
            print(f"❌ {table_name}: 作成されませんでした")
    
    conn.close()

def main():
    """メイン処理"""
    if len(sys.argv) > 1:
        # 個別日付指定
        target_date = sys.argv[1]
        file_path = f"yDate/{target_date}.xlsx"
        
        if not os.path.exists(file_path):
            # .xlsxがない場合は他の拡張子を試す
            alt_files = [f"yDate/{target_date}.csv", f"yDate/{target_date}rase.xlsx"]
            for alt_file in alt_files:
                if os.path.exists(alt_file):
                    file_path = alt_file
                    break
        
        force_import_single_file(file_path, target_date)
    else:
        # 全欠損日付処理
        force_import_missing_dates()

if __name__ == "__main__":
    main()
