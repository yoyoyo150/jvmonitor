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

def check_20250503_marks():
    print("=== 2025年5月3日の馬印データ確認 ===\n")

    # 1. オメガタキシードの2025年5月3日のデータを確認
    print("1. オメガタキシードの2025年5月3日のデータを確認")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # オメガタキシードの2025年5月3日のデータ
    cursor.execute("""
        SELECT HorseName, Mark1, Mark2, Mark3, Mark4, Mark5, Mark6, Mark7, Mark8,
               ZI_INDEX, ZM_VALUE, ImportedAt
        FROM HORSE_MARKS 
        WHERE SourceDate = '20250503' AND HorseName = 'オメガタキシード'
    """)
    
    omega_data = cursor.fetchone()
    if omega_data:
        horse_name, m1, m2, m3, m4, m5, m6, m7, m8, zi, zm, imported_at = omega_data
        print(f"馬名: {horse_name}")
        print(f"馬印1: {m1}")
        print(f"馬印2: {m2}")
        print(f"馬印3: {m3}")
        print(f"馬印4: {m4}")
        print(f"馬印5: {m5}")
        print(f"馬印6: {m6}")
        print(f"馬印7: {m7}")
        print(f"馬印8: {m8}")
        print(f"ZI指数: {zi}")
        print(f"ZM値: {zm}")
        print(f"インポート時刻: {imported_at}")
    else:
        print("❌ オメガタキシードの2025年5月3日のデータが見つかりません")

    # 2. 2025年5月3日の全馬印データの状況
    print("\n2. 2025年5月3日の全馬印データの状況")
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN Mark1 IS NOT NULL AND Mark1 != '' THEN 1 END) as mark1_count,
            COUNT(CASE WHEN Mark2 IS NOT NULL AND Mark2 != '' THEN 1 END) as mark2_count,
            COUNT(CASE WHEN Mark3 IS NOT NULL AND Mark3 != '' THEN 1 END) as mark3_count,
            COUNT(CASE WHEN Mark4 IS NOT NULL AND Mark4 != '' THEN 1 END) as mark4_count,
            COUNT(CASE WHEN Mark5 IS NOT NULL AND Mark5 != '' THEN 1 END) as mark5_count,
            COUNT(CASE WHEN Mark6 IS NOT NULL AND Mark6 != '' THEN 1 END) as mark6_count,
            COUNT(CASE WHEN Mark7 IS NOT NULL AND Mark7 != '' THEN 1 END) as mark7_count,
            COUNT(CASE WHEN Mark8 IS NOT NULL AND Mark8 != '' THEN 1 END) as mark8_count,
            COUNT(CASE WHEN ZI_INDEX IS NOT NULL AND ZI_INDEX != '' THEN 1 END) as zi_count,
            COUNT(CASE WHEN ZM_VALUE IS NOT NULL AND ZM_VALUE != '' THEN 1 END) as zm_count
        FROM HORSE_MARKS 
        WHERE SourceDate = '20250503'
    """)
    
    mark_stats = cursor.fetchone()
    total, m1, m2, m3, m4, m5, m6, m7, m8, zi, zm = mark_stats
    print(f"総レコード数: {total} 件")
    print(f"馬印1: {m1} 件 ({m1/total*100:.1f}%)")
    print(f"馬印2: {m2} 件 ({m2/total*100:.1f}%)")
    print(f"馬印3: {m3} 件 ({m3/total*100:.1f}%)")
    print(f"馬印4: {m4} 件 ({m4/total*100:.1f}%)")
    print(f"馬印5: {m5} 件 ({m5/total*100:.1f}%)")
    print(f"馬印6: {m6} 件 ({m6/total*100:.1f}%)")
    print(f"馬印7: {m7} 件 ({m7/total*100:.1f}%)")
    print(f"馬印8: {m8} 件 ({m8/total*100:.1f}%)")
    print(f"ZI指数: {zi} 件 ({zi/total*100:.1f}%)")
    print(f"ZM値: {zm} 件 ({zm/total*100:.1f}%)")

    # 3. Excelファイルの2025年5月3日のデータを確認
    print("\n3. Excelファイルの2025年5月3日のデータを確認")
    excel_file = "20250503.xlsx"
    excel_path = os.path.join(YDATE_DIR, excel_file)
    
    if os.path.exists(excel_path):
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
            
            # オメガタキシードのデータを検索
            omega_excel = df[df['馬名S'] == 'オメガタキシード']
            if not omega_excel.empty:
                row = omega_excel.iloc[0]
                print("Excelファイルのオメガタキシードのデータ:")
                print(f"馬名: {row.get('馬名S', '')}")
                print(f"馬印1: {row.get('馬印1', '')}")
                print(f"馬印2: {row.get('馬印2', '')}")
                print(f"馬印3: {row.get('馬印3', '')}")
                print(f"馬印4: {row.get('馬印4', '')}")
                print(f"馬印5: {row.get('馬印5', '')}")
                print(f"馬印6: {row.get('馬印6', '')}")
                print(f"馬印7: {row.get('馬印7', '')}")
                print(f"馬印8: {row.get('馬印8', '')}")
                print(f"ZI指数: {row.get('ZI指数', '')}")
                print(f"ZM値: {row.get('ZM値', '')}")
            else:
                print("❌ Excelファイルにオメガタキシードのデータが見つかりません")
                
        except Exception as e:
            print(f"Excelファイル読み込みエラー: {e}")
    else:
        print(f"❌ Excelファイルが見つかりません: {excel_path}")

    conn.close()

if __name__ == '__main__':
    check_20250503_marks()

