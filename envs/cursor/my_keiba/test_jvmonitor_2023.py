import sqlite3
import sys
import io
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DB_PATH = 'ecore.db'

def test_jvmonitor_2023_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=== JVMonitor 2023年データテスト ===\n")

    # 1. 2023年のレースデータ確認
    print("1. 2023年のレースデータ確認")
    cursor.execute("""
        SELECT COUNT(*) FROM N_RACE 
        WHERE Year = '2023'
    """)
    race_2023_count = cursor.fetchone()[0]
    print(f"2023年レース数: {race_2023_count:,} 件")

    # 2. 2023年の出馬データ確認
    print("\n2. 2023年の出馬データ確認")
    cursor.execute("""
        SELECT COUNT(*) FROM N_UMA_RACE 
        WHERE Year = '2023'
    """)
    uma_race_2023_count = cursor.fetchone()[0]
    print(f"2023年出馬数: {uma_race_2023_count:,} 件")

    # 3. プラダリアの2023年データ確認
    print("\n3. プラダリアの2023年データ確認")
    cursor.execute("""
        SELECT COUNT(*) FROM N_UMA_RACE 
        WHERE Bamei = 'プラダリア' AND Year = '2023'
    """)
    pradaria_2023_count = cursor.fetchone()[0]
    print(f"プラダリアの2023年出馬数: {pradaria_2023_count} 件")

    # 4. JVMonitor用テーブルの確認
    print("\n4. JVMonitor用テーブルの確認")
    cursor.execute("SELECT COUNT(*) FROM NL_SE_RACE_UMA WHERE Year = '2023'")
    nl_se_2023_count = cursor.fetchone()[0]
    print(f"NL_SE_RACE_UMA 2023年データ: {nl_se_2023_count:,} 件")

    # 5. DateSelectionテーブルの確認
    print("\n5. DateSelectionテーブルの確認")
    cursor.execute("SELECT COUNT(*) FROM DateSelection WHERE Year = '2023'")
    date_selection_2023_count = cursor.fetchone()[0]
    print(f"DateSelection 2023年データ: {date_selection_2023_count:,} 件")

    # 6. 2023年の開催日一覧
    print("\n6. 2023年の開催日一覧（最新10日）")
    cursor.execute("""
        SELECT RaceDate, RaceCount, VenueCount 
        FROM DateSelection 
        WHERE Year = '2023' 
        ORDER BY RaceDate DESC 
        LIMIT 10
    """)
    dates_2023 = cursor.fetchall()
    for date_info in dates_2023:
        print(f"  {date_info[0][4:6]}/{date_info[0][6:8]}: {date_info[1]} レース, {date_info[2]} 開催場")

    # 7. プラダリアの2023年詳細成績
    print("\n7. プラダリアの2023年詳細成績")
    cursor.execute("""
        SELECT 
            r.Year || r.MonthDay as RaceDate,
            r.JyoCD,
            r.RaceNum,
            ur.Umaban,
            ur.Bamei,
            ur.KisyuRyakusyo,
            ur.NyusenJyuni,
            ur.KakuteiJyuni,
            ur.Time,
            ur.Futan
        FROM N_UMA_RACE ur
        JOIN N_RACE r ON ur.Year = r.Year AND ur.MonthDay = r.MonthDay 
            AND ur.JyoCD = r.JyoCD AND ur.RaceNum = r.RaceNum
        WHERE ur.Bamei = 'プラダリア' AND ur.Year = '2023'
        ORDER BY r.Year || r.MonthDay
    """)
    pradaria_races = cursor.fetchall()
    for race in pradaria_races:
        print(f"  {race[0][4:6]}/{race[0][6:8]} 場{race[1]} {race[2]}R ({race[6]}位) - {race[5]}")

    conn.close()
    print("\n=== テスト完了 ===")
    print("JVMonitorで2023年のデータが表示されるか確認してください。")

if __name__ == '__main__':
    test_jvmonitor_2023_data()
