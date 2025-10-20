# -*- coding: utf-8 -*-
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
