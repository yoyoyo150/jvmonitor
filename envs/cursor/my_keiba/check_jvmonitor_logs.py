# -*- coding: utf-8 -*-
import sqlite3
import sys
import io
import os
from datetime import datetime

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_jvmonitor_logs():
    """JVMonitorのログファイルを確認"""
    print("=== JVMonitorログファイル確認 ===\n")
    
    # 1. JVMonitorのログファイルを探す
    jvmonitor_path = "C:\\my_project_folder\\envs\\cursor\\my_keiba\\JVMonitor\\JVMonitor\\bin\\Debug\\net6.0-windows"
    
    print("1. JVMonitorログファイルの検索")
    log_files = []
    
    if os.path.exists(jvmonitor_path):
        for file in os.listdir(jvmonitor_path):
            if file.endswith(('.log', '.txt')) or 'log' in file.lower():
                log_files.append(file)
                print(f"  発見: {file}")
    
    # 2. debug_log.txtの確認
    debug_log_path = os.path.join(jvmonitor_path, "debug_log.txt")
    if os.path.exists(debug_log_path):
        print(f"\n2. debug_log.txtの内容確認")
        try:
            with open(debug_log_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                print(f"ファイルサイズ: {len(content):,} 文字")
                print(f"行数: {len(content.splitlines()):,} 行")
                
                # 最後の20行を表示
                lines = content.splitlines()
                if len(lines) > 20:
                    print("\n最後の20行:")
                    for line in lines[-20:]:
                        print(f"  {line}")
                else:
                    print("\n全内容:")
                    for line in lines:
                        print(f"  {line}")
        except Exception as e:
            print(f"ファイル読み込みエラー: {e}")
    else:
        print(f"\n2. debug_log.txtが見つかりません: {debug_log_path}")
    
    # 3. その他のログファイルの確認
    print(f"\n3. その他のログファイルの確認")
    for log_file in log_files:
        if log_file != "debug_log.txt":
            log_path = os.path.join(jvmonitor_path, log_file)
            try:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    print(f"\n{log_file} (サイズ: {len(content):,} 文字):")
                    lines = content.splitlines()
                    if len(lines) > 10:
                        print("  最後の10行:")
                        for line in lines[-10:]:
                            print(f"    {line}")
                    else:
                        for line in lines:
                            print(f"    {line}")
            except Exception as e:
                print(f"  {log_file} 読み込みエラー: {e}")

def check_jvmonitor_process():
    """JVMonitorプロセスの確認"""
    print("\n=== JVMonitorプロセス確認 ===\n")
    
    import subprocess
    try:
        # 実行中のJVMonitorプロセスを確認
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq JVMonitor.exe'], 
                               capture_output=True, text=True, encoding='cp932')
        
        if 'JVMonitor.exe' in result.stdout:
            print("JVMonitor.exeが実行中です:")
            print(result.stdout)
        else:
            print("JVMonitor.exeは実行されていません")
            
    except Exception as e:
        print(f"プロセス確認エラー: {e}")

def create_log_viewer():
    """ログビューアーの作成"""
    print("\n=== ログビューアーの作成 ===\n")
    
    viewer_content = '''# -*- coding: utf-8 -*-
import os
import sys
import io
from datetime import datetime

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def view_jvmonitor_logs():
    """JVMonitorのログを表示"""
    jvmonitor_path = "C:\\\\my_project_folder\\\\envs\\\\cursor\\\\my_keiba\\\\JVMonitor\\\\JVMonitor\\\\bin\\\\Debug\\\\net6.0-windows"
    debug_log_path = os.path.join(jvmonitor_path, "debug_log.txt")
    
    if os.path.exists(debug_log_path):
        print("=== JVMonitor debug_log.txt ===")
        try:
            with open(debug_log_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
                
                print(f"ファイルサイズ: {len(content):,} 文字")
                print(f"行数: {len(lines):,} 行")
                print("=" * 50)
                
                # 全内容を表示
                for i, line in enumerate(lines, 1):
                    print(f"{i:4d}: {line}")
                    
        except Exception as e:
            print(f"ファイル読み込みエラー: {e}")
    else:
        print("debug_log.txtが見つかりません")

if __name__ == "__main__":
    view_jvmonitor_logs()
'''
    
    with open('jvmonitor_log_viewer.py', 'w', encoding='utf-8') as f:
        f.write(viewer_content)
    
    print("[OK] jvmonitor_log_viewer.py を作成しました")

if __name__ == "__main__":
    check_jvmonitor_logs()
    check_jvmonitor_process()
    create_log_viewer()


