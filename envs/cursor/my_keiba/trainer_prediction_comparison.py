#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調教師予想手法の比較システム
1. 前月までの半年前の馬印5,6の数値の優秀調教師
2. 開催日の9か月間の成績で予想
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

class TrainerPredictionComparison:
    """調教師予想手法の比較クラス"""
    
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
    
    def get_trainer_performance_period(self, start_date, end_date):
        """指定期間の調教師成績取得"""
        try:
            query = f"""
            SELECT 
                ChokyosiRyakusyo as TrainerName,
                COUNT(*) as TotalRaces,
                SUM(CASE WHEN KakuteiJyuni = '1' THEN 1 ELSE 0 END) as WinCount,
                SUM(CASE WHEN KakuteiJyuni = '2' THEN 1 ELSE 0 END) as PlaceCount,
                SUM(CASE WHEN KakuteiJyuni = '3' THEN 1 ELSE 0 END) as ShowCount,
                SUM(CASE WHEN KakuteiJyuni IN ('4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18') THEN 1 ELSE 0 END) as OtherCount
            FROM N_UMA_RACE
            WHERE (Year || MonthDay) >= '{start_date}'
            AND (Year || MonthDay) <= '{end_date}'
            AND ChokyosiRyakusyo IS NOT NULL AND ChokyosiRyakusyo != ''
            AND KakuteiJyuni IS NOT NULL AND KakuteiJyuni != ''
            GROUP BY ChokyosiRyakusyo
            HAVING COUNT(*) >= 1
            """
            
            df = pd.read_sql_query(query, self.conn)
            
            # 着順率計算
            df['PlaceRate'] = (df['WinCount'] + df['PlaceCount'] + df['ShowCount']) / df['TotalRaces']
            df['WinRate'] = df['WinCount'] / df['TotalRaces']
            
            return df
            
        except Exception as e:
            print(f"調教師成績取得エラー: {e}")
            return None
    
    def get_mark5_mark6_trainers(self, target_date, months_back=6):
        """馬印5,6の優秀調教師取得（半年前）"""
        try:
            # 半年前の期間を計算
            target_dt = datetime.strptime(target_date, '%Y%m%d')
            start_dt = target_dt - timedelta(days=months_back*30)
            end_dt = target_dt - timedelta(days=1)
            
            start_date = start_dt.strftime('%Y%m%d')
            end_date = end_dt.strftime('%Y%m%d')
            
            print(f"馬印5,6分析期間: {start_date} ～ {end_date}")
            
            # HORSE_MARKSテーブルから馬印5,6のデータを取得
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
            WHERE SourceDate >= '{start_date}'
            AND SourceDate <= '{end_date}'
            AND TRAINER_NAME IS NOT NULL AND TRAINER_NAME != ''
            AND Mark5 IS NOT NULL AND Mark5 != '' AND Mark5 != '0'
            AND Mark6 IS NOT NULL AND Mark6 != '' AND Mark6 != '0'
            AND CHAKU IS NOT NULL AND CHAKU != ''
            GROUP BY TRAINER_NAME
            HAVING COUNT(*) >= 1
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
            
            print(f"馬印5,6分析結果: {len(df)}名の調教師")
            return df
            
        except Exception as e:
            print(f"馬印5,6分析エラー: {e}")
            return None
    
    def get_nine_month_trainers(self, target_date):
        """9か月間の成績で調教師取得"""
        try:
            # 9か月前の期間を計算
            target_dt = datetime.strptime(target_date, '%Y%m%d')
            start_dt = target_dt - timedelta(days=9*30)
            end_dt = target_dt - timedelta(days=1)
            
            start_date = start_dt.strftime('%Y%m%d')
            end_date = end_dt.strftime('%Y%m%d')
            
            print(f"9か月間分析期間: {start_date} ～ {end_date}")
            
            # 9か月間の成績を取得
            df = self.get_trainer_performance_period(start_date, end_date)
            
            if df is not None:
                print(f"9か月間分析結果: {len(df)}名の調教師")
                return df
            else:
                return None
                
        except Exception as e:
            print(f"9か月間分析エラー: {e}")
            return None
    
    def calculate_hit_rate_and_recovery(self, trainer_list, target_date):
        """的中率と回収率の計算"""
        try:
            # 対象日のレース結果を取得
            query = f"""
            SELECT 
                ChokyosiRyakusyo as TrainerName,
                KakuteiJyuni as FinishOrder,
                Odds as TanshoOdds,
                Fukasyokin as FukushoOdds
            FROM N_UMA_RACE
            WHERE (Year || MonthDay) = '{target_date}'
            AND ChokyosiRyakusyo IS NOT NULL AND ChokyosiRyakusyo != ''
            AND KakuteiJyuni IS NOT NULL AND KakuteiJyuni != ''
            """
            
            race_results = pd.read_sql_query(query, self.conn)
            
            if race_results.empty:
                print(f"対象日 {target_date} のレース結果が見つかりません")
                return None
            
            # 調教師リストとの照合
            target_trainers = set(trainer_list['TrainerName'].tolist())
            race_trainers = set(race_results['TrainerName'].tolist())
            
            common_trainers = target_trainers & race_trainers
            
            if not common_trainers:
                print("対象調教師がレースに参加していません")
                return None
            
            # 的中率と回収率の計算
            total_bets = len(common_trainers)
            hits = 0
            total_return = 0.0
            
            for trainer in common_trainers:
                trainer_races = race_results[race_results['TrainerName'] == trainer]
                
                for _, race in trainer_races.iterrows():
                    finish_order = race['FinishOrder']
                    tansho_odds = float(race['TanshoOdds']) if race['TanshoOdds'] and race['TanshoOdds'] != '0' else 0
                    fukusho_odds = float(race['FukushoOdds']) if race['FukushoOdds'] and race['FukushoOdds'] != '0' else 0
                    
                    # 的中判定（1着、2着、3着）
                    if finish_order in ['1', '2', '3']:
                        hits += 1
                        if finish_order == '1' and tansho_odds > 0:
                            total_return += tansho_odds
                        if finish_order in ['2', '3'] and fukusho_odds > 0:
                            total_return += fukusho_odds
            
            hit_rate = hits / total_bets if total_bets > 0 else 0
            recovery_rate = total_return / total_bets if total_bets > 0 else 0
            
            return {
                'total_bets': total_bets,
                'hits': hits,
                'hit_rate': hit_rate,
                'total_return': total_return,
                'recovery_rate': recovery_rate,
                'common_trainers': list(common_trainers)
            }
            
        except Exception as e:
            print(f"的中率・回収率計算エラー: {e}")
            return None
    
    def compare_methods(self, target_date):
        """2つの手法の比較"""
        print(f"=== 予想手法比較: {target_date} ===")
        
        try:
            # 手法1: 半年前の馬印5,6の優秀調教師
            print("\n--- 手法1: 半年前の馬印5,6の優秀調教師 ---")
            mark_trainers = self.get_mark5_mark6_trainers(target_date, months_back=6)
            
            if mark_trainers is not None:
                # 上位20名を選択
                top_mark_trainers = mark_trainers.head(20)
                print(f"選択された調教師: {len(top_mark_trainers)}名")
                print("上位5名:")
                for _, row in top_mark_trainers.head(5).iterrows():
                    print(f"  {row['TrainerName']}: 馬印スコア{row['MarkScore']:.2f}, 着順率{row['PlaceRate']:.2f}")
                
                # 的中率・回収率計算
                mark_results = self.calculate_hit_rate_and_recovery(top_mark_trainers, target_date)
            else:
                mark_results = None
            
            # 手法2: 9か月間の成績で調教師
            print("\n--- 手法2: 9か月間の成績で調教師 ---")
            nine_month_trainers = self.get_nine_month_trainers(target_date)
            
            if nine_month_trainers is not None:
                # 上位20名を選択（着順率順）
                top_nine_month_trainers = nine_month_trainers.sort_values('PlaceRate', ascending=False).head(20)
                print(f"選択された調教師: {len(top_nine_month_trainers)}名")
                print("上位5名:")
                for _, row in top_nine_month_trainers.head(5).iterrows():
                    print(f"  {row['TrainerName']}: 着順率{row['PlaceRate']:.2f}, レース数{row['TotalRaces']}")
                
                # 的中率・回収率計算
                nine_month_results = self.calculate_hit_rate_and_recovery(top_nine_month_trainers, target_date)
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
    
    def run_comparison_analysis(self, target_dates):
        """複数日の比較分析"""
        print("=== 複数日の比較分析開始 ===")
        
        results = []
        
        for target_date in target_dates:
            print(f"\n{'='*50}")
            print(f"分析日: {target_date}")
            print(f"{'='*50}")
            
            comparison_result = self.compare_methods(target_date)
            if comparison_result:
                results.append({
                    'date': target_date,
                    'mark_method': comparison_result['mark_method'],
                    'nine_month_method': comparison_result['nine_month_method']
                })
        
        # 全体の集計
        if results:
            print("\n=== 全体集計 ===")
            
            mark_hit_rates = []
            mark_recovery_rates = []
            nine_month_hit_rates = []
            nine_month_recovery_rates = []
            
            for result in results:
                if result['mark_method']:
                    mark_hit_rates.append(result['mark_method']['hit_rate'])
                    mark_recovery_rates.append(result['mark_method']['recovery_rate'])
                
                if result['nine_month_method']:
                    nine_month_hit_rates.append(result['nine_month_method']['hit_rate'])
                    nine_month_recovery_rates.append(result['nine_month_method']['recovery_rate'])
            
            if mark_hit_rates:
                print(f"手法1 (馬印5,6) 平均的中率: {np.mean(mark_hit_rates):.2%}")
                print(f"手法1 (馬印5,6) 平均回収率: {np.mean(mark_recovery_rates):.2%}")
            
            if nine_month_hit_rates:
                print(f"手法2 (9か月間) 平均的中率: {np.mean(nine_month_hit_rates):.2%}")
                print(f"手法2 (9か月間) 平均回収率: {np.mean(nine_month_recovery_rates):.2%}")
        
        return results

def main():
    """メイン実行"""
    comparison = TrainerPredictionComparison()
    
    if not comparison.connect():
        return
    
    try:
        # 対象日を設定（9/27と9/28）
        target_dates = ['20250927', '20250928']
        
        # 比較分析実行
        results = comparison.run_comparison_analysis(target_dates)
        
        if results:
            print("\n=== 分析完了 ===")
            print(f"分析日数: {len(results)}")
        else:
            print("分析に失敗しました")
    
    finally:
        comparison.disconnect()

if __name__ == "__main__":
    main()




