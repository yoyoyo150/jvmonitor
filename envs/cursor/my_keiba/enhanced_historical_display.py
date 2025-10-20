# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def get_venue_name(jyo_cd):
    """開催場名を取得"""
    venues = {
        '01': '札幌', '02': '函館', '03': '福島', '04': '新潟', '05': '東京',
        '06': '中山', '07': '中京', '08': '京都', '09': '阪神', '10': '小倉'
    }
    return venues.get(jyo_cd, f'場{jyo_cd}')

def get_races_by_year(year):
    """指定年のレースを取得"""
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
    WHERE Year = ?
    ORDER BY MonthDay DESC, JyoCD, RaceNum
    """
    
    cursor.execute(query, (year,))
    results = cursor.fetchall()
    conn.close()
    
    return results

def get_races_by_month(year, month):
    """指定年月のレースを取得"""
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
    WHERE Year = ? AND SUBSTR(MonthDay, 1, 2) = ?
    ORDER BY MonthDay DESC, JyoCD, RaceNum
    """
    
    cursor.execute(query, (year, month.zfill(2)))
    results = cursor.fetchall()
    conn.close()
    
    return results

def display_recent_races():
    """2024年以降のレースを並べる形式で表示"""
    print("=== 2024年以降のレース一覧 ===")
    
    for year in ['2025', '2024']:
        races = get_races_by_year(year)
        if not races:
            continue
            
        print(f"\n【{year}年】")
        print("=" * 50)
        
        # 月別にグループ化
        monthly_races = {}
        for race in races:
            year, monthday, jyo_cd, race_num, hondai, kyori, hasso_time, toroku, syusso = race
            month = monthday[:2]
            if month not in monthly_races:
                monthly_races[month] = []
            monthly_races[month].append(race)
        
        # 月別に表示
        for month in sorted(monthly_races.keys(), reverse=True):
            month_races = monthly_races[month]
            print(f"\n{year}年{month}月 ({len(month_races)}レース)")
            print("-" * 30)
            
            for race in month_races[:20]:  # 月あたり最大20レース表示
                year, monthday, jyo_cd, race_num, hondai, kyori, hasso_time, toroku, syusso = race
                venue_name = get_venue_name(jyo_cd)
                date_str = f"{monthday[:2]}月{monthday[2:]}日"
                print(f"  {date_str} {venue_name} {race_num}R: {hondai} ({kyori}m, {hasso_time})")
                print(f"    登録:{toroku}頭 出走:{syusso}頭")
            
            if len(month_races) > 20:
                print(f"    ... 他{len(month_races) - 20}レース")

def display_historical_races():
    """2023年以前のレースをアコーデオン式で表示"""
    print("=== 2023年以前のレース一覧（アコーデオン式） ===")
    
    for year in ['2023', '2022', '2021', '2020', '2019', '2018', '2017']:
        races = get_races_by_year(year)
        if not races:
            continue
            
        print(f"\n【{year}年】 ({len(races)}レース)")
        print("=" * 50)
        
        # 月別にグループ化
        monthly_races = {}
        for race in races:
            year, monthday, jyo_cd, race_num, hondai, kyori, hasso_time, toroku, syusso = race
            month = monthday[:2]
            if month not in monthly_races:
                monthly_races[month] = []
            monthly_races[month].append(race)
        
        # 月別にアコーデオン式で表示
        for month in sorted(monthly_races.keys(), reverse=True):
            month_races = monthly_races[month]
            month_name = f"{year}年{month}月"
            print(f"\n▼ {month_name} ({len(month_races)}レース)")
            
            # 最初の5レースのみ表示
            for i, race in enumerate(month_races[:5]):
                year, monthday, jyo_cd, race_num, hondai, kyori, hasso_time, toroku, syusso = race
                venue_name = get_venue_name(jyo_cd)
                date_str = f"{monthday[:2]}月{monthday[2:]}日"
                print(f"  {date_str} {venue_name} {race_num}R: {hondai} ({kyori}m, {hasso_time})")
                print(f"    登録:{toroku}頭 出走:{syusso}頭")
            
            if len(month_races) > 5:
                print(f"  ... 他{len(month_races) - 5}レース")
                print(f"  [Enter] キーで{month_name}の全レースを表示")
                
                # ユーザー入力待ち
                input()
                print(f"\n{month_name}の全レース:")
                print("-" * 30)
                
                for race in month_races:
                    year, monthday, jyo_cd, race_num, hondai, kyori, hasso_time, toroku, syusso = race
                    venue_name = get_venue_name(jyo_cd)
                    date_str = f"{monthday[:2]}月{monthday[2:]}日"
                    print(f"  {date_str} {venue_name} {race_num}R: {hondai} ({kyori}m, {hasso_time})")
                    print(f"    登録:{toroku}頭 出走:{syusso}頭")

def display_race_detail(year, monthday, jyo_cd, race_num):
    """特定レースの詳細を表示"""
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    # レース基本情報
    race_query = """
    SELECT Hondai, Fukudai, Kyori, HassoTime, TorokuTosu, SyussoTosu, TenkoCD, SibaBabaCD
    FROM N_RACE
    WHERE Year = ? AND MonthDay = ? AND JyoCD = ? AND RaceNum = ?
    """
    
    cursor.execute(race_query, (year, monthday, jyo_cd, race_num))
    race_info = cursor.fetchone()
    
    if not race_info:
        print("レース情報が見つかりません。")
        conn.close()
        return
    
    hondai, fukudai, kyori, hasso_time, toroku, syusso, tenko, siba_baba = race_info
    venue_name = get_venue_name(jyo_cd)
    date_str = f"{year}年{monthday[:2]}月{monthday[2:]}日"
    
    print(f"=== レース詳細 ===")
    print(f"開催日: {date_str}")
    print(f"開催場: {venue_name}")
    print(f"レース: {race_num}R")
    print(f"レース名: {hondai}")
    if fukudai:
        print(f"副題: {fukudai}")
    print(f"距離: {kyori}m")
    print(f"発走時刻: {hasso_time}")
    print(f"登録頭数: {toroku}頭")
    print(f"出走頭数: {syusso}頭")
    print(f"天候: {tenko}")
    print(f"芝馬場: {siba_baba}")
    
    # 出馬表
    uma_query = """
    SELECT 
        Wakuban,
        Umaban,
        Bamei,
        KisyuRyakusyo,
        ChokyosiRyakusyo,
        BaTaijyu,
        Odds,
        Ninki,
        Honsyokin
    FROM N_UMA_RACE
    WHERE Year = ? AND MonthDay = ? AND JyoCD = ? AND RaceNum = ?
    ORDER BY Umaban
    """
    
    cursor.execute(uma_query, (year, monthday, jyo_cd, race_num))
    horses = cursor.fetchall()
    
    print(f"\n=== 出馬表 ===")
    for horse in horses:
        waku, uma, bamei, kisyu, chokyosi, taijyu, odds, ninki, honsyokin = horse
        print(f"{waku}-{uma}: {bamei}")
        print(f"  騎手: {kisyu} / 調教師: {chokyosi}")
        print(f"  馬体重: {taijyu}kg")
        print(f"  オッズ: {odds} / 人気: {ninki}")
        print(f"  本賞金: {honsyokin}円")
        print()
    
    conn.close()

def main():
    """メイン実行"""
    print("競馬過去データ表示システム")
    print("=" * 50)
    
    while True:
        print("\n選択してください:")
        print("1. 2024年以降のレース（並べる形式）")
        print("2. 2023年以前のレース（アコーデオン式）")
        print("3. 特定レースの詳細表示")
        print("4. 終了")
        
        choice = input("選択 (1-4): ")
        
        if choice == '1':
            display_recent_races()
        
        elif choice == '2':
            display_historical_races()
        
        elif choice == '3':
            print("\nレース詳細を表示するレースを選択してください:")
            print("年を入力してください (例: 2024):")
            year = input("年: ")
            
            races = get_races_by_year(year)
            if not races:
                print("該当するレースが見つかりません。")
                continue
            
            print(f"\n{year}年のレース一覧:")
            for i, race in enumerate(races[:20], 1):
                year, monthday, jyo_cd, race_num, hondai, kyori, hasso_time, toroku, syusso = race
                venue_name = get_venue_name(jyo_cd)
                date_str = f"{year}年{monthday[:2]}月{monthday[2:]}日"
                print(f"{i}. {date_str} {venue_name} {race_num}R: {hondai}")
            
            try:
                race_choice = int(input("レース番号を入力: ")) - 1
                if 0 <= race_choice < len(races):
                    selected_race = races[race_choice]
                    year, monthday, jyo_cd, race_num = selected_race[0], selected_race[1], selected_race[2], selected_race[3]
                    display_race_detail(year, monthday, jyo_cd, race_num)
                else:
                    print("無効な選択です。")
            except ValueError:
                print("数値を入力してください。")
        
        elif choice == '4':
            print("終了します。")
            break
        
        else:
            print("無効な選択です。")

if __name__ == "__main__":
    main()


