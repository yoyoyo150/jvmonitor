#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
今日の競馬データ更新スクリプト
JVMonitorのデータ更新機能を呼び出して、最新データを反映
"""

import subprocess
import os
import sys
from datetime import datetime

def update_jvmonitor_data():
    """JVMonitorのデータ更新を実行"""
    print("今日の競馬データ更新を開始します...")
    print(f"現在の日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    
    # JVMonitorのパス
    jvmonitor_path = r"C:\my_project_folder\envs\cursor\my_keiba\JVMonitor\JVMonitor\bin\Debug\net6.0-windows\JVMonitor.exe"
    
    if not os.path.exists(jvmonitor_path):
        print(f"エラー: JVMonitorが見つかりません: {jvmonitor_path}")
        return False
    
    try:
        print("JVMonitorを起動してデータ更新を実行します...")
        
        # JVMonitorを起動（バックグラウンドで実行）
        process = subprocess.Popen([jvmonitor_path], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True,
                                 encoding='utf-8')
        
        print("JVMonitorが起動しました。")
        print("手動でデータ更新ボタンを押してください。")
        print("更新完了後、このスクリプトを終了してください。")
        
        # プロセスの終了を待つ
        process.wait()
        
        print("JVMonitorが終了しました。")
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        return False

def check_latest_data():
    """最新データの確認"""
    print("\n最新データの確認中...")
    
    try:
        import sqlite3
        
        # ecore.dbの最新データ確認
        ecore_db = r"C:\my_project_folder\envs\cursor\my_keiba\ecore.db"
        if os.path.exists(ecore_db):
            conn = sqlite3.connect(ecore_db)
            cursor = conn.cursor()
            
            # 最新のMakeDateを取得
            cursor.execute("SELECT MAX(MakeDate) FROM N_RACE WHERE MakeDate IS NOT NULL;")
            latest_date = cursor.fetchone()[0]
            
            if latest_date:
                print(f"ecore.db 最新データ: {latest_date}")
            else:
                print("ecore.db にデータが見つかりません")
            
            conn.close()
        
        # excel_data.dbの最新データ確認
        excel_db = r"C:\my_project_folder\envs\cursor\my_keiba\excel_data.db"
        if os.path.exists(excel_db):
            conn = sqlite3.connect(excel_db)
            cursor = conn.cursor()
            
            # 最新のSourceDateを取得
            cursor.execute("SELECT MAX(SourceDate) FROM HORSE_MARKS WHERE SourceDate IS NOT NULL;")
            latest_date = cursor.fetchone()[0]
            
            if latest_date:
                print(f"excel_data.db 最新データ: {latest_date}")
            else:
                print("excel_data.db にデータが見つかりません")
            
            conn.close()
            
    except Exception as e:
        print(f"データ確認エラー: {e}")

def main():
    """メイン処理"""
    print("=" * 50)
    print("競馬データ更新システム")
    print("=" * 50)
    
    # 現在のデータ状況を確認
    check_latest_data()
    
    print("\n" + "=" * 50)
    print("データ更新の実行")
    print("=" * 50)
    
    # データ更新の実行
    if update_jvmonitor_data():
        print("\nデータ更新が完了しました。")
        
        # 更新後のデータ確認
        print("\n" + "=" * 50)
        print("更新後のデータ確認")
        print("=" * 50)
        check_latest_data()
    else:
        print("データ更新に失敗しました。")

if __name__ == "__main__":
    main()


