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

def check_20250503():
    print("=== 20250503のデータ状況確認 ===\n")

    # 1. データベースの状況確認
    print("1. データベースの状況確認")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 20250503のレコード数
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
                COUNT(CASE WHEN Mark3 IS NOT NULL AND Mark3 != '' THEN 1 END) as mark3_count
            FROM HORSE_MARKS 
            WHERE SourceDate = '20250503'
        """)
        
        mark_stats = cursor.fetchone()
        total, m1, m2, m3 = mark_stats
        print(f"馬印データ: 馬印1={m1}({m1/total*100:.1f}%), 馬印2={m2}({m2/total*100:.1f}%), 馬印3={m3}({m3/total*100:.1f}%)")
        
        # サンプルデータ
        cursor.execute("""
            SELECT HorseName, Mark1, Mark2, Mark3, ImportedAt
            FROM HORSE_MARKS 
            WHERE SourceDate = '20250503'
            LIMIT 5
        """)
        
        samples = cursor.fetchall()
        print("サンプルデータ:")
        for sample in samples:
            horse_name, m1, m2, m3, imported_at = sample
            print(f"  {horse_name}: 馬印1={m1}, 馬印2={m2}, 馬印3={m3}, インポート時刻={imported_at}")
    else:
        print("❌ データベースに20250503のデータがありません")
    
    conn.close()

    # 2. Excelファイルの状況確認
    print("\n2. Excelファイルの状況確認")
    excel_file = "20250503.xlsx"
    excel_path = os.path.join(YDATE_DIR, excel_file)
    
    if os.path.exists(excel_path):
        try:
            # UTF-8エンコーディングでExcelファイルを読み込み
            df = pd.read_excel(excel_path, engine='openpyxl')
            print(f"✅ Excelファイルが存在します: {len(df)} 行")
            
            # ファイルの更新時刻
            mod_time = datetime.fromtimestamp(os.path.getmtime(excel_path))
            print(f"ファイル更新時刻: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 馬印1のデータ確認
            if '馬印1' in df.columns:
                mark1_data = df['馬印1'].dropna()
                print(f"Excelの馬印1データ: {len(mark1_data)} 件")
                print(f"Excelの馬印1例: {mark1_data.head(5).tolist()}")
            else:
                print("Excelに馬印1列がありません")
                
            # 馬印2のデータ確認
            if '馬印2' in df.columns:
                mark2_data = df['馬印2'].dropna()
                print(f"Excelの馬印2データ: {len(mark2_data)} 件")
                print(f"Excelの馬印2例: {mark2_data.head(5).tolist()}")
            else:
                print("Excelに馬印2列がありません")
                
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
                print("✅ データ整合性: OK")
            else:
                print(f"⚠️ データ整合性: 不一致 (DB:{db_count}, Excel:{excel_count})")
        except Exception as e:
            print(f"❌ 整合性確認エラー: {e}")
    elif db_count == 0 and os.path.exists(excel_path):
        print("❌ データ整合性: Excelファイルは存在するが、データベースにインポートされていない")
    else:
        print("❌ データ整合性: ファイルまたはデータが存在しない")

if __name__ == '__main__':
    check_20250503()

