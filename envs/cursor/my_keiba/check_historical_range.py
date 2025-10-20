import sqlite3

def check_historical_data_range():
    # ecore.dbの過去データ範囲確認
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()

    print('=== ecore.db 過去データ範囲確認 ===')
    tables_to_check = ['N_RACE', 'N_UMA_RACE']
    for table in tables_to_check:
        try:
            cursor.execute(f'SELECT MIN(MakeDate), MAX(MakeDate) FROM {table}')
            min_date, max_date = cursor.fetchone()
            print(f'{table}: {min_date} ～ {max_date}')
            
            # 2023年以降のデータ数を確認
            cursor.execute(f'SELECT COUNT(*) FROM {table} WHERE MakeDate >= "20230101"')
            count_2023 = cursor.fetchone()[0]
            print(f'  2023年以降のデータ数: {count_2023:,}件')
            
        except Exception as e:
            print(f'{table}: エラー - {e}')

    conn.close()

if __name__ == "__main__":
    check_historical_data_range()








