# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_historical_data():
    """過去データの詳細調査"""
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    print("=== 過去データ（2017年以降）の詳細調査 ===\n")
    
    # 1. 年別データの詳細確認
    print("1. 年別データの詳細確認")
    cursor.execute("""
        SELECT 
            Year,
            COUNT(*) as race_count,
            COUNT(DISTINCT MonthDay) as race_days,
            MIN(MonthDay) as first_day,
            MAX(MonthDay) as last_day
        FROM N_RACE 
        WHERE Year >= '2017'
        GROUP BY Year 
        ORDER BY Year
    """)
    yearly_details = cursor.fetchall()
    
    print("年別レース詳細:")
    for year, race_count, race_days, first_day, last_day in yearly_details:
        print(f"  {year}年: {race_count:,} レース ({race_days} 開催日)")
        print(f"    期間: {first_day} ～ {last_day}")
    
    print("\n" + "="*50 + "\n")
    
    # 2. 出馬データの年別確認
    print("2. 出馬データの年別確認")
    cursor.execute("""
        SELECT 
            Year,
            COUNT(*) as uma_count,
            COUNT(DISTINCT KettoNum) as unique_horses
        FROM N_UMA_RACE 
        WHERE Year >= '2017'
        GROUP BY Year 
        ORDER BY Year
    """)
    yearly_umas = cursor.fetchall()
    
    print("年別出馬詳細:")
    for year, uma_count, unique_horses in yearly_umas:
        print(f"  {year}年: {uma_count:,} 出馬 ({unique_horses:,} 頭の馬)")
    
    print("\n" + "="*50 + "\n")
    
    # 3. 開催場別データ確認
    print("3. 開催場別データ確認（2017年以降）")
    cursor.execute("""
        SELECT 
            JyoCD,
            COUNT(*) as race_count,
            COUNT(DISTINCT Year || MonthDay) as race_days
        FROM N_RACE 
        WHERE Year >= '2017'
        GROUP BY JyoCD 
        ORDER BY race_count DESC
    """)
    venue_data = cursor.fetchall()
    
    venue_names = {
        '01': '札幌', '02': '函館', '03': '福島', '04': '新潟', '05': '東京',
        '06': '中山', '07': '中京', '08': '京都', '09': '阪神', '10': '小倉'
    }
    
    print("開催場別レース数:")
    for jyo_cd, race_count, race_days in venue_data:
        venue_name = venue_names.get(jyo_cd, f'場{jyo_cd}')
        print(f"  {venue_name} ({jyo_cd}): {race_count:,} レース ({race_days} 開催日)")
    
    print("\n" + "="*50 + "\n")
    
    # 4. 月別データ確認（2017年以降）
    print("4. 月別データ確認（2017年以降）")
    cursor.execute("""
        SELECT 
            Year,
            SUBSTR(MonthDay, 1, 2) as Month,
            COUNT(*) as race_count
        FROM N_RACE 
        WHERE Year >= '2017'
        GROUP BY Year, SUBSTR(MonthDay, 1, 2)
        ORDER BY Year, Month
    """)
    monthly_data = cursor.fetchall()
    
    print("月別レース数:")
    current_year = None
    for year, month, race_count in monthly_data:
        if current_year != year:
            print(f"\n{year}年:")
            current_year = year
        print(f"  {month}月: {race_count:,} レース")
    
    print("\n" + "="*50 + "\n")
    
    # 5. サンプルレースの表示
    print("5. サンプルレースの表示（2017年以降）")
    cursor.execute("""
        SELECT 
            Year,
            MonthDay,
            JyoCD,
            RaceNum,
            Hondai,
            Kyori,
            HassoTime,
            TorokuTosu,
            SyussoTosu
        FROM N_RACE 
        WHERE Year >= '2017'
        ORDER BY Year, MonthDay, JyoCD, RaceNum
        LIMIT 10
    """)
    sample_races = cursor.fetchall()
    
    print("サンプルレース:")
    for race in sample_races:
        year, monthday, jyo_cd, race_num, hondai, kyori, hasso_time, toroku, syusso = race
        venue_name = venue_names.get(jyo_cd, f'場{jyo_cd}')
        date_str = f"{year}年{monthday[:2]}月{monthday[2:]}日"
        print(f"  {date_str} {venue_name} {race_num}R: {hondai} ({kyori}m, {hasso_time})")
        print(f"    登録:{toroku}頭 出走:{syusso}頭")
    
    print("\n" + "="*50 + "\n")
    
    # 6. データの欠損確認
    print("6. データの欠損確認")
    cursor.execute("""
        SELECT 
            Year,
            COUNT(*) as race_count,
            COUNT(CASE WHEN Hondai != '' THEN 1 END) as with_title,
            COUNT(CASE WHEN Kyori != '' AND Kyori != '0000' THEN 1 END) as with_distance,
            COUNT(CASE WHEN HassoTime != '' AND HassoTime != '0000' THEN 1 END) as with_time
        FROM N_RACE 
        WHERE Year >= '2017'
        GROUP BY Year 
        ORDER BY Year
    """)
    data_quality = cursor.fetchall()
    
    print("データ品質:")
    for year, race_count, with_title, with_distance, with_time in data_quality:
        print(f"  {year}年: {race_count:,} レース")
        print(f"    レース名: {with_title:,} ({with_title/race_count*100:.1f}%)")
        print(f"    距離情報: {with_distance:,} ({with_distance/race_count*100:.1f}%)")
        print(f"    発走時刻: {with_time:,} ({with_time/race_count*100:.1f}%)")
    
    conn.close()

def create_historical_display_system():
    """過去データ表示システムの作成"""
    system_code = '''# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def get_historical_races(year=None, month=None, venue=None, limit=50):
    """過去レースの取得"""
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    query = """
    SELECT 
        Year,
        MonthDay,
        JyoCD,
        RaceNum,
        Hondai,
        Kyori,
        HassoTime,
        TorokuTosu,
        SyussoTosu
    FROM N_RACE
    WHERE Year >= '2017'
    """
    params = []
    
    if year:
        query += " AND Year = ?"
        params.append(year)
    
    if month:
        query += " AND SUBSTR(MonthDay, 1, 2) = ?"
        params.append(month.zfill(2))
    
    if venue:
        query += " AND JyoCD = ?"
        params.append(venue)
    
    query += " ORDER BY Year DESC, MonthDay DESC, JyoCD, RaceNum"
    query += f" LIMIT {limit}"
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    return results

def get_venue_name(jyo_cd):
    """開催場名を取得"""
    venues = {
        '01': '札幌', '02': '函館', '03': '福島', '04': '新潟', '05': '東京',
        '06': '中山', '07': '中京', '08': '京都', '09': '阪神', '10': '小倉'
    }
    return venues.get(jyo_cd, f'場{jyo_cd}')

def display_historical_races():
    """過去レースの表示"""
    print("=== 過去レース一覧（2017年以降） ===")
    
    # 年別選択
    print("表示する年を選択してください:")
    print("1. 2017年")
    print("2. 2018年") 
    print("3. 2019年")
    print("4. 2020年")
    print("5. 2021年")
    print("6. 2022年")
    print("7. 2023年")
    print("8. 2024年")
    print("9. 2025年")
    print("0. 全て")
    
    choice = input("選択 (0-9): ")
    
    year_map = {
        '1': '2017', '2': '2018', '3': '2019', '4': '2020', '5': '2021',
        '6': '2022', '7': '2023', '8': '2024', '9': '2025', '0': None
    }
    
    selected_year = year_map.get(choice)
    
    races = get_historical_races(year=selected_year, limit=100)
    
    if not races:
        print("該当するレースが見つかりません。")
        return
    
    print(f"\\n=== {selected_year or '全'}年のレース一覧 ===")
    for race in races:
        year, monthday, jyo_cd, race_num, hondai, kyori, hasso_time, toroku, syusso = race
        venue_name = get_venue_name(jyo_cd)
        date_str = f"{year}年{monthday[:2]}月{monthday[2:]}日"
        print(f"{date_str} {venue_name} {race_num}R: {hondai} ({kyori}m, {hasso_time})")
        print(f"  登録:{toroku}頭 出走:{syusso}頭")

if __name__ == "__main__":
    display_historical_races()
'''
    
    with open('historical_race_display.py', 'w', encoding='utf-8') as f:
        f.write(system_code)
    
    print("過去データ表示システムを作成しました: historical_race_display.py")

if __name__ == "__main__":
    check_historical_data()
    create_historical_display_system()


