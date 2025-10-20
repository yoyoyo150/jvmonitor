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

def investigate_omega_tuxedo():
    print("=== オメガタキシードの詳細調査 ===\n")

    # 1. オメガタキシードの全データを確認
    print("1. オメガタキシードの全データを確認")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # オメガタキシードの全データ
    cursor.execute("""
        SELECT SourceDate, HorseName, Mark1, Mark2, Mark3, Mark4, Mark5, Mark6, Mark7, Mark8,
               ZI_INDEX, ZM_VALUE, ImportedAt
        FROM HORSE_MARKS 
        WHERE HorseName = 'オメガタキシード'
        ORDER BY SourceDate DESC
    """)
    
    omega_all_data = cursor.fetchall()
    if omega_all_data:
        print(f"オメガタキシードのデータ: {len(omega_all_data)} 件")
        print("全データ:")
        for data in omega_all_data:
            date, name, m1, m2, m3, m4, m5, m6, m7, m8, zi, zm, imported_at = data
            print(f"  {date}: 馬印1={m1}, 馬印2={m2}, 馬印3={m3}, 馬印4={m4}, 馬印5={m5}, 馬印6={m6}, 馬印7={m7}, 馬印8={m8}, ZI={zi}, ZM={zm}")
    else:
        print("❌ オメガタキシードのデータが全く見つかりません")

    # 2. 類似の馬名を検索
    print("\n2. 類似の馬名を検索")
    cursor.execute("""
        SELECT DISTINCT HorseName 
        FROM HORSE_MARKS 
        WHERE HorseName LIKE '%オメガ%' OR HorseName LIKE '%タキシード%'
        ORDER BY HorseName
    """)
    
    similar_horses = cursor.fetchall()
    if similar_horses:
        print("類似の馬名:")
        for horse in similar_horses:
            print(f"  {horse[0]}")
    else:
        print("類似の馬名が見つかりません")

    # 3. 2025年5月3日の全馬名を確認
    print("\n3. 2025年5月3日の全馬名を確認")
    cursor.execute("""
        SELECT HorseName 
        FROM HORSE_MARKS 
        WHERE SourceDate = '20250503'
        ORDER BY HorseName
    """)
    
    all_horses_20250503 = cursor.fetchall()
    print(f"2025年5月3日の全馬名: {len(all_horses_20250503)} 件")
    
    # オメガで始まる馬名を検索
    omega_horses = [horse[0] for horse in all_horses_20250503 if 'オメガ' in horse[0]]
    if omega_horses:
        print("オメガで始まる馬名:")
        for horse in omega_horses:
            print(f"  {horse}")
    else:
        print("オメガで始まる馬名が見つかりません")

    # 4. Excelファイルの2025年5月3日の全馬名を確認
    print("\n4. Excelファイルの2025年5月3日の全馬名を確認")
    excel_file = "20250503.xlsx"
    excel_path = os.path.join(YDATE_DIR, excel_file)
    
    if os.path.exists(excel_path):
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
            
            # オメガで始まる馬名を検索
            omega_excel_horses = df[df['馬名S'].str.contains('オメガ', na=False)]['馬名S'].tolist()
            if omega_excel_horses:
                print("Excelファイルのオメガで始まる馬名:")
                for horse in omega_excel_horses:
                    print(f"  {horse}")
            else:
                print("Excelファイルにオメガで始まる馬名が見つかりません")
                
            # タキシードを含む馬名を検索
            tuxedo_excel_horses = df[df['馬名S'].str.contains('タキシード', na=False)]['馬名S'].tolist()
            if tuxedo_excel_horses:
                print("Excelファイルのタキシードを含む馬名:")
                for horse in tuxedo_excel_horses:
                    print(f"  {horse}")
            else:
                print("Excelファイルにタキシードを含む馬名が見つかりません")
                
        except Exception as e:
            print(f"Excelファイル読み込みエラー: {e}")
    else:
        print(f"❌ Excelファイルが見つかりません: {excel_path}")

    # 5. 問題の原因分析
    print("\n5. 問題の原因分析")
    if not omega_all_data:
        print("❌ オメガタキシードのデータがデータベースに全く存在しません")
        print("   原因: 馬名の表記が異なる可能性があります")
    elif not any(data[0] == '20250503' for data in omega_all_data):
        print("❌ オメガタキシードの2025年5月3日のデータが存在しません")
        print("   原因: 該当日のレースに出走していない可能性があります")
    else:
        print("✅ オメガタキシードのデータは存在します")

    conn.close()

if __name__ == '__main__':
    investigate_omega_tuxedo()

