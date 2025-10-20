import sqlite3
import sys
import io
import pandas as pd
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DB_PATH = 'excel_data.db'
YDATE_DIR = r"C:\my_project_folder\envs\cursor\my_keiba\yDate"

def check_mark3_status():
    print("=== 馬印3の状況確認 ===\n")

    # 1. Excelファイルを読み込み
    latest_file = "20251005.xlsx"
    file_path = os.path.join(YDATE_DIR, latest_file)
    
    try:
        df = pd.read_excel(file_path)
        print(f"[OK] Excelファイル読み込み成功: {len(df)} 行")
    except Exception as e:
        print(f"[ERROR] ファイル読み込みエラー: {e}")
        return

    # 2. 馬印3のデータを確認
    print("\n2. 馬印3のデータを確認")
    mark3_data = df['馬印3'].dropna()
    print(f"Excelの馬印3データ: {len(mark3_data)} 件")
    print(f"データ例: {mark3_data.head(10).tolist()}")
    
    # 3. データベースの状況を確認
    print("\n3. データベースの状況を確認")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS WHERE SourceDate = ?", (latest_file.replace('.xlsx', ''),))
    db_count = cursor.fetchone()[0]
    print(f"データベースのレコード数: {db_count} 件")
    
    cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS WHERE SourceDate = ? AND Mark3 IS NOT NULL AND Mark3 != ''", (latest_file.replace('.xlsx', ''),))
    db_mark3_count = cursor.fetchone()[0]
    print(f"データベースの馬印3データ: {db_mark3_count} 件")
    
    # 4. 反映率を計算
    print("\n4. 反映率を計算")
    if len(mark3_data) > 0:
        reflection_rate = (db_mark3_count / len(mark3_data)) * 100
        print(f"馬印3の反映率: {reflection_rate:.1f}%")
        
        if reflection_rate >= 90:
            print("[OK] 馬印3のデータは正常に反映されています")
        elif reflection_rate >= 70:
            print("[WARNING] 馬印3のデータが一部不足しています")
        else:
            print("[ERROR] 馬印3のデータが大幅に不足しています")
    else:
        print("[INFO] Excelに馬印3のデータがありません")
    
    # 5. 不足しているデータの詳細
    print("\n5. 不足しているデータの詳細")
    missing_count = len(mark3_data) - db_mark3_count
    print(f"不足している馬印3データ: {missing_count} 件")
    
    if missing_count > 0:
        # 馬印3が空のレコードを特定
        cursor.execute("""
            SELECT id, HorseName, Mark3 
            FROM HORSE_MARKS 
            WHERE SourceDate = ? AND (Mark3 IS NULL OR Mark3 = '')
            LIMIT 5
        """, (latest_file.replace('.xlsx', ''),))
        
        empty_records = cursor.fetchall()
        print(f"馬印3が空のレコード（最初の5件）:")
        for record_id, horse_name, current_mark3 in empty_records:
            print(f"  {horse_name}: {current_mark3}")
    
    conn.close()
    print("\n=== 確認完了 ===")

if __name__ == '__main__':
    check_mark3_status()


