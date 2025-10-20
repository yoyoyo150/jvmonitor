# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def get_race_list(limit=20):
    """レース一覧を取得（シンプル版）"""
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
    WHERE Year >= '2024'
    ORDER BY Year DESC, MonthDay DESC, JyoCD, RaceNum
    LIMIT ?
    """
    
    cursor.execute(query, (limit,))
    results = cursor.fetchall()
    conn.close()
    
    return results

def get_race_horses(year, monthday, jyo_cd, race_num):
    """特定レースの出馬表を取得"""
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    query = """
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
    
    cursor.execute(query, (year, monthday, jyo_cd, race_num))
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

def display_race_list():
    """レース一覧を表示"""
    print("=== 最近のレース一覧 ===")
    races = get_race_list(20)
    
    for race in races:
        year, monthday, jyo_cd, race_num, hondai, kyori, hasso_time, toroku, syusso = race
        venue_name = get_venue_name(jyo_cd)
        date_str = f"{year}年{monthday[:2]}月{monthday[2:]}日"
        
        print(f"{date_str} {venue_name} {race_num}R: {hondai} ({kyori}m, {hasso_time})")
        print(f"  登録:{toroku}頭 出走:{syusso}頭")

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
    horses = get_race_horses(year, monthday, jyo_cd, race_num)
    
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
    print("競馬出馬表表示システム")
    print("=" * 50)
    
    while True:
        print("\n選択してください:")
        print("1. レース一覧表示")
        print("2. 特定レースの詳細表示")
        print("3. 終了")
        
        choice = input("選択 (1-3): ")
        
        if choice == '1':
            display_race_list()
        
        elif choice == '2':
            print("\nレース詳細を表示するレースを選択してください:")
            races = get_race_list(10)
            
            for i, race in enumerate(races, 1):
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
        
        elif choice == '3':
            print("終了します。")
            break
        
        else:
            print("無効な選択です。")

if __name__ == "__main__":
    main()


