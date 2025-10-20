# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_202405_data():
    """2024年5月のデータを詳細調査"""
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    print("=== 2024年5月のデータ詳細調査 ===\n")
    
    # 1. 2024年5月のレースデータ確認
    print("1. 2024年5月のレースデータ確認")
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
        WHERE Year = '2024' AND MonthDay LIKE '05%'
        ORDER BY MonthDay, JyoCD, RaceNum
    """)
    may_races = cursor.fetchall()
    
    print(f"2024年5月のレース数: {len(may_races)} 件")
    
    if may_races:
        print("\n2024年5月のレース一覧:")
        for race in may_races[:10]:  # 最初の10レース表示
            year, monthday, jyo_cd, race_num, hondai, kyori, hasso_time, toroku, syusso = race
            date_str = f"{monthday[:2]}月{monthday[2:]}日"
            print(f"  {date_str} 場{jyo_cd} {race_num}R: {hondai} ({kyori}m, {hasso_time})")
            print(f"    登録:{toroku}頭 出走:{syusso}頭")
    else:
        print("2024年5月のレースデータが見つかりません。")
    
    print("\n" + "="*50 + "\n")
    
    # 2. 2024年5月の出馬データ確認
    print("2. 2024年5月の出馬データ確認")
    cursor.execute("""
        SELECT COUNT(*) FROM N_UMA_RACE
        WHERE Year = '2024' AND MonthDay LIKE '05%'
    """)
    may_umas = cursor.fetchone()[0]
    print(f"2024年5月の出馬数: {may_umas:,} 件")
    
    # 3. NL_SE_RACE_UMAテーブルの2024年5月データ確認
    print("\n3. NL_SE_RACE_UMAテーブルの2024年5月データ確認")
    cursor.execute("""
        SELECT COUNT(*) FROM NL_SE_RACE_UMA
        WHERE Year = '2024' AND MonthDay LIKE '05%'
    """)
    nl_may_umas = cursor.fetchone()[0]
    print(f"NL_SE_RACE_UMA 2024年5月: {nl_may_umas:,} 件")
    
    # 4. 2024年5月の日別データ確認
    print("\n4. 2024年5月の日別データ確認")
    cursor.execute("""
        SELECT 
            MonthDay,
            COUNT(*) as race_count,
            COUNT(DISTINCT JyoCD) as venue_count
        FROM N_RACE
        WHERE Year = '2024' AND MonthDay LIKE '05%'
        GROUP BY MonthDay
        ORDER BY MonthDay
    """)
    daily_races = cursor.fetchall()
    
    print("2024年5月の日別レース数:")
    for monthday, race_count, venue_count in daily_races:
        date_str = f"{monthday[:2]}月{monthday[2:]}日"
        print(f"  {date_str}: {race_count} レース ({venue_count} 開催場)")
    
    print("\n" + "="*50 + "\n")
    
    # 5. 2024年5月の開催場別データ確認
    print("5. 2024年5月の開催場別データ確認")
    cursor.execute("""
        SELECT 
            JyoCD,
            COUNT(*) as race_count,
            COUNT(DISTINCT MonthDay) as race_days
        FROM N_RACE
        WHERE Year = '2024' AND MonthDay LIKE '05%'
        GROUP BY JyoCD
        ORDER BY race_count DESC
    """)
    venue_races = cursor.fetchall()
    
    venue_names = {
        '01': '札幌', '02': '函館', '03': '福島', '04': '新潟', '05': '東京',
        '06': '中山', '07': '中京', '08': '京都', '09': '阪神', '10': '小倉'
    }
    
    print("2024年5月の開催場別レース数:")
    for jyo_cd, race_count, race_days in venue_races:
        venue_name = venue_names.get(jyo_cd, f'場{jyo_cd}')
        print(f"  {venue_name} ({jyo_cd}): {race_count} レース ({race_days} 開催日)")
    
    print("\n" + "="*50 + "\n")
    
    # 6. サンプルレースの出馬表確認
    print("6. サンプルレースの出馬表確認")
    if may_races:
        sample_race = may_races[0]
        year, monthday, jyo_cd, race_num = sample_race[0], sample_race[1], sample_race[2], sample_race[3]
        
        cursor.execute("""
            SELECT 
                Wakuban,
                Umaban,
                Bamei,
                KisyuRyakusyo,
                ChokyosiRyakusyo,
                BaTaijyu,
                Odds,
                Ninki
            FROM N_UMA_RACE
            WHERE Year = ? AND MonthDay = ? AND JyoCD = ? AND RaceNum = ?
            ORDER BY Umaban
        """, (year, monthday, jyo_cd, race_num))
        
        horses = cursor.fetchall()
        
        print(f"サンプルレース: {year}年{monthday[:2]}月{monthday[2:]}日 場{jyo_cd} {race_num}R")
        print(f"出馬頭数: {len(horses)} 頭")
        
        for horse in horses[:5]:  # 最初の5頭表示
            waku, uma, bamei, kisyu, chokyosi, taijyu, odds, ninki = horse
            print(f"  {waku}-{uma}: {bamei} ({kisyu}/{chokyosi}) 体重:{taijyu}kg オッズ:{odds} 人気:{ninki}")
    
    print("\n" + "="*50 + "\n")
    
    # 7. JVMonitor用データの確認
    print("7. JVMonitor用データの確認")
    cursor.execute("""
        SELECT COUNT(*) FROM NL_SE_RACE_UMA
        WHERE Year = '2024' AND MonthDay LIKE '05%'
    """)
    jvmonitor_may = cursor.fetchone()[0]
    print(f"JVMonitor用2024年5月データ: {jvmonitor_may:,} 件")
    
    if jvmonitor_may == 0:
        print("[WARNING] JVMonitor用の2024年5月データがありません")
        print("データ移行が必要です。")
        
        # データ移行の実行
        print("\nデータ移行を実行します...")
        cursor.execute("""
            INSERT OR REPLACE INTO NL_SE_RACE_UMA 
            SELECT 
                Year,
                MonthDay,
                JyoCD,
                RaceNum,
                Wakuban,
                Umaban,
                KettoNum,
                Bamei,
                KisyuRyakusyo,
                ChokyosiRyakusyo,
                BaTaijyu,
                Odds,
                Ninki,
                Honsyokin,
                Fukasyokin,
                NyusenJyuni,
                KakuteiJyuni,
                Time,
                ChakusaCD
            FROM N_UMA_RACE
            WHERE Year = '2024' AND MonthDay LIKE '05%'
        """)
        
        moved_count = cursor.rowcount
        print(f"[OK] {moved_count:,} 件のデータを移行しました")
        
        conn.commit()
    else:
        print("[OK] JVMonitor用の2024年5月データは存在します")
    
    conn.close()

def fix_202405_data():
    """2024年5月のデータを修正"""
    print("\n=== 2024年5月データ修正 ===")
    
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    try:
        # 2024年5月のデータをNL_SE_RACE_UMAに移行
        cursor.execute("""
            INSERT OR REPLACE INTO NL_SE_RACE_UMA 
            SELECT 
                Year,
                MonthDay,
                JyoCD,
                RaceNum,
                Wakuban,
                Umaban,
                KettoNum,
                Bamei,
                KisyuRyakusyo,
                ChokyosiRyakusyo,
                BaTaijyu,
                Odds,
                Ninki,
                Honsyokin,
                Fukasyokin,
                NyusenJyuni,
                KakuteiJyuni,
                Time,
                ChakusaCD
            FROM N_UMA_RACE
            WHERE Year = '2024' AND MonthDay LIKE '05%'
        """)
        
        moved_count = cursor.rowcount
        print(f"[OK] 2024年5月のデータ {moved_count:,} 件を移行しました")
        
        # 確認
        cursor.execute("""
            SELECT COUNT(*) FROM NL_SE_RACE_UMA
            WHERE Year = '2024' AND MonthDay LIKE '05%'
        """)
        final_count = cursor.fetchone()[0]
        print(f"[OK] 移行後のデータ数: {final_count:,} 件")
        
        conn.commit()
        print("[OK] 2024年5月のデータ修正が完了しました")
        
    except Exception as e:
        print(f"[ERROR] データ修正エラー: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_202405_data()
    fix_202405_data()


