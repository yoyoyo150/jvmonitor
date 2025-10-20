import sqlite3
import os
import pandas as pd
from datetime import datetime

def investigate_date_issue():
    """異常な日付データの原因を調査"""
    
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    print("=== 異常な日付データの詳細調査 ===")
    
    # 異常な日付のパターンを確認
    cursor.execute("""
        SELECT SourceDate, COUNT(*) as count
        FROM HORSE_MARKS 
        WHERE SourceDate LIKE '25025%'
        GROUP BY SourceDate 
        ORDER BY SourceDate DESC
    """)
    
    print("\n異常な日付パターン:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]:,}件")
    
    # 正常な日付のパターンも確認
    cursor.execute("""
        SELECT SourceDate, COUNT(*) as count
        FROM HORSE_MARKS 
        WHERE SourceDate NOT LIKE '25025%' AND SourceDate LIKE '2025%'
        GROUP BY SourceDate 
        ORDER BY SourceDate DESC
        LIMIT 10
    """)
    
    print("\n正常な日付パターン:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]:,}件")
    
    # ファイル名から日付を抽出する処理を確認
    print("\n=== yDateフォルダの実際のファイル名 ===")
    ydate_files = []
    if os.path.exists('yDate'):
        for file in os.listdir('yDate'):
            if file.endswith(('.xlsx', '.xls', '.csv')):
                ydate_files.append(file)
    
    ydate_files.sort()
    print(f"総ファイル数: {len(ydate_files)}")
    print("最新10ファイル:")
    for file in ydate_files[-10:]:
        print(f"  {file}")
    
    # 異常な日付のサンプルデータを確認
    cursor.execute("""
        SELECT SourceDate, HorseNameS, Trainer_Name, Mark5, Mark6
        FROM HORSE_MARKS 
        WHERE SourceDate LIKE '25025%'
        LIMIT 5
    """)
    
    print("\n異常な日付のサンプルデータ:")
    for row in cursor.fetchall():
        print(f"  日付: {row[0]}, 馬名: {row[1]}, 調教師: {row[2]}, M5: {row[3]}, M6: {row[4]}")
    
    conn.close()

if __name__ == "__main__":
    investigate_date_issue()




