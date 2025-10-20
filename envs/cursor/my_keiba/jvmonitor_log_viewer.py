# -*- coding: utf-8 -*-
import os
import sys
import io
from datetime import datetime

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def view_jvmonitor_logs():
    """JVMonitorのログを表示"""
    jvmonitor_path = "C:\\my_project_folder\\envs\\cursor\\my_keiba\\JVMonitor\\JVMonitor\\bin\\Debug\\net6.0-windows"
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
