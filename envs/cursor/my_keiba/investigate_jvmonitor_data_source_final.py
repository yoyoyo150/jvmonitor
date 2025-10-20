import sqlite3
import os

def investigate_jvmonitor_data_source_final():
    """JVMonitorのデータソースを最終的に特定"""
    
    print("=== JVMonitorのデータソース最終調査 ===")
    
    # 1. ecore.dbの全テーブル確認
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
    
    # 2. ナムラクレアのデータを各Mark関連テーブルで検索
    print("\n2. ナムラクレアのデータ検索:")
    for table_name, columns in mark_tables:
        try:
            # 馬名カラムを推測
            name_columns = [col for col in columns if 'name' in col.lower() or 'horse' in col.lower() or 'bamei' in col.lower()]
            if name_columns:
                name_col = name_columns[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {name_col} LIKE '%ナムラクレア%'")
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"  {table_name}: {count}件のデータ発見")
                    
                    # サンプルデータを表示
                    cursor.execute(f"""
                        SELECT *
                        FROM {table_name}
                        WHERE {name_col} LIKE '%ナムラクレア%'
                        LIMIT 3
                    """)
                    sample_data = cursor.fetchall()
                    print(f"    サンプルデータ:")
                    for i, row in enumerate(sample_data):
                        print(f"      レコード{i+1}: {row[:5]}...")  # 最初の5カラムのみ表示
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
    
    # 4. 他のデータベースファイル確認
    print("\n4. 他のデータベースファイル:")
    db_files = ['excel_data.db', 'integrated_horse_system.db']
    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"  {db_file}: 存在")
            try:
                conn2 = sqlite3.connect(db_file)
                cursor2 = conn2.cursor()
                cursor2.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables2 = cursor2.fetchall()
                print(f"    テーブル数: {len(tables2)}")
                
                # Mark関連テーブルを探す
                for table in tables2:
                    table_name = table[0]
                    cursor2.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor2.fetchall()
                    column_names = [col[1] for col in columns]
                    
                    if any('Mark' in col or 'ZI' in col or 'ZM' in col for col in column_names):
                        print(f"    Mark関連テーブル: {table_name}")
            except Exception as e:
                print(f"    エラー: {e}")
        else:
            print(f"  {db_file}: 存在しない")
    
    conn.close()
    
    print("\n=== 結論 ===")
    print("JVMonitorのMark5/Mark6データソースを特定する必要があります。")
    print("可能性:")
    print("1. 別のデータベースファイル")
    print("2. 外部ファイル（CSV、JSON等）")
    print("3. 計算で生成")
    print("4. ネットワーク経由で取得")

if __name__ == "__main__":
    investigate_jvmonitor_data_source_final()




