#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
9月の結果デバッグ
的中率0%の原因を特定
"""
import sqlite3
import pandas as pd
import sys
import os
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def debug_september_results():
    """9月の結果デバッグ"""
    db_path = "ecore.db"
    
    try:
        conn = sqlite3.connect(db_path)
        print("データベース接続成功")
        
        # 1. 9月のレース結果確認
        print("=== 9月のレース結果確認 ===")
        
        sql_september = """
        SELECT 
            Year || MonthDay as Date,
            JyoCD,
            RaceNum,
            Bamei,
            ChokyosiRyakusyo as TrainerName,
            KakuteiJyuni as FinishOrder,
            Odds as TanshoOdds,
            Fukasyokin as FukushoOdds
        FROM N_UMA_RACE
        WHERE (Year || MonthDay) >= '20250901'
        AND (Year || MonthDay) <= '20250930'
        AND ChokyosiRyakusyo IS NOT NULL AND ChokyosiRyakusyo != ''
        AND KakuteiJyuni IS NOT NULL AND KakuteiJyuni != ''
        ORDER BY Year, MonthDay, JyoCD, RaceNum, Umaban
        LIMIT 20
        """
        
        september_results = pd.read_sql_query(sql_september, conn)
        print(f"9月のレース結果: {len(september_results)}件")
        
        for _, row in september_results.iterrows():
            print(f"  {row['Date']} {row['JyoCD']}{row['RaceNum']} {row['Bamei']} ({row['TrainerName']}) - 着順:{row['FinishOrder']} 単勝:{row['TanshoOdds']} 複勝:{row['FukushoOdds']}")
        
        # 2. 木村哲也の9月の参加確認
        print("\n=== 木村哲也の9月の参加確認 ===")
        
        sql_kimura = """
        SELECT 
            Year || MonthDay as Date,
            JyoCD,
            RaceNum,
            Bamei,
            ChokyosiRyakusyo as TrainerName,
            KakuteiJyuni as FinishOrder,
            Odds as TanshoOdds,
            Fukasyokin as FukushoOdds
        FROM N_UMA_RACE
        WHERE (Year || MonthDay) >= '20250901'
        AND (Year || MonthDay) <= '20250930'
        AND ChokyosiRyakusyo = '木村哲也'
        ORDER BY Year, MonthDay, JyoCD, RaceNum, Umaban
        """
        
        kimura_results = pd.read_sql_query(sql_kimura, conn)
        print(f"木村哲也の9月の参加: {len(kimura_results)}件")
        
        for _, row in kimura_results.iterrows():
            print(f"  {row['Date']} {row['JyoCD']}{row['RaceNum']} {row['Bamei']} - 着順:{row['FinishOrder']} 単勝:{row['TanshoOdds']} 複勝:{row['FukushoOdds']}")
        
        # 3. 中内田充の9月の参加確認
        print("\n=== 中内田充の9月の参加確認 ===")
        
        sql_nakauchi = """
        SELECT 
            Year || MonthDay as Date,
            JyoCD,
            RaceNum,
            Bamei,
            ChokyosiRyakusyo as TrainerName,
            KakuteiJyuni as FinishOrder,
            Odds as TanshoOdds,
            Fukasyokin as FukushoOdds
        FROM N_UMA_RACE
        WHERE (Year || MonthDay) >= '20250901'
        AND (Year || MonthDay) <= '20250930'
        AND ChokyosiRyakusyo = '中内田充'
        ORDER BY Year, MonthDay, JyoCD, RaceNum, Umaban
        """
        
        nakauchi_results = pd.read_sql_query(sql_nakauchi, conn)
        print(f"中内田充の9月の参加: {len(nakauchi_results)}件")
        
        for _, row in nakauchi_results.iterrows():
            print(f"  {row['Date']} {row['JyoCD']}{row['RaceNum']} {row['Bamei']} - 着順:{row['FinishOrder']} 単勝:{row['TanshoOdds']} 複勝:{row['FukushoOdds']}")
        
        # 4. 9月の着順分布確認
        print("\n=== 9月の着順分布確認 ===")
        
        sql_finish_distribution = """
        SELECT 
            KakuteiJyuni as FinishOrder,
            COUNT(*) as Count
        FROM N_UMA_RACE
        WHERE (Year || MonthDay) >= '20250901'
        AND (Year || MonthDay) <= '20250930'
        AND KakuteiJyuni IS NOT NULL AND KakuteiJyuni != ''
        GROUP BY KakuteiJyuni
        ORDER BY CAST(KakuteiJyuni AS INTEGER)
        """
        
        finish_distribution = pd.read_sql_query(sql_finish_distribution, conn)
        print("9月の着順分布:")
        for _, row in finish_distribution.iterrows():
            print(f"  着順{row['FinishOrder']}: {row['Count']}件")
        
        # 5. 9月の調教師別成績確認
        print("\n=== 9月の調教師別成績確認 ===")
        
        sql_trainer_september = """
        SELECT 
            ChokyosiRyakusyo as TrainerName,
            COUNT(*) as TotalRaces,
            SUM(CASE WHEN KakuteiJyuni = '1' THEN 1 ELSE 0 END) as WinCount,
            SUM(CASE WHEN KakuteiJyuni = '2' THEN 1 ELSE 0 END) as PlaceCount,
            SUM(CASE WHEN KakuteiJyuni = '3' THEN 1 ELSE 0 END) as ShowCount
        FROM N_UMA_RACE
        WHERE (Year || MonthDay) >= '20250901'
        AND (Year || MonthDay) <= '20250930'
        AND ChokyosiRyakusyo IS NOT NULL AND ChokyosiRyakusyo != ''
        AND KakuteiJyuni IS NOT NULL AND KakuteiJyuni != ''
        GROUP BY ChokyosiRyakusyo
        HAVING COUNT(*) >= 5
        ORDER BY (SUM(CASE WHEN KakuteiJyuni = '1' THEN 1 ELSE 0 END) + SUM(CASE WHEN KakuteiJyuni = '2' THEN 1 ELSE 0 END) + SUM(CASE WHEN KakuteiJyuni = '3' THEN 1 ELSE 0 END)) / COUNT(*) DESC
        LIMIT 10
        """
        
        trainer_september = pd.read_sql_query(sql_trainer_september, conn)
        print("9月の調教師別成績（上位10名）:")
        for _, row in trainer_september.iterrows():
            place_rate = (row['WinCount'] + row['PlaceCount'] + row['ShowCount']) / row['TotalRaces']
            print(f"  {row['TrainerName']}: {row['WinCount']}-{row['PlaceCount']}-{row['ShowCount']}-{row['TotalRaces']-row['WinCount']-row['PlaceCount']-row['ShowCount']}/{row['TotalRaces']} (着順率:{place_rate:.2f})")
        
        conn.close()
        print("\n=== デバッグ完了 ===")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_september_results()




