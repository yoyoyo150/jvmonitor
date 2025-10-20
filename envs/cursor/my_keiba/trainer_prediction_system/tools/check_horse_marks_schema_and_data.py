#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HORSE_MARKSテーブルのMark5/Mark6データ確認スクリプト
"""
import sqlite3
import pandas as pd
import sys
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def check_horse_marks_schema_and_data(db_path="ecore.db"):
    """HORSE_MARKSテーブルのスキーマとMark5/Mark6データをチェック"""
    print("=== HORSE_MARKSテーブルのMark5/Mark6データ確認を開始します ===")
    
    try:
        conn = sqlite3.connect(db_path)
        print("データベース接続成功")
        
        # 1. HORSE_MARKS テーブルのスキーマ確認
        print("\n--- HORSE_MARKS テーブルのスキーマ --- ")
        query_schema = "PRAGMA table_info(HORSE_MARKS)"
        df_schema = pd.read_sql_query(query_schema, conn)
        
        if not df_schema.empty:
            print("HORSE_MARKSテーブルの構造:")
            print(df_schema.to_string())
        else:
            print("HORSE_MARKSテーブルが見つかりません。")
            
        # 2. Mark5/Mark6 がNULLでないレコードをサンプリング
        print("\n--- HORSE_MARKS の Mark5/Mark6 データ（NULLでないもの） --- ")
        query_sample_marks = """
        SELECT 
            SourceDate, 
            HorseName, 
            TRAINER_NAME, 
            CHAKU, 
            Mark5, 
            Mark6
        FROM HORSE_MARKS
        WHERE Mark5 IS NOT NULL AND Mark5 != '' AND Mark5 != '0'
        AND Mark6 IS NOT NULL AND Mark6 != '' AND Mark6 != '0'
        LIMIT 20
        """
        df_sample_marks = pd.read_sql_query(query_sample_marks, conn)
        
        if not df_sample_marks.empty:
            print("Mark5/Mark6データが存在するレコードのサンプル:")
            print(df_sample_marks.to_string())
        else:
            print("Mark5/Mark6データがNULLでないレコードは見つかりませんでした。")
            
        # 3. トウシンマカオのMark5/Mark6データを確認
        print("\n--- トウシンマカオの Mark5/Mark6 データ --- ")
        query_toshin_macao_marks = f"""
        SELECT 
            SourceDate, 
            HorseName, 
            TRAINER_NAME, 
            CHAKU, 
            Mark5, 
            Mark6
        FROM HORSE_MARKS
        WHERE HorseName = 'トウシンマカオ'
        AND SourceDate = '20250928'
        AND JyoCD = '06'
        AND RaceNum = '11'
        """
        df_toshin_macao_marks = pd.read_sql_query(query_toshin_macao_marks, conn)
        
        if not df_toshin_macao_marks.empty:
            print("トウシンマカオのMark5/Mark6データが見つかりました:")
            print(df_toshin_macao_marks.to_string())
        else:
            print("トウシンマカオのMark5/Mark6データは見つかりませんでした。")

        conn.close()
        print("\n=== データ確認完了 ===")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_horse_marks_schema_and_data()
