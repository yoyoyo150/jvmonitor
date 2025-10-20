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

def adjust_period_final():
    """期間の最終調整"""
    db_path = "ecore.db"
    
    try:
        conn = sqlite3.connect(db_path)
        print("データベース接続成功")
        
        # 1. 期間の最終調整
        print("=== 期間の最終調整 ===")
        
        # 様々な期間での芝・ダート件数確認
        periods = [
            ("20250201", "20250928", "2/1-9/28"),
            ("20250201", "20250915", "2/1-9/15"),
            ("20250201", "20250910", "2/1-9/10"),
            ("20250201", "20250905", "2/1-9/5"),
            ("20250201", "20250831", "2/1-8/31"),
            ("20250201", "20250825", "2/1-8/25"),
            ("20250201", "20250820", "2/1-8/20"),
            ("20250201", "20250815", "2/1-8/15"),
            ("20250201", "20250810", "2/1-8/10"),
            ("20250201", "20250805", "2/1-8/5"),
            ("20250201", "20250731", "2/1-7/31"),
            ("20250201", "20250725", "2/1-7/25"),
            ("20250201", "20250720", "2/1-7/20"),
            ("20250201", "20250715", "2/1-7/15"),
            ("20250201", "20250710", "2/1-7/10"),
            ("20250201", "20250705", "2/1-7/5"),
            ("20250201", "20250630", "2/1-6/30"),
            ("20250201", "20250625", "2/1-6/25"),
            ("20250201", "20250620", "2/1-6/20"),
            ("20250201", "20250615", "2/1-6/15"),
            ("20250201", "20250610", "2/1-6/10"),
            ("20250201", "20250605", "2/1-6/5"),
            ("20250201", "20250531", "2/1-5/31"),
            ("20250201", "20250525", "2/1-5/25"),
            ("20250201", "20250520", "2/1-5/20"),
            ("20250201", "20250515", "2/1-5/15"),
            ("20250201", "20250510", "2/1-5/10"),
            ("20250201", "20250505", "2/1-5/5"),
            ("20250201", "20250430", "2/1-4/30"),
            ("20250201", "20250425", "2/1-4/25"),
            ("20250201", "20250420", "2/1-4/20"),
            ("20250201", "20250415", "2/1-4/15"),
            ("20250201", "20250410", "2/1-4/10"),
            ("20250201", "20250405", "2/1-4/5"),
            ("20250201", "20250331", "2/1-3/31"),
            ("20250201", "20250325", "2/1-3/25"),
            ("20250201", "20250320", "2/1-3/20"),
            ("20250201", "20250315", "2/1-3/15"),
            ("20250201", "20250310", "2/1-3/10"),
            ("20250201", "20250305", "2/1-3/5"),
            ("20250201", "20250228", "2/1-2/28"),
            ("20250201", "20250225", "2/1-2/25"),
            ("20250201", "20250220", "2/1-2/20"),
            ("20250201", "20250215", "2/1-2/15"),
            ("20250201", "20250210", "2/1-2/10"),
            ("20250201", "20250205", "2/1-2/5")
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
    adjust_period_final()




