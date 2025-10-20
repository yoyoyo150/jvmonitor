#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終修正版の調教師予想手法比較システム
正しい的中率と回収率の計算
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

class FinalCorrectTrainerPredictionComparison:
    """最終修正版の調教師予想手法比較クラス"""
    
    def __init__(self, db_path="ecore.db"):
        """初期化"""
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """データベース接続"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            print("データベース接続成功")
            return True
        except Exception as e:
            print(f"データベース接続エラー: {e}")
            return False
    
    def disconnect(self):
        """データベース切断"""
        if self.conn:
            self.conn.close()
    
    def get_mark5_mark6_trainers_dec_aug(self):
        """12月から8月の馬印5,6の優秀調教師取得"""
        try:
            print("=== 手法1: 12月から8月の馬印5,6の優秀調教師 ===")
            
            # 12月から8月の期間
            query = f"""
            SELECT 
                TRAINER_NAME as TrainerName,
                COUNT(*) as TotalRaces,
                AVG(CAST(Mark5 AS INTEGER)) as AvgMark5,
                AVG(CAST(Mark6 AS INTEGER)) as AvgMark6,
                SUM(CASE WHEN CHAKU = '1' THEN 1 ELSE 0 END) as WinCount,
                SUM(CASE WHEN CHAKU = '2' THEN 1 ELSE 0 END) as PlaceCount,
                SUM(CASE WHEN CHAKU = '3' THEN 1 ELSE 0 END) as ShowCount
            FROM HORSE_MARKS
            WHERE SourceDate >= '20241201'
            AND SourceDate <= '20250831'
            AND TRAINER_NAME IS NOT NULL AND TRAINER_NAME != ''
            AND Mark5 IS NOT NULL AND Mark5 != '' AND Mark5 != '0'
            AND Mark6 IS NOT NULL AND Mark6 != '' AND Mark6 != '0'
            AND CHAKU IS NOT NULL AND CHAKU != ''
            GROUP BY TRAINER_NAME
            HAVING COUNT(*) >= 3
            ORDER BY AVG(CAST(Mark5 AS INTEGER)) + AVG(CAST(Mark6 AS INTEGER)) ASC
            """
            
            df = pd.read_sql_query(query, self.conn)
            
            if df.empty:
                print("馬印5,6のデータが見つかりません")
                return None
            
            # 馬印5,6の合計スコア計算（低い方が良い）
            df['MarkScore'] = df['AvgMark5'] + df['AvgMark6']
            df['PlaceRate'] = (df['WinCount'] + df['PlaceCount'] + df['ShowCount']) / df['TotalRaces']
            
            # 優秀調教師の選定（馬印スコアが低く、着順率が高い）
            df['PerformanceScore'] = df['PlaceRate'] * 10 - df['MarkScore'] * 0.1
            df = df.sort_values('PerformanceScore', ascending=False)
            
            print(f"12月から8月の馬印5,6分析結果: {len(df)}名の調教師")
            print("上位10名:")
            for _, row in df.head(10).iterrows():
                print(f"  {row['TrainerName']}: 馬印スコア{row['MarkScore']:.2f}, 着順率{row['PlaceRate']:.2f}, レース数{row['TotalRaces']}")
            
            return df
            
        except Exception as e:
            print(f"馬印5,6分析エラー: {e}")
            return None
    
    def get_nine_month_trainers_dec_aug(self):
        """12月から8月の9か月間の成績で調教師取得"""
        try:
            print("\n=== 手法2: 12月から8月の9か月間の成績で調教師 ===")
            
            # 12月から8月の期間の成績を取得
            query = f"""
            SELECT 
                ChokyosiRyakusyo as TrainerName,
                COUNT(*) as TotalRaces,
                SUM(CASE WHEN KakuteiJyuni = '1' THEN 1 ELSE 0 END) as WinCount,
                SUM(CASE WHEN KakuteiJyuni = '2' THEN 1 ELSE 0 END) as PlaceCount,
                SUM(CASE WHEN KakuteiJyuni = '3' THEN 1 ELSE 0 END) as ShowCount,
                SUM(CASE WHEN KakuteiJyuni IN ('4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18') THEN 1 ELSE 0 END) as OtherCount
            FROM N_UMA_RACE
            WHERE (Year || MonthDay) >= '20241201'
            AND (Year || MonthDay) <= '20250831'
            AND ChokyosiRyakusyo IS NOT NULL AND ChokyosiRyakusyo != ''
            AND KakuteiJyuni IS NOT NULL AND KakuteiJyuni != ''
            GROUP BY ChokyosiRyakusyo
            HAVING COUNT(*) >= 3
            ORDER BY (SUM(CASE WHEN KakuteiJyuni = '1' THEN 1 ELSE 0 END) + SUM(CASE WHEN KakuteiJyuni = '2' THEN 1 ELSE 0 END) + SUM(CASE WHEN KakuteiJyuni = '3' THEN 1 ELSE 0 END)) / COUNT(*) DESC
            """
            
            df = pd.read_sql_query(query, self.conn)
            
            if df.empty:
                print("9か月間のデータが見つかりません")
                return None
            
            # 着順率計算
            df['PlaceRate'] = (df['WinCount'] + df['PlaceCount'] + df['ShowCount']) / df['TotalRaces']
            df['WinRate'] = df['WinCount'] / df['TotalRaces']
            
            print(f"12月から8月の9か月間分析結果: {len(df)}名の調教師")
            print("上位10名:")
            for _, row in df.head(10).iterrows():
                print(f"  {row['TrainerName']}: 着順率{row['PlaceRate']:.2f}, レース数{row['TotalRaces']}")
            
            return df
            
        except Exception as e:
            print(f"9か月間分析エラー: {e}")
            return None
    
    def calculate_september_performance_correct(self, trainer_list, top_n=20):
        """9月の成績計算（修正版）"""
        try:
            print(f"\n=== 9月の成績計算（上位{top_n}名） ===")
            
            # 上位調教師を選択
            top_trainers = trainer_list.head(top_n)
            trainer_names = top_trainers['TrainerName'].tolist()
            
            print(f"対象調教師: {len(trainer_names)}名")
            for trainer in trainer_names[:5]:
                print(f"  {trainer}")
            
            # 9月のレース結果を取得
            query = f"""
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
            AND ChokyosiRyakusyo IN ({','.join([f"'{name}'" for name in trainer_names])})
            AND KakuteiJyuni IS NOT NULL AND KakuteiJyuni != ''
            ORDER BY Year, MonthDay, JyoCD, RaceNum, Umaban
            """
            
            september_results = pd.read_sql_query(query, self.conn)
            
            if september_results.empty:
                print("9月のレース結果が見つかりません")
                return None
            
            print(f"9月のレース結果: {len(september_results)}件")
            
            # 的中率と回収率の計算（修正版）
            total_bets = len(september_results)
            hits = 0
            total_return = 0.0
            
            # 各レースの詳細を表示
            print("\n=== 各レースの詳細 ===")
            for _, race in september_results.iterrows():
                finish_order = race['FinishOrder']
                tansho_odds = race['TanshoOdds']
                fukusho_odds = race['FukushoOdds']
                
                # 的中判定（1着、2着、3着）
                is_hit = finish_order in ['1', '2', '3']
                if is_hit:
                    hits += 1
                
                # 回収計算（オッズが正しい場合のみ）
                race_return = 0.0
                if is_hit:
                    if finish_order == '1' and tansho_odds and tansho_odds != '0000':
                        try:
                            race_return += float(tansho_odds) / 100.0  # オッズを正規化
                        except:
                            pass
                    if finish_order in ['2', '3'] and fukusho_odds and fukusho_odds != '00000000':
                        try:
                            race_return += float(fukusho_odds) / 100.0  # オッズを正規化
                        except:
                            pass
                
                total_return += race_return
                
                print(f"  {race['Date']} {race['JyoCD']}{race['RaceNum']} {race['Bamei']} ({race['TrainerName']}) - 着順:{finish_order} {'✅' if is_hit else '❌'} 単勝:{tansho_odds} 複勝:{fukusho_odds} 回収:{race_return:.2f}")
            
            hit_rate = hits / total_bets if total_bets > 0 else 0
            recovery_rate = total_return / total_bets if total_bets > 0 else 0
            
            print(f"\n=== 成績サマリー ===")
            print(f"総レース数: {total_bets}")
            print(f"的中数: {hits}")
            print(f"的中率: {hit_rate:.2%}")
            print(f"総回収: {total_return:.2f}")
            print(f"回収率: {recovery_rate:.2%}")
            
            return {
                'total_bets': total_bets,
                'hits': hits,
                'hit_rate': hit_rate,
                'total_return': total_return,
                'recovery_rate': recovery_rate,
                'september_results': september_results
            }
            
        except Exception as e:
            print(f"9月の成績計算エラー: {e}")
            return None
    
    def compare_methods(self):
        """2つの手法の比較"""
        print("=== 正しい予想手法比較 ===")
        
        try:
            # 手法1: 12月から8月の馬印5,6の優秀調教師
            mark_trainers = self.get_mark5_mark6_trainers_dec_aug()
            
            if mark_trainers is not None:
                mark_results = self.calculate_september_performance_correct(mark_trainers, top_n=20)
            else:
                mark_results = None
            
            # 手法2: 12月から8月の9か月間の成績で調教師
            nine_month_trainers = self.get_nine_month_trainers_dec_aug()
            
            if nine_month_trainers is not None:
                nine_month_results = self.calculate_september_performance_correct(nine_month_trainers, top_n=20)
            else:
                nine_month_results = None
            
            # 結果の比較
            print("\n=== 結果比較 ===")
            
            if mark_results:
                print(f"手法1 (馬印5,6): 的中率{mark_results['hit_rate']:.2%}, 回収率{mark_results['recovery_rate']:.2%}")
            else:
                print("手法1 (馬印5,6): データなし")
            
            if nine_month_results:
                print(f"手法2 (9か月間): 的中率{nine_month_results['hit_rate']:.2%}, 回収率{nine_month_results['recovery_rate']:.2%}")
            else:
                print("手法2 (9か月間): データなし")
            
            # 優劣判定
            if mark_results and nine_month_results:
                if mark_results['hit_rate'] > nine_month_results['hit_rate']:
                    print("✅ 手法1 (馬印5,6) が的中率で優位")
                elif nine_month_results['hit_rate'] > mark_results['hit_rate']:
                    print("✅ 手法2 (9か月間) が的中率で優位")
                else:
                    print("🤝 的中率は同等")
                
                if mark_results['recovery_rate'] > nine_month_results['recovery_rate']:
                    print("✅ 手法1 (馬印5,6) が回収率で優位")
                elif nine_month_results['recovery_rate'] > mark_results['recovery_rate']:
                    print("✅ 手法2 (9か月間) が回収率で優位")
                else:
                    print("🤝 回収率は同等")
            
            return {
                'mark_method': mark_results,
                'nine_month_method': nine_month_results
            }
            
        except Exception as e:
            print(f"比較分析エラー: {e}")
            return None

def main():
    """メイン実行"""
    comparison = FinalCorrectTrainerPredictionComparison()
    
    if not comparison.connect():
        return
    
    try:
        # 比較分析実行
        results = comparison.compare_methods()
        
        if results:
            print("\n=== 分析完了 ===")
        else:
            print("分析に失敗しました")
    
    finally:
        comparison.disconnect()

if __name__ == "__main__":
    main()




