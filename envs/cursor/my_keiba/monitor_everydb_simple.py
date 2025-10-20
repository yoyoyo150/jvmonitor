#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EveryDB2.3監視スクリプト
"""
import time
import os
import sqlite3

def monitor_everydb():
    db_file = "ecore.db"
    last_size = 0
    
    while True:
        if os.path.exists(db_file):
            current_size = os.path.getsize(db_file)
            if current_size != last_size:
                print(f"{time.strftime('%H:%M:%S')} - データベース更新中: {current_size:,} bytes")
                last_size = current_size
            else:
                print(f"{time.strftime('%H:%M:%S')} - 待機中...")
        else:
            print(f"{time.strftime('%H:%M:%S')} - データベースファイルが見つかりません")
        
        time.sleep(10)  # 10秒間隔で監視

if __name__ == "__main__":
    monitor_everydb()
