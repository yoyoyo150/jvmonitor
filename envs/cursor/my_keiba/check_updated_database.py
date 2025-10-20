#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新されたデータベースの確認
1年分のエクセルデータの状況を調査
"""
import sqlite3
import pandas as pd
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def check_updated_database():
    """更新されたデータベースの確認"""
    db_path = "ecore.db"
    
    try:
        conn = sqlite3.connect(db_path)
        print("データベース接続成功")
        
        # 1. データの期間確認
        print("=== データの期間確認 ===")
        
        sql_date_range = """
        SELECT 
            MIN(Year || MonthDay) as MinDate,
            MAX(Year || MonthDay) as MaxDate,
            COUNT(DISTINCT Year || MonthDay) as DateCount
        FROM N_UMA_RACE
        WHERE Year IS NOT NULL AND MonthDay IS NOT NULL
        """
        
        date_range = pd.read_sql_query(sql_date_range, conn)
        print(f"データ期間: {date_range['MinDate'].iloc[0]} ～ {date_range['MaxDate'].iloc[0]}")
        print(f"日付数: {date_range['DateCount'].iloc[0]}日")
        
        # 2. 月別データ数確認
        print("\n=== 月別データ数確認 ===")
        
        sql_monthly = """
        SELECT 
            SUBSTR(Year || MonthDay, 1, 6) as YearMonth,
            COUNT(DISTINCT Year || MonthDay) as DateCount,
            COUNT(*) as RaceCount
        FROM N_UMA_RACE
        WHERE Year IS NOT NULL AND MonthDay IS NOT NULL
        GROUP BY YearMonth
        ORDER BY YearMonth
        """
        
        monthly_data = pd.read_sql_query(sql_monthly, conn)
        print("月別データ数:")
        for _, row in monthly_data.iterrows():
            print(f"  {row['YearMonth']}: {row['DateCount']}日, {row['RaceCount']}レース")
        
        # 3. 調教師数の推移確認
        print("\n=== 調教師数の推移確認 ===")
        
        sql_trainer_monthly = """
        SELECT 
            SUBSTR(Year || MonthDay, 1, 6) as YearMonth,
            COUNT(DISTINCT ChokyosiRyakusyo) as TrainerCount
        FROM N_UMA_RACE
        WHERE ChokyosiRyakusyo IS NOT NULL AND ChokyosiRyakusyo != ''
        GROUP BY YearMonth
        ORDER BY YearMonth
        """
        
        trainer_monthly = pd.read_sql_query(sql_trainer_monthly, conn)
        print("月別調教師数:")
        for _, row in trainer_monthly.iterrows():
            print(f"  {row['YearMonth']}: {row['TrainerCount']}名")
        
        # 4. 馬印5,6のデータ確認
        print("\n=== 馬印5,6のデータ確認 ===")
        
        # HORSE_MARKSテーブルで馬印データを確認
        sql_marks = """
        SELECT 
            SourceDate,
            COUNT(*) as TotalRecords,
            COUNT(CASE WHEN Mark5 IS NOT NULL AND Mark5 != '' THEN 1 END) as Mark5Count,
            COUNT(CASE WHEN Mark6 IS NOT NULL AND Mark6 != '' THEN 1 END) as Mark6Count,
            COUNT(CASE WHEN Mark5 IS NOT NULL AND Mark5 != '' AND Mark6 IS NOT NULL AND Mark6 != '' THEN 1 END) as BothMarksCount
        FROM HORSE_MARKS
        WHERE SourceDate IS NOT NULL
        GROUP BY SourceDate
        ORDER BY SourceDate DESC
        LIMIT 10
        """
        
        marks_data = pd.read_sql_query(sql_marks, conn)
        print("馬印データ（最新10日）:")
        for _, row in marks_data.iterrows():
            print(f"  {row['SourceDate']}: 総数{row['TotalRecords']}, Mark5:{row['Mark5Count']}, Mark6:{row['Mark6Count']}, 両方:{row['BothMarksCount']}")
        
        # 5. 最新データの確認
        print("\n=== 最新データの確認 ===")
        
        sql_latest = """
        SELECT 
            Year,
            MonthDay,
            JyoCD,
            RaceNum,
            Bamei,
            ChokyosiRyakusyo,
            KakuteiJyuni
        FROM N_UMA_RACE
        WHERE (Year || MonthDay) = (
            SELECT MAX(Year || MonthDay) FROM N_UMA_RACE
        )
        ORDER BY JyoCD, RaceNum, Umaban
        LIMIT 10
        """
        
        latest_data = pd.read_sql_query(sql_latest, conn)
        print(f"最新データ（{latest_data['Year'].iloc[0]}{latest_data['MonthDay'].iloc[0]}）:")
        for _, row in latest_data.iterrows():
            print(f"  {row['JyoCD']}{row['RaceNum']} {row['Bamei']} ({row['ChokyosiRyakusyo']}) - 着順:{row['KakuteiJyuni']}")
        
        conn.close()
        print("\n=== データベース確認完了 ===")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_updated_database()




