#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合データベース設計スクリプト
ecore.dbをベースとして、excel_data.dbの拡張データを統合
"""
import sqlite3
import pandas as pd
import sys
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def design_integrated_database():
    """統合データベースの設計と実装"""
    print("=== 統合データベース設計開始 ===")
    
    try:
        # 統合データベースの作成
        integrated_db_path = "integrated_horse_system.db"
        integrated_conn = sqlite3.connect(integrated_db_path)
        
        # 1. 馬マスターテーブル（ecore.dbのN_UMAをベース）
        print("\n--- 馬マスターテーブルの作成 ---")
        integrated_conn.execute("""
        CREATE TABLE IF NOT EXISTS horse_master (
            KettoNum TEXT PRIMARY KEY,
            Bamei TEXT NOT NULL,
            BirthDate TEXT,
            SexCD TEXT,
            HinsyuCD TEXT,
            KeiroCD TEXT,
            TozaiCD TEXT,
            ChokyosiCode TEXT,
            ChokyosiRyakusyo TEXT,
            Syotai TEXT,
            BreederCode TEXT,
            BreederName TEXT,
            SanchiName TEXT,
            BanusiCode TEXT,
            BanusiName TEXT,
            CreatedAt TEXT DEFAULT (datetime('now')),
            UpdatedAt TEXT DEFAULT (datetime('now'))
        );
        """)
        print("✅ 馬マスターテーブル作成完了")
        
        # 2. 血統テーブル（ecore.dbのN_UMAの血統情報をベース）
        print("\n--- 血統テーブルの作成 ---")
        integrated_conn.execute("""
        CREATE TABLE IF NOT EXISTS pedigree (
            KettoNum TEXT PRIMARY KEY,
            FatherKettoNum TEXT,
            MotherKettoNum TEXT,
            GrandfatherFather TEXT,
            GrandmotherFather TEXT,
            GrandfatherMother TEXT,
            GrandmotherMother TEXT,
            FOREIGN KEY (KettoNum) REFERENCES horse_master(KettoNum)
        );
        """)
        print("✅ 血統テーブル作成完了")
        
        # 3. レース結果テーブル（ecore.dbのN_UMA_RACEをベース）
        print("\n--- レース結果テーブルの作成 ---")
        integrated_conn.execute("""
        CREATE TABLE IF NOT EXISTS race_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            KettoNum TEXT NOT NULL,
            RaceDate TEXT NOT NULL,
            JyoCD TEXT,
            RaceNum TEXT,
            Umaban TEXT,
            Bamei TEXT,
            SexCD TEXT,
            HinsyuCD TEXT,
            KeiroCD TEXT,
            Barei TEXT,
            ChokyosiCode TEXT,
            ChokyosiRyakusyo TEXT,
            KisyuCode TEXT,
            KisyuRyakusyo TEXT,
            KakuteiJyuni TEXT,
            DochakuKubun TEXT,
            DochakuTosu TEXT,
            Time TEXT,
            Odds TEXT,
            Ninki TEXT,
            Honsyokin TEXT,
            Fukasyokin TEXT,
            CreatedAt TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (KettoNum) REFERENCES horse_master(KettoNum)
        );
        """)
        print("✅ レース結果テーブル作成完了")
        
        # 4. 独自変数テーブル（excel_data.dbの拡張データ）
        print("\n--- 独自変数テーブルの作成 ---")
        integrated_conn.execute("""
        CREATE TABLE IF NOT EXISTS custom_variables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            KettoNum TEXT NOT NULL,
            RaceDate TEXT NOT NULL,
            JyoCD TEXT,
            RaceNum TEXT,
            Umaban TEXT,
            Bamei TEXT,
            -- 馬印データ
            Mark1 TEXT,
            Mark2 TEXT,
            Mark3 TEXT,
            Mark4 TEXT,
            Mark5 TEXT,
            Mark6 TEXT,
            Mark7 TEXT,
            Mark8 TEXT,
            -- 前走データ
            Prev_Mark1 TEXT,
            Prev_Mark2 TEXT,
            Prev_Mark3 TEXT,
            Prev_Mark4 TEXT,
            Prev_Mark5 TEXT,
            Prev_Mark6 TEXT,
            Prev_Mark7 TEXT,
            Prev_Mark8 TEXT,
            -- 独自指標
            ZI_Index TEXT,
            ZM_Value TEXT,
            Index_Rank1 TEXT,
            Index_Rank2 TEXT,
            Index_Rank3 TEXT,
            Index_Rank4 TEXT,
            Index_Diff1 TEXT,
            Index_Diff2 TEXT,
            Index_Diff4 TEXT,
            Original_Val TEXT,
            Accel_Val TEXT,
            -- その他の独自変数
            Prev_Kyakushitsu TEXT,
            Prev_Ninki TEXT,
            Prev_Chaku_Juni TEXT,
            Prev_Chaku_Sa TEXT,
            Prev_Tsuka1 TEXT,
            Prev_Tsuka2 TEXT,
            Prev_Tsuka3 TEXT,
            Prev_Tsuka4 TEXT,
            Prev_3F_Juni TEXT,
            Prev_Tosu TEXT,
            Prev_Race_Mark TEXT,
            Prev_Race_Mark2 TEXT,
            Prev_Race_Mark3 TEXT,
            Father_Type_Name TEXT,
            Damsire_Type_Name TEXT,
            Total_Horses TEXT,
            Work1 TEXT,
            Work2 TEXT,
            Prev_Track_Name TEXT,
            Same_Track_Flag TEXT,
            Prev_Kinryo TEXT,
            Prev_Bataiju TEXT,
            Prev_Bataiju_Zogen TEXT,
            Age_At_Race TEXT,
            Interval TEXT,
            Kyumei_Senme TEXT,
            Kinryo_Sa TEXT,
            Kyori_Sa TEXT,
            Prev_Shiba_Da TEXT,
            Prev_Kyori_M TEXT,
            Career_Total TEXT,
            Career_Latest TEXT,
            Class_C TEXT,
            Prev_Umaban TEXT,
            Prev_Shiba_Da_1 TEXT,
            Current_Shiba_Da TEXT,
            Prev_Baba_Jotai TEXT,
            Prev_Class TEXT,
            T_Mark_Diff TEXT,
            Matchup_Mining_Val TEXT,
            Matchup_Mining_Rank TEXT,
            Kokyusen_Flag TEXT,
            B_Flag TEXT,
            Syozoku TEXT,
            Check_Trainer_Type TEXT,
            Check_Jockey_Type TEXT,
            Syozoku_1 TEXT,
            Trainer_Name TEXT,
            Fukusho_Odds_Lower TEXT,
            Fukusho_Odds_Upper TEXT,
            Tan_Odds TEXT,
            Wakuban TEXT,
            Course_Group_Count TEXT,
            Course_Group_Name1 TEXT,
            Ninki_Rank TEXT,
            Norikae_Flag TEXT,
            Prev_Race_ID_New TEXT,
            SourceFile TEXT,
            ImportedAt TEXT,
            CreatedAt TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (KettoNum) REFERENCES horse_master(KettoNum)
        );
        """)
        print("✅ 独自変数テーブル作成完了")
        
        # 5. インデックスの作成
        print("\n--- インデックスの作成 ---")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_horse_master_ketto ON horse_master(KettoNum);",
            "CREATE INDEX IF NOT EXISTS idx_pedigree_ketto ON pedigree(KettoNum);",
            "CREATE INDEX IF NOT EXISTS idx_race_results_ketto ON race_results(KettoNum);",
            "CREATE INDEX IF NOT EXISTS idx_race_results_date ON race_results(RaceDate);",
            "CREATE INDEX IF NOT EXISTS idx_race_results_jyo_race ON race_results(JyoCD, RaceNum);",
            "CREATE INDEX IF NOT EXISTS idx_custom_variables_ketto ON custom_variables(KettoNum);",
            "CREATE INDEX IF NOT EXISTS idx_custom_variables_date ON custom_variables(RaceDate);",
            "CREATE INDEX IF NOT EXISTS idx_custom_variables_jyo_race ON custom_variables(JyoCD, RaceNum);"
        ]
        
        for index_sql in indexes:
            integrated_conn.execute(index_sql)
        print("✅ インデックス作成完了")
        
        # 6. テーブル一覧の確認
        print("\n--- 作成されたテーブル一覧 ---")
        query_tables = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        df_tables = pd.read_sql_query(query_tables, integrated_conn)
        print(f"テーブル数: {len(df_tables)}")
        for table in df_tables['name']:
            print(f"  - {table}")
        
        integrated_conn.close()
        print(f"\n✅ 統合データベース設計完了: {integrated_db_path}")
        
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    design_integrated_database()




