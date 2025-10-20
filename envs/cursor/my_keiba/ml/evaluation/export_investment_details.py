#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投資対象馬の詳細情報出力スクリプト
具体的に何R何番を買うのかを明確に表示
"""

import argparse
import sys
import os
import sqlite3
import pandas as pd
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='投資対象馬の詳細情報出力')
    parser.add_argument('--date-from', required=True, help='開始日 (YYYY-MM-DD)')
    parser.add_argument('--date-to', required=True, help='終了日 (YYYY-MM-DD)')
    parser.add_argument('--scenario', default='PRE', help='シナリオ (PRE/LIVE)')
    parser.add_argument('--output-txt', help='テキスト出力ファイルパス')
    
    args = parser.parse_args()
    
    print(f"[INFO] 投資対象馬詳細出力: {args.date_from} ～ {args.date_to} ({args.scenario})")
    
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
        
        # 投資対象の予測データ取得
        pred_query = """
            SELECT Year, MonthDay, JyoCD, RaceNum, Umaban, WinScore, PlaceScore, 
                   RankGrade, M5Value, TrainerScore, Odds
            FROM Predictions 
            WHERE Scenario = ? AND (Year || MonthDay) BETWEEN ? AND ?
            AND InvestFlag >= 1
            ORDER BY Year, MonthDay, JyoCD, RaceNum, Umaban
        """
        
        predictions_df = pd.read_sql_query(pred_query, pred_conn, 
                                         params=[args.scenario, date_from, date_to])
        
        if predictions_df.empty:
            print(f"[WARN] 投資対象の予測データが見つかりません")
            return 0
        
        print(f"[INFO] 投資対象数: {len(predictions_df)}")
        
        # 馬名と結果を取得
        investment_details = []
        
        for _, pred in predictions_df.iterrows():
            # 馬名とレース情報を取得
            horse_query = """
                SELECT ur.Bamei, ur.KakuteiJyuni, ur.Honsyokin, ur.Fukasyokin,
                       r.Hondai, ur.Odds as RealOdds
                FROM N_UMA_RACE ur
                LEFT JOIN N_RACE r ON ur.Year = r.Year AND ur.MonthDay = r.MonthDay 
                                   AND ur.JyoCD = r.JyoCD AND ur.RaceNum = r.RaceNum
                WHERE ur.Year = ? AND ur.MonthDay = ? AND ur.JyoCD = ? 
                AND ur.RaceNum = ? AND ur.Umaban = ?
            """
            
            cursor = ecore_conn.cursor()
            cursor.execute(horse_query, (
                pred['Year'], pred['MonthDay'], pred['JyoCD'],
                pred['RaceNum'], pred['Umaban']
            ))
            
            result = cursor.fetchone()
            if result:
                bamei, kakutei_jyuni, honsyokin, fukasyokin, race_name, real_odds = result
                
                # 払戻金を円に変換
                win_payout = int(honsyokin) / 100.0 if honsyokin and str(honsyokin).isdigit() else 0
                place_payout = int(fukasyokin) / 100.0 if fukasyokin and str(fukasyokin).isdigit() else 0
                
                # 的中判定
                win_hit = "○" if kakutei_jyuni == 1 else "×"
                place_hit = "○" if kakutei_jyuni in [1, 2, 3] else "×"
                
                investment_details.append({
                    'date': f"{pred['Year']}/{pred['MonthDay'][0:2]}/{pred['MonthDay'][2:4]}",
                    'race_info': f"{pred['JyoCD']}{int(pred['RaceNum']):02d}R",
                    'umaban': f"{int(pred['Umaban']):02d}番",
                    'bamei': bamei or "不明",
                    'race_name': race_name or "不明",
                    'rank_grade': pred['RankGrade'],
                    'win_score': pred['WinScore'],
                    'real_odds': real_odds or 0,
                    'kakutei_jyuni': kakutei_jyuni or 99,
                    'win_hit': win_hit,
                    'place_hit': place_hit,
                    'win_payout': win_payout,
                    'place_payout': place_payout
                })
        
        # 結果表示
        output_lines = []
        output_lines.append("=" * 80)
        output_lines.append("投資対象馬 詳細リスト")
        output_lines.append(f"期間: {args.date_from} ～ {args.date_to}")
        output_lines.append(f"シナリオ: {args.scenario}")
        output_lines.append("=" * 80)
        output_lines.append("")
        
        current_date = ""
        total_investment = 0
        total_win_payout = 0
        total_place_payout = 0
        
        for detail in investment_details:
            if detail['date'] != current_date:
                if current_date:
                    output_lines.append("")
                current_date = detail['date']
                output_lines.append(f"■ {current_date}")
                output_lines.append("-" * 60)
            
            # 投資情報
            race_info = f"{detail['race_info']} {detail['umaban']} {detail['bamei']}"
            rank_info = f"[{detail['rank_grade']}ランク]"
            score_info = f"予想スコア:{detail['win_score']:.3f}"
            odds_info = f"実際オッズ:{detail['real_odds']:.1f}倍" if detail['real_odds'] > 0 else "オッズ不明"
            
            output_lines.append(f"  {race_info:<30} {rank_info} {score_info} {odds_info}")
            
            # 結果情報
            jyuni = int(detail['kakutei_jyuni']) if detail['kakutei_jyuni'] else 99
            result_info = f"着順:{jyuni:2d}位"
            win_result = f"単勝{detail['win_hit']} {detail['win_payout']:>6.0f}円" if detail['win_payout'] > 0 else f"単勝{detail['win_hit']}    0円"
            place_result = f"複勝{detail['place_hit']} {detail['place_payout']:>6.0f}円" if detail['place_payout'] > 0 else f"複勝{detail['place_hit']}    0円"
            
            output_lines.append(f"    → {result_info} | {win_result} | {place_result}")
            output_lines.append("")
            
            # 合計計算
            total_investment += 100  # 100円固定
            total_win_payout += detail['win_payout']
            total_place_payout += detail['place_payout']
        
        # サマリー
        win_roi = ((total_win_payout - total_investment) / total_investment * 100) if total_investment > 0 else -100
        place_roi = ((total_place_payout - total_investment) / total_investment * 100) if total_investment > 0 else -100
        
        output_lines.append("=" * 80)
        output_lines.append("投資成績サマリー")
        output_lines.append("=" * 80)
        output_lines.append(f"投資対象数: {len(investment_details)}頭")
        output_lines.append(f"総投資額: {total_investment:,}円 (100円×{len(investment_details)}頭)")
        output_lines.append(f"単勝回収額: {total_win_payout:,.0f}円 (ROI: {win_roi:+.1f}%)")
        output_lines.append(f"複勝回収額: {total_place_payout:,.0f}円 (ROI: {place_roi:+.1f}%)")
        output_lines.append("")
        output_lines.append("※ 各馬100円ずつ単勝・複勝に投資した場合の計算")
        output_lines.append("=" * 80)
        
        # 画面出力
        for line in output_lines:
            print(line)
        
        # ファイル出力
        if args.output_txt:
            output_dir = os.path.dirname(args.output_txt)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            with open(args.output_txt, 'w', encoding='utf-8') as f:
                f.write('\n'.join(output_lines))
            
            print(f"[INFO] 詳細リストを保存しました: {args.output_txt}")
        
        ecore_conn.close()
        pred_conn.close()
        
        print(f"[OK] 投資対象馬詳細出力完了")
        return 0
        
    except Exception as e:
        print(f"[ERROR] 出力エラー: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
