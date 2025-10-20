import sqlite3
import os

def fix_jvmonitor_mark_display():
    """JVMonitorのMark5/Mark6表示を修正"""
    
    print("=== JVMonitorのMark5/Mark6表示修正 ===")
    
    # 1. excel_data.dbのデータ確認
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    # ナムラクレアの全データを確認
    cursor.execute("""
        SELECT SourceDate, HorseName, Mark5, Mark6, ZI_INDEX
        FROM HORSE_MARKS
        WHERE HorseName = 'ナムラクレア'
        ORDER BY SourceDate DESC
        LIMIT 10
    """)
    
    data = cursor.fetchall()
    print("excel_data.db内のデータ:")
    for row in data:
        print(f"  {row[0]} | {row[1]} | M5:{row[2]} | M6:{row[3]} | ZI:{row[4]}")
    
    # 2. JVMonitorが使用する可能性のあるテーブルを確認
    print("\n=== JVMonitor関連テーブルの確認 ===")
    
    # ecore.dbの確認
    if os.path.exists('ecore.db'):
        print("ecore.dbが存在します")
        conn_ecore = sqlite3.connect('ecore.db')
        cursor_ecore = conn_ecore.cursor()
        
        # テーブル一覧
        cursor_ecore.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor_ecore.fetchall()
        print(f"ecore.dbのテーブル数: {len(tables)}")
        
        # N_UMA_RACEテーブルでナムラクレアを検索
        cursor_ecore.execute("""
            SELECT COUNT(*) FROM N_UMA_RACE 
            WHERE Bamei LIKE '%ナムラクレア%'
        """)
        count = cursor_ecore.fetchone()[0]
        print(f"ecore.db内のナムラクレアレコード数: {count}")
        
        conn_ecore.close()
    
    # 3. データ統合の提案
    print("\n=== 修正提案 ===")
    print("1. JVMonitorがMark5/Mark6データを正しく読み込めていない")
    print("2. excel_data.dbとecore.dbの連携が必要")
    print("3. JVMonitorのデータ更新機能を再実行")
    
    conn.close()

if __name__ == "__main__":
    fix_jvmonitor_mark_display()




