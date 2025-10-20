#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正しいオッズデータの取得元を特定
"""
import sqlite3
import pandas as pd
import sys
import os
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def find_correct_odds_source():
    """正しいオッズデータの取得元を特定"""
    db_path = "ecore.db"
    
    try:
        conn = sqlite3.connect(db_path)
        print("データベース接続成功")
        
        # 1. データベース内の全テーブルを確認
        print("=== データベース内の全テーブル確認 ===")
        
        query_tables = """
        SELECT name FROM sqlite_master WHERE type='table' ORDER BY name
        """
        
        tables = pd.read_sql_query(query_tables, conn)
        print(f"データベース内のテーブル数: {len(tables)}")
        
        # オッズ関連のテーブルを探す
        odds_tables = tables[tables['name'].str.contains('odds|odds|オッズ|ODDS', case=False, na=False)]
        if not odds_tables.empty:
            print("オッズ関連のテーブル:")
            for _, row in odds_tables.iterrows():
                print(f"  {row['name']}")
        
        # 2. HORSE_MARKSテーブルのオッズデータを確認
        print(f"\n=== HORSE_MARKSテーブルのオッズデータ確認 ===")
        
        query_horse_marks_odds = """
        SELECT 
            SourceDate,
            JyoCD,
            RaceNum,
            HorseName,
            TRAINER_NAME as TrainerName,
            CHAKU as FinishOrder,
            TANSHO_ODDS as TanshoOdds,
            FUKUSHO_ODDS as FukushoOdds
        FROM HORSE_MARKS
        WHERE SourceDate = '20250928'
        AND JyoCD = '06'
        AND RaceNum = '11'
        AND HorseName = 'ウインカーネリアン'
        """
        
        horse_marks_odds = pd.read_sql_query(query_horse_marks_odds, conn)
        
        if not horse_marks_odds.empty:
            print("HORSE_MARKSテーブルのオッズデータ:")
            for _, row in horse_marks_odds.iterrows():
                print(f"  {row['HorseName']} ({row['TrainerName']}) - 着順:{row['FinishOrder']} 単勝:{row['TanshoOdds']} 複勝:{row['FukushoOdds']}")
        else:
            print("HORSE_MARKSテーブルにウインカーネリアンのデータが見つかりません")
        
        # 3. 他のテーブルでオッズデータを探す
        print(f"\n=== 他のテーブルでオッズデータを探す ===")
        
        # テーブル名に'odds'が含まれるものを探す
        for _, table_row in tables.iterrows():
            table_name = table_row['name']
            if 'odds' in table_name.lower():
                print(f"テーブル: {table_name}")
                
                # テーブルの構造を確認
                query_table_schema = f"PRAGMA table_info({table_name})"
                schema = pd.read_sql_query(query_table_schema, conn)
                
                print(f"  構造:")
                for _, col_row in schema.iterrows():
                    print(f"    {col_row['name']}: {col_row['type']}")
                
                # 9月28日のデータを確認
                query_table_data = f"""
                SELECT * FROM {table_name} 
                WHERE (Year || MonthDay) = '20250928' 
                AND JyoCD = '06' 
                AND RaceNum = '11'
                LIMIT 5
                """
                
                try:
                    table_data = pd.read_sql_query(query_table_data, conn)
                    if not table_data.empty:
                        print(f"  データ例:")
                        for _, row in table_data.iterrows():
                            print(f"    {row.to_dict()}")
                except:
                    print(f"  データ取得エラー")
        
        # 4. 正しいオッズデータの取得方法を提案
        print(f"\n=== 正しいオッズデータの取得方法 ===")
        print("1. TARGET frontier JVのオッズデータを使用")
        print("2. データベースのオッズデータは信頼できない")
        print("3. 実際のオッズデータを手動で入力する必要がある")
        
        conn.close()
        print("\n=== 正しいオッズデータの取得元特定完了 ===")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_correct_odds_source()




