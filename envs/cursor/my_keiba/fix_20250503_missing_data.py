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

def fix_20250503_missing_data():
    print("=== 2025年5月3日の欠損データ修正 ===\n")

    # 1. Excelファイルからデータを読み込み
    print("1. Excelファイルからデータを読み込み")
    excel_file = "20250503.xlsx"
    excel_path = os.path.join(YDATE_DIR, excel_file)
    
    if not os.path.exists(excel_path):
        print(f"❌ Excelファイルが見つかりません: {excel_path}")
        return
    
    try:
        df = pd.read_excel(excel_path, engine='openpyxl')
        print(f"✅ Excelファイル読み込み成功: {len(df)} 行")
    except Exception as e:
        print(f"❌ Excelファイル読み込みエラー: {e}")
        return

    # 2. データベースに接続
    print("\n2. データベースに接続")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 3. 欠損データを特定
    print("\n3. 欠損データを特定")
    
    # ZI指数とZM値が欠損しているレコードを特定
    cursor.execute("""
        SELECT HorseName, ZI_INDEX, ZM_VALUE
        FROM HORSE_MARKS 
        WHERE SourceDate = '20250503' 
        AND (ZI_INDEX IS NULL OR ZI_INDEX = '' OR ZM_VALUE IS NULL OR ZM_VALUE = '')
        LIMIT 10
    """)
    
    missing_data = cursor.fetchall()
    print(f"ZI指数・ZM値が欠損しているレコード: {len(missing_data)} 件")
    print("欠損データの例（最初の10件）:")
    for record in missing_data:
        horse_name, zi, zm = record
        print(f"  {horse_name}: ZI={zi}, ZM={zm}")

    # 4. Excelファイルから欠損データを補完
    print("\n4. Excelファイルから欠損データを補完")
    
    updated_count = 0
    for index, row in df.iterrows():
        horse_name = row.get('馬名S', '')
        if not horse_name:
            continue
            
        # Excelからデータを取得
        zi_index = row.get('ZI指数', '')
        zm_value = row.get('ZM値', '')
        mark1 = row.get('馬印1', '')
        mark3 = row.get('馬印3', '')
        
        # データベースを更新
        try:
            cursor.execute("""
                UPDATE HORSE_MARKS 
                SET ZI_INDEX = ?, ZM_VALUE = ?, Mark1 = ?, Mark3 = ?
                WHERE SourceDate = '20250503' AND HorseName = ?
            """, (
                str(zi_index) if pd.notna(zi_index) else None,
                str(zm_value) if pd.notna(zm_value) else None,
                str(mark1) if pd.notna(mark1) else None,
                str(mark3) if pd.notna(mark3) else None,
                horse_name
            ))
            
            if cursor.rowcount > 0:
                updated_count += 1
                
        except Exception as e:
            print(f"更新エラー {horse_name}: {e}")
            continue

    # 5. 変更をコミット
    conn.commit()
    print(f"\n✅ {updated_count} 件のレコードを更新しました")

    # 6. 更新結果を確認
    print("\n6. 更新結果を確認")
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN Mark1 IS NOT NULL AND Mark1 != '' THEN 1 END) as mark1_count,
            COUNT(CASE WHEN Mark2 IS NOT NULL AND Mark2 != '' THEN 1 END) as mark2_count,
            COUNT(CASE WHEN Mark3 IS NOT NULL AND Mark3 != '' THEN 1 END) as mark3_count,
            COUNT(CASE WHEN ZI_INDEX IS NOT NULL AND ZI_INDEX != '' THEN 1 END) as zi_count,
            COUNT(CASE WHEN ZM_VALUE IS NOT NULL AND ZM_VALUE != '' THEN 1 END) as zm_count
        FROM HORSE_MARKS 
        WHERE SourceDate = '20250503'
    """)
    
    updated_stats = cursor.fetchone()
    total, m1, m2, m3, zi, zm = updated_stats
    print(f"更新後の状況:")
    print(f"  総レコード数: {total} 件")
    print(f"  馬印1: {m1} 件 ({m1/total*100:.1f}%)")
    print(f"  馬印2: {m2} 件 ({m2/total*100:.1f}%)")
    print(f"  馬印3: {m3} 件 ({m3/total*100:.1f}%)")
    print(f"  ZI指数: {zi} 件 ({zi/total*100:.1f}%)")
    print(f"  ZM値: {zm} 件 ({zm/total*100:.1f}%)")

    # 7. オメガタキシードのデータを確認
    print("\n7. オメガタキシードのデータを確認")
    cursor.execute("""
        SELECT HorseName, Mark1, Mark2, Mark3, Mark4, Mark5, Mark6, Mark7, Mark8,
               ZI_INDEX, ZM_VALUE
        FROM HORSE_MARKS 
        WHERE SourceDate = '20250503' AND HorseName = 'オメガタキシード'
    """)
    
    omega_data = cursor.fetchone()
    if omega_data:
        horse_name, m1, m2, m3, m4, m5, m6, m7, m8, zi, zm = omega_data
        print(f"✅ オメガタキシードのデータ:")
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
        print("❌ オメガタキシードのデータが見つかりません")

    conn.close()
    print("\n=== 修正完了 ===")

if __name__ == '__main__':
    fix_20250503_missing_data()

