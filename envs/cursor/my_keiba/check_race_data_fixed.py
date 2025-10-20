import sqlite3

def check_race_data_fixed():
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()

    print('=== 実際のレースデータ確認（修正版） ===')

    # 10/11のレースデータ
    print('【10/11 (20251011)】')
    cursor.execute("""
        SELECT Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, Hondai, Kyori, GradeCD
        FROM N_RACE 
        WHERE MakeDate = "20251011"
        ORDER BY JyoCD, Kaiji, Nichiji, RaceNum
    """)
    races_11 = cursor.fetchall()
    print(f'レース数: {len(races_11)}')
    for race in races_11[:5]:
        print(f'  {race[0]}/{race[1]} {race[2]}{race[3]}{race[4]}R {race[6]} {race[7]}m (G{race[8]})')

    print()

    # 10/12のレースデータ
    print('【10/12 (20251012)】')
    cursor.execute("""
        SELECT Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, Hondai, Kyori, GradeCD
        FROM N_RACE 
        WHERE MakeDate = "20251012"
        ORDER BY JyoCD, Kaiji, Nichiji, RaceNum
    """)
    races_12 = cursor.fetchall()
    print(f'レース数: {len(races_12)}')
    for race in races_12[:5]:
        print(f'  {race[0]}/{race[1]} {race[2]}{race[3]}{race[4]}R {race[6]} {race[7]}m (G{race[8]})')

    print()

    # 10/13のレースデータ
    print('【10/13 (20251013)】')
    cursor.execute("""
        SELECT Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, Hondai, Kyori, GradeCD
        FROM N_RACE 
        WHERE MakeDate = "20251013"
        ORDER BY JyoCD, Kaiji, Nichiji, RaceNum
    """)
    races_13 = cursor.fetchall()
    print(f'レース数: {len(races_13)}')
    for race in races_13[:5]:
        print(f'  {race[0]}/{race[1]} {race[2]}{race[3]}{race[4]}R {race[6]} {race[7]}m (G{race[8]})')

    print()

    # 出走馬データも確認
    print('【出走馬データ確認】')
    for date in ['20251011', '20251012', '20251013']:
        cursor.execute("""
            SELECT COUNT(*) FROM N_UMA_RACE 
            WHERE MakeDate = ?
        """, (date,))
        uma_count = cursor.fetchone()[0]
        print(f'{date}: {uma_count}頭')

    conn.close()

if __name__ == "__main__":
    check_race_data_fixed()








