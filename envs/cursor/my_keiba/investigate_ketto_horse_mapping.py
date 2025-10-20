#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
血統番号と馬名の対応関係調査スクリプト
ecore.dbで血統番号と馬名の対応を確認
"""
import sqlite3
import pandas as pd
import sys

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def investigate_ketto_horse_mapping():
    """血統番号と馬名の対応関係を調査"""
    print("=== 血統番号と馬名の対応関係調査開始 ===")
    
    try:
        conn = sqlite3.connect('ecore.db')
        
        # 1. N_UMAテーブルから血統番号と馬名の対応を取得
        print("\n--- N_UMAテーブルから血統番号と馬名の対応 ---")
        query_uma = """
        SELECT 
            KettoNum,
            Bamei,
            BirthDate,
            SexCD,
            HinsyuCD
        FROM N_UMA 
        WHERE KettoNum IS NOT NULL 
        AND Bamei IS NOT NULL
        ORDER BY KettoNum
        LIMIT 10
        """
        df_uma = pd.read_sql_query(query_uma, conn)
        print(f"レコード数: {len(df_uma)}")
        print(df_uma.to_string(index=False))
        
        # 2. N_UMA_RACEテーブルから血統番号と馬名の対応を取得
        print("\n--- N_UMA_RACEテーブルから血統番号と馬名の対応 ---")
        query_uma_race = """
        SELECT 
            KettoNum,
            Bamei,
            Year || MonthDay as RaceDate,
            JyoCD,
            RaceNum
        FROM N_UMA_RACE 
        WHERE KettoNum IS NOT NULL 
        AND Bamei IS NOT NULL
        ORDER BY RaceDate DESC
        LIMIT 10
        """
        df_uma_race = pd.read_sql_query(query_uma_race, conn)
        print(f"レコード数: {len(df_uma_race)}")
        print(df_uma_race.to_string(index=False))
        
        # 3. 血統番号の重複チェック
        print("\n--- 血統番号の重複チェック ---")
        query_duplicate_ketto = """
        SELECT 
            KettoNum,
            COUNT(*) as count,
            GROUP_CONCAT(DISTINCT Bamei) as horse_names
        FROM N_UMA_RACE 
        WHERE KettoNum IS NOT NULL 
        AND Bamei IS NOT NULL
        GROUP BY KettoNum
        HAVING COUNT(*) > 1
        ORDER BY count DESC
        LIMIT 10
        """
        df_duplicate = pd.read_sql_query(query_duplicate_ketto, conn)
        print(f"重複する血統番号数: {len(df_duplicate)}")
        if not df_duplicate.empty:
            print(df_duplicate.to_string(index=False))
        
        # 4. 馬名の重複チェック
        print("\n--- 馬名の重複チェック ---")
        query_duplicate_horse = """
        SELECT 
            Bamei,
            COUNT(*) as count,
            GROUP_CONCAT(DISTINCT KettoNum) as ketto_nums
        FROM N_UMA_RACE 
        WHERE KettoNum IS NOT NULL 
        AND Bamei IS NOT NULL
        GROUP BY Bamei
        HAVING COUNT(*) > 1
        ORDER BY count DESC
        LIMIT 10
        """
        df_duplicate_horse = pd.read_sql_query(query_duplicate_horse, conn)
        print(f"重複する馬名数: {len(df_duplicate_horse)}")
        if not df_duplicate_horse.empty:
            print(df_duplicate_horse.to_string(index=False))
        
        # 5. 血統番号の形式確認
        print("\n--- 血統番号の形式確認 ---")
        query_ketto_format = """
        SELECT 
            KettoNum,
            LENGTH(KettoNum) as length,
            COUNT(*) as count
        FROM N_UMA_RACE 
        WHERE KettoNum IS NOT NULL 
        GROUP BY KettoNum, LENGTH(KettoNum)
        ORDER BY count DESC
        LIMIT 10
        """
        df_ketto_format = pd.read_sql_query(query_ketto_format, conn)
        print(f"血統番号の形式:")
        print(df_ketto_format.to_string(index=False))
        
        # 6. 馬名の形式確認
        print("\n--- 馬名の形式確認 ---")
        query_horse_format = """
        SELECT 
            Bamei,
            LENGTH(Bamei) as length,
            COUNT(*) as count
        FROM N_UMA_RACE 
        WHERE Bamei IS NOT NULL 
        GROUP BY Bamei, LENGTH(Bamei)
        ORDER BY count DESC
        LIMIT 10
        """
        df_horse_format = pd.read_sql_query(query_horse_format, conn)
        print(f"馬名の形式:")
        print(df_horse_format.to_string(index=False))
        
        # 7. 血統番号と馬名の一意性確認
        print("\n--- 血統番号と馬名の一意性確認 ---")
        query_unique_ketto = """
        SELECT COUNT(DISTINCT KettoNum) as unique_ketto_count
        FROM N_UMA_RACE 
        WHERE KettoNum IS NOT NULL
        """
        df_unique_ketto = pd.read_sql_query(query_unique_ketto, conn)
        print(f"ユニークな血統番号数: {df_unique_ketto['unique_ketto_count'].iloc[0]}")
        
        query_unique_horse = """
        SELECT COUNT(DISTINCT Bamei) as unique_horse_count
        FROM N_UMA_RACE 
        WHERE Bamei IS NOT NULL
        """
        df_unique_horse = pd.read_sql_query(query_unique_horse, conn)
        print(f"ユニークな馬名数: {df_unique_horse['unique_horse_count'].iloc[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    investigate_ketto_horse_mapping()




