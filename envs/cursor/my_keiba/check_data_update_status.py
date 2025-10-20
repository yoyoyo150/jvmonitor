import sqlite3
import os

def check_data_update_status():
    """データベースの更新状況を確認"""
    
    # excel_data.dbの状況確認
    if os.path.exists('excel_data.db'):
        conn = sqlite3.connect('excel_data.db')
        cursor = conn.cursor()
        
        # テーブル一覧
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print('=== excel_data.db テーブル一覧 ===')
        for table in tables:
            print(f'- {table[0]}')
        
        # HORSE_MARKSテーブルのレコード数確認
        if any('HORSE_MARKS' in str(table) for table in tables):
            cursor.execute('SELECT COUNT(*) FROM HORSE_MARKS')
            count = cursor.fetchone()[0]
            print(f'\n=== HORSE_MARKS レコード数 ===')
            print(f'総レコード数: {count:,}件')
            
            # 最新のデータ日付確認
            cursor.execute('SELECT MAX(SourceDate) FROM HORSE_MARKS')
            latest_date = cursor.fetchone()[0]
            print(f'最新データ日付: {latest_date}')
            
            # 日付別レコード数（最新5日）
            cursor.execute('''
                SELECT SourceDate, COUNT(*) as count 
                FROM HORSE_MARKS 
                GROUP BY SourceDate 
                ORDER BY SourceDate DESC 
                LIMIT 5
            ''')
            print(f'\n=== 最新5日間のデータ ===')
            for row in cursor.fetchall():
                print(f'{row[0]}: {row[1]:,}件')
        
        conn.close()
    else:
        print('excel_data.db が見つかりません')

if __name__ == "__main__":
    check_data_update_status()




