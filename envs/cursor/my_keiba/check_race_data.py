import sqlite3

def check_race_data():
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()

    print('=== 実際のレースデータ確認 ===')

    # 10/11のレースデータ
    print('【10/11 (20251011)】')
    cursor.execute("""
        SELECT Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, RaceName, Distance
        FROM N_RACE 
        WHERE MakeDate = "20251011"
        ORDER BY JyoCD, Kaiji, Nichiji, RaceNum
    """)
    races_11 = cursor.fetchall()
    print(f'レース数: {len(races_11)}')
    for race in races_11[:3]:
        print(f'  {race[0]}/{race[1]} {race[2]}{race[3]}{race[4]}R {race[6]} {race[7]}m')

    print()

    # 10/12のレースデータ
    print('【10/12 (20251012)】')
    cursor.execute("""
        SELECT Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, RaceName, Distance
        FROM N_RACE 
        WHERE MakeDate = "20251012"
        ORDER BY JyoCD, Kaiji, Nichiji, RaceNum
    """)
    races_12 = cursor.fetchall()
    print(f'レース数: {len(races_12)}')
    for race in races_12[:3]:
        print(f'  {race[0]}/{race[1]} {race[2]}{race[3]}{race[4]}R {race[6]} {race[7]}m')

    print()

    # 10/13のレースデータ
    print('【10/13 (20251013)】')
    cursor.execute("""
        SELECT Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, RaceName, Distance
        FROM N_RACE 
        WHERE MakeDate = "20251013"
        ORDER BY JyoCD, Kaiji, Nichiji, RaceNum
    """)
    races_13 = cursor.fetchall()
    print(f'レース数: {len(races_13)}')
    for race in races_13[:3]:
        print(f'  {race[0]}/{race[1]} {race[2]}{race[3]}{race[4]}R {race[6]} {race[7]}m')

    conn.close()

if __name__ == "__main__":
    check_race_data()








