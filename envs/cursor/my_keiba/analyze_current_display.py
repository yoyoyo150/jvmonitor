import sqlite3
import os

def analyze_current_display():
    """現在JVMonitorに表示されているデータの正確な分析"""
    
    print("=== 現在の表示データの分析 ===")
    
    # 1. ecore.dbのN_UMA_RACEテーブル構造確認
    print("\n1. N_UMA_RACEテーブルの構造:")
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(N_UMA_RACE)")
    columns = cursor.fetchall()
    
    # Mark関連カラムを特定
    mark_columns = []
    for col in columns:
        if 'Mark' in col[1] or 'ZI' in col[1] or 'ZM' in col[1]:
            mark_columns.append((col[1], col[2]))
    
    print(f"Mark関連カラム: {mark_columns}")
    
    # 2. ナムラクレアの実際のデータ確認
    print("\n2. ナムラクレアの実際のデータ:")
    cursor.execute("""
        SELECT Kaiji, Nichiji, RaceNum, Bamei, 
               CASE WHEN EXISTS(SELECT 1 FROM pragma_table_info('N_UMA_RACE') WHERE name='Mark5') 
                    THEN Mark5 ELSE 'カラムなし' END as Mark5,
               CASE WHEN EXISTS(SELECT 1 FROM pragma_table_info('N_UMA_RACE') WHERE name='Mark6') 
                    THEN Mark6 ELSE 'カラムなし' END as Mark6
        FROM N_UMA_RACE
        WHERE Bamei LIKE '%ナムラクレア%'
        ORDER BY Kaiji DESC, Nichiji DESC, RaceNum DESC
        LIMIT 5
    """)
    
    data = cursor.fetchall()
    for row in data:
        print(f"  {row[0]}/{row[1]} R{row[2]} | {row[3]} | M5:{row[4]} | M6:{row[5]}")
    
    # 3. 現在表示されているMark5/Mark6の値の確認
    print("\n3. 現在表示されているMark5/Mark6の値:")
    
    # 最新3レースのMark5/Mark6値を確認
    cursor.execute("""
        SELECT Kaiji, Nichiji, RaceNum, Bamei
        FROM N_UMA_RACE
        WHERE Bamei LIKE '%ナムラクレア%'
        ORDER BY Kaiji DESC, Nichiji DESC, RaceNum DESC
        LIMIT 3
    """)
    
    recent_races = cursor.fetchall()
    print("最新3レース:")
    for row in recent_races:
        print(f"  {row[0]}/{row[1]} R{row[2]} | {row[3]}")
    
    # 4. データソースの特定
    print("\n4. データソースの特定:")
    print("JVMonitorが表示しているMark5/Mark6データは:")
    print("- N_UMA_RACEテーブル内の既存カラムか")
    print("- 別のテーブルから取得しているか")
    print("- 計算で生成されているか")
    print("- 外部ファイルから読み込んでいるか")
    
    conn.close()
    
    print("\n=== 安全な確認手順 ===")
    print("1. 現在の表示データの正確なソースを特定")
    print("2. データベース構造を変更せずに調査")
    print("3. バックアップを取ってから慎重に検証")

if __name__ == "__main__":
    analyze_current_display()




