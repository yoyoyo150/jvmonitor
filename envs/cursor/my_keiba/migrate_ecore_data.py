#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ecore.dbからのデータ移行スクリプト
統合データベースにecore.dbのデータを移行
"""
import sqlite3
import pandas as pd
import sys
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def migrate_ecore_data():
    """ecore.dbからのデータ移行"""
    print("=== ecore.dbからのデータ移行開始 ===")
    
    try:
        # データベース接続
        ecore_conn = sqlite3.connect('ecore.db')
        integrated_conn = sqlite3.connect('integrated_horse_system.db')
        
        # 1. 馬マスターデータの移行
        print("\n--- 馬マスターデータの移行 ---")
        query_horse_master = """
        SELECT DISTINCT
            KettoNum,
            Bamei,
            BirthDate,
            SexCD,
            HinsyuCD,
            KeiroCD,
            TozaiCD,
            ChokyosiCode,
            ChokyosiRyakusyo,
            Syotai,
            BreederCode,
            BreederName,
            SanchiName,
            BanusiCode,
            BanusiName
        FROM N_UMA 
        WHERE KettoNum IS NOT NULL 
        AND Bamei IS NOT NULL
        AND KettoNum != '0000000000'
        ORDER BY KettoNum
        """
        df_horse_master = pd.read_sql_query(query_horse_master, ecore_conn)
        print(f"移行対象の馬数: {len(df_horse_master)}")
        
        # 馬マスターデータを挿入
        for _, row in df_horse_master.iterrows():
            integrated_conn.execute("""
            INSERT OR REPLACE INTO horse_master (
                KettoNum, Bamei, BirthDate, SexCD, HinsyuCD, KeiroCD, TozaiCD,
                ChokyosiCode, ChokyosiRyakusyo, Syotai, BreederCode, BreederName,
                SanchiName, BanusiCode, BanusiName
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['KettoNum'], row['Bamei'], row['BirthDate'], row['SexCD'],
                row['HinsyuCD'], row['KeiroCD'], row['TozaiCD'], row['ChokyosiCode'],
                row['ChokyosiRyakusyo'], row['Syotai'], row['BreederCode'],
                row['BreederName'], row['SanchiName'], row['BanusiCode'], row['BanusiName']
            ))
        
        integrated_conn.commit()
        print("✅ 馬マスターデータ移行完了")
        
        # 2. 血統データの移行
        print("\n--- 血統データの移行 ---")
        query_pedigree = """
        SELECT DISTINCT
            KettoNum,
            Ketto3InfoHansyokuNum1 as FatherKettoNum,
            Ketto3InfoHansyokuNum2 as MotherKettoNum,
            Ketto3InfoBamei1 as GrandfatherFather,
            Ketto3InfoBamei2 as GrandmotherFather,
            Ketto3InfoBamei3 as GrandfatherMother,
            Ketto3InfoBamei4 as GrandmotherMother
        FROM N_UMA 
        WHERE KettoNum IS NOT NULL 
        AND KettoNum != '0000000000'
        ORDER BY KettoNum
        """
        df_pedigree = pd.read_sql_query(query_pedigree, ecore_conn)
        print(f"移行対象の血統データ数: {len(df_pedigree)}")
        
        # 血統データを挿入
        for _, row in df_pedigree.iterrows():
            integrated_conn.execute("""
            INSERT OR REPLACE INTO pedigree (
                KettoNum, FatherKettoNum, MotherKettoNum, GrandfatherFather,
                GrandmotherFather, GrandfatherMother, GrandmotherMother
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                row['KettoNum'], row['FatherKettoNum'], row['MotherKettoNum'],
                row['GrandfatherFather'], row['GrandmotherFather'],
                row['GrandfatherMother'], row['GrandmotherMother']
            ))
        
        integrated_conn.commit()
        print("✅ 血統データ移行完了")
        
        # 3. レース結果データの移行
        print("\n--- レース結果データの移行 ---")
        query_race_results = """
        SELECT 
            KettoNum,
            Year || MonthDay as RaceDate,
            JyoCD,
            RaceNum,
            Umaban,
            Bamei,
            SexCD,
            HinsyuCD,
            KeiroCD,
            Barei,
            ChokyosiCode,
            ChokyosiRyakusyo,
            KisyuCode,
            KisyuRyakusyo,
            KakuteiJyuni,
            DochakuKubun,
            DochakuTosu,
            Time,
            Odds,
            Ninki,
            Honsyokin,
            Fukasyokin
        FROM N_UMA_RACE 
        WHERE KettoNum IS NOT NULL 
        AND Bamei IS NOT NULL
        AND KettoNum != '0000000000'
        ORDER BY RaceDate DESC
        LIMIT 10000
        """
        df_race_results = pd.read_sql_query(query_race_results, ecore_conn)
        print(f"移行対象のレース結果数: {len(df_race_results)}")
        
        # レース結果データを挿入
        for _, row in df_race_results.iterrows():
            integrated_conn.execute("""
            INSERT OR REPLACE INTO race_results (
                KettoNum, RaceDate, JyoCD, RaceNum, Umaban, Bamei, SexCD,
                HinsyuCD, KeiroCD, Barei, ChokyosiCode, ChokyosiRyakusyo,
                KisyuCode, KisyuRyakusyo, KakuteiJyuni, DochakuKubun,
                DochakuTosu, Time, Odds, Ninki, Honsyokin, Fukasyokin
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['KettoNum'], row['RaceDate'], row['JyoCD'], row['RaceNum'],
                row['Umaban'], row['Bamei'], row['SexCD'], row['HinsyuCD'],
                row['KeiroCD'], row['Barei'], row['ChokyosiCode'], row['ChokyosiRyakusyo'],
                row['KisyuCode'], row['KisyuRyakusyo'], row['KakuteiJyuni'],
                row['DochakuKubun'], row['DochakuTosu'], row['Time'], row['Odds'],
                row['Ninki'], row['Honsyokin'], row['Fukasyokin']
            ))
        
        integrated_conn.commit()
        print("✅ レース結果データ移行完了")
        
        # 4. 移行結果の確認
        print("\n--- 移行結果の確認 ---")
        query_horse_count = "SELECT COUNT(*) as count FROM horse_master"
        df_horse_count = pd.read_sql_query(query_horse_count, integrated_conn)
        print(f"移行された馬数: {df_horse_count['count'].iloc[0]}")
        
        query_pedigree_count = "SELECT COUNT(*) as count FROM pedigree"
        df_pedigree_count = pd.read_sql_query(query_pedigree_count, integrated_conn)
        print(f"移行された血統データ数: {df_pedigree_count['count'].iloc[0]}")
        
        query_race_count = "SELECT COUNT(*) as count FROM race_results"
        df_race_count = pd.read_sql_query(query_race_count, integrated_conn)
        print(f"移行されたレース結果数: {df_race_count['count'].iloc[0]}")
        
        # データベース接続を閉じる
        ecore_conn.close()
        integrated_conn.close()
        
        print("\n✅ ecore.dbからのデータ移行が完了しました")
        
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    migrate_ecore_data()




