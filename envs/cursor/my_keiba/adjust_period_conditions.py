#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
期間の調整
2/1から開始の期間を調整
"""
import sqlite3
import pandas as pd
import sys
import os
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def adjust_period_conditions():
    """期間の調整"""
    db_path = "ecore.db"
    
    try:
        conn = sqlite3.connect(db_path)
        print("データベース接続成功")
        
        # 1. 期間の調整
        print("=== 期間の調整 ===")
        
        # 様々な期間での芝・ダート件数確認
        periods = [
            ("20250201", "20250928", "2/1-9/28"),
            ("20250301", "20250928", "3/1-9/28"),
            ("20250401", "20250928", "4/1-9/28"),
            ("20250501", "20250928", "5/1-9/28"),
            ("20250601", "20250928", "6/1-9/28"),
            ("20250701", "20250928", "7/1-9/28"),
            ("20250801", "20250928", "8/1-9/28"),
            ("20250901", "20250928", "9/1-9/28")
        ]
        
        for start_date, end_date, period_name in periods:
            print(f"\n{period_name}の期間:")
            
            # 芝の件数（馬印5+馬印6の条件）
            sql_turf_marks = f"""
            SELECT COUNT(*) as TurfMarksCount
            FROM HORSE_MARKS
            WHERE SourceDate >= '{start_date}'
            AND SourceDate <= '{end_date}'
            AND Mark5 IS NOT NULL AND Mark5 != ''
            AND Mark6 IS NOT NULL AND Mark6 != ''
            AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) >= 1
            AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) <= 6
            AND SHIBA_DA = '芝'
            """
            
            turf_marks_count = pd.read_sql_query(sql_turf_marks, conn).iloc[0]['TurfMarksCount']
            print(f"  芝: {turf_marks_count}件")
            
            # ダートの件数（馬印5+馬印6の条件）
            sql_dirt_marks = f"""
            SELECT COUNT(*) as DirtMarksCount
            FROM HORSE_MARKS
            WHERE SourceDate >= '{start_date}'
            AND SourceDate <= '{end_date}'
            AND Mark5 IS NOT NULL AND Mark5 != ''
            AND Mark6 IS NOT NULL AND Mark6 != ''
            AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) >= 1
            AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) <= 6
            AND SHIBA_DA = 'ダ'
            """
            
            dirt_marks_count = pd.read_sql_query(sql_dirt_marks, conn).iloc[0]['DirtMarksCount']
            print(f"  ダート: {dirt_marks_count}件")
            
            # TARGET frontierとの比較
            turf_diff = turf_marks_count - 697
            dirt_diff = dirt_marks_count - 388
            print(f"  芝の差: {turf_diff}件")
            print(f"  ダートの差: {dirt_diff}件")
            
            if abs(turf_diff) <= 2 and abs(dirt_diff) <= 2:
                print(f"  ✅ 目標範囲内（±2）です！")
            else:
                print(f"  ❌ 目標範囲外です。")
        
        # 2. 最適な期間の特定
        print(f"\n=== 最適な期間の特定 ===")
        
        best_period = None
        best_turf_diff = float('inf')
        best_dirt_diff = float('inf')
        
        for start_date, end_date, period_name in periods:
            # 芝の件数（馬印5+馬印6の条件）
            sql_turf_marks = f"""
            SELECT COUNT(*) as TurfMarksCount
            FROM HORSE_MARKS
            WHERE SourceDate >= '{start_date}'
            AND SourceDate <= '{end_date}'
            AND Mark5 IS NOT NULL AND Mark5 != ''
            AND Mark6 IS NOT NULL AND Mark6 != ''
            AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) >= 1
            AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) <= 6
            AND SHIBA_DA = '芝'
            """
            
            turf_marks_count = pd.read_sql_query(sql_turf_marks, conn).iloc[0]['TurfMarksCount']
            
            # ダートの件数（馬印5+馬印6の条件）
            sql_dirt_marks = f"""
            SELECT COUNT(*) as DirtMarksCount
            FROM HORSE_MARKS
            WHERE SourceDate >= '{start_date}'
            AND SourceDate <= '{end_date}'
            AND Mark5 IS NOT NULL AND Mark5 != ''
            AND Mark6 IS NOT NULL AND Mark6 != ''
            AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) >= 1
            AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) <= 6
            AND SHIBA_DA = 'ダ'
            """
            
            dirt_marks_count = pd.read_sql_query(sql_dirt_marks, conn).iloc[0]['DirtMarksCount']
            
            # 差の計算
            turf_diff = abs(turf_marks_count - 697)
            dirt_diff = abs(dirt_marks_count - 388)
            
            # 最適な期間の更新
            if turf_diff < best_turf_diff and dirt_diff < best_dirt_diff:
                best_period = period_name
                best_turf_diff = turf_diff
                best_dirt_diff = dirt_diff
        
        print(f"最適な期間: {best_period}")
        print(f"芝の差: {best_turf_diff}件")
        print(f"ダートの差: {best_dirt_diff}件")
        
        # 3. 推奨アクション
        print(f"\n=== 推奨アクション ===")
        if best_turf_diff <= 2 and best_dirt_diff <= 2:
            print("✅ 目標範囲内です！")
        else:
            print("1. 馬印5+馬印6の条件の調整")
            print("2. コースタイプの条件の調整")
            print("3. 目標範囲内（±2）になるまで調整")
        
        conn.close()
        print("\n=== 調整完了 ===")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    adjust_period_conditions()




