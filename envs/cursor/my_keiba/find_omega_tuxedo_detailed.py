import sqlite3
import sys
import io
import pandas as pd
import os
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DB_PATH = 'ecore.db'
YDATE_DIR = r"C:\my_project_folder\envs\cursor\my_keiba\yDate"

def find_omega_tuxedo_detailed():
    print("=== オメガタキシードの詳細調査 ===\n")

    # 1. オメガタキシードの全データを確認
    print("1. オメガタキシードの全データを確認")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT SourceDate, HorseName, Mark1, Mark2, Mark3, ZI_INDEX, ZM_VALUE
        FROM HORSE_MARKS 
        WHERE HorseName = 'オメガタキシード'
        ORDER BY SourceDate DESC
    """)
    
    omega_all_data = cursor.fetchall()
    if omega_all_data:
        print(f"オメガタキシードのデータ: {len(omega_all_data)} 件")
        print("全データ:")
        for data in omega_all_data:
            date, name, m1, m2, m3, zi, zm = data
            print(f"  {date}: 馬印1={m1}, 馬印2={m2}, 馬印3={m3}, ZI={zi}, ZM={zm}")
    else:
        print("❌ オメガタキシードのデータが全く見つかりません")

    # 2. 2025年5月3日と5月4日の全馬名を確認
    print("\n2. 2025年5月3日と5月4日の全馬名を確認")
    cursor.execute("""
        SELECT SourceDate, HorseName
        FROM HORSE_MARKS 
        WHERE SourceDate IN ('20250503', '20250504')
        ORDER BY SourceDate, HorseName
    """)
    
    all_horses = cursor.fetchall()
    print(f"2025年5月3日と5月4日の全馬名: {len(all_horses)} 件")
    
    # オメガで始まる馬名を検索
    omega_horses = [horse for date, horse in all_horses if 'オメガ' in horse]
    if omega_horses:
        print("オメガで始まる馬名:")
        for horse in omega_horses:
            print(f"  {horse}")
    else:
        print("オメガで始まる馬名が見つかりません")

    # 3. タキシードを含む馬名を検索
    print("\n3. タキシードを含む馬名を検索")
    tuxedo_horses = [horse for date, horse in all_horses if 'タキシード' in horse]
    if tuxedo_horses:
        print("タキシードを含む馬名:")
        for horse in tuxedo_horses:
            print(f"  {horse}")
    else:
        print("タキシードを含む馬名が見つかりません")

    # 4. 画面で表示されている馬名を検索
    print("\n4. 画面で表示されている馬名を検索")
    screen_horses = ["イデアイゴッソウ", "オメガタキシード"]
    
    for horse_name in screen_horses:
        cursor.execute("""
            SELECT SourceDate, HorseName, Mark1, Mark2, Mark3, ZI_INDEX, ZM_VALUE
            FROM HORSE_MARKS 
            WHERE SourceDate IN ('20250503', '20250504') AND HorseName = ?
        """, (horse_name,))
        
        result = cursor.fetchone()
        if result:
            date, name, m1, m2, m3, zi, zm = result
            print(f"✅ {horse_name} が見つかりました:")
            print(f"  日付: {date}")
            print(f"  馬印1: {m1}, 馬印2: {m2}, 馬印3: {m3}, ZI: {zi}, ZM: {zm}")
        else:
            print(f"❌ {horse_name} が見つかりません")

    # 5. 類似の馬名を検索
    print("\n5. 類似の馬名を検索")
    similar_patterns = ['オメガ', 'タキシード', 'イデア', 'ゴッソウ']
    
    for pattern in similar_patterns:
        cursor.execute("""
            SELECT DISTINCT HorseName
            FROM HORSE_MARKS 
            WHERE SourceDate IN ('20250503', '20250504') AND HorseName LIKE ?
        """, (f'%{pattern}%',))
        
        similar_horses = cursor.fetchall()
        if similar_horses:
            print(f"{pattern}を含む馬名:")
            for horse in similar_horses:
                print(f"  {horse[0]}")
        else:
            print(f"{pattern}を含む馬名が見つかりません")

    conn.close()

    # 6. 問題の分析
    print("\n6. 問題の分析")
    print("画面で表示されている馬名がデータベースに存在しない原因:")
    print("1. 馬名の表記が異なる")
    print("2. データのインポートが不完全")
    print("3. 画面のデータソースが異なる")
    print("4. データの欠損")

if __name__ == '__main__':
    find_omega_tuxedo_detailed()

