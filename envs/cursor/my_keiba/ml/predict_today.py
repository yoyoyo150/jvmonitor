#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
今日の予測実行スクリプト（6段階ランクシステム）
JVMonitorから呼び出される予測機能
"""

import argparse
import sys
import os
import sqlite3
import pandas as pd
import json
from datetime import datetime

def load_rank_rules():
    """ランクルール設定の読み込み"""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'rank_rules.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_rank_grade(uma_data, scenario, rank_rules):
    """ランクグレードの計算"""
    if scenario not in rank_rules:
        return 'E'
    
    rules = rank_rules[scenario]['rules']
    
    # データの取得（実際のデータベースから取得する場合はここで実装）
    win_score = uma_data.get('win_score', 0.0)
    m5_value = uma_data.get('m5_value', 10.0)
    zi_value = uma_data.get('zi_value', 0)
    zm_value = uma_data.get('zm_value', 100)
    trainer_win_rate = uma_data.get('trainer_win_rate', 0.0)
    odds = uma_data.get('odds', 100.0)
    
    # ランク判定（S→A→B→C→D→Eの順で判定）
    for grade in ['S', 'A', 'B', 'C', 'D', 'E']:
        if grade not in rules:
            continue
            
        conditions = rules[grade]['conditions']
        
        # 条件チェック
        if (win_score >= conditions.get('win_score_min', 0.0) and
            m5_value <= conditions.get('m5_max', 10.0) and
            zi_value >= conditions.get('zi_min', 0) and
            zm_value <= conditions.get('zm_max', 100) and
            trainer_win_rate >= conditions.get('trainer_win_rate_min', 0.0)):
            
            # LIVEシナリオの場合はオッズ条件もチェック
            if scenario == 'LIVE':
                if (odds >= conditions.get('odds_min', 2.0) and
                    odds <= conditions.get('odds_max', 100.0)):
                    return grade
            else:
                return grade
    
    return 'E'

def main():
    parser = argparse.ArgumentParser(description='今日の予測実行（6段階ランクシステム）')
    parser.add_argument('--date', required=True, help='予測対象日 (YYYY-MM-DD)')
    parser.add_argument('--scenario', default='PRE', help='シナリオ (PRE/LIVE)')
    
    args = parser.parse_args()
    
    # 日付を正規化
    date_str = args.date.replace('-', '')
    year = date_str[:4]
    month_day = date_str[4:]
    
    print(f"[INFO] 予測実行開始: {args.date} ({args.scenario})")
    
    # ランクルール読み込み
    try:
        rank_rules = load_rank_rules()
        investment_grades = rank_rules[args.scenario]['investment_grades']
        print(f"[INFO] 投資対象ランク: {', '.join(investment_grades)}")
    except Exception as e:
        print(f"[ERROR] ランクルール読み込みエラー: {e}")
        return 1
    
    try:
        # データベース接続
        db_path = os.path.join(os.path.dirname(__file__), '..', 'ecore.db')
        if not os.path.exists(db_path):
            print(f"[ERROR] データベースが見つかりません: {db_path}")
            return 1
            
        conn = sqlite3.connect(db_path)
        
        # レースデータ確認
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM N_RACE 
            WHERE Year = ? AND MonthDay = ?
        """, (year, month_day))
        
        race_count = cursor.fetchone()[0]
        
        if race_count == 0:
            print(f"[WARN] 対象日のレースデータが見つかりません: {args.date}")
            return 0
            
        print(f"[INFO] レース数: {race_count}")
        
        # 出走馬データ確認
        cursor.execute("""
            SELECT COUNT(*) FROM N_UMA_RACE 
            WHERE Year = ? AND MonthDay = ?
        """, (year, month_day))
        
        uma_count = cursor.fetchone()[0]
        print(f"[INFO] 出走馬数: {uma_count}")
        
        if uma_count == 0:
            print(f"[WARN] 対象日の出走馬データが見つかりません: {args.date}")
            return 0
        
        # 予測データをpredictions.dbに保存
        predictions_db = os.path.join(os.path.dirname(__file__), '..', 'predictions.db')
        pred_conn = sqlite3.connect(predictions_db)
        
        # 既存の予測データを削除
        pred_conn.execute("""
            DELETE FROM Predictions 
            WHERE Year = ? AND MonthDay = ? AND Scenario = ?
        """, (year, month_day, args.scenario))
        
        # 予測データを生成
        sample_predictions = []
        rank_distribution = {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
        
        cursor.execute("""
            SELECT DISTINCT JyoCD, RaceNum, Umaban 
            FROM N_UMA_RACE 
            WHERE Year = ? AND MonthDay = ?
            ORDER BY JyoCD, RaceNum, Umaban
        """, (year, month_day))
        
        for row in cursor.fetchall():
            jyo_cd, race_num, uma_ban = row
            
            # サンプル予測データ生成（実際の予測ロジックに置き換え）
            win_score = 0.2 + (hash(f"{jyo_cd}{race_num}{uma_ban}") % 100) / 500.0
            m5_value = 1.0 + (hash(f"m5{jyo_cd}{race_num}{uma_ban}") % 50) / 10.0
            zi_value = 50 + (hash(f"zi{jyo_cd}{race_num}{uma_ban}") % 30)
            zm_value = 10 + (hash(f"zm{jyo_cd}{race_num}{uma_ban}") % 40)
            trainer_win_rate = 0.05 + (hash(f"tr{jyo_cd}{race_num}{uma_ban}") % 20) / 100.0
            odds = 2.0 + (hash(f"odds{jyo_cd}{race_num}{uma_ban}") % 200) / 10.0
            
            uma_data = {
                'win_score': win_score,
                'm5_value': m5_value,
                'zi_value': zi_value,
                'zm_value': zm_value,
                'trainer_win_rate': trainer_win_rate,
                'odds': odds
            }
            
            # ランクグレード計算
            rank_grade = calculate_rank_grade(uma_data, args.scenario, rank_rules)
            rank_distribution[rank_grade] += 1
            
            # 投資フラグ判定
            invest_flag = 1 if rank_grade in investment_grades else 0
            
            place_score = win_score + 0.1
            
            sample_predictions.append((
                year, month_day, jyo_cd, race_num, uma_ban,
                args.scenario, win_score, place_score, odds, invest_flag,
                m5_value, trainer_win_rate, 'sample_hash', 'v2.0', rank_grade
            ))
        
        # 予測データを挿入
        pred_conn.executemany("""
            INSERT INTO Predictions 
            (Year, MonthDay, JyoCD, RaceNum, Umaban, Scenario, WinScore, PlaceScore, 
             Odds, InvestFlag, M5Value, TrainerScore, FeaturesHash, ModelVersion, RankGrade)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_predictions)
        
        pred_conn.commit()
        pred_conn.close()
        conn.close()
        
        # 結果表示
        invest_count = sum(1 for _, _, _, _, _, _, _, _, _, flag, _, _, _, _, _ in sample_predictions if flag == 1)
        
        print(f"[INFO] === ランク分布 ===")
        for grade in ['S', 'A', 'B', 'C', 'D', 'E']:
            count = rank_distribution[grade]
            marker = "★" if grade in investment_grades else " "
            print(f"[INFO] {marker} {grade}ランク: {count}件")
        
        print(f"[INFO] 投資候補数: {invest_count}件")
        print(f"[OK] 予測データを保存しました: {len(sample_predictions)}件")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] 予測実行エラー: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

