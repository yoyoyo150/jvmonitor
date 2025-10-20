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

def find_omega_tuxedo():
    print("=== オメガタキシードの特定 ===\n")

    # 1. Excelファイルからオメガタキシードを検索
    print("1. Excelファイルからオメガタキシードを検索")
    excel_file = "20250503.xlsx"
    excel_path = os.path.join(YDATE_DIR, excel_file)
    
    if not os.path.exists(excel_path):
        print(f"❌ Excelファイルが見つかりません: {excel_path}")
        return
    
    try:
        df = pd.read_excel(excel_path, engine='openpyxl')
        print(f"✅ Excelファイル読み込み成功: {len(df)} 行")
        
        # オメガタキシードを検索
        omega_excel = df[df['馬名S'].str.contains('オメガタキシード', na=False)]
        if not omega_excel.empty:
            print("✅ Excelファイルでオメガタキシードを発見:")
            for i, row in omega_excel.iterrows():
                print(f"  馬名: {row.get('馬名S', '')}")
                print(f"  馬印1: {row.get('馬印1', '')}")
                print(f"  馬印2: {row.get('馬印2', '')}")
                print(f"  馬印3: {row.get('馬印3', '')}")
                print(f"  ZI指数: {row.get('ZI指数', '')}")
                print(f"  ZM値: {row.get('ZM値', '')}")
        else:
            print("❌ Excelファイルにオメガタキシードが見つかりません")
            
            # 類似の馬名を検索
            print("\n類似の馬名を検索:")
            similar_horses = df[df['馬名S'].str.contains('オメガ', na=False) | df['馬名S'].str.contains('タキシード', na=False)]
            if not similar_horses.empty:
                print("オメガまたはタキシードを含む馬名:")
                for i, row in similar_horses.iterrows():
                    print(f"  {row.get('馬名S', '')}")
            else:
                print("類似の馬名が見つかりません")
                
    except Exception as e:
        print(f"❌ Excelファイル読み込みエラー: {e}")
        return

    # 2. データベースからオメガタキシードを検索
    print("\n2. データベースからオメガタキシードを検索")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # オメガタキシードを検索
    cursor.execute("""
        SELECT HorseName, Mark1, Mark2, Mark3, Mark4, Mark5, Mark6, Mark7, Mark8,
               ZI_INDEX, ZM_VALUE
        FROM HORSE_MARKS 
        WHERE SourceDate = '20250503' AND HorseName = 'オメガタキシード'
    """)
    
    omega_db = cursor.fetchone()
    if omega_db:
        print("✅ データベースでオメガタキシードを発見:")
        horse_name, m1, m2, m3, m4, m5, m6, m7, m8, zi, zm = omega_db
        print(f"  馬名: {horse_name}")
        print(f"  馬印1: {m1}")
        print(f"  馬印2: {m2}")
        print(f"  馬印3: {m3}")
        print(f"  馬印4: {m4}")
        print(f"  馬印5: {m5}")
        print(f"  馬印6: {m6}")
        print(f"  馬印7: {m7}")
        print(f"  馬印8: {m8}")
        print(f"  ZI指数: {zi}")
        print(f"  ZM値: {zm}")
    else:
        print("❌ データベースにオメガタキシードが見つかりません")
        
        # 類似の馬名を検索
        print("\n類似の馬名を検索:")
        cursor.execute("""
            SELECT HorseName, Mark1, Mark2, Mark3, ZI_INDEX, ZM_VALUE
            FROM HORSE_MARKS 
            WHERE SourceDate = '20250503' 
            AND (HorseName LIKE '%オメガ%' OR HorseName LIKE '%タキシード%')
        """)
        
        similar_db = cursor.fetchall()
        if similar_db:
            print("オメガまたはタキシードを含む馬名:")
            for record in similar_db:
                horse_name, m1, m2, m3, zi, zm = record
                print(f"  {horse_name}: 馬印1={m1}, 馬印2={m2}, 馬印3={m3}, ZI={zi}, ZM={zm}")
        else:
            print("類似の馬名が見つかりません")

    conn.close()

    # 3. 問題の原因分析
    print("\n3. 問題の原因分析")
    if omega_excel.empty and not omega_db:
        print("❌ オメガタキシードのデータがExcelファイルにもデータベースにも存在しません")
        print("   原因: 馬名の表記が異なるか、データが欠損している可能性があります")
    elif not omega_excel.empty and not omega_db:
        print("❌ オメガタキシードのデータがExcelファイルには存在するが、データベースに存在しません")
        print("   原因: インポート処理が失敗している可能性があります")
    elif omega_excel.empty and omega_db:
        print("❌ オメガタキシードのデータがデータベースには存在するが、Excelファイルに存在しません")
        print("   原因: データの不整合が発生している可能性があります")
    else:
        print("✅ オメガタキシードのデータは正常に存在します")

if __name__ == '__main__':
    find_omega_tuxedo()

