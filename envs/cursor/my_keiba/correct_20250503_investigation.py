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

def correct_20250503_investigation():
    print("=== 2025年5月3日の正しい調査 ===\n")

    # 1. データベースの2025年5月3日の全データを確認
    print("1. データベースの2025年5月3日の全データを確認")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 2025年5月3日の全レコード数
    cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS WHERE SourceDate = '20250503'")
    db_count = cursor.fetchone()[0]
    print(f"データベースのレコード数: {db_count} 件")
    
    # 全馬名を表示
    cursor.execute("""
        SELECT HorseName, Mark1, Mark2, Mark3, ZI_INDEX, ZM_VALUE
        FROM HORSE_MARKS 
        WHERE SourceDate = '20250503'
        ORDER BY HorseName
    """)
    
    all_horses = cursor.fetchall()
    print(f"\n2025年5月3日の全馬名（{len(all_horses)}件）:")
    for i, (horse_name, m1, m2, m3, zi, zm) in enumerate(all_horses, 1):
        print(f"  {i:2d}. {horse_name}: 馬印1={m1}, 馬印2={m2}, 馬印3={m3}, ZI={zi}, ZM={zm}")

    # 2. 画面で表示されている馬名を検索
    print("\n2. 画面で表示されている馬名を検索")
    
    # 画面で確認できる馬名を検索
    screen_horses = [
        "イデアイゴッソウ",  # 画面で確認できる馬名
        "オメガタキシード",  # ユーザーが言及した馬名
    ]
    
    for horse_name in screen_horses:
        cursor.execute("""
            SELECT HorseName, Mark1, Mark2, Mark3, ZI_INDEX, ZM_VALUE
            FROM HORSE_MARKS 
            WHERE SourceDate = '20250503' AND HorseName = ?
        """, (horse_name,))
        
        result = cursor.fetchone()
        if result:
            print(f"✅ {horse_name} が見つかりました:")
            horse_name, m1, m2, m3, zi, zm = result
            print(f"  馬印1: {m1}, 馬印2: {m2}, 馬印3: {m3}, ZI: {zi}, ZM: {zm}")
        else:
            print(f"❌ {horse_name} が見つかりません")

    # 3. Excelファイルの2025年5月3日の全データを確認
    print("\n3. Excelファイルの2025年5月3日の全データを確認")
    excel_file = "20250503.xlsx"
    excel_path = os.path.join(YDATE_DIR, excel_file)
    
    if os.path.exists(excel_path):
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
            print(f"✅ Excelファイル読み込み成功: {len(df)} 行")
            
            # 全馬名を表示
            print(f"\nExcelファイルの全馬名（{len(df)}件）:")
            for i, row in df.iterrows():
                horse_name = row.get('馬名S', '')
                mark1 = row.get('馬印1', '')
                mark2 = row.get('馬印2', '')
                mark3 = row.get('馬印3', '')
                zi = row.get('ZI指数', '')
                zm = row.get('ZM値', '')
                print(f"  {i+1:2d}. {horse_name}: 馬印1={mark1}, 馬印2={mark2}, 馬印3={mark3}, ZI={zi}, ZM={zm}")
                
        except Exception as e:
            print(f"❌ Excelファイル読み込みエラー: {e}")
    else:
        print(f"❌ Excelファイルが見つかりません: {excel_path}")

    # 4. データの整合性確認
    print("\n4. データの整合性確認")
    if db_count > 0 and os.path.exists(excel_path):
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
            excel_count = len(df)
            
            print(f"データベース: {db_count} 件")
            print(f"Excelファイル: {excel_count} 件")
            
            if db_count == excel_count:
                print("✅ レコード数は一致しています")
            else:
                print(f"⚠️ レコード数が不一致")
                
        except Exception as e:
            print(f"❌ 整合性確認エラー: {e}")

    conn.close()

if __name__ == '__main__':
    correct_20250503_investigation()

