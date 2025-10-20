import sqlite3
import os

def check_jvmonitor_actual_data_source():
    """JVMonitorの実際のデータソースを確認"""
    
    print("=== JVMonitorの実際のデータソース確認 ===")
    
    # 1. excel_data.dbのHORSE_MARKSテーブル確認
    print("\n1. excel_data.dbのHORSE_MARKSテーブル:")
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS")
    count = cursor.fetchone()[0]
    print(f"HORSE_MARKSレコード数: {count:,}")
    
    # ナムラクレアのデータ確認
    cursor.execute("""
        SELECT SourceDate, HorseName, Mark5, Mark6, ZI_INDEX, ZM_VALUE
        FROM HORSE_MARKS
        WHERE HorseName LIKE '%ナムラクレア%'
        ORDER BY SourceDate DESC
        LIMIT 10
    """)
    
    data = cursor.fetchall()
    print(f"ナムラクレアのデータ: {len(data)}件")
    
    if data:
        print("SourceDate | HorseName | Mark5 | Mark6 | ZI_INDEX | ZM_VALUE")
        print("------------------------------------------------------------")
        for row in data:
            print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}")
    
    # 2. JVMonitorの設定ファイル確認
    print("\n2. JVMonitorの設定ファイル:")
    config_files = [
        'JVMonitor/JVMonitor/appsettings.json',
        'JVMonitor/JVMonitor/bin/Debug/net6.0-windows/appsettings.json'
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"  {config_file}: 存在")
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"    内容: {content[:200]}...")
        else:
            print(f"  {config_file}: 存在しない")
    
    # 3. JVMonitorの実行ファイル確認
    print("\n3. JVMonitorの実行ファイル:")
    jvmonitor_exe = "JVMonitor/JVMonitor/bin/Debug/net6.0-windows/JVMonitor.exe"
    if os.path.exists(jvmonitor_exe):
        print(f"  {jvmonitor_exe}: 存在")
        print(f"    ファイルサイズ: {os.path.getsize(jvmonitor_exe):,} bytes")
    else:
        print(f"  {jvmonitor_exe}: 存在しない")
    
    # 4. プロセス確認
    print("\n4. 実行中のJVMonitorプロセス:")
    import subprocess
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq JVMonitor.exe'], 
                              capture_output=True, text=True)
        if 'JVMonitor.exe' in result.stdout:
            print("  JVMonitor.exeが実行中")
        else:
            print("  JVMonitor.exeは実行されていない")
    except Exception as e:
        print(f"  プロセス確認エラー: {e}")
    
    conn.close()
    
    print("\n=== 結論 ===")
    print("JVMonitorが表示しているMark5/Mark6データは:")
    print("1. excel_data.dbのHORSE_MARKSテーブルから取得している可能性")
    print("2. または、別のソースから取得している可能性")
    print("3. JVMonitorの設定ファイルでデータソースを確認する必要がある")

if __name__ == "__main__":
    check_jvmonitor_actual_data_source()




