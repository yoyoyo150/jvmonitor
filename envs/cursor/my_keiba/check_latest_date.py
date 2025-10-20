import sqlite3
import sys
import io
import os
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DB_PATH = 'ecore.db'
YDATE_DIR = r"C:\my_project_folder\envs\cursor\my_keiba\yDate"

def check_latest_date():
    print("=== 最新の日付の確認 ===\n")

    # 1. データベースの最新日付を確認
    print("1. データベースの最新日付を確認")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(SourceDate) FROM HORSE_MARKS")
    latest_db_date = cursor.fetchone()[0]
    print(f"データベースの最新日付: {latest_db_date}")
    
    # 最新日付のレコード数
    cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS WHERE SourceDate = ?", (latest_db_date,))
    latest_count = cursor.fetchone()[0]
    print(f"最新日付のレコード数: {latest_count} 件")
    
    # 最新5日分のデータ
    cursor.execute("""
        SELECT SourceDate, COUNT(*) as count
        FROM HORSE_MARKS 
        GROUP BY SourceDate 
        ORDER BY SourceDate DESC 
        LIMIT 5
    """)
    
    recent_dates = cursor.fetchall()
    print("最新5日分のデータ:")
    for date, count in recent_dates:
        print(f"  {date}: {count} 件")
    
    conn.close()

    # 2. Excelファイルの最新日付を確認
    print("\n2. Excelファイルの最新日付を確認")
    excel_files = [f for f in os.listdir(YDATE_DIR) if f.endswith('.xlsx')]
    excel_files.sort(reverse=True)
    
    if excel_files:
        latest_excel = excel_files[0]
        latest_excel_date = latest_excel.replace('.xlsx', '')
        print(f"最新のExcelファイル: {latest_excel}")
        print(f"Excelファイルの最新日付: {latest_excel_date}")
        
        # 最新5件のExcelファイル
        print("最新5件のExcelファイル:")
        for i, file in enumerate(excel_files[:5]):
            file_path = os.path.join(YDATE_DIR, file)
            file_size = os.path.getsize(file_path)
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            print(f"  {file}: {file_size:,} bytes, 更新: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("Excelファイルが見つかりません")

    # 3. 日付の整合性確認
    print("\n3. 日付の整合性確認")
    if latest_db_date == latest_excel_date:
        print("✅ データベースとExcelファイルの最新日付が一致しています")
    else:
        print(f"❌ 日付が一致していません")
        print(f"   データベース: {latest_db_date}")
        print(f"   Excelファイル: {latest_excel_date}")

    # 4. 今日の日付との比較
    print("\n4. 今日の日付との比較")
    today = datetime.now().strftime('%Y%m%d')
    print(f"今日の日付: {today}")
    
    if latest_db_date == today:
        print("✅ データベースの最新日付は今日です")
    elif latest_db_date > today:
        print("⚠️ データベースの最新日付が未来の日付です")
    else:
        print("⚠️ データベースの最新日付が過去の日付です")

if __name__ == '__main__':
    check_latest_date()

