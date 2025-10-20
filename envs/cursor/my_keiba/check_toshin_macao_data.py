#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
トウシンマカオのデータベースデータ確認スクリプト
"""
import sqlite3
import pandas as pd
import sys
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def check_toshin_macao_data(db_path="ecore.db"):
    """トウシンマカオのデータベースデータをチェック"""
    print("=== トウシンマカオのデータ確認を開始します ===")
    
    try:
        conn = sqlite3.connect(db_path)
        print("データベース接続成功")
        
        race_date = '20250928'
        jyo_cd = '06' # 中山
        race_num = '11' # 11R
        horse_name = 'トウシンマカオ'
        
        print(f"対象レース: {race_date} 中山{race_num}R - {horse_name}")
        
        # 1. N_UMA_RACE テーブルのデータを確認
        print("\n--- N_UMA_RACE テーブル --- ")
        query_n_uma_race = f"""
        SELECT 
            Year || MonthDay AS Date,
            JyoCD,
            RaceNum,
            Bamei,
            ChokyosiRyakusyo AS TrainerName,
            KakuteiJyuni AS FinishOrder,
            Odds AS TanshoOdds_NUMA,
            Fukasyokin AS Fukasyokin_NUMA,
            Ninki AS Ninki_NUMA
        FROM N_UMA_RACE
        WHERE (Year || MonthDay) = '{race_date}'
        AND JyoCD = '{jyo_cd}'
        AND RaceNum = '{race_num}'
        AND Bamei = '{horse_name}'
        """
        df_n_uma_race = pd.read_sql_query(query_n_uma_race, conn)
        
        if not df_n_uma_race.empty:
            print("N_UMA_RACEにデータが見つかりました:")
            print(df_n_uma_race.iloc[0].to_string())
        else:
            print("N_UMA_RACEにデータが見つかりません。")
            
        # 2. HORSE_MARKS テーブルのデータを確認
        print("\n--- HORSE_MARKS テーブル --- ")
        query_horse_marks = f"""
        SELECT 
            SourceDate AS Date,
            JyoCD,
            RaceNum,
            HorseName,
            TRAINER_NAME AS TrainerName,
            CHAKU AS FinishOrder,
            Mark5,
            Mark6
        FROM HORSE_MARKS
        WHERE SourceDate = '{race_date}'
        AND JyoCD = '{jyo_cd}'
        AND RaceNum = '{race_num}'
        AND HorseName = '{horse_name}'
        """
        df_horse_marks = pd.read_sql_query(query_horse_marks, conn)
        
        if not df_horse_marks.empty:
            print("HORSE_MARKSにデータが見つかりました:")
            print(df_horse_marks.iloc[0].to_string())
        else:
            print("HORSE_MARKSにデータが見つかりません。")
            
        # 3. N_ODDS_TANPUKU テーブルのデータを確認
        print("\n--- N_ODDS_TANPUKU テーブル --- ")
        query_odds_tanpuku = f"""
        SELECT 
            Year || MonthDay AS Date,
            JyoCD,
            RaceNum,
            Umaban,
            TanOdds AS TanOdds_ODDS,
            TanNinki AS TanNinki_ODDS,
            FukuOddsLow AS FukuOddsLow_ODDS,
            FukuOddsHigh AS FukuOddsHigh_ODDS,
            FukuNinki AS FukuNinki_ODDS
        FROM N_ODDS_TANPUKU
        WHERE (Year || MonthDay) = '{race_date}'
        AND JyoCD = '{jyo_cd}'
        AND RaceNum = '{race_num}'
        AND Umaban = (
            SELECT Umaban FROM N_UMA_RACE
            WHERE (Year || MonthDay) = '{race_date}'
            AND JyoCD = '{jyo_cd}'
            AND RaceNum = '{race_num}'
            AND Bamei = '{horse_name}'
        )
        """
        df_odds_tanpuku = pd.read_sql_query(query_odds_tanpuku, conn)
        
        if not df_odds_tanpuku.empty:
            print("N_ODDS_TANPUKUにデータが見つかりました:")
            print(df_odds_tanpuku.iloc[0].to_string())
        else:
            print("N_ODDS_TANPUKUにデータが見つかりません。")
            
        conn.close()
        print("\n=== データ確認完了 ===")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_toshin_macao_data()




