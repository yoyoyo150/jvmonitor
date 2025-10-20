import sqlite3
import sys
import io
import os
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DB_PATH = 'excel_data.db'
YDATE_DIR = r"C:\my_project_folder\envs\cursor\my_keiba\yDate"

def check_button_functionality():
    print("=== ボタン機能の確認 ===\n")

    # 1. 最新の更新状況を確認
    print("1. 最新の更新状況を確認")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(ImportedAt) FROM HORSE_MARKS")
    latest_import = cursor.fetchone()[0]
    print(f"最新のインポート時刻: {latest_import}")
    
    cursor.execute("SELECT MAX(SourceDate) FROM HORSE_MARKS")
    latest_date = cursor.fetchone()[0]
    print(f"最新のデータ日付: {latest_date}")

    # 2. 最新のExcelファイルの存在確認
    print("\n2. 最新のExcelファイルの存在確認")
    latest_excel = f"{latest_date}.xlsx"
    excel_path = os.path.join(YDATE_DIR, latest_excel)
    
    if os.path.exists(excel_path):
        file_size = os.path.getsize(excel_path)
        mod_time = datetime.fromtimestamp(os.path.getmtime(excel_path))
        print(f"[OK] {latest_excel} が存在します")
        print(f"ファイルサイズ: {file_size:,} bytes")
        print(f"最終更新: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"[ERROR] {latest_excel} が見つかりません")

    # 3. データの整合性確認
    print("\n3. データの整合性確認")
    cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS WHERE SourceDate = ?", (latest_date,))
    db_count = cursor.fetchone()[0]
    print(f"データベースのレコード数: {db_count} 件")
    
    # 4. 馬印データの完全性確認
    print("\n4. 馬印データの完全性確認")
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN Mark1 IS NOT NULL AND Mark1 != '' THEN 1 END) as mark1_count,
            COUNT(CASE WHEN Mark2 IS NOT NULL AND Mark2 != '' THEN 1 END) as mark2_count,
            COUNT(CASE WHEN Mark3 IS NOT NULL AND Mark3 != '' THEN 1 END) as mark3_count,
            COUNT(CASE WHEN Mark4 IS NOT NULL AND Mark4 != '' THEN 1 END) as mark4_count,
            COUNT(CASE WHEN Mark5 IS NOT NULL AND Mark5 != '' THEN 1 END) as mark5_count,
            COUNT(CASE WHEN Mark6 IS NOT NULL AND Mark6 != '' THEN 1 END) as mark6_count
        FROM HORSE_MARKS
        WHERE SourceDate = ?
    """, (latest_date,))
    
    mark_stats = cursor.fetchone()
    total, m1, m2, m3, m4, m5, m6 = mark_stats
    print(f"馬印1: {m1}/{total} ({m1/total*100:.1f}%)")
    print(f"馬印2: {m2}/{total} ({m2/total*100:.1f}%)")
    print(f"馬印3: {m3}/{total} ({m3/total*100:.1f}%)")
    print(f"馬印4: {m4}/{total} ({m4/total*100:.1f}%)")
    print(f"馬印5: {m5}/{total} ({m5/total*100:.1f}%)")
    print(f"馬印6: {m6}/{total} ({m6/total*100:.1f}%)")

    # 5. ボタン機能の診断
    print("\n5. ボタン機能の診断")
    
    # 最新のインポート時刻が最近かどうか
    if latest_import:
        import_time = datetime.strptime(latest_import, '%Y-%m-%d %H:%M:%S')
        now = datetime.now()
        time_diff = now - import_time
        
        if time_diff.total_seconds() < 3600:  # 1時間以内
            print("[OK] 最近のインポートが実行されています")
        else:
            print(f"[WARNING] 最後のインポートから {time_diff.total_seconds()/3600:.1f} 時間経過しています")
    
    # データの整合性
    if m2 == total and m5 == total and m6 == total:
        print("[OK] 主要な馬印データ（2, 5, 6）は正常に反映されています")
    else:
        print("[WARNING] 主要な馬印データに問題があります")
    
    # 6. 推奨アクション
    print("\n6. 推奨アクション")
    print("ボタンが機能していない場合の対処法:")
    print("1. アプリケーションを再起動してください")
    print("2. 最新のExcelファイルがyDateフォルダに存在することを確認してください")
    print("3. データベースの権限を確認してください")
    print("4. ログファイルを確認してエラーメッセージを確認してください")

    conn.close()

if __name__ == '__main__':
    check_button_functionality()


