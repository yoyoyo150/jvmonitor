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

def check_import_process():
    print("=== インポート処理の詳細調査 ===\n")

    # 1. インポート処理のログを確認
    print("1. インポート処理のログを確認")
    
    # 最近のインポート処理を確認
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # インポート時刻の分布を確認
    cursor.execute("""
        SELECT SourceDate, ImportedAt, COUNT(*) as count
        FROM HORSE_MARKS 
        WHERE ImportedAt >= datetime('now', '-1 day')
        GROUP BY SourceDate, ImportedAt
        ORDER BY ImportedAt DESC
        LIMIT 20
    """)
    
    recent_imports = cursor.fetchall()
    print("最近1日間のインポート処理:")
    for date, imported_at, count in recent_imports:
        print(f"  {date} {imported_at}: {count} 件")

    # 2. 特定の日付のインポート状況を詳細確認
    print("\n2. 特定の日付のインポート状況を詳細確認")
    
    test_dates = ['20250503', '20250504', '20250505']
    
    for test_date in test_dates:
        print(f"\n--- {test_date} ---")
        
        # データベースの状況
        cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS WHERE SourceDate = ?", (test_date,))
        db_count = cursor.fetchone()[0]
        print(f"データベース: {db_count} 件")
        
        # Excelファイルの状況
        excel_file = f"{test_date}.xlsx"
        excel_path = os.path.join(YDATE_DIR, excel_file)
        
        if os.path.exists(excel_path):
            try:
                # UTF-8エンコーディングでExcelファイルを読み込み
                df = pd.read_excel(excel_path, engine='openpyxl')
                excel_count = len(df)
                print(f"Excelファイル: {excel_count} 行")
                
                # ファイルの更新時刻
                mod_time = datetime.fromtimestamp(os.path.getmtime(excel_path))
                print(f"ファイル更新時刻: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # データの整合性
                if db_count == excel_count:
                    print("✅ データ整合性: OK")
                elif db_count == 0:
                    print("❌ データ整合性: インポートされていない")
                else:
                    print(f"⚠️ データ整合性: 不一致 (DB:{db_count}, Excel:{excel_count})")
                    
            except Exception as e:
                print(f"Excelファイル読み込みエラー: {e}")
        else:
            print(f"Excelファイルが見つかりません: {excel_path}")

    # 3. インポート処理のパターン分析
    print("\n3. インポート処理のパターン分析")
    
    # 日付順にインポート状況を確認
    cursor.execute("""
        SELECT SourceDate, COUNT(*) as count, MAX(ImportedAt) as last_import
        FROM HORSE_MARKS 
        WHERE SourceDate >= '20250501' AND SourceDate <= '20250510'
        GROUP BY SourceDate
        ORDER BY SourceDate
    """)
    
    may_imports = cursor.fetchall()
    print("2025年5月のインポート状況:")
    for date, count, last_import in may_imports:
        print(f"  {date}: {count} 件, 最終インポート: {last_import}")

    # 4. 問題の原因特定
    print("\n4. 問題の原因特定")
    
    # インポートされていない日付を特定
    cursor.execute("""
        SELECT DISTINCT SourceDate 
        FROM HORSE_MARKS 
        WHERE SourceDate >= '20250501' AND SourceDate <= '20250510'
        ORDER BY SourceDate
    """)
    
    imported_dates = set([row[0] for row in cursor.fetchall()])
    expected_dates = [f"202505{i:02d}" for i in range(1, 11)]
    
    missing_dates = [date for date in expected_dates if date not in imported_dates]
    print(f"インポートされていない日付: {missing_dates}")
    
    # 5. 解決策の提案
    print("\n5. 解決策の提案")
    
    if missing_dates:
        print("以下の日付がインポートされていません:")
        for date in missing_dates:
            excel_file = f"{date}.xlsx"
            excel_path = os.path.join(YDATE_DIR, excel_file)
            if os.path.exists(excel_path):
                print(f"  {date}: Excelファイルは存在するが、データベースにインポートされていない")
            else:
                print(f"  {date}: Excelファイルが存在しない")
        
        print("\n推奨アクション:")
        print("1. 不足している日付のExcelファイルを確認")
        print("2. 手動でインポート処理を実行")
        print("3. インポート処理のログを確認してエラーを特定")
    else:
        print("✅ 全ての日付が正常にインポートされています")

    conn.close()

if __name__ == '__main__':
    check_import_process()

