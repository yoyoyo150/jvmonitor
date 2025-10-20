import sqlite3
import os
from datetime import datetime, timedelta

def check_historical_data_coverage():
    """古いデータの登録状況を包括的に調査"""
    
    print("=== 歴史的データの登録状況調査 ===")
    
    # yDateフォルダのファイル分析
    print("\n1. yDateフォルダのファイル分析")
    ydate_files = []
    if os.path.exists('yDate'):
        for file in os.listdir('yDate'):
            if file.endswith(('.xlsx', '.xls', '.csv')) and not file.startswith('25025'):
                ydate_files.append(file)
    
    ydate_files.sort()
    print(f"総ファイル数: {len(ydate_files)}")
    
    # 年別ファイル数
    year_counts = {}
    for file in ydate_files:
        if file.startswith('2024'):
            year_counts['2024'] = year_counts.get('2024', 0) + 1
        elif file.startswith('2025'):
            year_counts['2025'] = year_counts.get('2025', 0) + 1
    
    print(f"2024年ファイル数: {year_counts.get('2024', 0)}")
    print(f"2025年ファイル数: {year_counts.get('2025', 0)}")
    
    # 最新と最古のファイル
    if ydate_files:
        print(f"最古ファイル: {ydate_files[0]}")
        print(f"最新ファイル: {ydate_files[-1]}")
    
    # データベースの状況確認
    print("\n2. データベースの状況確認")
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    # 年別レコード数
    cursor.execute("""
        SELECT 
            CASE 
                WHEN SourceDate LIKE '2024%' THEN '2024'
                WHEN SourceDate LIKE '2025%' THEN '2025'
                ELSE 'その他'
            END as year,
            COUNT(*) as count
        FROM HORSE_MARKS 
        GROUP BY year
        ORDER BY year
    """)
    
    print("\n年別レコード数:")
    for row in cursor.fetchall():
        print(f"  {row[0]}年: {row[1]:,}件")
    
    # 月別データ分布（2024年）
    cursor.execute("""
        SELECT SourceDate, COUNT(*) as count
        FROM HORSE_MARKS 
        WHERE SourceDate LIKE '2024%'
        GROUP BY SourceDate 
        ORDER BY SourceDate DESC
        LIMIT 10
    """)
    
    print("\n2024年の最新10日間:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]:,}件")
    
    # 月別データ分布（2025年）
    cursor.execute("""
        SELECT SourceDate, COUNT(*) as count
        FROM HORSE_MARKS 
        WHERE SourceDate LIKE '2025%'
        GROUP BY SourceDate 
        ORDER BY SourceDate DESC
        LIMIT 10
    """)
    
    print("\n2025年の最新10日間:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]:,}件")
    
    # データの欠落期間を特定
    print("\n3. データ欠落期間の特定")
    
    # 2024年のファイルとDBの比較
    files_2024 = [f for f in ydate_files if f.startswith('2024')]
    print(f"2024年ファイル数: {len(files_2024)}")
    
    cursor.execute("SELECT COUNT(DISTINCT SourceDate) FROM HORSE_MARKS WHERE SourceDate LIKE '2024%'")
    db_2024_days = cursor.fetchone()[0]
    print(f"2024年DB日数: {db_2024_days}")
    
    if len(files_2024) > db_2024_days:
        print("⚠️ 2024年のファイル数 > DB日数 → データ欠落の可能性")
    
    conn.close()

if __name__ == "__main__":
    check_historical_data_coverage()




