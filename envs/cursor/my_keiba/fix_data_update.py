# -*- coding: utf-8 -*-
import sqlite3
import sys
import io
import subprocess
import os

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_jvmonitor_status():
    """JVMonitorの状態を確認"""
    print("=== JVMonitor状態確認 ===\n")
    
    # JVMonitorのプロセス確認
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq JVMonitor.exe'], 
                              capture_output=True, text=True, encoding='utf-8')
        if 'JVMonitor.exe' in result.stdout:
            print("JVMonitor.exe は実行中です")
        else:
            print("JVMonitor.exe は実行されていません")
    except Exception as e:
        print(f"プロセス確認エラー: {e}")
    
    print("\n" + "="*50 + "\n")

def suggest_solutions():
    """解決策を提案"""
    print("=== 出馬表データ更新の解決策 ===\n")
    
    print("1. JVMonitorの再起動")
    print("   - JVMonitor.exeを終了")
    print("   - 再起動してデータ取得を試行")
    
    print("\n2. EveryDB2.3での手動データ更新")
    print("   - EveryDB2.3を起動")
    print("   - 最新データをダウンロード")
    print("   - データベースに反映")
    
    print("\n3. データベース設定の確認")
    print("   - 接続設定の確認")
    print("   - データソースの確認")
    
    print("\n4. ネットワーク接続の確認")
    print("   - JRA-VANへの接続確認")
    print("   - 認証情報の確認")
    
    print("\n" + "="*50 + "\n")

def create_data_update_script():
    """データ更新用スクリプトを作成"""
    script_content = '''# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_latest_data():
    """最新データの確認"""
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    print("=== 最新データ確認 ===")
    
    # 最新レース日
    cursor.execute("SELECT MAX(Year || MonthDay) FROM N_RACE")
    latest_race = cursor.fetchone()[0]
    print(f"最新レース日: {latest_race}")
    
    # 最新出馬日
    cursor.execute("SELECT MAX(Year || MonthDay) FROM N_UMA_RACE")
    latest_uma = cursor.fetchone()[0]
    print(f"最新出馬日: {latest_uma}")
    
    # 今日のデータ
    today = "20251007"
    cursor.execute("SELECT COUNT(*) FROM N_RACE WHERE Year || MonthDay = ?", (today,))
    today_races = cursor.fetchone()[0]
    print(f"今日のレース数: {today_races}")
    
    cursor.execute("SELECT COUNT(*) FROM N_UMA_RACE WHERE Year || MonthDay = ?", (today,))
    today_umas = cursor.fetchone()[0]
    print(f"今日の出馬数: {today_umas}")
    
    conn.close()

if __name__ == "__main__":
    check_latest_data()
'''
    
    with open('check_latest_data.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("データ確認スクリプトを作成しました: check_latest_data.py")

def main():
    """メイン実行"""
    print("出馬表データ更新問題の診断と解決策\n")
    
    check_jvmonitor_status()
    suggest_solutions()
    create_data_update_script()
    
    print("=== 推奨アクション ===")
    print("1. JVMonitorを再起動してください")
    print("2. EveryDB2.3で最新データをダウンロードしてください")
    print("3. データ更新後、check_latest_data.pyを実行して確認してください")

if __name__ == "__main__":
    main()


