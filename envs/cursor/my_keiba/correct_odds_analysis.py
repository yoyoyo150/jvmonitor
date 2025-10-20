#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正しいオッズデータを使用した分析
N_ODDS_TANPUKUテーブルから正しいオッズデータを取得
"""
import sqlite3
import pandas as pd
import sys
import os
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def correct_odds_analysis():
    """正しいオッズデータを使用した分析"""
    db_path = "ecore.db"
    
    try:
        conn = sqlite3.connect(db_path)
        print("データベース接続成功")
        
        # 1. 9月28日中山11Rの正しいオッズデータを取得
        print("=== 9月28日中山11Rの正しいオッズデータ ===")
        
        query_correct_odds = """
        SELECT 
            o.Year || o.MonthDay as Date,
            o.JyoCD,
            o.RaceNum,
            o.Umaban,
            o.TanOdds,
            o.TanNinki,
            o.FukuOddsLow,
            o.FukuOddsHigh,
            o.FukuNinki,
            r.Bamei as HorseName,
            r.ChokyosiRyakusyo as TrainerName,
            r.KakuteiJyuni as FinishOrder
        FROM N_ODDS_TANPUKU o
        LEFT JOIN N_UMA_RACE r ON (
            o.Year = r.Year AND 
            o.MonthDay = r.MonthDay AND 
            o.JyoCD = r.JyoCD AND 
            o.RaceNum = r.RaceNum AND 
            o.Umaban = r.Umaban
        )
        WHERE o.Year = '2025'
        AND o.MonthDay = '0928'
        AND o.JyoCD = '06'
        AND o.RaceNum = '11'
        ORDER BY o.Umaban
        """
        
        correct_odds = pd.read_sql_query(query_correct_odds, conn)
        
        if not correct_odds.empty:
            print(f"9月28日中山11R: {len(correct_odds)}頭")
            for _, row in correct_odds.iterrows():
                print(f"  {row['Umaban']}番 {row['HorseName']} ({row['TrainerName']}) - 着順:{row['FinishOrder']} 単勝:{row['TanOdds']} 複勝:{row['FukuOddsLow']}-{row['FukuOddsHigh']} 人気:{row['TanNinki']}")
        else:
            print("9月28日中山11Rのオッズデータが見つかりません")
        
        # 2. ウインカーネリアンの正しいオッズデータを確認
        print(f"\n=== ウインカーネリアンの正しいオッズデータ ===")
        
        query_winner_correct = """
        SELECT 
            o.Year || o.MonthDay as Date,
            o.JyoCD,
            o.RaceNum,
            o.Umaban,
            o.TanOdds,
            o.TanNinki,
            o.FukuOddsLow,
            o.FukuOddsHigh,
            o.FukuNinki,
            r.Bamei as HorseName,
            r.ChokyosiRyakusyo as TrainerName,
            r.KakuteiJyuni as FinishOrder
        FROM N_ODDS_TANPUKU o
        LEFT JOIN N_UMA_RACE r ON (
            o.Year = r.Year AND 
            o.MonthDay = r.MonthDay AND 
            o.JyoCD = r.JyoCD AND 
            o.RaceNum = r.RaceNum AND 
            o.Umaban = r.Umaban
        )
        WHERE o.Year = '2025'
        AND o.MonthDay = '0928'
        AND o.JyoCD = '06'
        AND o.RaceNum = '11'
        AND r.Bamei = 'ウインカーネリアン'
        """
        
        winner_correct = pd.read_sql_query(query_winner_correct, conn)
        
        if not winner_correct.empty:
            print("ウインカーネリアンの正しいオッズデータ:")
            for _, row in winner_correct.iterrows():
                print(f"  {row['HorseName']} ({row['TrainerName']}) - 着順:{row['FinishOrder']} 単勝:{row['TanOdds']} 複勝:{row['FukuOddsLow']}-{row['FukuOddsHigh']} 人気:{row['TanNinki']}")
        else:
            print("ウインカーネリアンの正しいオッズデータが見つかりません")
        
        # 3. 正しい回収率の計算
        print(f"\n=== 正しい回収率の計算 ===")
        
        # 選定調教師の9月成績を正しいオッズデータで計算
        selected_trainers = ["庄野靖志", "中内田充", "堀宣行", "木原一良", "木村哲也", "斉藤崇史", "森一誠", "佐々木晶", "田中博康", "伊藤大士"]
        
        query_september_correct = """
        SELECT 
            r.ChokyosiRyakusyo as TrainerName,
            r.Bamei as HorseName,
            r.KakuteiJyuni as FinishOrder,
            o.TanOdds,
            o.FukuOddsLow,
            o.FukuOddsHigh
        FROM N_UMA_RACE r
        LEFT JOIN N_ODDS_TANPUKU o ON (
            r.Year = o.Year AND 
            r.MonthDay = o.MonthDay AND 
            r.JyoCD = o.JyoCD AND 
            r.RaceNum = o.RaceNum AND 
            r.Umaban = o.Umaban
        )
        WHERE r.Year = '2025'
        AND r.MonthDay >= '0901'
        AND r.MonthDay <= '0930'
        AND r.ChokyosiRyakusyo IN ({})
        AND r.KakuteiJyuni IS NOT NULL AND r.KakuteiJyuni != ''
        AND r.KakuteiJyuni NOT IN ('00', '止', '除', '取')
        ORDER BY r.Year, r.MonthDay, r.JyoCD, r.RaceNum, r.Umaban
        """.format(','.join([f"'{name}'" for name in selected_trainers]))
        
        september_correct = pd.read_sql_query(query_september_correct, conn)
        
        if not september_correct.empty:
            print(f"選定調教師の9月成績（正しいオッズデータ）: {len(september_correct)}件")
            
            # 的中率と回収率の計算
            total_races = len(september_correct)
            hits = 0
            total_return = 0.0
            
            for _, row in september_correct.iterrows():
                finish_order = row['FinishOrder']
                tansho_odds = float(row['TanOdds']) if row['TanOdds'] and row['TanOdds'] != '0000' else 0
                fuku_odds_low = float(row['FukuOddsLow']) if row['FukuOddsLow'] and row['FukuOddsLow'] != '0000' else 0
                fuku_odds_high = float(row['FukuOddsHigh']) if row['FukuOddsHigh'] and row['FukuOddsHigh'] != '0000' else 0
                
                # 的中判定（1着、2着、3着）
                is_hit = finish_order in ['1', '2', '3']
                if is_hit:
                    hits += 1
                
                # 回収計算
                race_return = 0.0
                if is_hit:
                    if finish_order == '1' and tansho_odds > 0:
                        race_return += tansho_odds
                    if finish_order in ['2', '3'] and fuku_odds_low > 0:
                        race_return += fuku_odds_low
                
                total_return += race_return
                
                print(f"  {row['HorseName']} ({row['TrainerName']}) - 着順:{finish_order} {'✅' if is_hit else '❌'} 単勝:{tansho_odds} 複勝:{fuku_odds_low}-{fuku_odds_high} 回収:{race_return:.2f}")
            
            hit_rate = hits / total_races if total_races > 0 else 0
            recovery_rate = total_return / total_races if total_races > 0 else 0
            
            print(f"\n=== 正しい成績サマリー ===")
            print(f"総レース数: {total_races}")
            print(f"的中数: {hits}")
            print(f"的中率: {hit_rate:.1%}")
            print(f"総回収: {total_return:.2f}")
            print(f"回収率: {recovery_rate:.1%}")
        else:
            print("選定調教師の9月データが見つかりません")
        
        conn.close()
        print("\n=== 正しいオッズデータ分析完了 ===")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    correct_odds_analysis()




