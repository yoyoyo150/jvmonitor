import sqlite3
import sys
import io
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DB_PATH = 'excel_data.db'

def check_excel_data_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=== excel_data.db 構造確認 ===\n")

    # 1. テーブル一覧
    print("1. テーブル一覧")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        print(f"  {table[0]}")

    # 2. 各テーブルのレコード数
    print("\n2. 各テーブルのレコード数")
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  {table[0]}: {count:,} 件")
        except Exception as e:
            print(f"  {table[0]}: エラー - {e}")

    # 3. 馬印関連テーブルの詳細確認
    print("\n3. 馬印関連テーブルの詳細確認")
    uma_mark_tables = [table[0] for table in tables if 'uma' in table[0].lower() or 'mark' in table[0].lower() or '印' in table[0]]
    
    for table_name in uma_mark_tables:
        print(f"\n{table_name} の構造:")
        try:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # サンプルデータ
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            samples = cursor.fetchall()
            print("  サンプルデータ:")
            for sample in samples:
                print(f"    {sample}")
        except Exception as e:
            print(f"  エラー: {e}")

    # 4. 最新の更新日時確認
    print("\n4. 最新の更新日時確認")
    for table in tables:
        try:
            # 日付関連カラムを探す
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            date_columns = [col[1] for col in columns if 'date' in col[1].lower() or 'time' in col[1].lower() or '日' in col[1]]
            
            if date_columns:
                date_col = date_columns[0]
                cursor.execute(f"SELECT MAX({date_col}) FROM {table[0]}")
                latest_date = cursor.fetchone()[0]
                print(f"  {table[0]}: 最新更新 {latest_date}")
        except Exception as e:
            pass

    conn.close()

if __name__ == '__main__':
    check_excel_data_db()