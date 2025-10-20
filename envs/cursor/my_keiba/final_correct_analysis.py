#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終修正版の正しい分析
お客様のTARGET frontier JVの条件に合わせた分析
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

def final_correct_analysis():
    """最終修正版の正しい分析"""
    db_path = "ecore.db"
    
    try:
        conn = sqlite3.connect(db_path)
        print("データベース接続成功")
        
        # お客様のデータを手動で入力
        user_data = {
            "木村哲也": {"win": 21, "place": 17, "show": 6, "other": 49, "total": 93, "place_rate": 0.473},
            "杉山晴紀": {"win": 18, "place": 6, "show": 8, "other": 51, "total": 83, "place_rate": 0.386},
            "斉藤崇史": {"win": 16, "place": 7, "show": 5, "other": 32, "total": 60, "place_rate": 0.467},
            "中内田充": {"win": 14, "place": 12, "show": 10, "other": 33, "total": 69, "place_rate": 0.522},
            "池江泰寿": {"win": 13, "place": 11, "show": 6, "other": 49, "total": 79, "place_rate": 0.380},
            "手塚貴久": {"win": 13, "place": 5, "show": 10, "other": 52, "total": 80, "place_rate": 0.350},
            "宮田敬介": {"win": 12, "place": 9, "show": 6, "other": 45, "total": 72, "place_rate": 0.375},
            "田中博康": {"win": 11, "place": 12, "show": 4, "other": 37, "total": 64, "place_rate": 0.422},
            "吉岡辰弥": {"win": 11, "place": 5, "show": 7, "other": 42, "total": 65, "place_rate": 0.354},
            "友道康夫": {"win": 10, "place": 8, "show": 5, "other": 33, "total": 56, "place_rate": 0.411},
            "鹿戸雄一": {"win": 9, "place": 10, "show": 12, "other": 57, "total": 88, "place_rate": 0.352},
            "藤岡健一": {"win": 9, "place": 7, "show": 10, "other": 47, "total": 73, "place_rate": 0.356},
            "上村洋行": {"win": 7, "place": 7, "show": 2, "other": 23, "total": 39, "place_rate": 0.410},
            "堀宣行": {"win": 7, "place": 3, "show": 1, "other": 11, "total": 22, "place_rate": 0.500},
            "田中克典": {"win": 7, "place": 2, "show": 7, "other": 27, "total": 43, "place_rate": 0.372},
            "須貝尚介": {"win": 6, "place": 6, "show": 7, "other": 29, "total": 48, "place_rate": 0.396},
            "萩原清": {"win": 6, "place": 1, "show": 2, "other": 16, "total": 25, "place_rate": 0.360},
            "上原佑紀": {"win": 5, "place": 11, "show": 5, "other": 30, "total": 51, "place_rate": 0.412},
            "松永幹夫": {"win": 5, "place": 4, "show": 4, "other": 24, "total": 37, "place_rate": 0.351},
            "森一誠": {"win": 5, "place": 4, "show": 3, "other": 14, "total": 26, "place_rate": 0.462},
            "長谷川浩": {"win": 5, "place": 3, "show": 2, "other": 16, "total": 26, "place_rate": 0.385},
            "武幸四郎": {"win": 4, "place": 2, "show": 1, "other": 10, "total": 17, "place_rate": 0.412},
            "庄野靖志": {"win": 4, "place": 1, "show": 1, "other": 5, "total": 11, "place_rate": 0.545},
            "小林真也": {"win": 3, "place": 5, "show": 3, "other": 19, "total": 30, "place_rate": 0.367},
            "佐々木晶": {"win": 3, "place": 4, "show": 6, "other": 16, "total": 29, "place_rate": 0.448},
            "伊藤大士": {"win": 3, "place": 2, "show": 3, "other": 11, "total": 19, "place_rate": 0.421},
            "木原一良": {"win": 1, "place": 1, "show": 2, "other": 4, "total": 8, "place_rate": 0.500}
        }
        
        print("=== お客様のTARGET frontier JVデータ分析 ===")
        print(f"総調教師数: {len(user_data)}名")
        
        # 35%以上の着順率を持つ調教師を特定
        high_performance_trainers = {name: data for name, data in user_data.items() if data['place_rate'] >= 0.35}
        
        print(f"\n=== 35%以上の着順率を持つ調教師 ===")
        print(f"該当調教師数: {len(high_performance_trainers)}名")
        
        for name, data in sorted(high_performance_trainers.items(), key=lambda x: x[1]['place_rate'], reverse=True):
            print(f"  {name}: {data['win']}-{data['place']}-{data['show']}-{data['other']}/{data['total']} (着順率:{data['place_rate']:.1%})")
        
        # 9月の成績検証（正しい方法）
        print(f"\n=== 9月の成績検証（正しい方法） ===")
        
        # お客様のデータから上位調教師を選択（着順率35%以上）
        top_trainers = [name for name, data in high_performance_trainers.items() if data['place_rate'] >= 0.35]
        
        print(f"検証対象調教師: {len(top_trainers)}名")
        
        # 9月のレース結果を取得（正しいテーブルと条件を使用）
        query_september = f"""
        SELECT 
            ChokyosiRyakusyo as TrainerName,
            COUNT(*) as TotalRaces,
            SUM(CASE WHEN KakuteiJyuni = '1' THEN 1 ELSE 0 END) as WinCount,
            SUM(CASE WHEN KakuteiJyuni = '2' THEN 1 ELSE 0 END) as PlaceCount,
            SUM(CASE WHEN KakuteiJyuni = '3' THEN 1 ELSE 0 END) as ShowCount
        FROM N_UMA_RACE
        WHERE (Year || MonthDay) >= '20250901'
        AND (Year || MonthDay) <= '20250930'
        AND ChokyosiRyakusyo IN ({','.join([f"'{name}'" for name in top_trainers])})
        AND KakuteiJyuni IS NOT NULL AND KakuteiJyuni != ''
        AND KakuteiJyuni NOT IN ('00', '止', '除', '取')
        GROUP BY ChokyosiRyakusyo
        ORDER BY (SUM(CASE WHEN KakuteiJyuni = '1' THEN 1 ELSE 0 END) + SUM(CASE WHEN KakuteiJyuni = '2' THEN 1 ELSE 0 END) + SUM(CASE WHEN KakuteiJyuni = '3' THEN 1 ELSE 0 END)) / COUNT(*) DESC
        """
        
        september_results = pd.read_sql_query(query_september, conn)
        
        if not september_results.empty:
            september_results['PlaceRate'] = (september_results['WinCount'] + september_results['PlaceCount'] + september_results['ShowCount']) / september_results['TotalRaces']
            
            print(f"\n9月の実際の成績:")
            for _, row in september_results.iterrows():
                print(f"  {row['TrainerName']}: {row['WinCount']}-{row['PlaceCount']}-{row['ShowCount']}-{row['TotalRaces']-row['WinCount']-row['PlaceCount']-row['ShowCount']}/{row['TotalRaces']} (着順率:{row['PlaceRate']:.1%})")
            
            # 的中率と回収率の計算
            total_races = september_results['TotalRaces'].sum()
            total_hits = september_results['WinCount'].sum() + september_results['PlaceCount'].sum() + september_results['ShowCount'].sum()
            hit_rate = total_hits / total_races if total_races > 0 else 0
            
            print(f"\n=== 9月の成績サマリー ===")
            print(f"総レース数: {total_races}")
            print(f"的中数: {total_hits}")
            print(f"的中率: {hit_rate:.1%}")
            
            # 回収率の計算（オッズデータが必要）
            print(f"\n=== 回収率の計算 ===")
            print("オッズデータが必要ですが、現在のデータベースには適切なオッズ情報が含まれていません。")
            print("TARGET frontier JVのオッズデータと比較する必要があります。")
            
        else:
            print("9月のデータが見つかりません")
        
        # 推奨手法の結論
        print(f"\n=== 推奨手法の結論 ===")
        print("1. お客様のTARGET frontier JVの分析条件を使用")
        print("2. 12月から8月の馬印5,6の優秀調教師を選定")
        print("3. 35%以上の着順率を持つ調教師を対象とする")
        print("4. 9月のレースに適用して成績を検証")
        
        # 具体的な推奨調教師
        print(f"\n=== 推奨調教師（着順率50%以上） ===")
        top_50_percent = {name: data for name, data in high_performance_trainers.items() if data['place_rate'] >= 0.50}
        for name, data in sorted(top_50_percent.items(), key=lambda x: x[1]['place_rate'], reverse=True):
            print(f"  {name}: 着順率{data['place_rate']:.1%} ({data['win']}-{data['place']}-{data['show']}-{data['other']}/{data['total']})")
        
        conn.close()
        print("\n=== 分析完了 ===")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    final_correct_analysis()




