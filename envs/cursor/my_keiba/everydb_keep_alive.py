#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EveryDB2.3 Keep Alive Script
画面が消えても継続実行を保証するスクリプト
"""

import os
import subprocess
import time
import psutil
import sqlite3
from datetime import datetime

class EveryDBKeepAlive:
    def __init__(self):
        self.everydb_path = r"J:\new program file\everydb230\everydb230\Application Files\EveryDB2.3_2_3_0_0\EveryDB2.3.exe"
        self.db_path = r"C:\my_project_folder\envs\cursor\my_keiba\ecore.db"
        self.check_interval = 60  # 1分間隔でチェック
        self.last_progress = None
        
    def get_everydb_processes(self):
        """EveryDB2.3のプロセスを取得"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'EveryDB' in proc.info['name'] or 'everydb' in proc.info['name'].lower():
                    processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes
    
    def check_database_progress(self):
        """データベースの進捗を確認"""
        try:
            if os.path.exists(self.db_path):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 馬数の確認
                cursor.execute("SELECT COUNT(*) FROM N_UMA;")
                horse_count = cursor.fetchone()[0]
                
                # レース数の確認
                cursor.execute("SELECT COUNT(*) FROM N_UMA_RACE;")
                race_count = cursor.fetchone()[0]
                
                # ファイルサイズの確認
                file_size = os.path.getsize(self.db_path)
                
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
    
    def is_progress_made(self, current_progress):
        """進捗があったかチェック"""
        if not self.last_progress:
            return True
        
        if 'error' in current_progress or 'error' in self.last_progress:
            return False
        
        # 馬数、レース数、ファイルサイズのいずれかが増加
        return (current_progress['horse_count'] > self.last_progress['horse_count'] or
                current_progress['race_count'] > self.last_progress['race_count'] or
                current_progress['file_size'] > self.last_progress['file_size'])
    
    def restart_everydb(self):
        """EveryDB2.3を再起動"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] EveryDB2.3を再起動中...")
        
        # 既存のプロセスを終了
        processes = self.get_everydb_processes()
        for proc in processes:
            try:
                proc.terminate()
                print(f"プロセス {proc.info['pid']} を終了しました")
            except Exception as e:
                print(f"プロセス終了エラー: {e}")
        
        # 少し待機
        time.sleep(5)
        
        # 新しいプロセスを開始
        try:
            subprocess.Popen(
                [self.everydb_path],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            print("EveryDB2.3を再起動しました")
            return True
        except Exception as e:
            print(f"再起動エラー: {e}")
            return False
    
    def run_keep_alive(self):
        """Keep Alive実行"""
        print("=== EveryDB2.3 Keep Alive ===")
        print("画面が消えても継続実行を保証します")
        print(f"チェック間隔: {self.check_interval}秒")
        print()
        
        consecutive_no_progress = 0
        max_no_progress = 3  # 3回連続で進捗がない場合は再起動
        
        while True:
            try:
                # プロセス確認
                processes = self.get_everydb_processes()
                if not processes:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] EveryDB2.3プロセスが見つかりません。再起動します。")
                    if self.restart_everydb():
                        consecutive_no_progress = 0
                        time.sleep(30)  # 再起動後は少し長めに待機
                        continue
                    else:
                        print("再起動に失敗しました。10秒後に再試行します。")
                        time.sleep(10)
                        continue
                
                # 進捗確認
                current_progress = self.check_database_progress()
                if current_progress and 'error' not in current_progress:
                    if self.is_progress_made(current_progress):
                        print(f"[{current_progress['timestamp']}] 進捗確認:")
                        print(f"  馬数: {current_progress['horse_count']:,}頭")
                        print(f"  レース数: {current_progress['race_count']:,}件")
                        print(f"  ファイルサイズ: {current_progress['file_size']:,} bytes")
                        print()
                        
                        consecutive_no_progress = 0
                        self.last_progress = current_progress
                    else:
                        consecutive_no_progress += 1
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 進捗なし ({consecutive_no_progress}/{max_no_progress})")
                        
                        if consecutive_no_progress >= max_no_progress:
                            print("進捗がありません。EveryDB2.3を再起動します。")
                            if self.restart_everydb():
                                consecutive_no_progress = 0
                                time.sleep(30)
                                continue
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] データベース確認エラー")
                    consecutive_no_progress += 1
                
                # 待機
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 停止要求を受信しました")
                break
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] エラー: {e}")
                time.sleep(10)
        
        print("Keep Aliveを終了しました")

def main():
    """メイン実行"""
    keep_alive = EveryDBKeepAlive()
    keep_alive.run_keep_alive()

if __name__ == "__main__":
    main()


