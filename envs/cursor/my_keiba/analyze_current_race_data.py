# -*- coding: utf-8 -*-
import sqlite3
import pandas as pd
from datetime import datetime
import sys
import io

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def analyze_current_race_data():
    conn = sqlite3.connect('ecore.db')
    
    print("=== 現在のデータベースで出馬表表示に利用可能なデータ分析 ===\n")
    
    # 1. レースデータの詳細分析
    print("1. レースデータの詳細分析")
    cursor = conn.cursor()
    
    # 年別レース数
    cursor.execute("""
        SELECT Year, COUNT(*) as race_count 
        FROM N_RACE 
        GROUP BY Year 
        ORDER BY Year DESC
    """)
    yearly_races = cursor.fetchall()
    print("年別レース数:")
    for year, count in yearly_races:
        print(f"  {year}年: {count:,} レース")
    
    print("\n" + "="*50 + "\n")
    
    # 2. 出馬データの詳細分析
    print("2. 出馬データの詳細分析")
    cursor.execute("""
        SELECT Year, COUNT(*) as uma_count 
        FROM N_UMA_RACE 
        GROUP BY Year 
        ORDER BY Year DESC
    """)
    yearly_umas = cursor.fetchall()
    print("年別出馬数:")
    for year, count in yearly_umas:
        print(f"  {year}年: {count:,} 出馬")
    
    print("\n" + "="*50 + "\n")
    
    # 3. 開催場別データ
    print("3. 開催場別データ")
    cursor.execute("""
        SELECT JyoCD, COUNT(*) as race_count 
        FROM N_RACE 
        GROUP BY JyoCD 
        ORDER BY race_count DESC
    """)
    jyo_data = cursor.fetchall()
    print("開催場別レース数:")
    for jyo, count in jyo_data:
        print(f"  場コード {jyo}: {count:,} レース")
    
    print("\n" + "="*50 + "\n")
    
    # 4. レース距離別データ
    print("4. レース距離別データ")
    cursor.execute("""
        SELECT Kyori, COUNT(*) as race_count 
        FROM N_RACE 
        WHERE Kyori != '' AND Kyori != '0000'
        GROUP BY Kyori 
        ORDER BY CAST(Kyori AS INTEGER)
    """)
    distance_data = cursor.fetchall()
    print("距離別レース数:")
    for distance, count in distance_data[:10]:  # 上位10位のみ表示
        print(f"  {distance}m: {count:,} レース")
    
    print("\n" + "="*50 + "\n")
    
    # 5. 最新データの詳細
    print("5. 最新データの詳細")
    cursor.execute("""
        SELECT Year, MonthDay, JyoCD, RaceNum, Hondai, Kyori, HassoTime
        FROM N_RACE 
        ORDER BY Year DESC, MonthDay DESC, JyoCD, RaceNum
        LIMIT 5
    """)
    latest_races = cursor.fetchall()
    print("最新レース情報:")
    for race in latest_races:
        year, monthday, jyo, race_num, hondai, kyori, hasso_time = race
        print(f"  {year}年{monthday} 場{jyo}R{race_num}: {hondai} ({kyori}m, {hasso_time})")
    
    print("\n" + "="*50 + "\n")
    
    # 6. 出馬表に必要な情報の充足度確認
    print("6. 出馬表表示に必要な情報の充足度確認")
    
    # レース基本情報
    cursor.execute("SELECT COUNT(*) FROM N_RACE WHERE Hondai != ''")
    race_with_title = cursor.fetchone()[0]
    print(f"レース名付きレース: {race_with_title:,} 件")
    
    # 距離情報
    cursor.execute("SELECT COUNT(*) FROM N_RACE WHERE Kyori != '' AND Kyori != '0000'")
    race_with_distance = cursor.fetchone()[0]
    print(f"距離情報付きレース: {race_with_distance:,} 件")
    
    # 発走時刻情報
    cursor.execute("SELECT COUNT(*) FROM N_RACE WHERE HassoTime != '' AND HassoTime != '0000'")
    race_with_time = cursor.fetchone()[0]
    print(f"発走時刻付きレース: {race_with_time:,} 件")
    
    # 出馬情報
    cursor.execute("SELECT COUNT(*) FROM N_UMA_RACE WHERE Bamei != ''")
    uma_with_name = cursor.fetchone()[0]
    print(f"馬名付き出馬: {uma_with_name:,} 件")
    
    # 騎手情報
    cursor.execute("SELECT COUNT(*) FROM N_UMA_RACE WHERE KisyuRyakusyo != ''")
    uma_with_jockey = cursor.fetchone()[0]
    print(f"騎手情報付き出馬: {uma_with_jockey:,} 件")
    
    # 調教師情報
    cursor.execute("SELECT COUNT(*) FROM N_UMA_RACE WHERE ChokyosiRyakusyo != ''")
    uma_with_trainer = cursor.fetchone()[0]
    print(f"調教師情報付き出馬: {uma_with_trainer:,} 件")
    
    print("\n" + "="*50 + "\n")
    
    # 7. 出馬表表示用のサンプルクエリ
    print("7. 出馬表表示用のサンプルクエリ")
    cursor.execute("""
        SELECT 
            r.Year || r.MonthDay as race_date,
            r.JyoCD,
            r.RaceNum,
            r.Hondai,
            r.Kyori,
            r.HassoTime,
            u.Wakuban,
            u.Umaban,
            u.Bamei,
            u.KisyuRyakusyo,
            u.ChokyosiRyakusyo,
            u.BaTaijyu,
            u.Odds,
            u.Ninki
        FROM N_RACE r
        JOIN N_UMA_RACE u ON r.Year = u.Year 
            AND r.MonthDay = u.MonthDay 
            AND r.JyoCD = u.JyoCD 
            AND r.RaceNum = u.RaceNum
        WHERE r.Year = '2024' 
            AND r.MonthDay = '1006'  -- 10月6日のレース
            AND r.JyoCD = '06'       -- 中山競馬場
        ORDER BY r.RaceNum, u.Umaban
        LIMIT 10
    """)
    sample_race_data = cursor.fetchall()
    print("サンプル出馬表データ (2024年10月6日 中山):")
    for row in sample_race_data:
        print(f"  {row[0]} 場{row[1]}R{row[2]}: {row[3]} ({row[4]}m, {row[5]})")
        print(f"    {row[6]}-{row[7]}: {row[8]} ({row[9]}/{row[10]}) 体重:{row[11]} オッズ:{row[12]} 人気:{row[13]}")
    
    conn.close()

if __name__ == "__main__":
    analyze_current_race_data()
