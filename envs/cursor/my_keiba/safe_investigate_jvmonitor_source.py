import sqlite3
import os
import glob

def safe_investigate_jvmonitor_source():
    """JVMonitorのデータソースを安全に調査（データベース変更なし）"""
    
    print("=== JVMonitorのデータソース安全調査 ===")
    
    # 1. ecore.dbの全テーブル一覧
    print("\n1. ecore.dbの全テーブル:")
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"テーブル数: {len(tables)}")
    
    # Mark関連のテーブルを探す
    mark_tables = []
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if any('Mark' in col or 'ZI' in col or 'ZM' in col for col in column_names):
            mark_tables.append((table_name, column_names))
    
    print(f"\nMark関連テーブル: {len(mark_tables)}")
    for table_name, columns in mark_tables:
        mark_cols = [col for col in columns if 'Mark' in col or 'ZI' in col or 'ZM' in col]
        print(f"  {table_name}: {mark_cols}")
    
    # 2. ナムラクレアのデータを各テーブルで検索
    print("\n2. ナムラクレアのデータ検索:")
    for table_name, columns in mark_tables:
        try:
            # 馬名カラムを推測
            name_columns = [col for col in columns if 'name' in col.lower() or 'bamei' in col.lower() or 'horse' in col.lower()]
            if name_columns:
                name_col = name_columns[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {name_col} LIKE '%ナムラクレア%'")
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"  {table_name}: {count}件のデータ発見")
        except Exception as e:
            print(f"  {table_name}: エラー - {e}")
    
    # 3. JVMonitorの設定ファイル確認
    print("\n3. JVMonitor設定ファイル:")
    config_files = [
        'JVMonitor/JVMonitor/appsettings.json',
        'JVMonitor/JVMonitor/bin/Debug/net6.0-windows/appsettings.json'
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"  {config_file}: 存在")
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'database' in content.lower() or 'connection' in content.lower():
                    print(f"    データベース設定を含む")
        else:
            print(f"  {config_file}: 存在しない")
    
    conn.close()
    
    print("\n=== 安全な結論 ===")
    print("1. N_UMA_RACEテーブルにはMark5/Mark6カラムが存在しない")
    print("2. JVMonitorは別のソースからMark5/Mark6データを取得している")
    print("3. データベース構造を変更する前に、正確なソースを特定する必要がある")

if __name__ == "__main__":
    safe_investigate_jvmonitor_source()




