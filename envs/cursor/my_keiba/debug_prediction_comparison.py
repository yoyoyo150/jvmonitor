#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
予想比較のデバッグ
問題の特定と修正
"""
import sqlite3
import pandas as pd
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def debug_prediction_comparison():
    """予想比較のデバッグ"""
    db_path = "ecore.db"
    
    try:
        conn = sqlite3.connect(db_path)
        print("データベース接続成功")
        
        # 1. 9/27と28のレース結果確認
        print("=== 9/27と28のレース結果確認 ===")
        
        sql_race_results = """
        SELECT 
            Year || MonthDay as Date,
            JyoCD,
            RaceNum,
            ChokyosiRyakusyo as TrainerName,
            KakuteiJyuni as FinishOrder,
            Odds as TanshoOdds,
            Fukasyokin as FukushoOdds
        FROM N_UMA_RACE
        WHERE (Year || MonthDay) IN ('20250927', '20250928')
        AND ChokyosiRyakusyo IS NOT NULL AND ChokyosiRyakusyo != ''
        ORDER BY Year, MonthDay, JyoCD, RaceNum, Umaban
        LIMIT 20
        """
        
        race_results = pd.read_sql_query(sql_race_results, conn)
        print(f"レース結果: {len(race_results)}件")
        
        for _, row in race_results.iterrows():
            print(f"  {row['Date']} {row['JyoCD']}{row['RaceNum']} {row['TrainerName']} - 着順:{row['FinishOrder']} 単勝:{row['TanshoOdds']} 複勝:{row['FukushoOdds']}")
        
        # 2. 馬印5,6のデータ確認
        print("\n=== 馬印5,6のデータ確認 ===")
        
        sql_marks = """
        SELECT 
            SourceDate,
            TRAINER_NAME as TrainerName,
            Mark5,
            Mark6,
            CHAKU as FinishOrder
        FROM HORSE_MARKS
        WHERE SourceDate >= '20250301'
        AND SourceDate <= '20250926'
        AND TRAINER_NAME IS NOT NULL AND TRAINER_NAME != ''
        AND Mark5 IS NOT NULL AND Mark5 != '' AND Mark5 != '0'
        AND Mark6 IS NOT NULL AND Mark6 != '' AND Mark6 != '0'
        AND CHAKU IS NOT NULL AND CHAKU != ''
        ORDER BY SourceDate DESC
        LIMIT 10
        """
        
        marks_data = pd.read_sql_query(sql_marks, conn)
        print(f"馬印データ: {len(marks_data)}件")
        
        for _, row in marks_data.iterrows():
            print(f"  {row['SourceDate']} {row['TrainerName']} - Mark5:{row['Mark5']}, Mark6:{row['Mark6']}, 着順:{row['FinishOrder']}")
        
        # 3. 調教師名の一致確認
        print("\n=== 調教師名の一致確認 ===")
        
        sql_trainer_names = """
        SELECT DISTINCT ChokyosiRyakusyo as N_UMA_RACE_Trainer
        FROM N_UMA_RACE
        WHERE (Year || MonthDay) IN ('20250927', '20250928')
        AND ChokyosiRyakusyo IS NOT NULL AND ChokyosiRyakusyo != ''
        ORDER BY ChokyosiRyakusyo
        LIMIT 10
        """
        
        n_uma_race_trainers = pd.read_sql_query(sql_trainer_names, conn)
        print(f"N_UMA_RACE調教師: {len(n_uma_race_trainers)}名")
        
        sql_marks_trainers = """
        SELECT DISTINCT TRAINER_NAME as HORSE_MARKS_Trainer
        FROM HORSE_MARKS
        WHERE SourceDate >= '20250301'
        AND SourceDate <= '20250926'
        AND TRAINER_NAME IS NOT NULL AND TRAINER_NAME != ''
        ORDER BY TRAINER_NAME
        LIMIT 10
        """
        
        horse_marks_trainers = pd.read_sql_query(sql_marks_trainers, conn)
        print(f"HORSE_MARKS調教師: {len(horse_marks_trainers)}名")
        
        # 4. 共通調教師の確認
        print("\n=== 共通調教師の確認 ===")
        
        sql_common_trainers = """
        SELECT DISTINCT 
            n.ChokyosiRyakusyo as N_UMA_RACE_Trainer,
            h.TRAINER_NAME as HORSE_MARKS_Trainer
        FROM N_UMA_RACE n
        INNER JOIN HORSE_MARKS h ON n.ChokyosiRyakusyo = h.TRAINER_NAME
        WHERE (n.Year || n.MonthDay) IN ('20250927', '20250928')
        AND n.ChokyosiRyakusyo IS NOT NULL AND n.ChokyosiRyakusyo != ''
        AND h.SourceDate >= '20250301'
        AND h.SourceDate <= '20250926'
        AND h.TRAINER_NAME IS NOT NULL AND h.TRAINER_NAME != ''
        LIMIT 10
        """
        
        common_trainers = pd.read_sql_query(sql_common_trainers, conn)
        print(f"共通調教師: {len(common_trainers)}名")
        
        for _, row in common_trainers.iterrows():
            print(f"  {row['N_UMA_RACE_Trainer']} = {row['HORSE_MARKS_Trainer']}")
        
        # 5. 具体的な調教師の成績確認
        print("\n=== 具体的な調教師の成績確認 ===")
        
        # 米川昇の成績確認
        sql_mikawa = """
        SELECT 
            SourceDate,
            TRAINER_NAME,
            Mark5,
            Mark6,
            CHAKU,
            COUNT(*) as RaceCount
        FROM HORSE_MARKS
        WHERE TRAINER_NAME = '米川昇'
        AND SourceDate >= '20250301'
        AND SourceDate <= '20250926'
        GROUP BY SourceDate, TRAINER_NAME, Mark5, Mark6, CHAKU
        ORDER BY SourceDate DESC
        LIMIT 5
        """
        
        mikawa_data = pd.read_sql_query(sql_mikawa, conn)
        print(f"米川昇のデータ: {len(mikawa_data)}件")
        
        for _, row in mikawa_data.iterrows():
            print(f"  {row['SourceDate']} Mark5:{row['Mark5']}, Mark6:{row['Mark6']}, 着順:{row['CHAKU']}")
        
        # 6. 9/27と28での米川昇の参加確認
        print("\n=== 9/27と28での米川昇の参加確認 ===")
        
        sql_mikawa_race = """
        SELECT 
            Year || MonthDay as Date,
            JyoCD,
            RaceNum,
            Bamei,
            ChokyosiRyakusyo,
            KakuteiJyuni
        FROM N_UMA_RACE
        WHERE (Year || MonthDay) IN ('20250927', '20250928')
        AND ChokyosiRyakusyo = '米川昇'
        """
        
        mikawa_race = pd.read_sql_query(sql_mikawa_race, conn)
        print(f"9/27と28での米川昇の参加: {len(mikawa_race)}件")
        
        for _, row in mikawa_race.iterrows():
            print(f"  {row['Date']} {row['JyoCD']}{row['RaceNum']} {row['Bamei']} - 着順:{row['KakuteiJyuni']}")
        
        conn.close()
        print("\n=== デバッグ完了 ===")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_prediction_comparison()




