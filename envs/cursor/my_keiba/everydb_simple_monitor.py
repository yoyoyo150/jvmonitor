#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EveryDB2.3 Simple Monitor
シンプルな監視スクリプト（psutil不要版）
"""

import os
import subprocess
import time
import sqlite3
from datetime import datetime

def check_database_progress():
    """データベースの進捗を確認"""
    db_path = r"C:\my_project_folder\envs\cursor\my_keiba\ecore.db"
    
    try:
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 馬数の確認
            cursor.execute("SELECT COUNT(*) FROM N_UMA;")
            horse_count = cursor.fetchone()[0]
            
            # レース数の確認
            cursor.execute("SELECT COUNT(*) FROM N_UMA_RACE;")
            race_count = cursor.fetchone()[0]
            
            # ファイルサイズの確認
            file_size = os.path.getsize(db_path)
            
            conn.close()
            
            return {
                'horse_count': horse_count,
                'race_count': race_count,
                'file_size': file_size,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    except Exception as e:
        return {'error': str(e), 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    return None

def restart_everydb():
    """EveryDB2.3を再起動"""
    everydb_path = r"J:\new program file\everydb230\everydb230\Application Files\EveryDB2.3_2_3_0_0\EveryDB2.3.exe"
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] EveryDB2.3を再起動中...")
    
    # 既存のプロセスを終了
    try:
        subprocess.run(['taskkill', '/IM', 'EveryDB2.3.exe', '/F'], 
                      capture_output=True, text=True)
        print("既存のEveryDB2.3プロセスを終了しました")
    except Exception as e:
        print(f"プロセス終了エラー: {e}")
    
    # 少し待機
    time.sleep(5)
    
    # 新しいプロセスを開始
    try:
        subprocess.Popen(
            [everydb_path],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        print("EveryDB2.3を再起動しました")
        return True
    except Exception as e:
        print(f"再起動エラー: {e}")
        return False

def simple_monitor():
    """シンプルな監視"""
    print("=== EveryDB2.3 Simple Monitor ===")
    print("データベースの進捗を監視します")
    print("画面が消えても処理は継続されます")
    print()
    
    last_horse_count = 0
    last_race_count = 0
    last_file_size = 0
    no_progress_count = 0
    max_no_progress = 5  # 5回連続で進捗がない場合は再起動
    
    while True:
        try:
            # 進捗確認
            progress = check_database_progress()
            
            if progress and 'error' not in progress:
                current_horse_count = progress['horse_count']
                current_race_count = progress['race_count']
                current_file_size = progress['file_size']
                
                # 進捗があったかチェック
                if (current_horse_count > last_horse_count or 
                    current_race_count > last_race_count or 
                    current_file_size > last_file_size):
                    
                    print(f"[{progress['timestamp']}] 進捗更新:")
                    print(f"  馬数: {current_horse_count:,}頭 (前回: {last_horse_count:,})")
                    print(f"  レース数: {current_race_count:,}件 (前回: {last_race_count:,})")
                    print(f"  ファイルサイズ: {current_file_size:,} bytes (前回: {last_file_size:,})")
                    print()
                    
                    last_horse_count = current_horse_count
                    last_race_count = current_race_count
                    last_file_size = current_file_size
                    no_progress_count = 0
                else:
                    no_progress_count += 1
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 進捗なし ({no_progress_count}/{max_no_progress})")
                    
                    if no_progress_count >= max_no_progress:
                        print("進捗がありません。EveryDB2.3を再起動します。")
                        if restart_everydb():
                            no_progress_count = 0
                            time.sleep(30)  # 再起動後は少し長めに待機
                            continue
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] データベース確認エラー")
                no_progress_count += 1
            
            # 60秒待機
            time.sleep(60)
            
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 停止要求を受信しました")
            break
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] エラー: {e}")
            time.sleep(10)
    
    print("監視を終了しました")

if __name__ == "__main__":
    simple_monitor()


