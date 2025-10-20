#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
コースタイプの条件の調整
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

def adjust_course_conditions():
    """コースタイプの条件の調整"""
    db_path = "ecore.db"
    
    try:
        conn = sqlite3.connect(db_path)
        print("データベース接続成功")
        
        # 1. コースタイプの条件の調整
        print("=== コースタイプの条件の調整 ===")
        
        # 様々なコースタイプの条件での芝・ダート件数確認
        course_conditions = [
            ("芝", "ダ", "芝・ダート"),
            ("芝", None, "芝のみ"),
            (None, "ダ", "ダートのみ"),
            ("芝", "芝", "芝のみ（重複）"),
            ("ダ", "ダ", "ダートのみ（重複）")
        ]
        
        for turf_condition, dirt_condition, condition_name in course_conditions:
            print(f"\n{condition_name}の条件:")
            
            # 芝の件数（馬印5+馬印6の条件）
            if turf_condition:
                sql_turf_marks = f"""
                SELECT COUNT(*) as TurfMarksCount
                FROM HORSE_MARKS
                WHERE SourceDate >= '20250901'
                AND SourceDate <= '20250928'
                AND Mark5 IS NOT NULL AND Mark5 != ''
                AND Mark6 IS NOT NULL AND Mark6 != ''
                AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) >= 1
                AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) <= 6
                AND SHIBA_DA = '{turf_condition}'
                """
                
                turf_marks_count = pd.read_sql_query(sql_turf_marks, conn).iloc[0]['TurfMarksCount']
                print(f"  芝: {turf_marks_count}件")
            else:
                turf_marks_count = 0
                print(f"  芝: 0件")
            
            # ダートの件数（馬印5+馬印6の条件）
            if dirt_condition:
                sql_dirt_marks = f"""
                SELECT COUNT(*) as DirtMarksCount
                FROM HORSE_MARKS
                WHERE SourceDate >= '20250901'
                AND SourceDate <= '20250928'
                AND Mark5 IS NOT NULL AND Mark5 != ''
                AND Mark6 IS NOT NULL AND Mark6 != ''
                AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) >= 1
                AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) <= 6
                AND SHIBA_DA = '{dirt_condition}'
                """
                
                dirt_marks_count = pd.read_sql_query(sql_dirt_marks, conn).iloc[0]['DirtMarksCount']
                print(f"  ダート: {dirt_marks_count}件")
            else:
                dirt_marks_count = 0
                print(f"  ダート: 0件")
            
            # TARGET frontierとの比較
            turf_diff = turf_marks_count - 697
            dirt_diff = dirt_marks_count - 388
            print(f"  芝の差: {turf_diff}件")
            print(f"  ダートの差: {dirt_diff}件")
            
            if abs(turf_diff) <= 2 and abs(dirt_diff) <= 2:
                print(f"  ✅ 目標範囲内（±2）です！")
            else:
                print(f"  ❌ 目標範囲外です。")
        
        # 2. 最適なコースタイプの条件の特定
        print(f"\n=== 最適なコースタイプの条件の特定 ===")
        
        best_condition = None
        best_turf_diff = float('inf')
        best_dirt_diff = float('inf')
        
        for turf_condition, dirt_condition, condition_name in course_conditions:
            # 芝の件数（馬印5+馬印6の条件）
            if turf_condition:
                sql_turf_marks = f"""
                SELECT COUNT(*) as TurfMarksCount
                FROM HORSE_MARKS
                WHERE SourceDate >= '20250901'
                AND SourceDate <= '20250928'
                AND Mark5 IS NOT NULL AND Mark5 != ''
                AND Mark6 IS NOT NULL AND Mark6 != ''
                AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) >= 1
                AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) <= 6
                AND SHIBA_DA = '{turf_condition}'
                """
                
                turf_marks_count = pd.read_sql_query(sql_turf_marks, conn).iloc[0]['TurfMarksCount']
            else:
                turf_marks_count = 0
            
            # ダートの件数（馬印5+馬印6の条件）
            if dirt_condition:
                sql_dirt_marks = f"""
                SELECT COUNT(*) as DirtMarksCount
                FROM HORSE_MARKS
                WHERE SourceDate >= '20250901'
                AND SourceDate <= '20250928'
                AND Mark5 IS NOT NULL AND Mark5 != ''
                AND Mark6 IS NOT NULL AND Mark6 != ''
                AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) >= 1
                AND (CAST(Mark5 AS INTEGER) + CAST(Mark6 AS INTEGER)) <= 6
                AND SHIBA_DA = '{dirt_condition}'
                """
                
                dirt_marks_count = pd.read_sql_query(sql_dirt_marks, conn).iloc[0]['DirtMarksCount']
            else:
                dirt_marks_count = 0
            
            # 差の計算
            turf_diff = abs(turf_marks_count - 697)
            dirt_diff = abs(dirt_marks_count - 388)
            
            # 最適な条件の更新
            if turf_diff < best_turf_diff and dirt_diff < best_dirt_diff:
                best_condition = condition_name
                best_turf_diff = turf_diff
                best_dirt_diff = dirt_diff
        
        print(f"最適なコースタイプの条件: {best_condition}")
        print(f"芝の差: {best_turf_diff}件")
        print(f"ダートの差: {best_dirt_diff}件")
        
        # 3. 推奨アクション
        print(f"\n=== 推奨アクション ===")
        if best_turf_diff <= 2 and best_dirt_diff <= 2:
            print("✅ 目標範囲内です！")
        else:
            print("1. 期間の調整")
            print("2. 馬印5+馬印6の条件の調整")
            print("3. 目標範囲内（±2）になるまで調整")
        
        conn.close()
        print("\n=== 調整完了 ===")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    adjust_course_conditions()




