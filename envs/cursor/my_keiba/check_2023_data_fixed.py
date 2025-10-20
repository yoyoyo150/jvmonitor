# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_2023_data():
    """2023年のデータを詳細調査"""
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    print("=== 2023年のデータ詳細調査 ===\n")
    
    # 1. 2023年のレースデータ確認
    print("1. 2023年のレースデータ確認")
    cursor.execute("""
        SELECT 
            Year,
            MonthDay,
            COUNT(*) as race_count,
            COUNT(DISTINCT JyoCD) as venue_count
        FROM N_RACE
        WHERE Year = '2023'
        GROUP BY Year, MonthDay
        ORDER BY MonthDay DESC
        LIMIT 20
    """)
    races_2023 = cursor.fetchall()
    
    print(f"2023年のレース日数: {len(races_2023)} 日")
    if races_2023:
        print("2023年のレース（最初の20日）:")
        for year, monthday, race_count, venue_count in races_2023:
            date_str = f"{monthday[:2]}月{monthday[2:]}日"
            print(f"  {date_str}: {race_count} レース, {venue_count} 開催場")
    else:
        print("2023年のレースデータが見つかりません")
    
    # 2. 2023年の出馬データ確認
    print("\n2. 2023年の出馬データ確認")
    cursor.execute("""
        SELECT COUNT(*) FROM N_UMA_RACE
        WHERE Year = '2023'
    """)
    uma_2023 = cursor.fetchone()[0]
    print(f"2023年の出馬数: {uma_2023:,} 件")
    
    # 3. プラダリアの2023年成績確認（N_UMA_RACEテーブルの構造を確認）
    print("\n3. プラダリアの2023年成績確認")
    
    # まずN_UMA_RACEテーブルの構造を確認
    cursor.execute("PRAGMA table_info(N_UMA_RACE)")
    uma_columns = cursor.fetchall()
    
    print("N_UMA_RACEテーブルのカラム構造:")
    for col in uma_columns:
        col_name, col_type = col[1], col[2]
        if 'Hondai' in col_name or 'Race' in col_name or 'Name' in col_name:
            print(f"  {col_name}: {col_type}")
    
    # プラダリアの2023年成績を取得
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
            Time
        FROM N_UMA_RACE
        WHERE Bamei = 'プラダリア' AND Year = '2023'
        ORDER BY MonthDay DESC
    """)
    pradaria_2023 = cursor.fetchall()
    
    print(f"\nプラダリアの2023年出馬数: {len(pradaria_2023)} 件")
    if pradaria_2023:
        print("プラダリアの2023年成績:")
        for race in pradaria_2023:
            year, monthday, jyo_cd, race_num, nyusen, kakutei, kisyu, honsyokin, time = race
            date_str = f"{monthday[:2]}月{monthday[2:]}日"
            print(f"  {date_str} 場{jyo_cd} {race_num}R")
            print(f"    着順: {kakutei or nyusen}位, 騎手: {kisyu}, 賞金: {honsyokin}円, タイム: {time}")
    else:
        print("プラダリアの2023年成績が見つかりません")
    
    # 4. 2023年の月別データ確認
    print("\n4. 2023年の月別データ確認")
    cursor.execute("""
        SELECT 
            SUBSTR(MonthDay, 1, 2) as month,
            COUNT(*) as race_count,
            COUNT(DISTINCT MonthDay) as race_days
        FROM N_RACE
        WHERE Year = '2023'
        GROUP BY SUBSTR(MonthDay, 1, 2)
        ORDER BY month DESC
    """)
    monthly_2023 = cursor.fetchall()
    
    print("2023年の月別レース数:")
    for month, race_count, race_days in monthly_2023:
        print(f"  {month}月: {race_count} レース ({race_days} 開催日)")
    
    # 5. 2023年の開催場別データ確認
    print("\n5. 2023年の開催場別データ確認")
    cursor.execute("""
        SELECT 
            JyoCD,
            COUNT(*) as race_count,
            COUNT(DISTINCT MonthDay) as race_days
        FROM N_RACE
        WHERE Year = '2023'
        GROUP BY JyoCD
        ORDER BY race_count DESC
    """)
    venue_2023 = cursor.fetchall()
    
    venue_names = {
        '01': '札幌', '02': '函館', '03': '福島', '04': '新潟', '05': '東京',
        '06': '中山', '07': '中京', '08': '京都', '09': '阪神', '10': '小倉'
    }
    
    print("2023年の開催場別レース数:")
    for jyo_cd, race_count, race_days in venue_2023:
        venue_name = venue_names.get(jyo_cd, f'場{jyo_cd}')
        print(f"  {venue_name} ({jyo_cd}): {race_count} レース ({race_days} 開催日)")
    
    # 6. プラダリアの全成績確認
    print("\n6. プラダリアの全成績確認")
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
    pradaria_all = cursor.fetchall()
    
    print("プラダリアの年別出馬数:")
    for year, race_count, first_race, last_race in pradaria_all:
        print(f"  {year}年: {race_count} 出馬 ({first_race} ～ {last_race})")
    
    # 7. データの欠損確認
    print("\n7. データの欠損確認")
    cursor.execute("""
        SELECT 
            Year,
            COUNT(*) as race_count
        FROM N_RACE
        WHERE Year BETWEEN '2020' AND '2025'
        GROUP BY Year
        ORDER BY Year DESC
    """)
    yearly_data = cursor.fetchall()
    
    print("年別レース数（2020-2025）:")
    for year, race_count in yearly_data:
        print(f"  {year}年: {race_count:,} レース")
    
    conn.close()

def check_jvmonitor_display_logic():
    """JVMonitorの表示ロジック確認"""
    print("\n=== JVMonitor表示ロジック確認 ===\n")
    
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    # 1. プラダリアの最新成績確認
    print("1. プラダリアの最新成績確認")
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
            Time
        FROM N_UMA_RACE
        WHERE Bamei = 'プラダリア'
        ORDER BY Year DESC, MonthDay DESC
        LIMIT 10
    """)
    latest_races = cursor.fetchall()
    
    print("プラダリアの最新10レース:")
    for race in latest_races:
        year, monthday, jyo_cd, race_num, nyusen, kakutei, kisyu, honsyokin, time = race
        date_str = f"{year}年{monthday[:2]}月{monthday[2:]}日"
        print(f"  {date_str} 場{jyo_cd} {race_num}R ({kakutei or nyusen}位)")
    
    # 2. 2023年のデータがJVMonitorで表示されるか確認
    print("\n2. 2023年のデータがJVMonitorで表示されるか確認")
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
        LIMIT 5
    """)
    sample_2023 = cursor.fetchall()
    
    print("2023年のサンプルレース:")
    for race in sample_2023:
        year, monthday, jyo_cd, race_num, horse_count = race
        date_str = f"{monthday[:2]}月{monthday[2:]}日"
        print(f"  {date_str} 場{jyo_cd} {race_num}R ({horse_count}頭)")
    
    # 3. プラダリアの2023年成績の詳細
    print("\n3. プラダリアの2023年成績の詳細")
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
        WHERE Bamei = 'プラダリア' AND Year = '2023'
        ORDER BY MonthDay DESC
    """)
    pradaria_2023_detail = cursor.fetchall()
    
    print("プラダリアの2023年成績詳細:")
    for race in pradaria_2023_detail:
        year, monthday, jyo_cd, race_num, nyusen, kakutei, kisyu, honsyokin, time, odds, ninki = race
        date_str = f"{monthday[:2]}月{monthday[2:]}日"
        print(f"  {date_str} 場{jyo_cd} {race_num}R")
        print(f"    着順: {kakutei or nyusen}位, 騎手: {kisyu}, 賞金: {honsyokin}円")
        print(f"    タイム: {time}, オッズ: {odds}, 人気: {ninki}")
    
    conn.close()

if __name__ == "__main__":
    check_2023_data()
    check_jvmonitor_display_logic()


