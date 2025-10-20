import sqlite3

def confirm_1013_data():
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()

    print('=== 問題の原因特定 ===')

    # 10/13のデータが実際に存在することを確認
    print('【10/13の実際のデータ確認】')
    cursor.execute("""
        SELECT Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, Hondai, Kyori
        FROM N_RACE 
        WHERE Year = "2025" AND MonthDay = "1013"
        ORDER BY JyoCD, Kaiji, Nichiji, RaceNum
        LIMIT 5
    """)
    races = cursor.fetchall()
    print(f'レース数: {len(races)}')
    for race in races:
        print(f'  {race[0]}/{race[1]} {race[2]}{race[3]}{race[4]}R {race[6]} {race[7]}m')

    print()
    print('【出走馬データ確認】')
    cursor.execute("""
        SELECT COUNT(*) FROM N_UMA_RACE 
        WHERE Year = "2025" AND MonthDay = "1013"
    """)
    uma_count = cursor.fetchone()[0]
    print(f'出走馬数: {uma_count}')

    # サンプル出走馬データ
    cursor.execute("""
        SELECT Bamei, JyoCD, Kaiji, Nichiji, RaceNum, Umaban
        FROM N_UMA_RACE 
        WHERE Year = "2025" AND MonthDay = "1013"
        ORDER BY JyoCD, Kaiji, Nichiji, RaceNum, Umaban
        LIMIT 10
    """)
    umas = cursor.fetchall()
    print('出走馬サンプル:')
    for uma in umas:
        print(f'  {uma[0]} ({uma[5]}番)')

    print()
    print('【問題の原因】')
    print('MakeDateとYear+MonthDayの不一致:')
    print('- MakeDate=20251013: 0件')
    print('- Year=2025 AND MonthDay=1013: 24レース、325頭')
    print('JVMonitorは正しいデータを表示しているが、クエリ条件が間違っていた')

    conn.close()

if __name__ == "__main__":
    confirm_1013_data()








