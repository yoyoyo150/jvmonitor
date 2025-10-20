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

def check_historical_marks():
    print("=== 過去の馬印データ確認 ===\n")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. 日付別の馬印データ状況を確認
    print("1. 日付別の馬印データ状況")
    cursor.execute("""
        SELECT 
            SourceDate,
            COUNT(*) as total_records,
            COUNT(CASE WHEN Mark1 IS NOT NULL AND Mark1 != '' THEN 1 END) as mark1_count,
            COUNT(CASE WHEN Mark2 IS NOT NULL AND Mark2 != '' THEN 1 END) as mark2_count,
            COUNT(CASE WHEN Mark3 IS NOT NULL AND Mark3 != '' THEN 1 END) as mark3_count,
            COUNT(CASE WHEN Mark4 IS NOT NULL AND Mark4 != '' THEN 1 END) as mark4_count,
            COUNT(CASE WHEN Mark5 IS NOT NULL AND Mark5 != '' THEN 1 END) as mark5_count,
            COUNT(CASE WHEN Mark6 IS NOT NULL AND Mark6 != '' THEN 1 END) as mark6_count
        FROM HORSE_MARKS 
        GROUP BY SourceDate 
        ORDER BY SourceDate DESC 
        LIMIT 10
    """)
    
    date_stats = cursor.fetchall()
    print("日付別統計:")
    for stats in date_stats:
        date, total, m1, m2, m3, m4, m5, m6 = stats
        print(f"  {date}: 総{total}件 - 馬印1:{m1}({m1/total*100:.1f}%) 馬印2:{m2}({m2/total*100:.1f}%) 馬印3:{m3}({m3/total*100:.1f}%) 馬印4:{m4}({m4/total*100:.1f}%) 馬印5:{m5}({m5/total*100:.1f}%) 馬印6:{m6}({m6/total*100:.1f}%)")

    # 2. 特定の馬（アッチャゴーラ）のデータを確認
    print("\n2. アッチャゴーラの馬印データ確認")
    cursor.execute("""
        SELECT SourceDate, Mark1, Mark2, Mark3, Mark4, Mark5, Mark6, Mark7, Mark8
        FROM HORSE_MARKS 
        WHERE HorseName = 'アッチャゴーラ'
        ORDER BY SourceDate DESC
        LIMIT 10
    """)
    
    accha_marks = cursor.fetchall()
    print("アッチャゴーラの馬印データ:")
    for record in accha_marks:
        date, m1, m2, m3, m4, m5, m6, m7, m8 = record
        print(f"  {date}: 馬印1={m1}, 馬印2={m2}, 馬印3={m3}, 馬印4={m4}, 馬印5={m5}, 馬印6={m6}, 馬印7={m7}, 馬印8={m8}")

    # 3. 馬印が空のレコードの分析
    print("\n3. 馬印が空のレコードの分析")
    cursor.execute("""
        SELECT SourceDate, COUNT(*) as empty_count
        FROM HORSE_MARKS 
        WHERE (Mark1 IS NULL OR Mark1 = '') 
        AND (Mark2 IS NULL OR Mark2 = '') 
        AND (Mark3 IS NULL OR Mark3 = '') 
        AND (Mark4 IS NULL OR Mark4 = '') 
        AND (Mark5 IS NULL OR Mark5 = '') 
        AND (Mark6 IS NULL OR Mark6 = '')
        GROUP BY SourceDate 
        ORDER BY SourceDate DESC
        LIMIT 10
    """)
    
    empty_stats = cursor.fetchall()
    print("馬印が全て空のレコード数:")
    for date, count in empty_stats:
        print(f"  {date}: {count} 件")

    # 4. Excelファイルの存在確認
    print("\n4. Excelファイルの存在確認")
    excel_files = [f for f in os.listdir(YDATE_DIR) if f.endswith('.xlsx')]
    excel_files.sort(reverse=True)
    
    print("yDateフォルダのExcelファイル（最新10件）:")
    for i, file in enumerate(excel_files[:10]):
        file_path = os.path.join(YDATE_DIR, file)
        file_size = os.path.getsize(file_path)
        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        print(f"  {file}: {file_size:,} bytes, 更新: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")

    conn.close()

if __name__ == '__main__':
    check_historical_marks()


