#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
オッズデータの確認
正しいオッズデータの取得方法を確認
"""
import sqlite3
import pandas as pd
import sys
import os
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def check_odds_data():
    """オッズデータの確認"""
    db_path = "ecore.db"
    
    try:
        conn = sqlite3.connect(db_path)
        print("データベース接続成功")
        
        # 1. 9月28日中山11Rの詳細データを確認
        print("=== 9月28日中山11Rの詳細データ確認 ===")
        
        query_928_detail = """
        SELECT 
            Year || MonthDay as Date,
            JyoCD,
            RaceNum,
            Bamei as HorseName,
            ChokyosiRyakusyo as TrainerName,
            KakuteiJyuni as FinishOrder,
            Odds as TanshoOdds,
            Fukasyokin as FukushoOdds,
            Ninki as NinkiRank
        FROM N_UMA_RACE
        WHERE (Year || MonthDay) = '20250928'
        AND JyoCD = '06'
        AND RaceNum = '11'
        ORDER BY Umaban
        """
        
        detail_928 = pd.read_sql_query(query_928_detail, conn)
        
        if not detail_928.empty:
            print(f"9月28日中山11R: {len(detail_928)}頭")
            for _, row in detail_928.iterrows():
                print(f"  {row['HorseName']} ({row['TrainerName']}) - 着順:{row['FinishOrder']} 単勝:{row['TanshoOdds']} 複勝:{row['FukushoOdds']} 人気:{row['NinkiRank']}")
        else:
            print("9月28日中山11Rのデータが見つかりません")
        
        # 2. ウインカーネリアンの詳細データを確認
        print(f"\n=== ウインカーネリアンの詳細データ確認 ===")
        
        query_winner = """
        SELECT 
            Year || MonthDay as Date,
            JyoCD,
            RaceNum,
            Bamei as HorseName,
            ChokyosiRyakusyo as TrainerName,
            KakuteiJyuni as FinishOrder,
            Odds as TanshoOdds,
            Fukasyokin as FukushoOdds,
            Ninki as NinkiRank
        FROM N_UMA_RACE
        WHERE (Year || MonthDay) = '20250928'
        AND JyoCD = '06'
        AND RaceNum = '11'
        AND Bamei = 'ウインカーネリアン'
        """
        
        winner_data = pd.read_sql_query(query_winner, conn)
        
        if not winner_data.empty:
            print("ウインカーネリアンの詳細データ:")
            for _, row in winner_data.iterrows():
                print(f"  {row['HorseName']} ({row['TrainerName']}) - 着順:{row['FinishOrder']} 単勝:{row['TanshoOdds']} 複勝:{row['FukushoOdds']} 人気:{row['NinkiRank']}")
        else:
            print("ウインカーネリアンのデータが見つかりません")
        
        # 3. データベースのテーブル構造を確認
        print(f"\n=== データベースのテーブル構造確認 ===")
        
        query_schema = """
        PRAGMA table_info(N_UMA_RACE)
        """
        
        schema = pd.read_sql_query(query_schema, conn)
        print("N_UMA_RACEテーブルの構造:")
        for _, row in schema.iterrows():
            print(f"  {row['name']}: {row['type']}")
        
        # 4. オッズデータの分布を確認
        print(f"\n=== オッズデータの分布確認 ===")
        
        query_odds_distribution = """
        SELECT 
            Odds as TanshoOdds,
            Fukasyokin as FukushoOdds,
            COUNT(*) as Count
        FROM N_UMA_RACE
        WHERE (Year || MonthDay) = '20250928'
        AND JyoCD = '06'
        AND RaceNum = '11'
        GROUP BY Odds, Fukasyokin
        ORDER BY Count DESC
        """
        
        odds_distribution = pd.read_sql_query(query_odds_distribution, conn)
        print("オッズデータの分布:")
        for _, row in odds_distribution.iterrows():
            print(f"  単勝:{row['TanshoOdds']} 複勝:{row['FukushoOdds']} 件数:{row['Count']}")
        
        # 5. 正しいオッズデータの取得方法を確認
        print(f"\n=== 正しいオッズデータの取得方法確認 ===")
        
        # 複勝オッズが1250円（12.5倍）の馬を探す
        query_correct_odds = """
        SELECT 
            Bamei as HorseName,
            ChokyosiRyakusyo as TrainerName,
            KakuteiJyuni as FinishOrder,
            Odds as TanshoOdds,
            Fukasyokin as FukushoOdds
        FROM N_UMA_RACE
        WHERE (Year || MonthDay) = '20250928'
        AND JyoCD = '06'
        AND RaceNum = '11'
        AND (Fukasyokin LIKE '%1250%' OR Fukasyokin LIKE '%12.5%' OR Fukasyokin = '1250')
        """
        
        correct_odds = pd.read_sql_query(query_correct_odds, conn)
        
        if not correct_odds.empty:
            print("複勝オッズ1250円の馬:")
            for _, row in correct_odds.iterrows():
                print(f"  {row['HorseName']} ({row['TrainerName']}) - 着順:{row['FinishOrder']} 単勝:{row['TanshoOdds']} 複勝:{row['FukushoOdds']}")
        else:
            print("複勝オッズ1250円の馬が見つかりません")
        
        conn.close()
        print("\n=== オッズデータ確認完了 ===")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_odds_data()