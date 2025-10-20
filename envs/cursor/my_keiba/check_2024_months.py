import sqlite3
import sys
import io
import pandas as pd
import os
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DB_PATH = 'ecore.db'
YDATE_DIR = r"C:\my_project_folder\envs\cursor\my_keiba\yDate"

def check_2024_months():
    print("=== 2024年の他の月の更新状況確認 ===\n")

    # 1. データベースの2024年データを確認
    print("1. データベースの2024年データを確認")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 2024年の日付別レコード数
    cursor.execute("""
        SELECT SourceDate, COUNT(*) as count
        FROM HORSE_MARKS 
        WHERE SourceDate LIKE '2024%'
        GROUP BY SourceDate 
        ORDER BY SourceDate DESC
    """)
    
    db_2024_dates = cursor.fetchall()
    print("データベースの2024年データ:")
    for date, count in db_2024_dates:
        print(f"  {date}: {count} 件")

    # 2. Excelファイルの2024年データを確認
    print("\n2. Excelファイルの2024年データを確認")
    excel_files = [f for f in os.listdir(YDATE_DIR) if f.endswith('.xlsx')]
    excel_2024_files = [f for f in excel_files if f.startswith('2024')]
    excel_2024_files.sort()
    
    print(f"2024年のExcelファイル数: {len(excel_2024_files)} 件")
    print("2024年のExcelファイル一覧:")
    for file in excel_2024_files:
        file_path = os.path.join(YDATE_DIR, file)
        file_size = os.path.getsize(file_path)
        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        print(f"  {file}: {file_size:,} bytes, 更新: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 3. 不足している2024年の日付を特定
    print("\n3. 不足している2024年の日付を特定")
    db_2024_date_set = set([date for date, _ in db_2024_dates])
    excel_2024_date_set = set([f.replace('.xlsx', '') for f in excel_2024_files])
    
    missing_in_db = excel_2024_date_set - db_2024_date_set
    missing_in_excel = db_2024_date_set - excel_2024_date_set
    
    if missing_in_db:
        print(f"Excelにあるがデータベースにない2024年の日付: {len(missing_in_db)} 日")
        print("最初の10日:")
        for date in sorted(missing_in_db)[:10]:
            print(f"  {date}")
        if len(missing_in_db) > 10:
            print(f"  ... 他 {len(missing_in_db) - 10} 日")
    else:
        print("[OK] 2024年のExcelデータは全てデータベースに存在します")
    
    if missing_in_excel:
        print(f"データベースにあるがExcelにない2024年の日付: {len(missing_in_excel)} 日")
        print("最初の10日:")
        for date in sorted(missing_in_excel)[:10]:
            print(f"  {date}")
        if len(missing_in_excel) > 10:
            print(f"  ... 他 {len(missing_in_excel) - 10} 日")
    else:
        print("[OK] 2024年のデータベースデータは全てExcelに存在します")

    # 4. 月別の集計
    print("\n4. 月別の集計")
    monthly_stats = {}
    
    for date, count in db_2024_dates:
        month = date[:6]  # YYYYMM
        if month not in monthly_stats:
            monthly_stats[month] = {'dates': 0, 'records': 0}
        monthly_stats[month]['dates'] += 1
        monthly_stats[month]['records'] += count
    
    print("2024年月別統計:")
    for month in sorted(monthly_stats.keys()):
        stats = monthly_stats[month]
        print(f"  {month}: {stats['dates']} 日, {stats['records']:,} 件")

    # 5. 特定の月の詳細確認（例：2024年10月）
    print("\n5. 特定の月の詳細確認（2024年10月）")
    oct_2024_dates = [date for date, _ in db_2024_dates if date.startswith('202410')]
    if oct_2024_dates:
        print("2024年10月のデータ:")
        for date in sorted(oct_2024_dates):
            cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS WHERE SourceDate = ?", (date,))
            count = cursor.fetchone()[0]
            print(f"  {date}: {count} 件")
    else:
        print("2024年10月のデータはありません")

    conn.close()

if __name__ == '__main__':
    check_2024_months()


