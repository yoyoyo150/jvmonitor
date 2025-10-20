import sqlite3
import os
import shutil

def clean_database_keep_files():
    """異常なファイルは保持しつつ、データベースのみクリーンアップ"""
    
    print("=== データベースクリーンアップ（ファイルは保持） ===")
    
    # バックアップ作成
    if os.path.exists('excel_data.db'):
        shutil.copy2('excel_data.db', 'excel_data_backup.db')
        print("バックアップ作成完了: excel_data_backup.db")
    
    # データベース接続
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    # 異常な日付のデータを削除
    print("\n=== 異常な日付データの削除 ===")
    cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS WHERE SourceDate LIKE '25025%'")
    abnormal_count = cursor.fetchone()[0]
    print(f"削除対象の異常データ: {abnormal_count:,}件")
    
    if abnormal_count > 0:
        cursor.execute("DELETE FROM HORSE_MARKS WHERE SourceDate LIKE '25025%'")
        conn.commit()
        print("異常な日付データを削除しました")
    
    # 正常なデータの確認
    cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS")
    total_count = cursor.fetchone()[0]
    print(f"\n残存データ: {total_count:,}件")
    
    # 最新の正常な日付を確認
    cursor.execute("""
        SELECT SourceDate, COUNT(*) as count
        FROM HORSE_MARKS 
        WHERE SourceDate LIKE '2025%'
        GROUP BY SourceDate 
        ORDER BY SourceDate DESC
        LIMIT 5
    """)
    
    print("\n=== 最新5日間の正常データ ===")
    for row in cursor.fetchall():
        print(f"{row[0]}: {row[1]:,}件")
    
    conn.close()
    print("\nデータベースクリーンアップ完了")

if __name__ == "__main__":
    clean_database_keep_files()
