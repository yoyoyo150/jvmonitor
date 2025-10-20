#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正しいテーブル（N_UMA_RACE）で候補生成
JVMonitorと同じテーブルを使用して候補生成
"""
import sqlite3
import pandas as pd
import sys
import os
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def correct_candidate_generation_n_uma_race():
    """正しいテーブル（N_UMA_RACE）で候補生成"""
    db_path = "ecore.db"
    
    try:
        conn = sqlite3.connect(db_path)
        print("データベース接続成功")
        
        # 1. N_UMA_RACEテーブルで9/27と28の着順データ確認
        print("=== N_UMA_RACEテーブルで9/27と28の着順データ確認 ===")
        
        sql_n_uma_race = """
        SELECT 
            Year,
            MonthDay,
            JyoCD,
            RaceNum,
            Bamei,
            ChokyosiRyakusyo,
            KakuteiJyuni,
            Odds,
            Ninki,
            Honsyokin,
            Fukasyokin
        FROM N_UMA_RACE
        WHERE (Year || MonthDay) IN ('20250927', '20250928')
        AND KakuteiJyuni IS NOT NULL AND KakuteiJyuni != ''
        ORDER BY Year, MonthDay, JyoCD, RaceNum, Umaban
        """
        
        n_uma_race = pd.read_sql_query(sql_n_uma_race, conn)
        print(f"N_UMA_RACEテーブルの着順データ: {len(n_uma_race)}件")
        
        # 2. 調教師別の着順データ確認
        print("\n=== 調教師別の着順データ確認 ===")
        
        sql_trainer_chaku = """
        SELECT 
            ChokyosiRyakusyo,
            COUNT(*) as TotalRaces,
            SUM(CASE WHEN KakuteiJyuni = '1' THEN 1 ELSE 0 END) as WinCount,
            SUM(CASE WHEN KakuteiJyuni = '2' THEN 1 ELSE 0 END) as PlaceCount,
            SUM(CASE WHEN KakuteiJyuni = '3' THEN 1 ELSE 0 END) as ShowCount,
            SUM(CASE WHEN KakuteiJyuni IN ('4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18') THEN 1 ELSE 0 END) as OtherCount
        FROM N_UMA_RACE
        WHERE (Year || MonthDay) IN ('20250927', '20250928')
        AND ChokyosiRyakusyo IS NOT NULL AND ChokyosiRyakusyo != ''
        GROUP BY ChokyosiRyakusyo
        ORDER BY TotalRaces DESC
        """
        
        trainer_chaku = pd.read_sql_query(sql_trainer_chaku, conn)
        print(f"調教師別の着順データ: {len(trainer_chaku)}名")
        
        for _, row in trainer_chaku.iterrows():
            trainer = row['ChokyosiRyakusyo']
            win = row['WinCount']
            place = row['PlaceCount'] 
            show = row['ShowCount']
            other = row['OtherCount']
            total = row['TotalRaces']
            result = f"{win}-{place}-{show}-{other}/{total}"
            print(f"  {trainer}: {result}")
        
        # 3. お客様の結果との比較
        print("\n=== お客様の結果との比較 ===")
        
        user_results = {
            "鹿戸雄一": "2-0-0-1/3",
            "小林真也": "1-1-0-0/2", 
            "寺島良": "1-1-0-0/2",
            "大竹正博": "1-1-0-0/2",
            "西園翔太": "1-0-1-0/2",
            "松永幹夫": "1-0-0-1/2",
            "小栗実": "1-0-0-0/1",
            "上村洋行": "1-0-0-0/1",
            "上原佑紀": "0-1-0-2/3",
            "池添学": "0-1-0-1/2",
            "高木登": "0-1-0-1/2",
            "宮田敬介": "0-1-0-0/1",
            "清水英克": "0-1-0-0/1",
            "宮地貴稔": "0-0-1-2/3",
            "堀内岳志": "0-0-1-2/3",
            "林徹": "0-0-1-1/2",
            "須貝尚介": "0-0-1-1/2",
            "前川恭子": "0-0-1-0/1",
            "福永祐一": "0-0-1-0/1",
            "長谷川浩": "0-0-1-0/1",
            "新谷功一": "0-0-1-0/1",
            "松下武士": "0-0-1-0/1",
            "田中勝春": "0-0-0-1/1",
            "森一誠": "0-0-0-1/1",
            "鈴木伸尋": "0-0-0-1/1",
            "千葉直人": "0-0-0-2/2",
            "東田明士": "0-0-0-1/1",
            "嘉藤貴行": "0-0-0-1/1",
            "伊坂重信": "0-0-0-1/1",
            "吉岡辰弥": "0-0-0-1/1",
            "斉藤崇史": "0-0-0-1/1",
            "森田直行": "0-0-0-1/1",
            "木村哲也": "0-0-0-1/1",
            "菊沢隆徳": "0-0-0-1/1",
            "久保田貴": "0-0-0-1/1",
            "大久保龍": "0-0-0-1/1",
            "田村康仁": "0-0-0-1/1"
        }
        
        # 比較
        matches = 0
        mismatches = 0
        
        for _, row in trainer_chaku.iterrows():
            trainer = row['ChokyosiRyakusyo']
            win = row['WinCount']
            place = row['PlaceCount'] 
            show = row['ShowCount']
            other = row['OtherCount']
            total = row['TotalRaces']
            my_result = f"{win}-{place}-{show}-{other}/{total}"
            
            if trainer in user_results:
                user_result = user_results[trainer]
                if my_result == user_result:
                    print(f"  {trainer}: {my_result} (一致)")
                    matches += 1
                else:
                    print(f"  {trainer}: 私={my_result}, お客様={user_result} (不一致)")
                    mismatches += 1
            else:
                print(f"  {trainer}: {my_result} (お客様の結果に含まれていない)")
        
        print(f"\n一致: {matches}名")
        print(f"不一致: {mismatches}名")
        
        # 4. レース別の着順データ確認
        print("\n=== レース別の着順データ確認 ===")
        
        for race_key in n_uma_race.groupby(['Year', 'MonthDay', 'JyoCD', 'RaceNum']).groups.keys():
            year, month_day, jyo_cd, race_num = race_key
            race_data = n_uma_race[
                (n_uma_race['Year'] == year) & 
                (n_uma_race['MonthDay'] == month_day) & 
                (n_uma_race['JyoCD'] == jyo_cd) & 
                (n_uma_race['RaceNum'] == race_num)
            ]
            print(f"  {year}{month_day} {jyo_cd}{race_num}: {len(race_data)}頭")
            
            # 着順データの分布
            race_chaku_dist = race_data['KakuteiJyuni'].value_counts().sort_index()
            for chaku, count in race_chaku_dist.items():
                print(f"    着順{chaku}: {count}件")
        
        # 5. CSV出力
        print("\n=== CSV出力 ===")
        
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        # N_UMA_RACEテーブルの着順データCSV出力
        csv_n_uma_race = output_dir / "n_uma_race_chaku.csv"
        n_uma_race.to_csv(csv_n_uma_race, index=False, encoding='utf-8-sig')
        print(f"N_UMA_RACEテーブルの着順データCSV保存: {csv_n_uma_race}")
        
        # 調教師別の着順データCSV出力
        csv_trainer_chaku = output_dir / "trainer_chaku_n_uma_race.csv"
        trainer_chaku.to_csv(csv_trainer_chaku, index=False, encoding='utf-8-sig')
        print(f"調教師別の着順データCSV保存: {csv_trainer_chaku}")
        
        conn.close()
        print("\n=== 正しいテーブルでの候補生成完了 ===")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    correct_candidate_generation_n_uma_race()




