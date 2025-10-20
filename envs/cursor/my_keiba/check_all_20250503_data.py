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

def check_all_20250503_data():
    print("=== 2025年5月3日の全データ状況確認 ===\n")

    # 1. データベースの2025年5月3日の全データ確認
    print("1. データベースの2025年5月3日の全データ確認")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 2025年5月3日の全レコード数
    cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS WHERE SourceDate = '20250503'")
    db_count = cursor.fetchone()[0]
    print(f"データベースのレコード数: {db_count} 件")
    
    if db_count > 0:
        # 馬印データの状況
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
        
        mark_stats = cursor.fetchone()
        total, m1, m2, m3, zi, zm = mark_stats
        print(f"馬印1: {m1} 件 ({m1/total*100:.1f}%)")
        print(f"馬印2: {m2} 件 ({m2/total*100:.1f}%)")
        print(f"馬印3: {m3} 件 ({m3/total*100:.1f}%)")
        print(f"ZI指数: {zi} 件 ({zi/total*100:.1f}%)")
        print(f"ZM値: {zm} 件 ({zm/total*100:.1f}%)")
        
        # サンプルデータ
        cursor.execute("""
            SELECT HorseName, Mark1, Mark2, Mark3, ZI_INDEX, ZM_VALUE
            FROM HORSE_MARKS 
            WHERE SourceDate = '20250503'
            LIMIT 10
        """)
        
        samples = cursor.fetchall()
        print("\nサンプルデータ（最初の10件）:")
        for sample in samples:
            horse_name, m1, m2, m3, zi, zm = sample
            print(f"  {horse_name}: 馬印1={m1}, 馬印2={m2}, 馬印3={m3}, ZI={zi}, ZM={zm}")
    else:
        print("❌ データベースに2025年5月3日のデータが全く存在しません")

    # 2. Excelファイルの2025年5月3日の全データ確認
    print("\n2. Excelファイルの2025年5月3日の全データ確認")
    excel_file = "20250503.xlsx"
    excel_path = os.path.join(YDATE_DIR, excel_file)
    
    if os.path.exists(excel_path):
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
            print(f"✅ Excelファイルが存在します: {len(df)} 行")
            
            # 馬印データの状況
            if '馬印1' in df.columns:
                mark1_data = df['馬印1'].dropna()
                print(f"Excelの馬印1データ: {len(mark1_data)} 件")
            else:
                print("Excelに馬印1列がありません")
                
            if '馬印2' in df.columns:
                mark2_data = df['馬印2'].dropna()
                print(f"Excelの馬印2データ: {len(mark2_data)} 件")
            else:
                print("Excelに馬印2列がありません")
                
            # サンプルデータ
            print("\nExcelファイルのサンプルデータ（最初の10件）:")
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

    # 3. データの整合性確認
    print("\n3. データの整合性確認")
    if db_count > 0 and os.path.exists(excel_path):
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
            excel_count = len(df)
            
            if db_count == excel_count:
                print("✅ レコード数は一致しています")
            else:
                print(f"⚠️ レコード数が不一致 (DB:{db_count}, Excel:{excel_count})")
                
            # 馬名の一致確認
            cursor.execute("SELECT HorseName FROM HORSE_MARKS WHERE SourceDate = '20250503' ORDER BY HorseName")
            db_horses = [row[0] for row in cursor.fetchall()]
            excel_horses = df['馬名S'].tolist()
            
            db_set = set(db_horses)
            excel_set = set(excel_horses)
            
            missing_in_db = excel_set - db_set
            missing_in_excel = db_set - excel_set
            
            if missing_in_db:
                print(f"Excelにあるがデータベースにない馬名: {len(missing_in_db)} 件")
                print("最初の5件:")
                for horse in list(missing_in_db)[:5]:
                    print(f"  {horse}")
            
            if missing_in_excel:
                print(f"データベースにあるがExcelにない馬名: {len(missing_in_excel)} 件")
                print("最初の5件:")
                for horse in list(missing_in_excel)[:5]:
                    print(f"  {horse}")
            
            if not missing_in_db and not missing_in_excel:
                print("✅ 馬名は完全に一致しています")
                
        except Exception as e:
            print(f"❌ 整合性確認エラー: {e}")

    # 4. 問題の原因分析
    print("\n4. 問題の原因分析")
    if db_count == 0:
        print("❌ データベースに2025年5月3日のデータが全く存在しません")
        print("   原因: インポート処理が失敗している可能性があります")
    elif db_count > 0:
        print("✅ データベースに2025年5月3日のデータは存在します")
        print("   問題: 馬印データが不完全にインポートされている可能性があります")

    conn.close()

if __name__ == '__main__':
    check_all_20250503_data()

