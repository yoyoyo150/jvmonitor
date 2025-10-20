import sqlite3
import sys
import io
import pandas as pd
import os
from datetime import datetime, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DB_PATH = 'excel_data.db'
YDATE_DIR = r"C:\my_project_folder\envs\cursor\my_keiba\yDate"

def check_excel_date_coverage():
    print("=== Excel日付カバレッジの確認 ===\n")

    # 1. データベースの日付範囲を確認
    print("1. データベースの日付範囲を確認")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT MIN(SourceDate), MAX(SourceDate) FROM HORSE_MARKS")
    min_date, max_date = cursor.fetchone()
    print(f"データベースの日付範囲: {min_date} ～ {max_date}")
    
    # 2. データベースの日付別レコード数
    print("\n2. データベースの日付別レコード数")
    cursor.execute("""
        SELECT SourceDate, COUNT(*) as count
        FROM HORSE_MARKS 
        GROUP BY SourceDate 
        ORDER BY SourceDate DESC 
        LIMIT 10
    """)
    
    db_dates = cursor.fetchall()
    print("データベースの日付別レコード数（最新10日）:")
    for date, count in db_dates:
        print(f"  {date}: {count} 件")

    # 3. Excelファイルの日付範囲を確認
    print("\n3. Excelファイルの日付範囲を確認")
    excel_files = [f for f in os.listdir(YDATE_DIR) if f.endswith('.xlsx')]
    excel_files.sort()
    
    if excel_files:
        print(f"Excelファイル数: {len(excel_files)} 件")
        print(f"最初のファイル: {excel_files[0]}")
        print(f"最後のファイル: {excel_files[-1]}")
        
        # 日付の抽出
        excel_dates = []
        for file in excel_files:
            if file.replace('.xlsx', '').isdigit() and len(file.replace('.xlsx', '')) == 8:
                excel_dates.append(file.replace('.xlsx', ''))
        
        if excel_dates:
            print(f"Excelファイルの日付範囲: {min(excel_dates)} ～ {max(excel_dates)}")
    else:
        print("[ERROR] Excelファイルが見つかりません")

    # 4. 不足している日付を特定
    print("\n4. 不足している日付を特定")
    db_date_set = set([date for date, _ in db_dates])
    excel_date_set = set(excel_dates) if excel_dates else set()
    
    missing_in_excel = db_date_set - excel_date_set
    missing_in_db = excel_date_set - db_date_set
    
    if missing_in_excel:
        print(f"データベースにあるがExcelにない日付: {sorted(missing_in_excel)}")
    else:
        print("[OK] データベースの日付は全てExcelに存在します")
    
    if missing_in_db:
        print(f"Excelにあるがデータベースにない日付: {sorted(missing_in_db)}")
    else:
        print("[OK] Excelの日付は全てデータベースに存在します")

    # 5. 特定の日付のExcelファイル内容を確認
    print("\n5. 特定の日付のExcelファイル内容を確認")
    test_date = "20251005"  # 最新の日付
    test_file = f"{test_date}.xlsx"
    test_path = os.path.join(YDATE_DIR, test_file)
    
    if os.path.exists(test_path):
        try:
            df = pd.read_excel(test_path)
            print(f"[OK] {test_file} の読み込み成功")
            print(f"行数: {len(df)} 行")
            print(f"列数: {len(df.columns)} 列")
            
            # 馬印関連の列を確認
            mark_columns = [col for col in df.columns if '馬印' in str(col)]
            print(f"馬印関連の列: {mark_columns}")
            
            # 馬印1のデータ確認
            if '馬印1' in df.columns:
                mark1_data = df['馬印1'].dropna()
                print(f"馬印1のデータ: {len(mark1_data)} 件")
                print(f"馬印1の例: {mark1_data.head(5).tolist()}")
            
        except Exception as e:
            print(f"[ERROR] {test_file} の読み込みエラー: {e}")
    else:
        print(f"[ERROR] {test_file} が見つかりません")

    conn.close()

if __name__ == '__main__':
    check_excel_date_coverage()


