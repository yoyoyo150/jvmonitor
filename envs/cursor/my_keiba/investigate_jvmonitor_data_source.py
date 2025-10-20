import sqlite3
import os
import glob

def investigate_jvmonitor_data_source():
    """JVMonitorのデータソースを徹底調査"""
    
    print("=== JVMonitorのデータソース調査 ===")
    
    # 1. プロジェクト内の全データベースファイルを確認
    print("\n1. プロジェクト内のデータベースファイル:")
    db_files = glob.glob("*.db")
    for db_file in db_files:
        size = os.path.getsize(db_file) / (1024*1024)  # MB
        print(f"  {db_file}: {size:.1f}MB")
    
    # 2. excel_data.dbの詳細確認
    print("\n2. excel_data.dbの詳細:")
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS")
    total_count = cursor.fetchone()[0]
    print(f"  総レコード数: {total_count:,}件")
    
    # ナムラクレアのデータ確認
    cursor.execute("""
        SELECT SourceDate, COUNT(*) as count
        FROM HORSE_MARKS 
        WHERE HorseName = 'ナムラクレア'
        GROUP BY SourceDate 
        ORDER BY SourceDate DESC
        LIMIT 5
    """)
    
    print("  ナムラクレアのデータ（最新5日）:")
    for row in cursor.fetchall():
        print(f"    {row[0]}: {row[1]}件")
    
    conn.close()
    
    # 3. JVMonitorが参照する可能性のあるデータベースを確認
    print("\n3. JVMonitor関連データベース:")
    
    # ecore.dbの確認
    if os.path.exists('ecore.db'):
        conn_ecore = sqlite3.connect('ecore.db')
        cursor_ecore = conn_ecore.cursor()
        
        cursor_ecore.execute("SELECT COUNT(*) FROM N_UMA_RACE WHERE Bamei LIKE '%ナムラクレア%'")
        count = cursor_ecore.fetchone()[0]
        print(f"  ecore.db内のナムラクレアレコード数: {count}")
        
        # N_UMA_RACEテーブルの構造確認
        cursor_ecore.execute("PRAGMA table_info(N_UMA_RACE)")
        columns = cursor_ecore.fetchall()
        mark_columns = [col for col in columns if 'Mark' in col[1] or 'ZI' in col[1]]
        print(f"  N_UMA_RACEのMark関連カラム: {[col[1] for col in mark_columns]}")
        
        conn_ecore.close()
    
    # 4. JVMonitorの設定ファイル確認
    print("\n4. JVMonitor設定ファイル:")
    config_files = glob.glob("**/*.json", recursive=True)
    for config_file in config_files:
        print(f"  {config_file}")
    
    # 5. 推奨解決策
    print("\n=== 推奨解決策 ===")
    print("1. JVMonitorがexcel_data.dbを参照していない可能性")
    print("2. JVMonitorの設定でデータベースパスを確認")
    print("3. 必要に応じて、excel_data.dbのデータをecore.dbに統合")

if __name__ == "__main__":
    investigate_jvmonitor_data_source()




