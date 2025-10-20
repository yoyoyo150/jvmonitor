import sqlite3
import sys
import io
import pandas as pd
import os
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DB_PATH = 'excel_data.db'
YDATE_DIR = r"C:\my_project_folder\envs\cursor\my_keiba\yDate"

def fix_horse_mark_update():
    print("=== 馬印更新（増分）の修正 ===\n")

    # 1. 最新のExcelファイルを確認
    print("1. 最新のExcelファイルを確認")
    latest_file = "20251005.xlsx"
    file_path = os.path.join(YDATE_DIR, latest_file)
    
    if not os.path.exists(file_path):
        print(f"[ERROR] ファイルが見つかりません: {file_path}")
        return
    
    # 2. Excelファイルを読み込み
    print("2. Excelファイルを読み込み")
    try:
        df = pd.read_excel(file_path)
        print(f"[OK] ファイル読み込み成功: {len(df)} 行")
    except Exception as e:
        print(f"[ERROR] ファイル読み込みエラー: {e}")
        return

    # 3. 馬印1のデータを確認
    print("\n3. 馬印1のデータを確認")
    mark1_data = df['馬印1'].dropna()
    print(f"Excelの馬印1データ: {len(mark1_data)} 件")
    print(f"データ例: {mark1_data.head(10).tolist()}")
    
    # 4. データベースの現在の状況を確認
    print("\n4. データベースの現在の状況を確認")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS WHERE SourceDate = ?", (latest_file.replace('.xlsx', ''),))
    db_count = cursor.fetchone()[0]
    print(f"データベースのレコード数: {db_count} 件")
    
    cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS WHERE SourceDate = ? AND Mark1 IS NOT NULL AND Mark1 != ''", (latest_file.replace('.xlsx', ''),))
    db_mark1_count = cursor.fetchone()[0]
    print(f"データベースの馬印1データ: {db_mark1_count} 件")
    
    # 5. 不足しているデータを特定
    print("\n5. 不足しているデータを特定")
    missing_count = len(mark1_data) - db_mark1_count
    print(f"不足している馬印1データ: {missing_count} 件")
    
    if missing_count > 0:
        print("[WARNING] 馬印1のデータが不完全に反映されています")
        
        # 6. 修正処理
        print("\n6. 修正処理を実行")
        
        # 馬印1が空のレコードを特定
        cursor.execute("""
            SELECT id, HorseName, Mark1 
            FROM HORSE_MARKS 
            WHERE SourceDate = ? AND (Mark1 IS NULL OR Mark1 = '')
        """, (latest_file.replace('.xlsx', ''),))
        
        empty_records = cursor.fetchall()
        print(f"馬印1が空のレコード: {len(empty_records)} 件")
        
        # Excelのデータと照合して更新
        updated_count = 0
        for record_id, horse_name, current_mark1 in empty_records:
            # 馬名でExcelのデータを検索
            excel_match = df[df['馬名S'] == horse_name]
            if not excel_match.empty:
                new_mark1 = excel_match.iloc[0]['馬印1']
                if pd.notna(new_mark1) and new_mark1 != '':
                    cursor.execute("""
                        UPDATE HORSE_MARKS 
                        SET Mark1 = ? 
                        WHERE id = ?
                    """, (str(new_mark1), record_id))
                    updated_count += 1
        
        conn.commit()
        print(f"[OK] {updated_count} 件の馬印1データを更新しました")
        
        # 7. 更新後の確認
        print("\n7. 更新後の確認")
        cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS WHERE SourceDate = ? AND Mark1 IS NOT NULL AND Mark1 != ''", (latest_file.replace('.xlsx', ''),))
        new_mark1_count = cursor.fetchone()[0]
        print(f"更新後の馬印1データ: {new_mark1_count} 件")
        
        if new_mark1_count >= len(mark1_data) * 0.9:  # 90%以上反映されていれば成功
            print("[OK] 馬印1のデータが正常に反映されました")
        else:
            print("[WARNING] まだ一部のデータが反映されていません")
    else:
        print("[OK] 馬印1のデータは正常に反映されています")
    
    conn.close()
    print("\n=== 修正完了 ===")

if __name__ == '__main__':
    fix_horse_mark_update()


