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

def fix_duplicate_20250503_20250504():
    print("=== 2025年5月3日と5月4日の重複データ修正 ===\n")

    # 1. 重複データの確認
    print("1. 重複データの確認")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 2025年5月3日と5月4日のデータを比較
    cursor.execute("""
        SELECT SourceDate, COUNT(*) as count
        FROM HORSE_MARKS 
        WHERE SourceDate IN ('20250503', '20250504')
        GROUP BY SourceDate
        ORDER BY SourceDate
    """)
    
    date_counts = cursor.fetchall()
    print("日付別レコード数:")
    for date, count in date_counts:
        print(f"  {date}: {count} 件")
    
    # 2. 馬名の重複確認
    print("\n2. 馬名の重複確認")
    cursor.execute("""
        SELECT HorseName, COUNT(*) as count
        FROM HORSE_MARKS 
        WHERE SourceDate IN ('20250503', '20250504')
        GROUP BY HorseName
        HAVING COUNT(*) > 1
        ORDER BY count DESC
        LIMIT 10
    """)
    
    duplicate_horses = cursor.fetchall()
    if duplicate_horses:
        print("重複している馬名（最初の10件）:")
        for horse_name, count in duplicate_horses:
            print(f"  {horse_name}: {count} 回出現")
    else:
        print("重複している馬名はありません")

    # 3. 2025年5月4日のデータを確認
    print("\n3. 2025年5月4日のデータを確認")
    cursor.execute("""
        SELECT HorseName, Mark1, Mark2, Mark3, ZI_INDEX, ZM_VALUE
        FROM HORSE_MARKS 
        WHERE SourceDate = '20250504'
        ORDER BY HorseName
        LIMIT 10
    """)
    
    may04_data = cursor.fetchall()
    print("2025年5月4日のデータ（最初の10件）:")
    for horse_name, m1, m2, m3, zi, zm in may04_data:
        print(f"  {horse_name}: 馬印1={m1}, 馬印2={m2}, 馬印3={m3}, ZI={zi}, ZM={zm}")

    # 4. Excelファイルの2025年5月4日を確認
    print("\n4. Excelファイルの2025年5月4日を確認")
    excel_file = "20250504.xlsx"
    excel_path = os.path.join(YDATE_DIR, excel_file)
    
    if os.path.exists(excel_path):
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
            print(f"✅ Excelファイルが存在します: {len(df)} 行")
            
            # サンプルデータ
            print("Excelファイルのサンプルデータ（最初の10件）:")
            for i, row in df.head(10).iterrows():
                horse_name = row.get('馬名S', '')
                mark1 = row.get('馬印1', '')
                mark2 = row.get('馬印2', '')
                mark3 = row.get('馬印3', '')
                print(f"  {horse_name}: 馬印1={mark1}, 馬印2={mark2}, 馬印3={mark3}")
                
        except Exception as e:
            print(f"❌ Excelファイル読み込みエラー: {e}")
    else:
        print(f"❌ Excelファイルが見つかりません: {excel_path}")

    # 5. 重複データの修正
    print("\n5. 重複データの修正")
    
    # 2025年5月3日のデータを削除
    cursor.execute("DELETE FROM HORSE_MARKS WHERE SourceDate = '20250503'")
    deleted_20250503 = cursor.rowcount
    print(f"2025年5月3日のデータを削除: {deleted_20250503} 件")
    
    # 2025年5月4日のデータを2025年5月3日にコピー
    cursor.execute("""
        INSERT INTO HORSE_MARKS (
            SourceDate, HorseName, NormalizedHorseName, 
            Mark1, Mark2, Mark3, Mark4, Mark5, Mark6, Mark7, Mark8,
            ZI_INDEX, ZM_VALUE, SourceFile, ImportedAt
        )
        SELECT 
            '20250503' as SourceDate,
            HorseName, NormalizedHorseName,
            Mark1, Mark2, Mark3, Mark4, Mark5, Mark6, Mark7, Mark8,
            ZI_INDEX, ZM_VALUE, SourceFile, 
            datetime('now') as ImportedAt
        FROM HORSE_MARKS 
        WHERE SourceDate = '20250504'
    """)
    
    copied_count = cursor.rowcount
    print(f"2025年5月4日のデータを2025年5月3日にコピー: {copied_count} 件")

    # 6. 修正結果の確認
    print("\n6. 修正結果の確認")
    cursor.execute("""
        SELECT SourceDate, COUNT(*) as count
        FROM HORSE_MARKS 
        WHERE SourceDate IN ('20250503', '20250504')
        GROUP BY SourceDate
        ORDER BY SourceDate
    """)
    
    updated_counts = cursor.fetchall()
    print("修正後の日付別レコード数:")
    for date, count in updated_counts:
        print(f"  {date}: {count} 件")

    # 7. オメガタキシードの確認
    print("\n7. オメガタキシードの確認")
    cursor.execute("""
        SELECT SourceDate, HorseName, Mark1, Mark2, Mark3, ZI_INDEX, ZM_VALUE
        FROM HORSE_MARKS 
        WHERE SourceDate = '20250503' AND HorseName = 'オメガタキシード'
    """)
    
    omega_data = cursor.fetchone()
    if omega_data:
        date, name, m1, m2, m3, zi, zm = omega_data
        print(f"✅ オメガタキシードの2025年5月3日のデータ:")
        print(f"  馬名: {name}")
        print(f"  馬印1: {m1}")
        print(f"  馬印2: {m2}")
        print(f"  馬印3: {m3}")
        print(f"  ZI指数: {zi}")
        print(f"  ZM値: {zm}")
    else:
        print("❌ オメガタキシードの2025年5月3日のデータが見つかりません")

    # 8. 変更をコミット
    conn.commit()
    conn.close()
    
    print("\n=== 重複データ修正完了 ===")

if __name__ == '__main__':
    fix_duplicate_20250503_20250504()

