# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_pradaria_complete_history():
    """プラダリアの完全な出走履歴を調査"""
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    print("=== プラダリアの完全な出走履歴調査 ===\n")
    
    # 1. プラダリアの全出走履歴
    print("1. プラダリアの全出走履歴")
    cursor.execute("""
        SELECT 
            Year,
            MonthDay,
            JyoCD,
            RaceNum,
            NyusenJyuni,
            KakuteiJyuni,
            KisyuRyakusyo,
            Honsyokin,
            Time,
            Odds,
            Ninki
        FROM N_UMA_RACE
        WHERE Bamei = 'プラダリア'
        ORDER BY Year DESC, MonthDay DESC
    """)
    all_races = cursor.fetchall()
    
    print(f"プラダリアの総出走数: {len(all_races)} 件")
    print("\nプラダリアの全出走履歴:")
    for race in all_races:
        year, monthday, jyo_cd, race_num, nyusen, kakutei, kisyu, honsyokin, time, odds, ninki = race
        date_str = f"{year}年{monthday[:2]}月{monthday[2:]}日"
        print(f"  {date_str} 場{jyo_cd} {race_num}R ({kakutei or nyusen}位)")
        print(f"    騎手: {kisyu}, 賞金: {honsyokin}円, タイム: {time}")
        print(f"    オッズ: {odds}, 人気: {ninki}")
        print()
    
    # 2. 年別出走数
    print("2. 年別出走数")
    cursor.execute("""
        SELECT 
            Year,
            COUNT(*) as race_count,
            MIN(MonthDay) as first_race,
            MAX(MonthDay) as last_race
        FROM N_UMA_RACE
        WHERE Bamei = 'プラダリア'
        GROUP BY Year
        ORDER BY Year DESC
    """)
    yearly_races = cursor.fetchall()
    
    print("プラダリアの年別出走数:")
    for year, race_count, first_race, last_race in yearly_races:
        print(f"  {year}年: {race_count} 出馬 ({first_race} ～ {last_race})")
    
    # 3. 2023年のデータが本当に存在するか確認
    print("\n3. 2023年のデータが本当に存在するか確認")
    cursor.execute("""
        SELECT 
            Year,
            MonthDay,
            JyoCD,
            RaceNum,
            COUNT(*) as horse_count
        FROM N_RACE
        WHERE Year = '2023'
        GROUP BY Year, MonthDay, JyoCD, RaceNum
        ORDER BY MonthDay DESC
        LIMIT 10
    """)
    sample_2023_races = cursor.fetchall()
    
    print("2023年のサンプルレース:")
    for race in sample_2023_races:
        year, monthday, jyo_cd, race_num, horse_count = race
        date_str = f"{monthday[:2]}月{monthday[2:]}日"
        print(f"  {date_str} 場{jyo_cd} {race_num}R ({horse_count}頭)")
    
    # 4. 2023年の出馬データの詳細確認
    print("\n4. 2023年の出馬データの詳細確認")
    cursor.execute("""
        SELECT 
            Year,
            MonthDay,
            JyoCD,
            RaceNum,
            Bamei,
            NyusenJyuni,
            KakuteiJyuni
        FROM N_UMA_RACE
        WHERE Year = '2023'
        ORDER BY MonthDay DESC
        LIMIT 20
    """)
    sample_2023_umas = cursor.fetchall()
    
    print("2023年のサンプル出馬データ:")
    for race in sample_2023_umas:
        year, monthday, jyo_cd, race_num, bamei, nyusen, kakutei = race
        date_str = f"{monthday[:2]}月{monthday[2:]}日"
        print(f"  {date_str} 場{jyo_cd} {race_num}R: {bamei} ({kakutei or nyusen}位)")
    
    # 5. プラダリアの血統情報確認
    print("\n5. プラダリアの血統情報確認")
    cursor.execute("""
        SELECT 
            KettoNum,
            Bamei,
            BameiKana,
            BameiEng,
            SexCD,
            HinsyuCD,
            KeiroCD,
            Barei,
            ChokyosiRyakusyo,
            BanusiName
        FROM N_UMA
        WHERE Bamei = 'プラダリア'
    """)
    horse_info = cursor.fetchall()
    
    if horse_info:
        print("プラダリアの血統情報:")
        for info in horse_info:
            ketto, bamei, kana, eng, sex, hinsyu, keiro, barei, chokyosi, banusi = info
            print(f"  血統番号: {ketto}")
            print(f"  馬名: {bamei} ({kana})")
            print(f"  英語名: {eng}")
            print(f"  性別: {sex}")
            print(f"  品種: {hinsyu}")
            print(f"  毛色: {keiro}")
            print(f"  年齢: {barei}")
            print(f"  調教師: {chokyosi}")
            print(f"  馬主: {banusi}")
    else:
        print("プラダリアの血統情報が見つかりません")
    
    conn.close()

def check_2023_data_quality():
    """2023年データの品質確認"""
    print("\n=== 2023年データの品質確認 ===\n")
    
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    # 1. 2023年のデータ範囲確認
    print("1. 2023年のデータ範囲確認")
    cursor.execute("""
        SELECT 
            MIN(MonthDay) as earliest,
            MAX(MonthDay) as latest,
            COUNT(DISTINCT MonthDay) as race_days
        FROM N_RACE
        WHERE Year = '2023'
    """)
    date_range = cursor.fetchone()
    earliest, latest, race_days = date_range
    print(f"2023年のデータ範囲: {earliest} ～ {latest}")
    print(f"2023年の開催日数: {race_days} 日")
    
    # 2. 2023年の開催場別データ確認
    print("\n2. 2023年の開催場別データ確認")
    cursor.execute("""
        SELECT 
            JyoCD,
            COUNT(*) as race_count,
            COUNT(DISTINCT MonthDay) as race_days
        FROM N_RACE
        WHERE Year = '2023'
        GROUP BY JyoCD
        ORDER BY race_count DESC
        LIMIT 10
    """)
    venue_data = cursor.fetchall()
    
    venue_names = {
        '01': '札幌', '02': '函館', '03': '福島', '04': '新潟', '05': '東京',
        '06': '中山', '07': '中京', '08': '京都', '09': '阪神', '10': '小倉'
    }
    
    print("2023年の開催場別データ:")
    for jyo_cd, race_count, race_days in venue_data:
        venue_name = venue_names.get(jyo_cd, f'場{jyo_cd}')
        print(f"  {venue_name} ({jyo_cd}): {race_count} レース ({race_days} 開催日)")
    
    # 3. 2023年の出馬データの品質確認
    print("\n3. 2023年の出馬データの品質確認")
    cursor.execute("""
        SELECT 
            COUNT(*) as total_umas,
            COUNT(DISTINCT Bamei) as unique_horses,
            COUNT(DISTINCT KisyuRyakusyo) as unique_jockeys
        FROM N_UMA_RACE
        WHERE Year = '2023'
    """)
    uma_stats = cursor.fetchone()
    total_umas, unique_horses, unique_jockeys = uma_stats
    print(f"2023年の出馬データ:")
    print(f"  総出馬数: {total_umas:,} 件")
    print(f"  出走馬数: {unique_horses:,} 頭")
    print(f"  騎手数: {unique_jockeys:,} 人")
    
    conn.close()

if __name__ == "__main__":
    check_pradaria_complete_history()
    check_2023_data_quality()


