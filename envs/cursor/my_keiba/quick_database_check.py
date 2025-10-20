#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データベースの簡潔な確認
JVMonitorが参照しているテーブルを特定
"""
import sqlite3
import pandas as pd
import sys
import os

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def quick_database_check():
    """データベースの簡潔な確認"""
    db_path = "ecore.db"
    
    try:
        conn = sqlite3.connect(db_path)
        print("データベース接続成功")
        
        # 1. 全テーブル確認
        print("=== 全テーブル確認 ===")
        tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name", conn)
        print(f"テーブル数: {len(tables)}")
        for _, row in tables.iterrows():
            print(f"  {row['name']}")
        
        # 2. N_UMA_RACEテーブルの9/27と28のデータ確認
        print("\n=== N_UMA_RACEテーブルの9/27と28のデータ確認 ===")
        try:
            sql_n_uma_race = """
            SELECT 
                Year,
                MonthDay,
                JyoCD,
                RaceNum,
                Bamei,
                TrainerName,
                KakuteiJyuni,
                TanshoOdds,
                FukushoOdds,
                NinkiRank
            FROM N_UMA_RACE
            WHERE (Year || MonthDay) IN ('20250927', '20250928')
            AND KakuteiJyuni IS NOT NULL AND KakuteiJyuni != ''
            ORDER BY Year, MonthDay, JyoCD, RaceNum, Umaban
            LIMIT 10
            """
            
            n_uma_race = pd.read_sql_query(sql_n_uma_race, conn)
            print(f"N_UMA_RACEテーブルの着順データ: {len(n_uma_race)}件")
            
            if len(n_uma_race) > 0:
                for _, row in n_uma_race.iterrows():
                    print(f"  {row['Year']}{row['MonthDay']} {row['JyoCD']}{row['RaceNum']} {row['Bamei']} ({row['TrainerName']}) - 着順:{row['KakuteiJyuni']} 人気:{row['NinkiRank']} 単勝:{row['TanshoOdds']} 複勝:{row['FukushoOdds']}")
            else:
                print("N_UMA_RACEテーブルに着順データがありません")
        except Exception as e:
            print(f"N_UMA_RACEテーブルの確認エラー: {e}")
        
        # 3. HORSE_MARKSテーブルの9/27と28のデータ確認
        print("\n=== HORSE_MARKSテーブルの9/27と28のデータ確認 ===")
        try:
            sql_horse_marks = """
            SELECT 
                SourceDate,
                JyoCD,
                RaceNum,
                HorseName,
                TRAINER_NAME,
                CHAKU,
                TANSHO_ODDS,
                FUKUSHO_ODDS,
                NINKI_RANK
            FROM HORSE_MARKS
            WHERE SourceDate IN ('20250927', '20250928')
            AND CHAKU IS NOT NULL AND CHAKU != ''
            ORDER BY SourceDate, JyoCD, RaceNum, Umaban
            LIMIT 10
            """
            
            horse_marks = pd.read_sql_query(sql_horse_marks, conn)
            print(f"HORSE_MARKSテーブルの着順データ: {len(horse_marks)}件")
            
            if len(horse_marks) > 0:
                for _, row in horse_marks.iterrows():
                    print(f"  {row['SourceDate']} {row['JyoCD']}{row['RaceNum']} {row['HorseName']} ({row['TRAINER_NAME']}) - 着順:{row['CHAKU']} 人気:{row['NINKI_RANK']} 単勝:{row['TANSHO_ODDS']} 複勝:{row['FUKUSHO_ODDS']}")
            else:
                print("HORSE_MARKSテーブルに着順データがありません")
        except Exception as e:
            print(f"HORSE_MARKSテーブルの確認エラー: {e}")
        
        # 4. 調教師別の着順データ確認（N_UMA_RACE）
        print("\n=== 調教師別の着順データ確認（N_UMA_RACE） ===")
        try:
            sql_trainer_chaku = """
            SELECT 
                TrainerName,
                COUNT(*) as TotalRaces,
                SUM(CASE WHEN KakuteiJyuni = '1' THEN 1 ELSE 0 END) as WinCount,
                SUM(CASE WHEN KakuteiJyuni = '2' THEN 1 ELSE 0 END) as PlaceCount,
                SUM(CASE WHEN KakuteiJyuni = '3' THEN 1 ELSE 0 END) as ShowCount,
                SUM(CASE WHEN KakuteiJyuni IN ('4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18') THEN 1 ELSE 0 END) as OtherCount
            FROM N_UMA_RACE
            WHERE (Year || MonthDay) IN ('20250927', '20250928')
            AND TrainerName IS NOT NULL AND TrainerName != ''
            GROUP BY TrainerName
            ORDER BY TotalRaces DESC
            LIMIT 10
            """
            
            trainer_chaku = pd.read_sql_query(sql_trainer_chaku, conn)
            print(f"調教師別の着順データ: {len(trainer_chaku)}名")
            
            for _, row in trainer_chaku.iterrows():
                trainer = row['TrainerName']
                win = row['WinCount']
                place = row['PlaceCount'] 
                show = row['ShowCount']
                other = row['OtherCount']
                total = row['TotalRaces']
                result = f"{win}-{place}-{show}-{other}/{total}"
                print(f"  {trainer}: {result}")
        except Exception as e:
            print(f"調教師別の着順データ確認エラー: {e}")
        
        conn.close()
        print("\n=== 簡潔なデータベース確認完了 ===")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_database_check()




