# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_database_issues():
    """データベースの問題を調査"""
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    print("=== データベース問題調査 ===\n")
    
    # 1. エラーで言及されているテーブルの確認
    print("1. エラーテーブルの確認")
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE '%SE_RACE_UMA%'
    """)
    se_tables = cursor.fetchall()
    print(f"SE_RACE_UMA関連テーブル: {len(se_tables)} 件")
    for table in se_tables:
        print(f"  - {table[0]}")
    
    print("\n" + "="*50 + "\n")
    
    # 2. 速報系テーブルの確認
    print("2. 速報系テーブルの確認")
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE 'S_%'
        ORDER BY name
    """)
    s_tables = cursor.fetchall()
    print(f"速報系テーブル: {len(s_tables)} 件")
    for table in s_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"  - {table[0]}: {count:,} 件")
    
    print("\n" + "="*50 + "\n")
    
    # 3. 最新データの確認
    print("3. 最新データの確認")
    cursor.execute("SELECT MAX(Year || MonthDay) FROM N_RACE")
    latest_race_date = cursor.fetchone()[0]
    print(f"最新レース日: {latest_race_date}")
    
    cursor.execute("SELECT MAX(Year || MonthDay) FROM N_UMA_RACE")
    latest_uma_date = cursor.fetchone()[0]
    print(f"最新出馬日: {latest_uma_date}")
    
    print("\n" + "="*50 + "\n")
    
    # 4. 今日のデータ確認
    print("4. 今日のデータ確認")
    today = "20251007"  # 2025年10月7日
    cursor.execute("SELECT COUNT(*) FROM N_RACE WHERE Year || MonthDay = ?", (today,))
    today_races = cursor.fetchone()[0]
    print(f"今日のレース数: {today_races} 件")
    
    cursor.execute("SELECT COUNT(*) FROM N_UMA_RACE WHERE Year || MonthDay = ?", (today,))
    today_umas = cursor.fetchone()[0]
    print(f"今日の出馬数: {today_umas} 件")
    
    print("\n" + "="*50 + "\n")
    
    # 5. データ更新状況の確認
    print("5. データ更新状況の確認")
    cursor.execute("""
        SELECT Year, COUNT(*) as race_count 
        FROM N_RACE 
        WHERE Year >= '2024'
        GROUP BY Year 
        ORDER BY Year DESC
    """)
    yearly_races = cursor.fetchall()
    print("年別レース数:")
    for year, count in yearly_races:
        print(f"  {year}年: {count:,} レース")
    
    print("\n" + "="*50 + "\n")
    
    # 6. 月別データ確認
    print("6. 2025年10月のデータ確認")
    cursor.execute("""
        SELECT MonthDay, COUNT(*) as race_count 
        FROM N_RACE 
        WHERE Year = '2025' AND MonthDay LIKE '10%'
        GROUP BY MonthDay 
        ORDER BY MonthDay DESC
    """)
    october_races = cursor.fetchall()
    print("2025年10月のレース数:")
    for monthday, count in october_races:
        print(f"  {monthday}: {count:,} レース")
    
    print("\n" + "="*50 + "\n")
    
    # 7. データベースサイズ確認
    print("7. データベースサイズ確認")
    cursor.execute("SELECT COUNT(*) FROM N_RACE")
    total_races = cursor.fetchone()[0]
    print(f"総レース数: {total_races:,} 件")
    
    cursor.execute("SELECT COUNT(*) FROM N_UMA_RACE")
    total_umas = cursor.fetchone()[0]
    print(f"総出馬数: {total_umas:,} 件")
    
    print("\n" + "="*50 + "\n")
    
    # 8. 推奨解決策
    print("8. 推奨解決策")
    print("出馬表が増えない原因:")
    print("1. 速報系テーブル(S_*)にデータが0件")
    print("2. 最新データの取得に失敗")
    print("3. データベーステーブルの不整合")
    print("\n解決方法:")
    print("1. EveryDB2.3でデータを再ダウンロード")
    print("2. JVMonitorの設定を確認")
    print("3. データベースの整合性チェック")
    
    conn.close()

if __name__ == "__main__":
    check_database_issues()


