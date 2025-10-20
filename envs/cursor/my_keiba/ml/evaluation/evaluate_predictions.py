#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
予測評価スクリプト
JVMonitorから呼び出される評価機能
"""

import argparse
import sys
import os
import sqlite3
import pandas as pd
import json
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='予測評価実行')
    parser.add_argument('--date-from', required=True, help='評価開始日 (YYYY-MM-DD)')
    parser.add_argument('--date-to', required=True, help='評価終了日 (YYYY-MM-DD)')
    parser.add_argument('--scenario', default='PRE', help='シナリオ (PRE/LIVE)')
    parser.add_argument('--output-json', help='JSON出力ファイルパス')
    
    args = parser.parse_args()
    
    print(f"[INFO] 評価実行開始: {args.date_from} ～ {args.date_to} ({args.scenario})")
    
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
            SELECT Year, MonthDay, JyoCD, RaceNum, Umaban, WinScore, PlaceScore, InvestFlag
            FROM Predictions 
            WHERE Scenario = ? AND (Year || MonthDay) BETWEEN ? AND ?
        """
        
        predictions_df = pd.read_sql_query(pred_query, pred_conn, 
                                         params=[args.scenario, date_from, date_to])
        
        if predictions_df.empty:
            print(f"[WARN] 評価対象の予測データが見つかりません")
            return 0
        
        print(f"[INFO] 予測データ数: {len(predictions_df)}")
        
        # 投資候補数
        invest_selections = len(predictions_df[predictions_df['InvestFlag'] >= 1])
        print(f"[INFO] 投資候補数: {invest_selections}")
        
        # レース結果データと突合
        joined_results = 0
        win_hits = 0
        place_hits = 0
        total_win_payout = 0
        total_place_payout = 0
        
        for _, pred in predictions_df.iterrows():
            if pred['InvestFlag'] < 1:
                continue
                
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
                joined_results += 1
                kakutei_jyuni, honsyokin, fukasyokin = result
                
                # 単勝的中判定
                if kakutei_jyuni == 1:
                    win_hits += 1
                    if honsyokin:
                        total_win_payout += honsyokin / 100.0  # 円に変換
                
                # 複勝的中判定
                if kakutei_jyuni in [1, 2, 3]:
                    place_hits += 1
                    if fukasyokin:
                        total_place_payout += fukasyokin / 100.0  # 円に変換
        
        # 指標計算
        total_predictions = len(predictions_df)
        win_hit_rate = (win_hits / invest_selections * 100) if invest_selections > 0 else 0
        place_hit_rate = (place_hits / invest_selections * 100) if invest_selections > 0 else 0
        
        # ROI計算（100円固定購入）
        total_investment = invest_selections * 100
        win_roi = ((total_win_payout - total_investment) / total_investment * 100) if total_investment > 0 else -100
        place_roi = ((total_place_payout - total_investment) / total_investment * 100) if total_investment > 0 else -100
        
        # 結果表示
        print(f"[INFO] === 評価結果サマリー ===")
        print(f"[INFO] 使用シナリオ: {args.scenario}")
        print(f"[INFO] 対象期間: {args.date_from} ～ {args.date_to}")
        print(f"[INFO] 予測データ数: {total_predictions}")
        print(f"[INFO] 投資候補数: {invest_selections}")
        print(f"[INFO] 結果突合数: {joined_results}")
        print(f"[INFO] 単勝的中数: {win_hits}")
        print(f"[INFO] 単勝的中率: {win_hit_rate:.1f}%")
        print(f"[INFO] 単勝ROI: {win_roi:.1f}%")
        print(f"[INFO] 複勝的中数: {place_hits}")
        print(f"[INFO] 複勝的中率: {place_hit_rate:.1f}%")
        print(f"[INFO] 複勝ROI: {place_roi:.1f}%")
        print(f"[INFO] 総投資額: {total_investment:,}円")
        print(f"[INFO] 総回収額: {total_win_payout + total_place_payout:.0f}円")
        
        # JSON出力
        result_data = {
            "scenario": args.scenario,
            "date_from": args.date_from,
            "date_to": args.date_to,
            "total_predictions": total_predictions,
            "invest_selections": invest_selections,
            "joined_results": joined_results,
            "win_hits": win_hits,
            "win_hit_rate": win_hit_rate / 100.0,
            "win_roi": win_roi / 100.0,
            "place_hits": place_hits,
            "place_hit_rate": place_hit_rate / 100.0,
            "place_roi": place_roi / 100.0,
            "total_investment": total_investment,
            "total_win_payout": total_win_payout,
            "total_place_payout": total_place_payout,
            "evaluation_type": "確定結果比較（前日予想検証）"
        }
        
        if args.output_json:
            with open(args.output_json, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            print(f"[INFO] 評価結果を保存しました: {args.output_json}")
        
        ecore_conn.close()
        pred_conn.close()
        
        print(f"[OK] 評価完了")
        return 0
        
    except Exception as e:
        print(f"[ERROR] 評価実行エラー: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
