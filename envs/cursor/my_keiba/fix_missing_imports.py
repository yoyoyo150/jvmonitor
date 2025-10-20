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

def fix_missing_imports():
    print("=== 不足しているインポートの修正 ===\n")

    # 1. 不足している日付を特定
    print("1. 不足している日付を特定")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # データベースにある日付を取得
    cursor.execute("SELECT DISTINCT SourceDate FROM HORSE_MARKS ORDER BY SourceDate")
    imported_dates = set([row[0] for row in cursor.fetchall()])
    
    # Excelファイルから日付を取得
    excel_files = [f for f in os.listdir(YDATE_DIR) if f.endswith('.xlsx')]
    excel_dates = set()
    for file in excel_files:
        if file.replace('.xlsx', '').isdigit() and len(file.replace('.xlsx', '')) == 8:
            excel_dates.add(file.replace('.xlsx', ''))
    
    # 不足している日付を特定
    missing_dates = excel_dates - imported_dates
    print(f"インポートされていない日付: {len(missing_dates)} 日")
    
    if missing_dates:
        print("不足している日付（最初の10日）:")
        for date in sorted(missing_dates)[:10]:
            print(f"  {date}")
        if len(missing_dates) > 10:
            print(f"  ... 他 {len(missing_dates) - 10} 日")
    else:
        print("✅ 全てのExcelファイルがインポート済みです")
        conn.close()
        return

    # 2. 不足している日付のExcelファイルを確認
    print("\n2. 不足している日付のExcelファイルを確認")
    
    valid_missing_dates = []
    for date in sorted(missing_dates):
        excel_file = f"{date}.xlsx"
        excel_path = os.path.join(YDATE_DIR, excel_file)
        
        if os.path.exists(excel_path):
            try:
                # UTF-8エンコーディングでExcelファイルを読み込み
                df = pd.read_excel(excel_path, engine='openpyxl')
                print(f"✅ {date}: {len(df)} 行のデータ")
                valid_missing_dates.append(date)
            except Exception as e:
                print(f"❌ {date}: Excelファイル読み込みエラー - {e}")
        else:
            print(f"❌ {date}: Excelファイルが見つかりません")

    # 3. 手動でインポート処理を実行
    print(f"\n3. 手動でインポート処理を実行")
    print(f"対象日付: {len(valid_missing_dates)} 日")
    
    if not valid_missing_dates:
        print("インポート可能なファイルがありません")
        conn.close()
        return

    # 最初の数日分を手動でインポート
    test_dates = valid_missing_dates[:3]  # 最初の3日分をテスト
    
    for date in test_dates:
        print(f"\n--- {date} のインポート処理 ---")
        
        excel_file = f"{date}.xlsx"
        excel_path = os.path.join(YDATE_DIR, excel_file)
        
        try:
            # UTF-8エンコーディングでExcelファイルを読み込み
            df = pd.read_excel(excel_path, engine='openpyxl')
            print(f"Excelファイル読み込み成功: {len(df)} 行")
            
            # データベースに挿入
            inserted_count = 0
            for index, row in df.iterrows():
                try:
                    # 基本的なデータを挿入
                    cursor.execute("""
                        INSERT INTO HORSE_MARKS (
                            SourceDate, HorseName, NormalizedHorseName, 
                            Mark1, Mark2, Mark3, Mark4, Mark5, Mark6, Mark7, Mark8,
                            SourceFile, ImportedAt
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        date,
                        row.get('馬名S', ''),
                        row.get('馬名S', ''),  # 正規化は簡略化
                        row.get('馬印1', ''),
                        row.get('馬印2', ''),
                        row.get('馬印3', ''),
                        row.get('馬印4', ''),
                        row.get('馬印5', ''),
                        row.get('馬印6', ''),
                        row.get('馬印7', ''),
                        row.get('馬印8', ''),
                        excel_file,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ))
                    inserted_count += 1
                except Exception as e:
                    print(f"行 {index} の挿入エラー: {e}")
                    continue
            
            conn.commit()
            print(f"✅ {date}: {inserted_count} 件のデータをインポートしました")
            
        except Exception as e:
            print(f"❌ {date}: インポートエラー - {e}")
            conn.rollback()

    # 4. インポート結果の確認
    print("\n4. インポート結果の確認")
    
    for date in test_dates:
        cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS WHERE SourceDate = ?", (date,))
        count = cursor.fetchone()[0]
        print(f"{date}: {count} 件")

    conn.close()
    
    # 5. 推奨アクション
    print("\n5. 推奨アクション")
    print("1. 残りの不足している日付も同様にインポート")
    print("2. インポート処理のログを確認してエラーの原因を特定")
    print("3. 自動インポート処理の改善")

if __name__ == '__main__':
    fix_missing_imports()

