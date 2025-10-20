#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ランク別成績分析スクリプト
ランクごとの件数・的中率・ROIを集計
"""

import argparse
import sys
import os
import sqlite3
import pandas as pd
import json
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='ランク別成績分析')
    parser.add_argument('--date-from', required=True, help='分析開始日 (YYYY-MM-DD)')
    parser.add_argument('--date-to', required=True, help='分析終了日 (YYYY-MM-DD)')
    parser.add_argument('--scenario', default='PRE', help='シナリオ (PRE/LIVE)')
    parser.add_argument('--output-csv', help='CSV出力ファイルパス')
    
    args = parser.parse_args()
    
    print(f"[INFO] ランク別成績分析開始: {args.date_from} ～ {args.date_to} ({args.scenario})")
    
    try:
        # データベース接続
        ecore_db = os.path.join(os.path.dirname(__file__), '..', '..', 'ecore.db')
        predictions_db = os.path.join(os.path.dirname(__file__), '..', '..', 'predictions.db')
        
        if not os.path.exists(ecore_db):
            print(f"[ERROR] ecore.dbが見つかりません: {ecore_db}")
            return 1
            
        if not os.path.exists(predictions_db):
            print(f"[ERROR] predictions.dbが見つかりません: {predictions_db}")
            return 1
        
        ecore_conn = sqlite3.connect(ecore_db)
        pred_conn = sqlite3.connect(predictions_db)
        
        # 日付範囲を正規化
        date_from = args.date_from.replace('-', '')
        date_to = args.date_to.replace('-', '')
        
        # 予測データ取得
        pred_query = """
            SELECT Year, MonthDay, JyoCD, RaceNum, Umaban, WinScore, PlaceScore, 
                   InvestFlag, RankGrade
            FROM Predictions 
            WHERE Scenario = ? AND (Year || MonthDay) BETWEEN ? AND ?
            AND RankGrade IS NOT NULL
        """
        
        predictions_df = pd.read_sql_query(pred_query, pred_conn, 
                                         params=[args.scenario, date_from, date_to])
        
        if predictions_df.empty:
            print(f"[WARN] 分析対象の予測データが見つかりません")
            return 0
        
        print(f"[INFO] 予測データ数: {len(predictions_df)}")
        
        # ランク別分析
        rank_metrics = []
        
        for rank_grade in ['S', 'A', 'B', 'C', 'D', 'E']:
            rank_data = predictions_df[predictions_df['RankGrade'] == rank_grade]
            
            if len(rank_data) == 0:
                continue
            
            total_count = len(rank_data)
            invest_count = len(rank_data[rank_data['InvestFlag'] >= 1])
            
            # レース結果との突合
            win_hits = 0
            place_hits = 0
            total_win_payout = 0
            total_place_payout = 0
            joined_count = 0
            
            for _, pred in rank_data.iterrows():
                # レース結果を検索
                result_query = """
                    SELECT KakuteiJyuni, Honsyokin, Fukasyokin
                    FROM N_UMA_RACE 
                    WHERE Year = ? AND MonthDay = ? AND JyoCD = ? 
                    AND RaceNum = ? AND Umaban = ?
                """
                
                cursor = ecore_conn.cursor()
                cursor.execute(result_query, (
                    pred['Year'], pred['MonthDay'], pred['JyoCD'],
                    pred['RaceNum'], pred['Umaban']
                ))
                
                result = cursor.fetchone()
                if result:
                    joined_count += 1
                    kakutei_jyuni, honsyokin, fukasyokin = result
                    
                    # 単勝的中判定
                    if kakutei_jyuni == 1:
                        win_hits += 1
                        if honsyokin and str(honsyokin).isdigit():
                            total_win_payout += int(honsyokin) / 100.0
                    
                    # 複勝的中判定
                    if kakutei_jyuni in [1, 2, 3]:
                        place_hits += 1
                        if fukasyokin and str(fukasyokin).isdigit():
                            total_place_payout += int(fukasyokin) / 100.0
            
            # 指標計算
            win_hit_rate = (win_hits / joined_count * 100) if joined_count > 0 else 0
            place_hit_rate = (place_hits / joined_count * 100) if joined_count > 0 else 0
            
            # ROI計算（100円固定購入）
            total_investment = joined_count * 100
            win_roi = ((total_win_payout - total_investment) / total_investment * 100) if total_investment > 0 else -100
            place_roi = ((total_place_payout - total_investment) / total_investment * 100) if total_investment > 0 else -100
            
            rank_metrics.append({
                'RankGrade': rank_grade,
                'TotalCount': total_count,
                'InvestCount': invest_count,
                'JoinedCount': joined_count,
                'WinHits': win_hits,
                'WinHitRate': win_hit_rate,
                'WinROI': win_roi,
                'PlaceHits': place_hits,
                'PlaceHitRate': place_hit_rate,
                'PlaceROI': place_roi,
                'TotalInvestment': total_investment,
                'WinPayout': total_win_payout,
                'PlacePayout': total_place_payout
            })
        
        # 結果表示
        print(f"[INFO] === ランク別成績分析結果 ===")
        print(f"[INFO] 対象期間: {args.date_from} ～ {args.date_to}")
        print(f"[INFO] シナリオ: {args.scenario}")
        print()
        
        for metrics in rank_metrics:
            print(f"[INFO] === {metrics['RankGrade']}ランク ===")
            print(f"[INFO] 総件数: {metrics['TotalCount']}")
            print(f"[INFO] 投資件数: {metrics['InvestCount']}")
            print(f"[INFO] 結果突合: {metrics['JoinedCount']}")
            print(f"[INFO] 単勝的中: {metrics['WinHits']}件 ({metrics['WinHitRate']:.1f}%)")
            print(f"[INFO] 単勝ROI: {metrics['WinROI']:.1f}%")
            print(f"[INFO] 複勝的中: {metrics['PlaceHits']}件 ({metrics['PlaceHitRate']:.1f}%)")
            print(f"[INFO] 複勝ROI: {metrics['PlaceROI']:.1f}%")
            print()
        
        # CSV出力
        if args.output_csv:
            # 出力ディレクトリの作成
            output_dir = os.path.dirname(args.output_csv)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            df = pd.DataFrame(rank_metrics)
            df.to_csv(args.output_csv, index=False, encoding='utf-8-sig')
            print(f"[INFO] CSV出力完了: {args.output_csv}")
        
        ecore_conn.close()
        pred_conn.close()
        
        print(f"[OK] ランク別成績分析完了")
        return 0
        
    except Exception as e:
        print(f"[ERROR] 分析実行エラー: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

