#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EveryDB2.3 Headless Runner
画面表示を無効にして実行するスクリプト
GDI+エラーを回避
"""

import os
import subprocess
import time
import sqlite3
from datetime import datetime

def run_everydb_headless():
    """画面表示を無効にしてEveryDB2.3を実行"""
    
    print("=== EveryDB2.3 Headless Runner ===")
    print("GDI+エラーを回避して実行します")
    print()
    
    everydb_path = r"J:\new program file\everydb230\everydb230\Application Files\EveryDB2.3_2_3_0_0\EveryDB2.3.exe"
    db_path = r"C:\my_project_folder\envs\cursor\my_keiba\ecore.db"
    
    # 1. 現在の状況確認
    print("1. 現在の状況確認")
    print("=" * 50)
    
    try:
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM N_UMA;")
            horse_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM N_UMA_RACE;")
            race_count = cursor.fetchone()[0]
            conn.close()
            
            print(f"現在の馬数: {horse_count:,}頭")
            print(f"現在のレース数: {race_count:,}件")
        else:
            print("データベースファイルが見つかりません")
    except Exception as e:
        print(f"データベース確認エラー: {e}")
    
    # 2. 既存プロセスの終了
    print(f"\n2. 既存プロセスの終了")
    print("=" * 50)
    
    try:
        result = subprocess.run(['taskkill', '/IM', 'EveryDB2.3.exe', '/F'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("既存のEveryDB2.3プロセスを終了しました")
        else:
            print("終了するプロセスはありませんでした")
    except Exception as e:
        print(f"プロセス終了エラー: {e}")
    
    # 3. 環境変数の設定（GDI+エラー回避）
    print(f"\n3. 環境変数設定")
    print("=" * 50)
    
    # 環境変数を設定してGDI+エラーを回避
    env = os.environ.copy()
    env['DISPLAY'] = ''  # ディスプレイを無効化
    env['GDI_PLUS_ERROR_MODE'] = '0'  # GDI+エラーモードを無効化
    
    print("環境変数を設定しました")
    
    # 4. ヘッドレス実行
    print(f"\n4. ヘッドレス実行開始")
    print("=" * 50)
    
    if not os.path.exists(everydb_path):
        print(f"エラー: EveryDB2.3が見つかりません")
        print(f"パス: {everydb_path}")
        return False
    
    try:
        print("EveryDB2.3をヘッドレスモードで開始中...")
        
        # ヘッドレス実行（画面表示なし）
        process = subprocess.Popen(
            [everydb_path],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW  # ウィンドウを作成しない
        )
        
        print("EveryDB2.3がヘッドレスモードで開始されました")
        print("画面が表示されませんが、処理は継続されます")
        print()
        
        # 5. 進捗監視
        print("5. 進捗監視開始")
        print("=" * 50)
        
        last_horse_count = 0
        last_race_count = 0
        no_progress_count = 0
        max_no_progress = 10  # 10回連続で進捗がない場合は警告
        
        while True:
            try:
                # プロセスが生きているかチェック
                if process.poll() is not None:
                    print("EveryDB2.3プロセスが終了しました")
                    break
                
                # データベースの進捗確認
                if os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM N_UMA;")
                    current_horse_count = cursor.fetchone()[0]
                    cursor.execute("SELECT COUNT(*) FROM N_UMA_RACE;")
                    current_race_count = cursor.fetchone()[0]
                    conn.close()
                    
                    # 進捗があったかチェック
                    if (current_horse_count > last_horse_count or 
                        current_race_count > last_race_count):
                        
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 進捗更新:")
                        print(f"  馬数: {current_horse_count:,}頭 (前回: {last_horse_count:,})")
                        print(f"  レース数: {current_race_count:,}件 (前回: {last_race_count:,})")
                        print()
                        
                        last_horse_count = current_horse_count
                        last_race_count = current_race_count
                        no_progress_count = 0
                    else:
                        no_progress_count += 1
                        if no_progress_count % 5 == 0:  # 5回ごとに表示
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] 進捗なし ({no_progress_count}/{max_no_progress})")
                        
                        if no_progress_count >= max_no_progress:
                            print("長時間進捗がありません。プロセスを確認してください。")
                            no_progress_count = 0
                
                # 60秒待機
                time.sleep(60)
                
            except KeyboardInterrupt:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 停止要求を受信しました")
                break
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 監視エラー: {e}")
                time.sleep(10)
        
        # プロセス終了
        try:
            process.terminate()
            print("EveryDB2.3プロセスを終了しました")
        except Exception as e:
            print(f"プロセス終了エラー: {e}")
        
        return True
        
    except Exception as e:
        print(f"エラー: EveryDB2.3の開始に失敗しました - {e}")
        return False

def main():
    """メイン実行"""
    run_everydb_headless()

if __name__ == "__main__":
    main()


