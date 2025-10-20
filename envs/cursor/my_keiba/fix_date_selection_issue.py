# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_date_selection_issue():
    """日付選択問題の調査"""
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    print("=== 日付選択問題の調査 ===\n")
    
    # 1. 2024年9月4日より過去のデータ確認
    print("1. 2024年9月4日より過去のデータ確認")
    cursor.execute("""
        SELECT 
            Year,
            MonthDay,
            COUNT(*) as race_count
        FROM N_RACE
        WHERE Year = '2024' AND MonthDay < '0904'
        GROUP BY Year, MonthDay
        ORDER BY MonthDay DESC
        LIMIT 10
    """)
    past_races = cursor.fetchall()
    
    print(f"2024年9月4日より過去のレース数: {len(past_races)} 日")
    for year, monthday, count in past_races:
        date_str = f"{monthday[:2]}月{monthday[2:]}日"
        print(f"  {date_str}: {count} レース")
    
    # 2. データベースの日付カラム構造確認
    print("\n2. データベースの日付カラム構造確認")
    cursor.execute("PRAGMA table_info(N_RACE)")
    race_columns = cursor.fetchall()
    
    print("N_RACEテーブルのカラム構造:")
    for col in race_columns:
        col_name, col_type = col[1], col[2]
        print(f"  {col_name}: {col_type}")
    
    # 3. idYearカラムの存在確認
    print("\n3. idYearカラムの存在確認")
    idyear_columns = [col for col in race_columns if 'idYear' in col[1] or 'Year' in col[1]]
    print(f"Year関連カラム: {len(idyear_columns)} 個")
    for col in idyear_columns:
        print(f"  {col[1]}: {col[2]}")
    
    # 4. 日付データの範囲確認
    print("\n4. 日付データの範囲確認")
    cursor.execute("""
        SELECT 
            MIN(Year || MonthDay) as earliest_date,
            MAX(Year || MonthDay) as latest_date,
            COUNT(DISTINCT Year || MonthDay) as total_days
        FROM N_RACE
    """)
    date_range = cursor.fetchone()
    earliest, latest, total_days = date_range
    print(f"データ範囲: {earliest} ～ {latest}")
    print(f"総開催日数: {total_days:,} 日")
    
    # 5. 2024年9月4日より過去の詳細データ
    print("\n5. 2024年9月4日より過去の詳細データ")
    cursor.execute("""
        SELECT 
            Year,
            MonthDay,
            JyoCD,
            COUNT(*) as race_count
        FROM N_RACE
        WHERE Year = '2024' AND MonthDay < '0904'
        GROUP BY Year, MonthDay, JyoCD
        ORDER BY MonthDay DESC, JyoCD
        LIMIT 20
    """)
    detailed_past = cursor.fetchall()
    
    print("2024年9月4日より過去の詳細データ:")
    for year, monthday, jyo_cd, count in detailed_past:
        date_str = f"{monthday[:2]}月{monthday[2:]}日"
        print(f"  {date_str} 場{jyo_cd}: {count} レース")
    
    conn.close()

def fix_date_selection_issue():
    """日付選択問題の修正"""
    print("\n=== 日付選択問題の修正 ===\n")
    
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    try:
        # 1. 不足しているテーブルの確認と作成
        print("1. 不足しているテーブルの確認")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE '%DATE%'
        """)
        date_tables = cursor.fetchall()
        print(f"日付関連テーブル: {len(date_tables)} 個")
        
        # 2. 日付インデックスの作成
        print("\n2. 日付インデックスの作成")
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_race_date 
                ON N_RACE (Year, MonthDay)
            """)
            print("[OK] レース日付インデックスを作成しました")
        except Exception as e:
            print(f"[ERROR] インデックス作成エラー: {e}")
        
        # 3. 日付ビューの作成
        print("\n3. 日付ビューの作成")
        try:
            cursor.execute("DROP VIEW IF EXISTS v_race_dates")
            cursor.execute("""
                CREATE VIEW v_race_dates AS
                SELECT 
                    Year,
                    MonthDay,
                    Year || MonthDay as RaceDate,
                    COUNT(*) as RaceCount,
                    COUNT(DISTINCT JyoCD) as VenueCount
                FROM N_RACE
                GROUP BY Year, MonthDay
                ORDER BY Year DESC, MonthDay DESC
            """)
            print("[OK] 日付ビューを作成しました")
        except Exception as e:
            print(f"[ERROR] ビュー作成エラー: {e}")
        
        # 4. 日付データの確認
        print("\n4. 日付データの確認")
        cursor.execute("""
            SELECT COUNT(*) FROM v_race_dates
            WHERE Year = '2024' AND MonthDay < '0904'
        """)
        past_dates = cursor.fetchone()[0]
        print(f"2024年9月4日より過去の開催日数: {past_dates} 日")
        
        # 5. サンプル日付データの表示
        print("\n5. サンプル日付データの表示")
        cursor.execute("""
            SELECT 
                Year,
                MonthDay,
                RaceDate,
                RaceCount,
                VenueCount
            FROM v_race_dates
            WHERE Year = '2024' AND MonthDay < '0904'
            ORDER BY MonthDay DESC
            LIMIT 10
        """)
        sample_dates = cursor.fetchall()
        
        print("2024年9月4日より過去のサンプル日付:")
        for year, monthday, race_date, race_count, venue_count in sample_dates:
            date_str = f"{monthday[:2]}月{monthday[2:]}日"
            print(f"  {date_str} ({race_date}): {race_count} レース, {venue_count} 開催場")
        
        conn.commit()
        print("\n[OK] 日付選択問題の修正が完了しました")
        
    except Exception as e:
        print(f"[ERROR] 修正エラー: {e}")
    finally:
        conn.close()

def create_date_fix_sql():
    """日付選択問題修正用SQLファイルの作成"""
    print("\n=== 日付選択問題修正用SQLファイルの作成 ===\n")
    
    sql_content = """
-- 日付選択問題修正用SQL
-- JVMonitorの日付選択問題を解決するためのSQL

-- 1. 日付インデックスの作成
CREATE INDEX IF NOT EXISTS idx_race_date ON N_RACE (Year, MonthDay);
CREATE INDEX IF NOT EXISTS idx_race_date_desc ON N_RACE (Year DESC, MonthDay DESC);

-- 2. 日付ビューの作成
DROP VIEW IF EXISTS v_race_dates;
CREATE VIEW v_race_dates AS
SELECT 
    Year,
    MonthDay,
    Year || MonthDay as RaceDate,
    COUNT(*) as RaceCount,
    COUNT(DISTINCT JyoCD) as VenueCount
FROM N_RACE
GROUP BY Year, MonthDay
ORDER BY Year DESC, MonthDay DESC;

-- 3. 日付選択用ビューの作成
DROP VIEW IF EXISTS v_date_selection;
CREATE VIEW v_date_selection AS
SELECT 
    Year,
    MonthDay,
    Year || MonthDay as RaceDate,
    Year || '/' || MonthDay as DisplayDate,
    COUNT(*) as RaceCount
FROM N_RACE
GROUP BY Year, MonthDay
ORDER BY Year DESC, MonthDay DESC;

-- 4. 過去データ確認用クエリ
SELECT 
    Year,
    MonthDay,
    RaceDate,
    RaceCount
FROM v_date_selection
WHERE Year = '2024' AND MonthDay < '0904'
ORDER BY MonthDay DESC
LIMIT 20;
"""
    
    with open('fix_date_selection.sql', 'w', encoding='utf-8') as f:
        f.write(sql_content)
    
    print("[OK] fix_date_selection.sql ファイルを作成しました")

if __name__ == "__main__":
    check_date_selection_issue()
    fix_date_selection_issue()
    create_date_fix_sql()


