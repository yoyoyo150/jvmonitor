import sqlite3
import pandas as pd
import os
from datetime import datetime

def migrate_2024_data_to_horse_marks():
    """2024年のExcelデータをHORSE_MARKSテーブルに安全に移行"""
    
    print("=== 2024年データのHORSE_MARKSテーブル移行 ===")
    
    # 1. バックアップ作成
    print("\n1. バックアップ作成中...")
    backup_name = f"ecore_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    os.system(f"copy ecore.db {backup_name}")
    print(f"バックアップ作成完了: {backup_name}")
    
    # 2. 2024年のExcelファイル一覧取得
    print("\n2. 2024年Excelファイルの確認...")
    ydate_2024_files = []
    for file in os.listdir('yDate'):
        if file.startswith('2024') and file.endswith('.xlsx'):
            ydate_2024_files.append(file)
    
    print(f"2024年Excelファイル数: {len(ydate_2024_files)}")
    print(f"ファイル例: {ydate_2024_files[:5]}")
    
    # 3. HORSE_MARKSテーブルの現在の状況確認
    print("\n3. HORSE_MARKSテーブルの現在の状況...")
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS")
    current_count = cursor.fetchone()[0]
    print(f"現在のHORSE_MARKSレコード数: {current_count:,}")
    
    cursor.execute("SELECT MIN(SourceDate), MAX(SourceDate) FROM HORSE_MARKS")
    date_range = cursor.fetchone()
    print(f"現在のデータ範囲: {date_range[0]} ～ {date_range[1]}")
    
    # 4. 2024年データの移行（安全な方法）
    print("\n4. 2024年データの移行開始...")
    
    migrated_count = 0
    error_count = 0
    
    for file in ydate_2024_files[:5]:  # 最初の5ファイルでテスト
        try:
            print(f"  処理中: {file}")
            
            # Excelファイルを読み込み
            df = pd.read_excel(f'yDate/{file}', encoding='cp932')
            
            # 必要なカラムを確認
            required_columns = ['HorseName', 'Mark5', 'Mark6', 'ZI_INDEX', 'ZM_VALUE']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"    警告: 必要なカラムが不足 - {missing_columns}")
                continue
            
            # データをHORSE_MARKSテーブルに挿入
            for _, row in df.iterrows():
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO HORSE_MARKS 
                        (SourceDate, HorseName, Mark5, Mark6, ZI_INDEX, ZM_VALUE, ImportedAt)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        file.replace('.xlsx', ''),  # ファイル名から日付を抽出
                        row['HorseName'],
                        row['Mark5'],
                        row['Mark6'],
                        row['ZI_INDEX'],
                        row['ZM_VALUE'],
                        datetime.now().isoformat()
                    ))
                    migrated_count += 1
                except Exception as e:
                    print(f"    エラー: {e}")
                    error_count += 1
                    continue
            
            conn.commit()
            print(f"    完了: {file}")
            
        except Exception as e:
            print(f"  エラー: {file} - {e}")
            error_count += 1
            continue
    
    # 5. 移行結果の確認
    print("\n5. 移行結果の確認...")
    cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS")
    new_count = cursor.fetchone()[0]
    print(f"移行後のHORSE_MARKSレコード数: {new_count:,}")
    print(f"追加されたレコード数: {new_count - current_count:,}")
    print(f"移行成功: {migrated_count}件")
    print(f"エラー: {error_count}件")
    
    # 6. ナムラクレアのデータ確認
    print("\n6. ナムラクレアのデータ確認...")
    cursor.execute("""
        SELECT SourceDate, HorseName, Mark5, Mark6, ZI_INDEX, ZM_VALUE
        FROM HORSE_MARKS
        WHERE HorseName LIKE '%ナムラクレア%'
        ORDER BY SourceDate DESC
        LIMIT 10
    """)
    
    data = cursor.fetchall()
    print(f"ナムラクレアのデータ: {len(data)}件")
    
    if data:
        print("SourceDate | HorseName | Mark5 | Mark6 | ZI_INDEX | ZM_VALUE")
        print("------------------------------------------------------------")
        for row in data:
            print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}")
    
    conn.close()
    
    print("\n=== 移行完了 ===")
    print("JVMonitorを再起動して、古いレースのMark5/Mark6データが表示されるか確認してください。")

if __name__ == "__main__":
    migrate_2024_data_to_horse_marks()




