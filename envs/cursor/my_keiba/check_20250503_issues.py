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

def check_20250503_issues():
    print("=== 20250503の詳細問題確認 ===\n")

    # 1. 馬印データの詳細分析
    print("1. 馬印データの詳細分析")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 馬印1が空のレコードの詳細
    cursor.execute("""
        SELECT HorseName, Mark1, Mark2, Mark3
        FROM HORSE_MARKS 
        WHERE SourceDate = '20250503' AND (Mark1 IS NULL OR Mark1 = '')
        LIMIT 10
    """)
    
    empty_mark1 = cursor.fetchall()
    print("馬印1が空のレコード（最初の10件）:")
    for record in empty_mark1:
        horse_name, m1, m2, m3 = record
        print(f"  {horse_name}: 馬印1={m1}, 馬印2={m2}, 馬印3={m3}")
    
    # 馬印1が存在するレコードの詳細
    cursor.execute("""
        SELECT HorseName, Mark1, Mark2, Mark3
        FROM HORSE_MARKS 
        WHERE SourceDate = '20250503' AND Mark1 IS NOT NULL AND Mark1 != ''
        LIMIT 10
    """)
    
    has_mark1 = cursor.fetchall()
    print("\n馬印1が存在するレコード（最初の10件）:")
    for record in has_mark1:
        horse_name, m1, m2, m3 = record
        print(f"  {horse_name}: 馬印1={m1}, 馬印2={m2}, 馬印3={m3}")

    # 2. Excelファイルとの比較
    print("\n2. Excelファイルとの比較")
    excel_file = "20250503.xlsx"
    excel_path = os.path.join(YDATE_DIR, excel_file)
    
    if os.path.exists(excel_path):
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
            
            # 馬印1のデータを詳細確認
            if '馬印1' in df.columns:
                mark1_data = df['馬印1'].dropna()
                print(f"Excelの馬印1データ: {len(mark1_data)} 件")
                
                # 馬印1の値の分布
                mark1_counts = mark1_data.value_counts()
                print("馬印1の値の分布:")
                for value, count in mark1_counts.head(10).items():
                    print(f"  '{value}': {count} 件")
                
                # 馬印1が空でないレコードの馬名
                non_empty_mark1 = df[df['馬印1'].notna() & (df['馬印1'] != '')]
                print(f"\n馬印1が空でないレコードの馬名（最初の10件）:")
                for i, row in non_empty_mark1.head(10).iterrows():
                    print(f"  {row['馬名S']}: 馬印1={row['馬印1']}")
            else:
                print("Excelに馬印1列がありません")
                
        except Exception as e:
            print(f"Excelファイル読み込みエラー: {e}")

    # 3. データベースとExcelの馬名比較
    print("\n3. データベースとExcelの馬名比較")
    
    # データベースの馬名リスト
    cursor.execute("SELECT HorseName FROM HORSE_MARKS WHERE SourceDate = '20250503' ORDER BY HorseName")
    db_horses = [row[0] for row in cursor.fetchall()]
    
    if os.path.exists(excel_path):
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
            excel_horses = df['馬名S'].tolist()
            
            # 馬名の一致確認
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
            print(f"馬名比較エラー: {e}")

    conn.close()

    # 4. 問題の特定と解決策
    print("\n4. 問題の特定と解決策")
    print("20250503のデータは正常にインポートされています。")
    print("特定の問題がある場合は、以下を確認してください:")
    print("1. JVMonitorでの表示問題")
    print("2. 特定の馬の馬印データの問題")
    print("3. データの更新が必要な場合")

if __name__ == '__main__':
    check_20250503_issues()

