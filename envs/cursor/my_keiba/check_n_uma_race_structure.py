#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
N_UMA_RACEテーブルの構造確認
JVMonitorが参照しているテーブルの構造を調査
"""
import sqlite3
import pandas as pd
import sys
import os

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def check_n_uma_race_structure():
    """N_UMA_RACEテーブルの構造確認"""
    db_path = "ecore.db"
    
    try:
        conn = sqlite3.connect(db_path)
        print("データベース接続成功")
        
        # 1. N_UMA_RACEテーブルの構造確認
        print("=== N_UMA_RACEテーブルの構造確認 ===")
        
        sql_table_info = "PRAGMA table_info(N_UMA_RACE)"
        table_info = pd.read_sql_query(sql_table_info, conn)
        print(f"N_UMA_RACEテーブルのカラム数: {len(table_info)}")
        
        for _, row in table_info.iterrows():
            print(f"  {row['name']}: {row['type']}")
        
        # 2. N_UMA_RACEテーブルの9/27と28のデータ確認
        print("\n=== N_UMA_RACEテーブルの9/27と28のデータ確認 ===")
        
        try:
            sql_n_uma_race = """
            SELECT *
            FROM N_UMA_RACE
            WHERE (Year || MonthDay) IN ('20250927', '20250928')
            ORDER BY Year, MonthDay, JyoCD, RaceNum, Umaban
            LIMIT 5
            """
            
            n_uma_race = pd.read_sql_query(sql_n_uma_race, conn)
            print(f"N_UMA_RACEテーブルの9/27と28のデータ: {len(n_uma_race)}件")
            
            if len(n_uma_race) > 0:
                print("N_UMA_RACEテーブルのサンプルデータ:")
                for _, row in n_uma_race.iterrows():
                    print(f"  {row.to_dict()}")
            else:
                print("N_UMA_RACEテーブルに9/27と28のデータがありません")
        except Exception as e:
            print(f"N_UMA_RACEテーブルの確認エラー: {e}")
        
        # 3. 着順データの分布確認（N_UMA_RACE）
        print("\n=== 着順データの分布確認（N_UMA_RACE） ===")
        
        try:
            sql_chaku_dist = """
            SELECT KakuteiJyuni, COUNT(*) as count 
            FROM N_UMA_RACE 
            WHERE (Year || MonthDay) IN ('20250927', '20250928')
            AND KakuteiJyuni IS NOT NULL AND KakuteiJyuni != ''
            GROUP BY KakuteiJyuni
            ORDER BY count DESC
            """
            chaku_dist = pd.read_sql_query(sql_chaku_dist, conn)
            print(f"着順データの分布: {len(chaku_dist)}件")
            
            for _, row in chaku_dist.iterrows():
                chaku_value = row['KakuteiJyuni'] if row['KakuteiJyuni'] is not None else 'None'
                count = row['count']
                print(f"  着順{chaku_value}: {count}件")
        except Exception as e:
            print(f"着順データの分布確認エラー: {e}")
        
        # 4. 調教師別の着順データ確認（N_UMA_RACE）
        print("\n=== 調教師別の着順データ確認（N_UMA_RACE） ===")
        
        try:
            # 調教師関連のカラムを探す
            trainer_columns = []
            for _, col in table_info.iterrows():
                col_name = col['name']
                if 'trainer' in col_name.lower() or 'Trainer' in col_name or 'chokyo' in col_name.lower() or 'Chokyo' in col_name:
                    trainer_columns.append(col_name)
            
            print(f"調教師関連のカラム: {trainer_columns}")
            
            if trainer_columns:
                trainer_col = trainer_columns[0]  # 最初の調教師カラムを使用
                
                sql_trainer_chaku = f"""
                SELECT 
                    {trainer_col},
                    COUNT(*) as TotalRaces,
                    SUM(CASE WHEN KakuteiJyuni = '1' THEN 1 ELSE 0 END) as WinCount,
                    SUM(CASE WHEN KakuteiJyuni = '2' THEN 1 ELSE 0 END) as PlaceCount,
                    SUM(CASE WHEN KakuteiJyuni = '3' THEN 1 ELSE 0 END) as ShowCount,
                    SUM(CASE WHEN KakuteiJyuni IN ('4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18') THEN 1 ELSE 0 END) as OtherCount
                FROM N_UMA_RACE
                WHERE (Year || MonthDay) IN ('20250927', '20250928')
                AND {trainer_col} IS NOT NULL AND {trainer_col} != ''
                GROUP BY {trainer_col}
                ORDER BY TotalRaces DESC
                LIMIT 10
                """
                
                trainer_chaku = pd.read_sql_query(sql_trainer_chaku, conn)
                print(f"調教師別の着順データ: {len(trainer_chaku)}名")
                
                for _, row in trainer_chaku.iterrows():
                    trainer = row[trainer_col]
                    win = row['WinCount']
                    place = row['PlaceCount'] 
                    show = row['ShowCount']
                    other = row['OtherCount']
                    total = row['TotalRaces']
                    result = f"{win}-{place}-{show}-{other}/{total}"
                    print(f"  {trainer}: {result}")
            else:
                print("調教師関連のカラムが見つかりません")
        except Exception as e:
            print(f"調教師別の着順データ確認エラー: {e}")
        
        conn.close()
        print("\n=== N_UMA_RACEテーブルの構造確認完了 ===")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_n_uma_race_structure()




