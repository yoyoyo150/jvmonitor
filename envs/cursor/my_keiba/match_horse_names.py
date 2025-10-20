#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
馬名照合スクリプト
excel_data.dbの馬名とecore.dbの馬名を照合し、血統番号を付与
"""
import sqlite3
import pandas as pd
import sys
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def match_horse_names():
    """馬名照合と血統番号付与"""
    print("=== 馬名照合と血統番号付与開始 ===")
    
    try:
        # データベース接続
        ecore_conn = sqlite3.connect('ecore.db')
        excel_conn = sqlite3.connect('trainer_prediction_system/excel_data.db')
        
        # 1. ecore.dbから血統番号と馬名の対応を取得
        print("\n--- ecore.dbから血統番号と馬名の対応を取得 ---")
        query_ecore = """
        SELECT DISTINCT
            KettoNum,
            Bamei
        FROM N_UMA_RACE 
        WHERE KettoNum IS NOT NULL 
        AND Bamei IS NOT NULL
        AND KettoNum != '0000000000'
        ORDER BY KettoNum
        """
        df_ecore = pd.read_sql_query(query_ecore, ecore_conn)
        print(f"ecore.dbの血統番号・馬名ペア数: {len(df_ecore)}")
        
        # 2. excel_data.dbから馬名を取得
        print("\n--- excel_data.dbから馬名を取得 ---")
        query_excel = """
        SELECT DISTINCT
            HorseNameS,
            NormalizedHorseName
        FROM excel_marks 
        WHERE HorseNameS IS NOT NULL
        ORDER BY HorseNameS
        """
        df_excel = pd.read_sql_query(query_excel, excel_conn)
        print(f"excel_data.dbの馬名数: {len(df_excel)}")
        
        # 3. 馬名の照合
        print("\n--- 馬名の照合 ---")
        # HorseNameSとBameiの照合
        match_horse_name = pd.merge(df_excel, df_ecore, 
                                   left_on='HorseNameS', right_on='Bamei', 
                                   how='left')
        match_horse_name_count = match_horse_name['KettoNum'].notna().sum()
        print(f"HorseNameSとBameiの照合成功数: {match_horse_name_count}")
        
        # NormalizedHorseNameとBameiの照合
        match_normalized = pd.merge(df_excel, df_ecore, 
                                   left_on='NormalizedHorseName', right_on='Bamei', 
                                   how='left')
        match_normalized_count = match_normalized['KettoNum'].notna().sum()
        print(f"NormalizedHorseNameとBameiの照合成功数: {match_normalized_count}")
        
        # 4. 照合結果の詳細確認
        print("\n--- 照合結果の詳細確認 ---")
        print("HorseNameSとBameiの照合結果:")
        print(f"  照合成功: {match_horse_name_count}")
        print(f"  照合失敗: {len(df_excel) - match_horse_name_count}")
        
        print("NormalizedHorseNameとBameiの照合結果:")
        print(f"  照合成功: {match_normalized_count}")
        print(f"  照合失敗: {len(df_excel) - match_normalized_count}")
        
        # 5. 照合失敗例の確認
        print("\n--- 照合失敗例の確認 ---")
        failed_matches = match_horse_name[match_horse_name['KettoNum'].isna()]
        if not failed_matches.empty:
            print("照合失敗した馬名（最初の10件）:")
            print(failed_matches[['HorseNameS', 'NormalizedHorseName']].head(10).to_string(index=False))
        
        # 6. 照合成功例の確認
        print("\n--- 照合成功例の確認 ---")
        successful_matches = match_horse_name[match_horse_name['KettoNum'].notna()]
        if not successful_matches.empty:
            print("照合成功した馬名（最初の10件）:")
            print(successful_matches[['HorseNameS', 'Bamei', 'KettoNum']].head(10).to_string(index=False))
        
        # 7. 血統番号付与の準備
        print("\n--- 血統番号付与の準備 ---")
        # 照合成功した馬名と血統番号のマッピングを作成
        horse_ketto_mapping = successful_matches[['HorseNameS', 'KettoNum']].drop_duplicates()
        print(f"血統番号付与対象の馬名数: {len(horse_ketto_mapping)}")
        
        # 8. excel_data.dbに血統番号カラムを追加
        print("\n--- excel_data.dbに血統番号カラムを追加 ---")
        try:
            # 血統番号カラムを追加
            excel_conn.execute("ALTER TABLE excel_marks ADD COLUMN KettoNum TEXT")
            print("✅ KettoNumカラムを追加しました")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✅ KettoNumカラムは既に存在します")
            else:
                print(f"❌ カラム追加エラー: {e}")
        
        # 9. 血統番号の更新
        print("\n--- 血統番号の更新 ---")
        update_count = 0
        for _, row in horse_ketto_mapping.iterrows():
            horse_name = row['HorseNameS']
            ketto_num = row['KettoNum']
            
            # 血統番号を更新
            update_query = """
            UPDATE excel_marks 
            SET KettoNum = ? 
            WHERE HorseNameS = ?
            """
            cursor = excel_conn.cursor()
            cursor.execute(update_query, (ketto_num, horse_name))
            update_count += cursor.rowcount
        
        excel_conn.commit()
        print(f"✅ {update_count}件の血統番号を更新しました")
        
        # 10. 更新結果の確認
        print("\n--- 更新結果の確認 ---")
        query_updated = """
        SELECT 
            COUNT(*) as total_records,
            COUNT(KettoNum) as records_with_ketto,
            COUNT(*) - COUNT(KettoNum) as records_without_ketto
        FROM excel_marks
        """
        df_updated = pd.read_sql_query(query_updated, excel_conn)
        print(f"総レコード数: {df_updated['total_records'].iloc[0]}")
        print(f"血統番号付与済み: {df_updated['records_with_ketto'].iloc[0]}")
        print(f"血統番号未付与: {df_updated['records_without_ketto'].iloc[0]}")
        
        # データベース接続を閉じる
        ecore_conn.close()
        excel_conn.close()
        
        print("\n✅ 馬名照合と血統番号付与が完了しました")
        
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    match_horse_names()




