#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HORSE_MARKSテーブルのMark5/Mark6データ詳細確認スクリプト
"""
import sqlite3
import pandas as pd
import sys

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def check_horse_marks_detail_data(db_path="ecore.db"):
    """HORSE_MARKSテーブルのMark5/Mark6データを詳細にチェック"""
    print("=== HORSE_MARKSテーブルのMark5/Mark6データ詳細確認を開始します ===")
    
    try:
        conn = sqlite3.connect(db_path)
        print("データベース接続成功")
        
        # 1. トウシンマカオのMark5/Mark6データを確認 (20250928 中山11R)
        print("\n--- トウシンマカオ (20250928 中山11R) の Mark5/Mark6 データ --- ")
        query_toshin_macao = f"""
        SELECT 
            SourceDate, HorseName, TRAINER_NAME, RaceNum, Mark5, Mark6
        FROM HORSE_MARKS
        WHERE HorseName = 'トウシンマカオ'
        AND SourceDate = '20250928'
        AND JyoCD = '06'
        AND RaceNum = '11'
        """
        df_toshin_macao = pd.read_sql_query(query_toshin_macao, conn)
        
        if not df_toshin_macao.empty:
            print("トウシンマカオのMark5/Mark6データが見つかりました:")
            print(df_toshin_macao.to_string())
        else:
            print("トウシンマカオのMark5/Mark6データは見つかりませんでした。")
            
        # 2. 最新日付のMark5/Mark6データサンプルを確認
        print("\n--- 最新日付のMark5/Mark6データサンプル (5件) --- ")
        query_latest_sample = """
        SELECT 
            SourceDate, HorseName, TRAINER_NAME, RaceNum, Mark5, Mark6
        FROM HORSE_MARKS
        ORDER BY SourceDate DESC, RaceNum DESC
        LIMIT 5
        """
        df_latest_sample = pd.read_sql_query(query_latest_sample, conn)
        
        if not df_latest_sample.empty:
            print("最新日付のMark5/Mark6データサンプル:")
            print(df_latest_sample.to_string())
        else:
            print("最新日付のMark5/Mark6データサンプルは見つかりませんでした。")

        # 3. 馬印5/馬印6に'?'を含むレコードのサンプルを確認
        print("\n--- 馬印5/馬印6に'?'を含むレコードのサンプル (5件) --- ")
        query_question_mark_sample = """
        SELECT 
            SourceDate, HorseName, TRAINER_NAME, RaceNum, Mark5, Mark6
        FROM HORSE_MARKS
        WHERE Mark5 = '？' OR Mark6 = '？'
        LIMIT 5
        """
        df_question_mark_sample = pd.read_sql_query(query_question_mark_sample, conn)
        
        if not df_question_mark_sample.empty:
            print("'？'を含むMark5/Mark6データサンプル:")
            print(df_question_mark_sample.to_string())
        else:
            print("'？'を含むMark5/Mark6データは見つかりませんでした。")
            
        conn.close()
        print("\n=== データ詳細確認完了 ===")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_horse_marks_detail_data()




