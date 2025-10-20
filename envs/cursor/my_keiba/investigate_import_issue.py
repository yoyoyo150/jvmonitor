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

def investigate_import_issue():
    print("=== インポート処理の問題調査 ===\n")

    # 1. 特定の日付のデータを詳細確認
    test_dates = ['20250503', '20250504']
    
    for test_date in test_dates:
        print(f"--- {test_date} の詳細調査 ---")
        
        # データベースの状況確認
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # データベースのレコード数
        cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS WHERE SourceDate = ?", (test_date,))
        db_count = cursor.fetchone()[0]
        print(f"データベースのレコード数: {db_count} 件")
        
        # インポート時刻の確認
        cursor.execute("SELECT MAX(ImportedAt) FROM HORSE_MARKS WHERE SourceDate = ?", (test_date,))
        import_time = cursor.fetchone()[0]
        print(f"最新のインポート時刻: {import_time}")
        
        # 馬印データの状況
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN Mark1 IS NOT NULL AND Mark1 != '' THEN 1 END) as mark1_count,
                COUNT(CASE WHEN Mark2 IS NOT NULL AND Mark2 != '' THEN 1 END) as mark2_count,
                COUNT(CASE WHEN Mark3 IS NOT NULL AND Mark3 != '' THEN 1 END) as mark3_count
            FROM HORSE_MARKS 
            WHERE SourceDate = ?
        """, (test_date,))
        
        mark_stats = cursor.fetchone()
        total, m1, m2, m3 = mark_stats
        if total > 0:
            print(f"馬印データ: 馬印1={m1}({m1/total*100:.1f}%), 馬印2={m2}({m2/total*100:.1f}%), 馬印3={m3}({m3/total*100:.1f}%)")
        else:
            print(f"馬印データ: データなし")
        
        # サンプルデータの確認
        cursor.execute("""
            SELECT HorseName, Mark1, Mark2, Mark3, ImportedAt
            FROM HORSE_MARKS 
            WHERE SourceDate = ?
            LIMIT 3
        """, (test_date,))
        
        samples = cursor.fetchall()
        print("サンプルデータ:")
        for sample in samples:
            horse_name, m1, m2, m3, imported_at = sample
            print(f"  {horse_name}: 馬印1={m1}, 馬印2={m2}, 馬印3={m3}, インポート時刻={imported_at}")
        
        conn.close()
        
        # Excelファイルの確認
        excel_file = f"{test_date}.xlsx"
        excel_path = os.path.join(YDATE_DIR, excel_file)
        
        if os.path.exists(excel_path):
            try:
                # UTF-8エンコーディングでExcelファイルを読み込み
                df = pd.read_excel(excel_path, engine='openpyxl')
                print(f"Excelファイル: {len(df)} 行")
                
                # 馬印1のデータ確認
                if '馬印1' in df.columns:
                    mark1_data = df['馬印1'].dropna()
                    print(f"Excelの馬印1データ: {len(mark1_data)} 件")
                    print(f"Excelの馬印1例: {mark1_data.head(3).tolist()}")
                else:
                    print("Excelに馬印1列がありません")
                    
            except Exception as e:
                print(f"Excelファイル読み込みエラー: {e}")
        else:
            print(f"Excelファイルが見つかりません: {excel_path}")
        
        print()

    # 2. インポート処理の重複確認
    print("--- インポート処理の重複確認 ---")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 同じ日付で複数回インポートされているか確認
    cursor.execute("""
        SELECT SourceDate, COUNT(*) as import_count, 
               MIN(ImportedAt) as first_import, 
               MAX(ImportedAt) as last_import
        FROM HORSE_MARKS 
        WHERE SourceDate IN ('20250503', '20250504')
        GROUP BY SourceDate
    """)
    
    import_stats = cursor.fetchall()
    print("インポート統計:")
    for date, count, first, last in import_stats:
        print(f"  {date}: {count} 回インポート, 最初={first}, 最後={last}")
    
    # 3. データの整合性確認
    print("\n--- データの整合性確認 ---")
    
    # 同じ日付で異なるインポート時刻のデータがあるか確認
    cursor.execute("""
        SELECT SourceDate, ImportedAt, COUNT(*) as count
        FROM HORSE_MARKS 
        WHERE SourceDate IN ('20250503', '20250504')
        GROUP BY SourceDate, ImportedAt
        ORDER BY SourceDate, ImportedAt
    """)
    
    import_details = cursor.fetchall()
    print("インポート詳細:")
    for date, imported_at, count in import_details:
        print(f"  {date} {imported_at}: {count} 件")
    
    # 4. 問題の原因分析
    print("\n--- 問題の原因分析 ---")
    
    # 最新のインポート時刻を確認
    cursor.execute("SELECT MAX(ImportedAt) FROM HORSE_MARKS")
    latest_import = cursor.fetchone()[0]
    print(f"全体の最新インポート時刻: {latest_import}")
    
    # インポート時刻の分布
    cursor.execute("""
        SELECT DATE(ImportedAt) as import_date, COUNT(DISTINCT SourceDate) as date_count
        FROM HORSE_MARKS 
        WHERE ImportedAt >= datetime('now', '-7 days')
        GROUP BY DATE(ImportedAt)
        ORDER BY import_date DESC
    """)
    
    recent_imports = cursor.fetchall()
    print("最近7日間のインポート状況:")
    for import_date, date_count in recent_imports:
        print(f"  {import_date}: {date_count} 日分のデータ")
    
    conn.close()

if __name__ == '__main__':
    investigate_import_issue()
