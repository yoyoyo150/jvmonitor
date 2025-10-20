#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正しい9月の成績分析
お客様のデータに基づく正確な分析
"""
import sqlite3
import pandas as pd
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def correct_september_analysis():
    """正しい9月の成績分析"""
    db_path = "ecore.db"
    
    try:
        conn = sqlite3.connect(db_path)
        print("データベース接続成功")
        
        # お客様のデータから選定調教師（着順率50%以上）
        selected_trainers = ["庄野靖志", "中内田充", "堀宣行", "木原一良", "木村哲也", "斉藤崇史", "森一誠", "佐々木晶", "田中博康", "伊藤大士"]
        
        print("=== 正しい9月の成績分析 ===")
        print(f"選定調教師数: {len(selected_trainers)}名")
        
        # 1. 9月の全レース結果を確認
        print("\n=== 9月の全レース結果確認 ===")
        
        query_september_all = """
        SELECT 
            Year || MonthDay as Date,
            JyoCD,
            RaceNum,
            Bamei as HorseName,
            ChokyosiRyakusyo as TrainerName,
            KakuteiJyuni as FinishOrder,
            Odds as WinOdds,
            Fukasyokin as PlaceOdds
        FROM N_UMA_RACE
        WHERE (Year || MonthDay) >= '20250901'
        AND (Year || MonthDay) <= '20250930'
        AND KakuteiJyuni IS NOT NULL AND KakuteiJyuni != ''
        AND KakuteiJyuni NOT IN ('00', '止', '除', '取')
        ORDER BY Year, MonthDay, JyoCD, RaceNum, Umaban
        LIMIT 50
        """
        
        september_all = pd.read_sql_query(query_september_all, conn)
        print(f"9月の全レース結果: {len(september_all)}件")
        
        if not september_all.empty:
            print("9月のレース結果（最初の20件）:")
            for _, row in september_all.head(20).iterrows():
                print(f"  {row['Date']} {row['JyoCD']}{row['RaceNum']} {row['HorseName']} ({row['TrainerName']}) - 着順:{row['FinishOrder']} 単勝:{row['WinOdds']} 複勝:{row['PlaceOdds']}")
        
        # 2. 選定調教師の9月成績を正しく取得
        print(f"\n=== 選定調教師の9月成績 ===")
        
        query_selected_trainers = f"""
        SELECT 
            ChokyosiRyakusyo as TrainerName,
            COUNT(*) as TotalRaces,
            SUM(CASE WHEN KakuteiJyuni = '1' THEN 1 ELSE 0 END) as WinCount,
            SUM(CASE WHEN KakuteiJyuni = '2' THEN 1 ELSE 0 END) as PlaceCount,
            SUM(CASE WHEN KakuteiJyuni = '3' THEN 1 ELSE 0 END) as ShowCount
        FROM N_UMA_RACE
        WHERE (Year || MonthDay) >= '20250901'
        AND (Year || MonthDay) <= '20250930'
        AND ChokyosiRyakusyo IN ({','.join([f"'{name}'" for name in selected_trainers])})
        AND KakuteiJyuni IS NOT NULL AND KakuteiJyuni != ''
        AND KakuteiJyuni NOT IN ('00', '止', '除', '取')
        GROUP BY ChokyosiRyakusyo
        ORDER BY (SUM(CASE WHEN KakuteiJyuni = '1' THEN 1 ELSE 0 END) + SUM(CASE WHEN KakuteiJyuni = '2' THEN 1 ELSE 0 END) + SUM(CASE WHEN KakuteiJyuni = '3' THEN 1 ELSE 0 END)) / COUNT(*) DESC
        """
        
        selected_results = pd.read_sql_query(query_selected_trainers, conn)
        
        if not selected_results.empty:
            selected_results['PlaceRate'] = (selected_results['WinCount'] + selected_results['PlaceCount'] + selected_results['ShowCount']) / selected_results['TotalRaces']
            
            print("選定調教師の9月成績:")
            for _, row in selected_results.iterrows():
                print(f"  {row['TrainerName']}: {row['WinCount']}-{row['PlaceCount']}-{row['ShowCount']}-{row['TotalRaces']-row['WinCount']-row['PlaceCount']-row['ShowCount']}/{row['TotalRaces']} (着順率:{row['PlaceRate']:.1%})")
            
            # 全体の的中率と回収率
            total_races = selected_results['TotalRaces'].sum()
            total_hits = selected_results['WinCount'].sum() + selected_results['PlaceCount'].sum() + selected_results['ShowCount'].sum()
            overall_hit_rate = total_hits / total_races if total_races > 0 else 0
            
            print(f"\n全体の成績サマリー:")
            print(f"  総レース数: {total_races}")
            print(f"  的中数: {total_hits}")
            print(f"  的中率: {overall_hit_rate:.1%}")
            
            # 回収率の計算
            print(f"\n回収率の計算:")
            print("  オッズデータが必要ですが、現在のデータベースには適切なオッズ情報が含まれていません。")
            print("  TARGET frontier JVのオッズデータと比較する必要があります。")
        else:
            print("選定調教師の9月データが見つかりません")
        
        # 3. 特定の調教師の詳細成績を確認
        print(f"\n=== 特定調教師の詳細成績確認 ===")
        
        for trainer in selected_trainers[:5]:  # 上位5名を確認
            print(f"\n--- {trainer} ---")
            
            query_trainer_detail = f"""
            SELECT 
                Year || MonthDay as Date,
                JyoCD,
                RaceNum,
                Bamei as HorseName,
                KakuteiJyuni as FinishOrder,
                Odds as WinOdds,
                Fukasyokin as PlaceOdds
            FROM N_UMA_RACE
            WHERE (Year || MonthDay) >= '20250901'
            AND (Year || MonthDay) <= '20250930'
            AND ChokyosiRyakusyo = '{trainer}'
            AND KakuteiJyuni IS NOT NULL AND KakuteiJyuni != ''
            ORDER BY Year, MonthDay, JyoCD, RaceNum
            LIMIT 10
            """
            
            trainer_detail = pd.read_sql_query(query_trainer_detail, conn)
            
            if not trainer_detail.empty:
                print(f"  {trainer}の9月成績: {len(trainer_detail)}件")
                for _, row in trainer_detail.iterrows():
                    print(f"    {row['Date']} {row['JyoCD']}{row['RaceNum']} {row['HorseName']} - 着順:{row['FinishOrder']} 単勝:{row['WinOdds']} 複勝:{row['PlaceOdds']}")
            else:
                print(f"  {trainer}の9月データが見つかりません")
        
        # 4. 9月28日の中山11Rの詳細確認
        print(f"\n=== 9月28日の中山11Rの詳細確認 ===")
        
        query_928_nakayama = """
        SELECT 
            Year || MonthDay as Date,
            JyoCD,
            RaceNum,
            Bamei as HorseName,
            ChokyosiRyakusyo as TrainerName,
            KakuteiJyuni as FinishOrder,
            Odds as WinOdds,
            Fukasyokin as PlaceOdds
        FROM N_UMA_RACE
        WHERE (Year || MonthDay) = '20250928'
        AND JyoCD = '06'
        AND RaceNum = '11'
        ORDER BY Umaban
        """
        
        nakayama_928 = pd.read_sql_query(query_928_nakayama, conn)
        
        if not nakayama_928.empty:
            print(f"9月28日中山11R: {len(nakayama_928)}頭")
            for _, row in nakayama_928.iterrows():
                print(f"  {row['HorseName']} ({row['TrainerName']}) - 着順:{row['FinishOrder']} 単勝:{row['WinOdds']} 複勝:{row['PlaceOdds']}")
        else:
            print("9月28日中山11Rのデータが見つかりません")
        
        conn.close()
        print("\n=== 正しい9月の成績分析完了 ===")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    correct_september_analysis()




