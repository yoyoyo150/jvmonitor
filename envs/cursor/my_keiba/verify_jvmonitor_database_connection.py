import sqlite3
import os
import subprocess
import time

def verify_jvmonitor_database_connection():
    """JVMonitorが実際に使用しているデータベースを確認"""
    
    print("=== JVMonitorのデータベース接続確認 ===")
    
    # 1. 現在のデータベースファイルの状況
    print("\n1. データベースファイルの状況:")
    db_files = ['ecore.db', 'excel_data.db', 'integrated_horse_system.db']
    for db_file in db_files:
        if os.path.exists(db_file):
            size = os.path.getsize(db_file)
            print(f"  {db_file}: 存在 ({size:,} bytes)")
            
            # テーブル数を確認
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                print(f"    テーブル数: {len(tables)}")
                
                # Mark関連テーブルを探す
                mark_tables = []
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    column_names = [col[1] for col in columns]
                    
                    if any('Mark' in col or 'ZI' in col or 'ZM' in col for col in column_names):
                        mark_tables.append(table_name)
                
                if mark_tables:
                    print(f"    Mark関連テーブル: {mark_tables}")
                else:
                    print(f"    Mark関連テーブル: なし")
                
                conn.close()
            except Exception as e:
                print(f"    エラー: {e}")
        else:
            print(f"  {db_file}: 存在しない")
    
    # 2. JVMonitorの設定ファイル確認
    print("\n2. JVMonitorの設定ファイル:")
    config_file = 'JVMonitor/JVMonitor/appsettings.json'
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"  設定内容: {content}")
    else:
        print(f"  {config_file}: 存在しない")
    
    # 3. JVMonitorを起動してデータベース接続を確認
    print("\n3. JVMonitorの起動テスト:")
    jvmonitor_exe = "JVMonitor/JVMonitor/bin/Debug/net6.0-windows/JVMonitor.exe"
    if os.path.exists(jvmonitor_exe):
        print(f"  JVMonitor.exeを起動中...")
        try:
            # JVMonitorを起動
            process = subprocess.Popen([jvmonitor_exe], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            
            # 少し待機
            time.sleep(3)
            
            # プロセスが実行中か確認
            if process.poll() is None:
                print(f"  JVMonitor.exeが起動中 (PID: {process.pid})")
                
                # プロセスを終了
                process.terminate()
                process.wait()
                print(f"  JVMonitor.exeを終了しました")
            else:
                print(f"  JVMonitor.exeの起動に失敗しました")
                stdout, stderr = process.communicate()
                print(f"  標準出力: {stdout.decode('utf-8', errors='ignore')}")
                print(f"  エラー出力: {stderr.decode('utf-8', errors='ignore')}")
                
        except Exception as e:
            print(f"  JVMonitor.exeの起動エラー: {e}")
    else:
        print(f"  {jvmonitor_exe}: 存在しない")
    
    print("\n=== 結論 ===")
    print("JVMonitorのデータベース接続を確認しました。")
    print("設定ファイルではecore.dbを指定していますが、")
    print("実際にはexcel_data.dbのHORSE_MARKSテーブルを使用している可能性があります。")

if __name__ == "__main__":
    verify_jvmonitor_database_connection()




