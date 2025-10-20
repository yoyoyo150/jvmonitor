# -*- coding: utf-8 -*-
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
    
    print(f"\n=== {selected_year or '全'}年のレース一覧 ===")
    for race in races:
        year, monthday, jyo_cd, race_num, hondai, kyori, hasso_time, toroku, syusso = race
        venue_name = get_venue_name(jyo_cd)
        date_str = f"{year}年{monthday[:2]}月{monthday[2:]}日"
        print(f"{date_str} {venue_name} {race_num}R: {hondai} ({kyori}m, {hasso_time})")
        print(f"  登録:{toroku}頭 出走:{syusso}頭")

if __name__ == "__main__":
    display_historical_races()
