import sqlite3

def investigate_1013_data():
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()

    print('=== 10/13データの詳細調査 ===')

    # 1. N_RACEテーブルの10/13データを詳細確認
    print('【N_RACE テーブル】')
    cursor.execute('SELECT COUNT(*) FROM N_RACE WHERE MakeDate = "20251013"')
    count = cursor.fetchone()[0]
    print(f'MakeDate=20251013のレコード数: {count}')

    # 2. 日付形式を確認
    print('\n【日付形式の確認】')
    cursor.execute('SELECT DISTINCT MakeDate FROM N_RACE WHERE MakeDate LIKE "2025101%" ORDER BY MakeDate')
    dates = cursor.fetchall()
    print('N_RACEの日付:')
    for date in dates:
        print(f'  {date[0]}')

    # 3. 10/13のデータが別の形式で存在するか確認
    print('\n【10/13の別形式確認】')
    cursor.execute('SELECT COUNT(*) FROM N_RACE WHERE Year = "2025" AND MonthDay = "1013"')
    count_alt = cursor.fetchone()[0]
    print(f'Year=2025 AND MonthDay=1013のレコード数: {count_alt}')

    # 4. N_UMA_RACEテーブルも同様に確認
    print('\n【N_UMA_RACE テーブル】')
    cursor.execute('SELECT COUNT(*) FROM N_UMA_RACE WHERE MakeDate = "20251013"')
    uma_count = cursor.fetchone()[0]
    print(f'MakeDate=20251013のレコード数: {uma_count}')

    cursor.execute('SELECT COUNT(*) FROM N_UMA_RACE WHERE Year = "2025" AND MonthDay = "1013"')
    uma_count_alt = cursor.fetchone()[0]
    print(f'Year=2025 AND MonthDay=1013のレコード数: {uma_count_alt}')

    # 5. 最新のMakeDateを確認
    print('\n【最新のMakeDate確認】')
    cursor.execute('SELECT MAX(MakeDate) FROM N_RACE')
    max_race_date = cursor.fetchone()[0]
    print(f'N_RACE最新MakeDate: {max_race_date}')

    cursor.execute('SELECT MAX(MakeDate) FROM N_UMA_RACE')
    max_uma_date = cursor.fetchone()[0]
    print(f'N_UMA_RACE最新MakeDate: {max_uma_date}')

    # 6. 10/13のデータが存在する可能性のある他のテーブルを確認
    print('\n【他のテーブルでの10/13データ確認】')
    tables_to_check = ['N_HANRO', 'N_WOOD_CHIP']
    for table in tables_to_check:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table} WHERE MakeDate = "20251013"')
            count = cursor.fetchone()[0]
            print(f'{table}: {count}件')
        except Exception as e:
            print(f'{table}: エラー - {e}')

    conn.close()

if __name__ == "__main__":
    investigate_1013_data()








