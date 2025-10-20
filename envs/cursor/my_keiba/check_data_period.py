# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_data_period():
    """データの取得期間を確認"""
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    print("=== データ取得期間の確認 ===\n")
    
    # 1. 全データの期間確認
    print("1. 全データの期間確認")
    cursor.execute("""
        SELECT 
            MIN(Year || MonthDay) as earliest_date,
            MAX(Year || MonthDay) as latest_date,
            COUNT(*) as total_races
        FROM N_RACE
    """)
    race_period = cursor.fetchone()
    earliest, latest, total = race_period
    print(f"レースデータ期間: {earliest} ～ {latest}")
    print(f"総レース数: {total:,} 件")
    
    # 2. 年別データの期間確認
    print("\n2. 年別データの期間確認")
    cursor.execute("""
        SELECT 
            Year,
            MIN(MonthDay) as earliest_monthday,
            MAX(MonthDay) as latest_monthday,
            COUNT(*) as race_count
        FROM N_RACE
        WHERE Year BETWEEN '2020' AND '2025'
        GROUP BY Year
        ORDER BY Year DESC
    """)
    yearly_periods = cursor.fetchall()
    
    print("年別データ期間:")
    for year, earliest_md, latest_md, count in yearly_periods:
        print(f"  {year}年: {earliest_md} ～ {latest_md} ({count:,} レース)")
    
    # 3. 2023年の詳細期間確認
    print("\n3. 2023年の詳細期間確認")
    cursor.execute("""
        SELECT 
            MonthDay,
            COUNT(*) as race_count,
            COUNT(DISTINCT JyoCD) as venue_count
        FROM N_RACE
        WHERE Year = '2023'
        GROUP BY MonthDay
        ORDER BY MonthDay DESC
        LIMIT 20
    """)
    monthly_2023 = cursor.fetchall()
    
    print("2023年の月別データ（最新20日）:")
    for monthday, race_count, venue_count in monthly_2023:
        date_str = f"{monthday[:2]}月{monthday[2:]}日"
        print(f"  {date_str}: {race_count} レース ({venue_count} 開催場)")
    
    # 4. プラダリアのデータ期間確認
    print("\n4. プラダリアのデータ期間確認")
    cursor.execute("""
        SELECT 
            Year,
            MIN(MonthDay) as earliest_race,
            MAX(MonthDay) as latest_race,
            COUNT(*) as race_count
        FROM N_UMA_RACE
        WHERE Bamei = 'プラダリア'
        GROUP BY Year
        ORDER BY Year DESC
    """)
    pradaria_periods = cursor.fetchall()
    
    print("プラダリアの年別データ期間:")
    for year, earliest, latest, count in pradaria_periods:
        print(f"  {year}年: {earliest} ～ {latest} ({count} 出馬)")
    
    # 5. データの欠損期間確認
    print("\n5. データの欠損期間確認")
    cursor.execute("""
        SELECT 
            Year,
            COUNT(*) as race_count
        FROM N_RACE
        WHERE Year BETWEEN '2020' AND '2025'
        GROUP BY Year
        ORDER BY Year DESC
    """)
    yearly_counts = cursor.fetchall()
    
    print("年別レース数:")
    for year, count in yearly_counts:
        print(f"  {year}年: {count:,} レース")
    
    # 6. 特定の日付のデータ確認
    print("\n6. 特定の日付のデータ確認")
    # 2023年10月9日の京都大賞典
    cursor.execute("""
        SELECT 
            Year,
            MonthDay,
            JyoCD,
            RaceNum,
            COUNT(*) as horse_count
        FROM N_RACE
        WHERE Year = '2023' AND MonthDay = '1009' AND JyoCD = '08'
        GROUP BY Year, MonthDay, JyoCD, RaceNum
    """)
    specific_race = cursor.fetchall()
    
    print("2023年10月9日 京都大賞典のレース数:")
    for race in specific_race:
        year, monthday, jyo_cd, race_num, horse_count = race
        print(f"  {year}年{monthday[:2]}月{monthday[2:]}日 場{jyo_cd} {race_num}R: {horse_count}頭")
    
    # 7. データベースの作成日時確認
    print("\n7. データベースの作成日時確認")
    cursor.execute("""
        SELECT 
            name,
            sql
        FROM sqlite_master 
        WHERE type='table' AND name='N_RACE'
    """)
    table_info = cursor.fetchone()
    
    if table_info:
        print("N_RACEテーブルの構造:")
        print(f"  テーブル名: {table_info[0]}")
        print(f"  作成SQL: {table_info[1][:200]}...")
    
    # 8. データの整合性確認
    print("\n8. データの整合性確認")
    cursor.execute("""
        SELECT 
            'N_RACE' as table_name,
            COUNT(*) as record_count
        FROM N_RACE
        UNION ALL
        SELECT 
            'N_UMA_RACE' as table_name,
            COUNT(*) as record_count
        FROM N_UMA_RACE
        UNION ALL
        SELECT 
            'N_UMA' as table_name,
            COUNT(*) as record_count
        FROM N_UMA
    """)
    table_counts = cursor.fetchall()
    
    print("テーブル別レコード数:")
    for table_name, count in table_counts:
        print(f"  {table_name}: {count:,} 件")
    
    conn.close()

def check_missing_data_periods():
    """欠損データ期間の確認"""
    print("\n=== 欠損データ期間の確認 ===\n")
    
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    # 1. 連続する日付の確認
    print("1. 連続する日付の確認")
    cursor.execute("""
        WITH date_series AS (
            SELECT DISTINCT Year || MonthDay as race_date
            FROM N_RACE
            WHERE Year = '2023'
            ORDER BY race_date
        )
        SELECT 
            race_date,
            LAG(race_date) OVER (ORDER BY race_date) as prev_date,
            CASE 
                WHEN LAG(race_date) OVER (ORDER BY race_date) IS NULL THEN 'First'
                WHEN CAST(race_date AS INTEGER) - CAST(LAG(race_date) OVER (ORDER BY race_date) AS INTEGER) = 1 THEN 'Continuous'
                ELSE 'Gap'
            END as status
        FROM date_series
        WHERE status = 'Gap'
        LIMIT 10
    """)
    gaps = cursor.fetchall()
    
    if gaps:
        print("2023年のデータ欠損期間:")
        for race_date, prev_date, status in gaps:
            print(f"  {race_date} (前日: {prev_date})")
    else:
        print("2023年のデータは連続しています")
    
    # 2. プラダリアの欠損期間確認
    print("\n2. プラダリアの欠損期間確認")
    cursor.execute("""
        SELECT 
            Year,
            COUNT(*) as race_count
        FROM N_UMA_RACE
        WHERE Bamei = 'プラダリア'
        GROUP BY Year
        ORDER BY Year
    """)
    pradaria_years = cursor.fetchall()
    
    print("プラダリアの出走年:")
    for year, count in pradaria_years:
        print(f"  {year}年: {count} 出馬")
    
    # 2023年が含まれているかチェック
    pradaria_2023 = any(year == '2023' for year, count in pradaria_years)
    if pradaria_2023:
        print("  [OK] プラダリアの2023年データが存在します")
    else:
        print("  [WARNING] プラダリアの2023年データが存在しません")
    
    conn.close()

if __name__ == "__main__":
    check_data_period()
    check_missing_data_periods()


