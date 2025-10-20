#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Predictions Database
予想データベースの構造を確認
"""

import sqlite3
import pandas as pd
from datetime import datetime

def check_predictions_db():
    """予想データベースの構造と内容を確認"""
    
    print("=== Predictions Database Check ===")
    print()
    
    try:
        conn = sqlite3.connect('predictions.db')
        cursor = conn.cursor()
        
        # 1. テーブル一覧
        print("1. テーブル一覧")
        print("=" * 50)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            print(f"- {table[0]}")
        
        print()
        
        # 2. Predictionsテーブルの構造
        if any('Predictions' in table[0] for table in tables):
            print("2. Predictionsテーブルの構造")
            print("=" * 50)
            cursor.execute("PRAGMA table_info(Predictions);")
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"- {col[1]} ({col[2]})")
            
            print()
            
            # 3. データ件数
            print("3. データ件数")
            print("=" * 50)
            cursor.execute("SELECT COUNT(*) FROM Predictions;")
            total_count = cursor.fetchone()[0]
            print(f"総件数: {total_count:,}件")
            
            # シナリオ別件数
            cursor.execute("SELECT Scenario, COUNT(*) FROM Predictions GROUP BY Scenario;")
            scenario_counts = cursor.fetchall()
            for scenario, count in scenario_counts:
                print(f"{scenario}: {count:,}件")
            
            print()
            
            # 4. 投資対象の確認
            print("4. 投資対象の確認")
            print("=" * 50)
            cursor.execute("SELECT COUNT(*) FROM Predictions WHERE InvestFlag = 1;")
            invest_count = cursor.fetchone()[0]
            print(f"投資対象: {invest_count:,}件")
            
            # 日付別投資対象
            cursor.execute("""
                SELECT Date, COUNT(*) 
                FROM Predictions 
                WHERE InvestFlag = 1 
                GROUP BY Date 
                ORDER BY Date;
            """)
            date_invest_counts = cursor.fetchall()
            for date, count in date_invest_counts:
                print(f"{date}: {count}件")
            
            print()
            
            # 5. サンプルデータ
            print("5. サンプルデータ（投資対象）")
            print("=" * 50)
            cursor.execute("""
                SELECT Date, JyoCD, RaceNum, UmaNum, WinScore, Odds, InvestFlag
                FROM Predictions 
                WHERE InvestFlag = 1 
                ORDER BY Date, JyoCD, RaceNum, UmaNum
                LIMIT 10;
            """)
            sample_data = cursor.fetchall()
            
            for row in sample_data:
                print(f"{row[0]} {row[1]} {row[2]}R {row[3]}番 - WinScore: {row[4]:.3f}, オッズ: {row[5]}, 投資: {row[6]}")
            
            print()
            
            # 6. 統計情報
            print("6. 統計情報")
            print("=" * 50)
            cursor.execute("""
                SELECT 
                    MIN(WinScore) as min_win_score,
                    MAX(WinScore) as max_win_score,
                    AVG(WinScore) as avg_win_score,
                    MIN(Odds) as min_odds,
                    MAX(Odds) as max_odds,
                    AVG(Odds) as avg_odds
                FROM Predictions 
                WHERE InvestFlag = 1;
            """)
            stats = cursor.fetchone()
            
            if stats:
                print(f"WinScore - 最小: {stats[0]:.3f}, 最大: {stats[1]:.3f}, 平均: {stats[2]:.3f}")
                print(f"オッズ - 最小: {stats[3]:.1f}, 最大: {stats[4]:.1f}, 平均: {stats[5]:.1f}")
        
        conn.close()
        
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    check_predictions_db()


