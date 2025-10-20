#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正しい検証分析
選定調教師のM5.6の優秀馬の月間成績と開催日成績を表示
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

def proper_verification_analysis():
    """正しい検証分析"""
    db_path = "ecore.db"
    
    try:
        conn = sqlite3.connect(db_path)
        print("データベース接続成功")
        
        # お客様のデータから選定調教師（着順率50%以上）
        selected_trainers = ["庄野靖志", "中内田充", "堀宣行", "木原一良", "木村哲也", "斉藤崇史", "森一誠", "佐々木晶", "田中博康", "伊藤大士"]
        
        print("=== 選定調教師のM5.6の優秀馬の成績分析 ===")
        print(f"選定調教師数: {len(selected_trainers)}名")
        
        for trainer in selected_trainers:
            print(f"\n--- {trainer} ---")
            
            # 1. 12月から8月のM5.6の優秀馬の成績
            print("【12月から8月のM5.6の優秀馬の成績】")
            query_mark_period = f"""
            SELECT 
                SourceDate,
                JyoCD,
                RaceNum,
                HorseName,
                Mark5,
                Mark6,
                CHAKU as FinishOrder,
                TANSHO_ODDS as WinOdds,
                FUKUSHO_ODDS as PlaceOdds
            FROM HORSE_MARKS
            WHERE SourceDate >= '20241201'
            AND SourceDate <= '20250831'
            AND TRAINER_NAME = '{trainer}'
            AND Mark5 IS NOT NULL AND Mark5 != '' AND Mark5 != '0'
            AND Mark6 IS NOT NULL AND Mark6 != '' AND Mark6 != '0'
            AND CHAKU IS NOT NULL AND CHAKU != ''
            ORDER BY SourceDate DESC
            LIMIT 20
            """
            
            mark_results = pd.read_sql_query(query_mark_period, conn)
            
            if not mark_results.empty:
                # Mark5+Mark6の合計スコア計算
                mark_results['Mark5_numeric'] = pd.to_numeric(mark_results['Mark5'], errors='coerce')
                mark_results['Mark6_numeric'] = pd.to_numeric(mark_results['Mark6'], errors='coerce')
                mark_results['MarkSum'] = mark_results['Mark5_numeric'] + mark_results['Mark6_numeric']
                
                # 優秀馬（MarkSumが低い）を選択
                excellent_horses = mark_results[mark_results['MarkSum'] <= 6].sort_values('MarkSum')
                
                print(f"  M5.6の優秀馬数: {len(excellent_horses)}頭")
                print("  優秀馬の成績:")
                for _, row in excellent_horses.head(10).iterrows():
                    print(f"    {row['SourceDate']} {row['JyoCD']}{row['RaceNum']} {row['HorseName']} - M5:{row['Mark5']} M6:{row['Mark6']} 合計:{row['MarkSum']} 着順:{row['FinishOrder']} 単勝:{row['WinOdds']} 複勝:{row['PlaceOdds']}")
                
                # 月間成績の集計
                monthly_stats = excellent_horses.groupby(excellent_horses['SourceDate'].str[:6]).apply(
                    lambda x: pd.Series({
                        'TotalRaces': len(x),
                        'Win': (x['FinishOrder'] == '1').sum(),
                        'Place': (x['FinishOrder'] == '2').sum(),
                        'Show': (x['FinishOrder'] == '3').sum(),
                        'AvgMarkSum': x['MarkSum'].mean()
                    })
                )
                
                print("  月間成績:")
                for month, stats in monthly_stats.iterrows():
                    place_rate = (stats['Win'] + stats['Place'] + stats['Show']) / stats['TotalRaces'] if stats['TotalRaces'] > 0 else 0
                    print(f"    {month}: {stats['Win']}-{stats['Place']}-{stats['Show']}-{stats['TotalRaces']-stats['Win']-stats['Place']-stats['Show']}/{stats['TotalRaces']} (着順率:{place_rate:.1%}) 平均M5+6:{stats['AvgMarkSum']:.1f}")
            else:
                print("  M5.6のデータが見つかりません")
            
            # 2. 9月の開催日成績
            print("\n【9月の開催日成績】")
            query_september = f"""
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
            """
            
            september_results = pd.read_sql_query(query_september, conn)
            
            if not september_results.empty:
                print(f"  9月の参加レース数: {len(september_results)}件")
                print("  9月の成績:")
                for _, row in september_results.iterrows():
                    print(f"    {row['Date']} {row['JyoCD']}{row['RaceNum']} {row['HorseName']} - 着順:{row['FinishOrder']} 単勝:{row['WinOdds']} 複勝:{row['PlaceOdds']}")
                
                # 9月の成績集計
                win_count = (september_results['FinishOrder'] == '1').sum()
                place_count = (september_results['FinishOrder'] == '2').sum()
                show_count = (september_results['FinishOrder'] == '3').sum()
                total_races = len(september_results)
                place_rate = (win_count + place_count + show_count) / total_races if total_races > 0 else 0
                
                print(f"  9月の成績サマリー: {win_count}-{place_count}-{show_count}-{total_races-win_count-place_count-show_count}/{total_races} (着順率:{place_rate:.1%})")
            else:
                print("  9月のデータが見つかりません")
        
        # 3. 全体の検証結果
        print(f"\n=== 全体の検証結果 ===")
        
        # 全選定調教師の9月成績を集計
        query_all_september = f"""
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
        GROUP BY ChokyosiRyakusyo
        ORDER BY (SUM(CASE WHEN KakuteiJyuni = '1' THEN 1 ELSE 0 END) + SUM(CASE WHEN KakuteiJyuni = '2' THEN 1 ELSE 0 END) + SUM(CASE WHEN KakuteiJyuni = '3' THEN 1 ELSE 0 END)) / COUNT(*) DESC
        """
        
        all_september_results = pd.read_sql_query(query_all_september, conn)
        
        if not all_september_results.empty:
            all_september_results['PlaceRate'] = (all_september_results['WinCount'] + all_september_results['PlaceCount'] + all_september_results['ShowCount']) / all_september_results['TotalRaces']
            
            print("全選定調教師の9月成績:")
            for _, row in all_september_results.iterrows():
                print(f"  {row['TrainerName']}: {row['WinCount']}-{row['PlaceCount']}-{row['ShowCount']}-{row['TotalRaces']-row['WinCount']-row['PlaceCount']-row['ShowCount']}/{row['TotalRaces']} (着順率:{row['PlaceRate']:.1%})")
            
            # 全体の的中率と回収率
            total_races = all_september_results['TotalRaces'].sum()
            total_hits = all_september_results['WinCount'].sum() + all_september_results['PlaceCount'].sum() + all_september_results['ShowCount'].sum()
            overall_hit_rate = total_hits / total_races if total_races > 0 else 0
            
            print(f"\n全体の成績サマリー:")
            print(f"  総レース数: {total_races}")
            print(f"  的中数: {total_hits}")
            print(f"  的中率: {overall_hit_rate:.1%}")
            
            # 回収率の計算（オッズデータが必要）
            print(f"\n回収率の計算:")
            print("  オッズデータが必要ですが、現在のデータベースには適切なオッズ情報が含まれていません。")
            print("  TARGET frontier JVのオッズデータと比較する必要があります。")
        else:
            print("9月のデータが見つかりません")
        
        conn.close()
        print("\n=== 検証分析完了 ===")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    proper_verification_analysis()
