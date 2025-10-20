#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
馬マスターテーブル作成スクリプト
血統番号を基にした馬管理システムの基盤を構築
"""
import sqlite3
import sys
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def create_horse_master_tables():
    """馬マスターテーブルを作成"""
    print("=== 馬マスターテーブル作成開始 ===")
    
    # データベースパス
    db_path = "horse_card_system.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 馬マスターテーブル
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS horse_master (
            ketto_num TEXT PRIMARY KEY,  -- 血統番号
            horse_name TEXT NOT NULL,    -- 馬名
            birth_date TEXT,             -- 生年月日
            sex TEXT,                    -- 性別
            color TEXT,                  -- 毛色
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
        """)
        print("✅ 馬マスターテーブル作成完了")
        
        # 2. 血統テーブル
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedigree (
            ketto_num TEXT PRIMARY KEY,  -- 血統番号
            father_ketto TEXT,           -- 父の血統番号
            mother_ketto TEXT,            -- 母の血統番号
            grandfather_father TEXT,      -- 祖父（父方）
            grandmother_father TEXT,     -- 祖母（父方）
            grandfather_mother TEXT,      -- 祖父（母方）
            grandmother_mother TEXT,     -- 祖母（母方）
            FOREIGN KEY (ketto_num) REFERENCES horse_master(ketto_num)
        );
        """)
        print("✅ 血統テーブル作成完了")
        
        # 3. レース結果テーブル
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS race_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ketto_num TEXT NOT NULL,     -- 血統番号
            race_date TEXT NOT NULL,      -- レース日
            race_name TEXT,               -- レース名
            finish_order TEXT,            -- 着順
            jockey_name TEXT,             -- 騎手名
            trainer_name TEXT,            -- 調教師名
            odds TEXT,                    -- オッズ
            FOREIGN KEY (ketto_num) REFERENCES horse_master(ketto_num)
        );
        """)
        print("✅ レース結果テーブル作成完了")
        
        # 4. 独自変数テーブル
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_variables (
            ketto_num TEXT NOT NULL,     -- 血統番号
            variable_name TEXT NOT NULL, -- 変数名
            variable_value TEXT,         -- 変数値
            source_date TEXT,            -- データソース日
            PRIMARY KEY (ketto_num, variable_name, source_date),
            FOREIGN KEY (ketto_num) REFERENCES horse_master(ketto_num)
        );
        """)
        print("✅ 独自変数テーブル作成完了")
        
        # 5. インデックスの作成
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_horse_master_ketto ON horse_master(ketto_num);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pedigree_ketto ON pedigree(ketto_num);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_race_results_ketto ON race_results(ketto_num);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_race_results_date ON race_results(race_date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_custom_variables_ketto ON custom_variables(ketto_num);")
        print("✅ インデックス作成完了")
        
        conn.commit()
        print(f"✅ 馬マスターテーブル作成完了: {db_path}")
        
        # テーブル一覧の確認
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\n作成されたテーブル: {[table[0] for table in tables]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_horse_master_tables()




