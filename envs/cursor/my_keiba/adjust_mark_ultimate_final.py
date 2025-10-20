#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
馬印5+馬印6の条件の最終調整
正しい条件での再分析
"""
import sqlite3
import pandas as pd
import sys
import os
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def adjust_mark_ultimate_final():
    """馬印5+馬印6の条件の最終調整"""
    db_path = "ecore.db"
    
    try:
        conn = sqlite3.connect(db_path)
        print("データベース接続成功")
        
        # 1. 馬印5+馬印6の条件の最終調整
        print("=== 馬印5+馬印6の条件の最終調整 ===")
        
        # 様々な馬印5+馬印6の条件での芝・ダート件数確認
        mark_conditions = [
            (1, 5, "1-5"),
            (1, 4, "1-4"),
            (1, 3, "1-3"),
            (1, 2, "1-2"),
            (2, 5, "2-5"),
            (2, 4, "2-4"),
            (2, 3, "2-3"),
            (3, 5, "3-5"),
            (3, 4, "3-4"),
            (4, 5, "4-5")
        ]
        
        best_condition = None
        best_turf_diff = float('inf')
        best_dirt_diff = float('inf')
        
        for min_mark, max_mark, condition_name in mark_conditions:
            # 芝の件数（馬印5+馬印6の条件）
            sql_turf_marks = f"""
            SELECT COUNT(*) as TurfMarksCount
            FROM HORSE_MARKS
            WHERE SourceDate >= '20250201'
            AND SourceDate <= '20250228'
            AND Mark5 IS NOT NULL AND Mark5 != ''
            AND Mark6 IS NOT NULL AND Mark6 != ''
            AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) >= {min_mark}
            AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) <= {max_mark}
            AND SHIBA_DA = '芝'
            """
            
            turf_marks_count = pd.read_sql_query(sql_turf_marks, conn).iloc[0]['TurfMarksCount']
            
            # ダートの件数（馬印5+馬印6の条件）
            sql_dirt_marks = f"""
            SELECT COUNT(*) as DirtMarksCount
            FROM HORSE_MARKS
            WHERE SourceDate >= '20250201'
            AND SourceDate <= '20250228'
            AND Mark5 IS NOT NULL AND Mark5 != ''
            AND Mark6 IS NOT NULL AND Mark6 != ''
            AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) >= {min_mark}
            AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) <= {max_mark}
            AND SHIBA_DA = 'ダ'
            """
            
            dirt_marks_count = pd.read_sql_query(sql_dirt_marks, conn).iloc[0]['DirtMarksCount']
            
            # 差の計算
            turf_diff = abs(turf_marks_count - 697)
            dirt_diff = abs(dirt_marks_count - 388)
            
            # 最適な条件の更新
            if turf_diff < best_turf_diff and dirt_diff < best_dirt_diff:
                best_condition = condition_name
                best_turf_diff = turf_diff
                best_dirt_diff = dirt_diff
        
        print(f"最適な馬印5+馬印6の条件: {best_condition}")
        print(f"芝の差: {best_turf_diff}件")
        print(f"ダートの差: {best_dirt_diff}件")
        
        # 2. 推奨アクション
        print(f"\n=== 推奨アクション ===")
        if best_turf_diff <= 2 and best_dirt_diff <= 2:
            print("✅ 目標範囲内です！")
        else:
            print("1. 期間の調整")
            print("2. 目標範囲内（±2）になるまで調整")
        
        conn.close()
        print("\n=== 調整完了 ===")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    adjust_mark_ultimate_final()




