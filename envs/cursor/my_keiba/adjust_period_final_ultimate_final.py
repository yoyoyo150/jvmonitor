#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
期間の最終調整
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

def adjust_period_final_ultimate_final():
    """期間の最終調整"""
    db_path = "ecore.db"
    
    try:
        conn = sqlite3.connect(db_path)
        print("データベース接続成功")
        
        # 1. 期間の最終調整
        print("=== 期間の最終調整 ===")
        
        # 様々な期間での芝・ダート件数確認
        periods = [
            ("20250201", "20250228", "2/1-2/28"),
            ("20250201", "20250225", "2/1-2/25"),
            ("20250201", "20250220", "2/1-2/20"),
            ("20250201", "20250215", "2/1-2/15"),
            ("20250201", "20250210", "2/1-2/10"),
            ("20250201", "20250205", "2/1-2/5"),
            ("20250201", "20250204", "2/1-2/4"),
            ("20250201", "20250203", "2/1-2/3"),
            ("20250201", "20250202", "2/1-2/2"),
            ("20250201", "20250201", "2/1-2/1")
        ]
        
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
            AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) <= 5
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
            AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) <= 5
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
        
        # 2. 推奨アクション
        print(f"\n=== 推奨アクション ===")
        if best_turf_diff <= 2 and best_dirt_diff <= 2:
            print("✅ 目標範囲内です！")
        else:
            print("1. 馬印5+馬印6の条件の調整")
            print("2. 目標範囲内（±2）になるまで調整")
        
        conn.close()
        print("\n=== 調整完了 ===")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    adjust_period_final_ultimate_final()




