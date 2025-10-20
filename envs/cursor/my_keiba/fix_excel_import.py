import sqlite3
import sys
import io
import pandas as pd
import os
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DB_PATH = 'excel_data.db'
YDATE_DIR = r"C:\my_project_folder\envs\cursor\my_keiba\yDate"

def fix_excel_import():
    print("=== Excel取り込みの修正 ===\n")

    # 1. 現在の状況を確認
    print("1. 現在の状況を確認")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(DISTINCT SourceDate) FROM HORSE_MARKS")
    db_date_count = cursor.fetchone()[0]
    print(f"データベースの日付数: {db_date_count} 日")
    
    # 2. Excelファイルの確認
    print("\n2. Excelファイルの確認")
    excel_files = [f for f in os.listdir(YDATE_DIR) if f.endswith('.xlsx')]
    excel_files.sort()
    print(f"Excelファイル数: {len(excel_files)} 件")
    
    # 3. 不足している日付を特定
    print("\n3. 不足している日付を特定")
    cursor.execute("SELECT DISTINCT SourceDate FROM HORSE_MARKS ORDER BY SourceDate")
    db_dates = set([row[0] for row in cursor.fetchall()])
    
    excel_dates = set()
    for file in excel_files:
        if file.replace('.xlsx', '').isdigit() and len(file.replace('.xlsx', '')) == 8:
            excel_dates.add(file.replace('.xlsx', ''))
    
    missing_dates = excel_dates - db_dates
    print(f"不足している日付数: {len(missing_dates)} 日")
    
    if missing_dates:
        print("不足している日付（最初の10日）:")
        for date in sorted(missing_dates)[:10]:
            print(f"  {date}")
        if len(missing_dates) > 10:
            print(f"  ... 他 {len(missing_dates) - 10} 日")

    # 4. 推奨アクション
    print("\n4. 推奨アクション")
    print("以下のコマンドを実行して、全Excelファイルを再取り込みしてください:")
    print()
    print("python tools/import_excel_marks.py --mode full --db excel_data.db --excel-dir yDate")
    print()
    print("このコマンドにより:")
    print("- 既存のデータが削除されます")
    print("- 全Excelファイルが再取り込みされます")
    print("- 不足している日付のデータが追加されます")

    # 5. 実行前の確認
    print("\n5. 実行前の確認")
    print("実行前に以下を確認してください:")
    print("1. Excelファイルが開かれていないこと")
    print("2. データベースがロックされていないこと")
    print("3. 十分なディスク容量があること")
    print("4. バックアップが必要な場合は事前に作成すること")

    conn.close()

if __name__ == '__main__':
    fix_excel_import()


