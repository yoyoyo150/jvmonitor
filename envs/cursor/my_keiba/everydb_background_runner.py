#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EveryDB2.3 Background Runner
画面が消えても継続実行するスクリプト
"""

import os
import subprocess
import time
import sqlite3
import threading
from datetime import datetime

class EveryDBBackgroundRunner:
    def __init__(self):
        self.everydb_path = r"J:\new program file\everydb230\everydb230\Application Files\EveryDB2.3_2_3_0_0\EveryDB2.3.exe"
        self.db_path = r"C:\my_project_folder\envs\cursor\my_keiba\ecore.db"
        self.is_running = False
        self.process = None
        self.monitor_thread = None
        
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
                
                # 最新の更新日時を確認
                cursor.execute("SELECT MAX(UpdatedAt) FROM N_UMA_RACE WHERE UpdatedAt IS NOT NULL;")
                latest_update = cursor.fetchone()[0]
                
                conn.close()
                
                return {
                    'horse_count': horse_count,
                    'race_count': race_count,
                    'latest_update': latest_update,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().strftime('%H:%M:%S')}
        
        return None
    
    def monitor_progress(self):
        """進捗を監視するスレッド"""
        last_horse_count = 0
        last_race_count = 0
        
        while self.is_running:
            try:
                progress = self.check_database_progress()
                if progress and 'error' not in progress:
                    current_horse_count = progress['horse_count']
                    current_race_count = progress['race_count']
                    
                    # 変化があった場合のみ表示
                    if (current_horse_count != last_horse_count or 
                        current_race_count != last_race_count):
                        
                        print(f"[{progress['timestamp']}] 進捗更新:")
                        print(f"  馬数: {current_horse_count:,}頭")
                        print(f"  レース数: {current_race_count:,}件")
                        if progress['latest_update']:
                            print(f"  最新更新: {progress['latest_update']}")
                        print()
                        
                        last_horse_count = current_horse_count
                        last_race_count = current_race_count
                    else:
                        print(f"[{progress['timestamp']}] 待機中...")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] データベース確認中...")
                
                time.sleep(30)  # 30秒間隔で監視
                
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 監視エラー: {e}")
                time.sleep(30)
    
    def start_everydb_background(self):
        """EveryDB2.3をバックグラウンドで開始"""
        print("=== EveryDB2.3 Background Runner ===")
        print("画面が消えても継続実行します")
        print()
        
        # 1. 現在の状況確認
        print("1. 現在の状況確認")
        print("=" * 50)
        
        progress = self.check_database_progress()
        if progress and 'error' not in progress:
            print(f"現在の馬数: {progress['horse_count']:,}頭")
            print(f"現在のレース数: {progress['race_count']:,}件")
            if progress['latest_update']:
                print(f"最新更新: {progress['latest_update']}")
        else:
            print("データベース確認エラー")
        
        # 2. EveryDB2.3の実行
        print(f"\n2. EveryDB2.3実行")
        print("=" * 50)
        
        if not os.path.exists(self.everydb_path):
            print(f"エラー: EveryDB2.3が見つかりません")
            print(f"パス: {self.everydb_path}")
            return False
        
        try:
            print(f"EveryDB2.3を開始中...")
            print(f"パス: {self.everydb_path}")
            
            # バックグラウンドで実行
            self.process = subprocess.Popen(
                [self.everydb_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            self.is_running = True
            print("EveryDB2.3が開始されました")
            
            # 監視スレッドを開始
            self.monitor_thread = threading.Thread(target=self.monitor_progress)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            print("監視スレッドが開始されました")
            print("画面が消えても処理は継続されます")
            print()
            
            return True
            
        except Exception as e:
            print(f"エラー: EveryDB2.3の開始に失敗しました - {e}")
            return False
    
    def stop_everydb(self):
        """EveryDB2.3を停止"""
        print("\n=== EveryDB2.3停止 ===")
        
        self.is_running = False
        
        if self.process:
            try:
                self.process.terminate()
                print("EveryDB2.3プロセスを終了しました")
            except Exception as e:
                print(f"プロセス終了エラー: {e}")
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            print("監視スレッドを停止しました")
        
        # 最終進捗確認
        print("\n最終進捗:")
        progress = self.check_database_progress()
        if progress and 'error' not in progress:
            print(f"馬数: {progress['horse_count']:,}頭")
            print(f"レース数: {progress['race_count']:,}件")
            if progress['latest_update']:
                print(f"最新更新: {progress['latest_update']}")
    
    def run_interactive(self):
        """対話的に実行"""
        if self.start_everydb_background():
            try:
                print("EveryDB2.3が実行中です")
                print("画面が消えても処理は継続されます")
                print("停止するには Ctrl+C を押してください")
                print()
                
                while self.is_running:
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print("\n停止要求を受信しました")
                self.stop_everydb()
        else:
            print("EveryDB2.3の開始に失敗しました")

def main():
    """メイン実行"""
    runner = EveryDBBackgroundRunner()
    runner.run_interactive()

if __name__ == "__main__":
    main()


