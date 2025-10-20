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

def correct_20250503_check():
    print("=== 2025年5月3日の正しい調査 ===\n")

    # 1. オメガタキシードの2025年5月3日のデータを再確認
    print("1. オメガタキシードの2025年5月3日のデータを再確認")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # より柔軟な検索条件で確認
    cursor.execute("""
        SELECT SourceDate, HorseName, Mark1, Mark2, Mark3, Mark4, Mark5, Mark6, Mark7, Mark8,
               ZI_INDEX, ZM_VALUE, ImportedAt
        FROM HORSE_MARKS 
        WHERE SourceDate = '20250503' AND HorseName LIKE '%オメガ%'
    """)
    
    omega_20250503 = cursor.fetchall()
    if omega_20250503:
        print("2025年5月3日のオメガで始まる馬名:")
        for data in omega_20250503:
            date, name, m1, m2, m3, m4, m5, m6, m7, m8, zi, zm, imported_at = data
            print(f"  {name}: 馬印1={m1}, 馬印2={m2}, 馬印3={m3}, 馬印4={m4}, 馬印5={m5}, 馬印6={m6}, 馬印7={m7}, 馬印8={m8}, ZI={zi}, ZM={zm}")
    else:
        print("❌ 2025年5月3日にオメガで始まる馬名が見つかりません")

    # 2. タキシードを含む馬名を検索
    print("\n2. タキシードを含む馬名を検索")
    cursor.execute("""
        SELECT SourceDate, HorseName, Mark1, Mark2, Mark3, Mark4, Mark5, Mark6, Mark7, Mark8,
               ZI_INDEX, ZM_VALUE, ImportedAt
        FROM HORSE_MARKS 
        WHERE SourceDate = '20250503' AND HorseName LIKE '%タキシード%'
    """)
    
    tuxedo_20250503 = cursor.fetchall()
    if tuxedo_20250503:
        print("2025年5月3日のタキシードを含む馬名:")
        for data in tuxedo_20250503:
            date, name, m1, m2, m3, m4, m5, m6, m7, m8, zi, zm, imported_at = data
            print(f"  {name}: 馬印1={m1}, 馬印2={m2}, 馬印3={m3}, 馬印4={m4}, 馬印5={m5}, 馬印6={m6}, 馬印7={m7}, 馬印8={m8}, ZI={zi}, ZM={zm}")
    else:
        print("❌ 2025年5月3日にタキシードを含む馬名が見つかりません")

    # 3. 戸崎圭太騎手の2025年5月3日のデータを確認
    print("\n3. 戸崎圭太騎手の2025年5月3日のデータを確認")
    cursor.execute("""
        SELECT HorseName, Mark1, Mark2, Mark3, Mark4, Mark5, Mark6, Mark7, Mark8,
               ZI_INDEX, ZM_VALUE, ImportedAt
        FROM HORSE_MARKS 
        WHERE SourceDate = '20250503' AND JOCKEY = '戸崎圭太'
    """)
    
    tozaki_20250503 = cursor.fetchall()
    if tozaki_20250503:
        print("戸崎圭太騎手の2025年5月3日の騎乗馬:")
        for data in tozaki_20250503:
            name, m1, m2, m3, m4, m5, m6, m7, m8, zi, zm, imported_at = data
            print(f"  {name}: 馬印1={m1}, 馬印2={m2}, 馬印3={m3}, 馬印4={m4}, 馬印5={m5}, 馬印6={m6}, 馬印7={m7}, 馬印8={m8}, ZI={zi}, ZM={zm}")
    else:
        print("❌ 戸崎圭太騎手の2025年5月3日の騎乗馬が見つかりません")

    # 4. Excelファイルの詳細確認
    print("\n4. Excelファイルの詳細確認")
    excel_file = "20250503.xlsx"
    excel_path = os.path.join(YDATE_DIR, excel_file)
    
    if os.path.exists(excel_path):
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
            
            # 戸崎圭太騎手のデータを検索
            tozaki_excel = df[df['騎手'] == '戸崎圭太']
            if not tozaki_excel.empty:
                print("Excelファイルの戸崎圭太騎手の騎乗馬:")
                for i, row in tozaki_excel.iterrows():
                    print(f"  {row.get('馬名S', '')}: 馬印1={row.get('馬印1', '')}, 馬印2={row.get('馬印2', '')}, 馬印3={row.get('馬印3', '')}")
            else:
                print("Excelファイルに戸崎圭太騎手のデータが見つかりません")
                
            # オメガタキシードを別の列名で検索
            possible_columns = ['馬名S', '馬名', 'HorseName', '馬名1', '馬名2']
            for col in possible_columns:
                if col in df.columns:
                    omega_excel = df[df[col].str.contains('オメガタキシード', na=False)]
                    if not omega_excel.empty:
                        print(f"Excelファイルの{col}列でオメガタキシードを発見:")
                        for i, row in omega_excel.iterrows():
                            print(f"  {row.get(col, '')}: 馬印1={row.get('馬印1', '')}, 馬印2={row.get('馬印2', '')}, 馬印3={row.get('馬印3', '')}")
                        break
            else:
                print("Excelファイルにオメガタキシードが見つかりません")
                
        except Exception as e:
            print(f"Excelファイル読み込みエラー: {e}")
    else:
        print(f"❌ Excelファイルが見つかりません: {excel_path}")

    # 5. 問題の特定
    print("\n5. 問題の特定")
    print("画面では2025年5月3日に3着で出走していることが確認されています。")
    print("データベースに該当データが存在しない原因:")
    print("1. 馬名の表記が異なる")
    print("2. データのインポートが不完全")
    print("3. データベースの構造の問題")

    conn.close()

if __name__ == '__main__':
    correct_20250503_check()

