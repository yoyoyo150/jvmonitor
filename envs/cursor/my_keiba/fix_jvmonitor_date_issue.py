# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def fix_jvmonitor_date_issue():
    """JVMonitorの日付選択問題を修正"""
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    print("=== JVMonitor日付選択問題修正 ===\n")
    
    try:
        # 1. 日付選択用テーブルの作成
        print("1. 日付選択用テーブルの作成")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS DateSelection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Year VARCHAR(4),
                MonthDay VARCHAR(4),
                RaceDate VARCHAR(8),
                DisplayDate VARCHAR(10),
                RaceCount INTEGER,
                VenueCount INTEGER,
                CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[OK] DateSelectionテーブルを作成しました")
        
        # 2. 既存データのクリア
        print("\n2. 既存データのクリア")
        cursor.execute("DELETE FROM DateSelection")
        print("[OK] 既存データをクリアしました")
        
        # 3. 日付データの挿入
        print("\n3. 日付データの挿入")
        cursor.execute("""
            INSERT INTO DateSelection (Year, MonthDay, RaceDate, DisplayDate, RaceCount, VenueCount)
            SELECT 
                Year,
                MonthDay,
                Year || MonthDay as RaceDate,
                Year || '/' || MonthDay as DisplayDate,
                COUNT(*) as RaceCount,
                COUNT(DISTINCT JyoCD) as VenueCount
            FROM N_RACE
            GROUP BY Year, MonthDay
            ORDER BY Year DESC, MonthDay DESC
        """)
        
        inserted_count = cursor.rowcount
        print(f"[OK] {inserted_count:,} 件の日付データを挿入しました")
        
        # 4. インデックスの作成
        print("\n4. インデックスの作成")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_date_selection_date ON DateSelection (Year, MonthDay)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_date_selection_race_date ON DateSelection (RaceDate)")
        print("[OK] インデックスを作成しました")
        
        # 5. 2024年9月4日より過去のデータ確認
        print("\n5. 2024年9月4日より過去のデータ確認")
        cursor.execute("""
            SELECT COUNT(*) FROM DateSelection
            WHERE Year = '2024' AND MonthDay < '0904'
        """)
        past_count = cursor.fetchone()[0]
        print(f"2024年9月4日より過去の開催日数: {past_count} 日")
        
        # 6. サンプルデータの表示
        print("\n6. サンプルデータの表示")
        cursor.execute("""
            SELECT 
                Year,
                MonthDay,
                DisplayDate,
                RaceCount,
                VenueCount
            FROM DateSelection
            WHERE Year = '2024' AND MonthDay < '0904'
            ORDER BY MonthDay DESC
            LIMIT 10
        """)
        sample_data = cursor.fetchall()
        
        print("2024年9月4日より過去のサンプルデータ:")
        for year, monthday, display_date, race_count, venue_count in sample_data:
            print(f"  {display_date}: {race_count} レース, {venue_count} 開催場")
        
        # 7. 全データの確認
        print("\n7. 全データの確認")
        cursor.execute("SELECT COUNT(*) FROM DateSelection")
        total_count = cursor.fetchone()[0]
        print(f"総開催日数: {total_count:,} 日")
        
        cursor.execute("SELECT MIN(RaceDate), MAX(RaceDate) FROM DateSelection")
        date_range = cursor.fetchone()
        print(f"データ範囲: {date_range[0]} ～ {date_range[1]}")
        
        conn.commit()
        print("\n[OK] JVMonitor日付選択問題の修正が完了しました")
        
    except Exception as e:
        print(f"[ERROR] 修正エラー: {e}")
        conn.rollback()
    finally:
        conn.close()

def create_jvmonitor_fix_sql():
    """JVMonitor修正用SQLファイルの作成"""
    print("\n=== JVMonitor修正用SQLファイルの作成 ===\n")
    
    sql_content = """
-- JVMonitor日付選択問題修正用SQL
-- 2024年9月4日より過去の日付が選択できない問題を解決

-- 1. 日付選択用テーブルの作成
CREATE TABLE IF NOT EXISTS DateSelection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Year VARCHAR(4),
    MonthDay VARCHAR(4),
    RaceDate VARCHAR(8),
    DisplayDate VARCHAR(10),
    RaceCount INTEGER,
    VenueCount INTEGER,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. 既存データのクリア
DELETE FROM DateSelection;

-- 3. 日付データの挿入
INSERT INTO DateSelection (Year, MonthDay, RaceDate, DisplayDate, RaceCount, VenueCount)
SELECT 
    Year,
    MonthDay,
    Year || MonthDay as RaceDate,
    Year || '/' || MonthDay as DisplayDate,
    COUNT(*) as RaceCount,
    COUNT(DISTINCT JyoCD) as VenueCount
FROM N_RACE
GROUP BY Year, MonthDay
ORDER BY Year DESC, MonthDay DESC;

-- 4. インデックスの作成
CREATE INDEX IF NOT EXISTS idx_date_selection_date ON DateSelection (Year, MonthDay);
CREATE INDEX IF NOT EXISTS idx_date_selection_race_date ON DateSelection (RaceDate);

-- 5. 2024年9月4日より過去のデータ確認
SELECT 
    Year,
    MonthDay,
    DisplayDate,
    RaceCount,
    VenueCount
FROM DateSelection
WHERE Year = '2024' AND MonthDay < '0904'
ORDER BY MonthDay DESC
LIMIT 20;

-- 6. 全データの確認
SELECT COUNT(*) as TotalDays FROM DateSelection;
SELECT MIN(RaceDate) as EarliestDate, MAX(RaceDate) as LatestDate FROM DateSelection;
"""
    
    with open('jvmonitor_date_fix.sql', 'w', encoding='utf-8') as f:
        f.write(sql_content)
    
    print("[OK] jvmonitor_date_fix.sql ファイルを作成しました")

if __name__ == "__main__":
    fix_jvmonitor_date_issue()
    create_jvmonitor_fix_sql()


