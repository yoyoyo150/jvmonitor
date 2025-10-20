#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excelファイル内のMark5/Mark6データ確認スクリプト（別ファイル指定用）
"""
import pandas as pd
import sys
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def check_excel_marks_data_specific_file(file_path: Path, sheet_name=0):
    """指定されたExcelファイル内のMark5/Mark6データをチェック"""
    print(f"=== Excelファイル {file_path.name} のMark5/Mark6データ確認を開始します ===")
    
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        print("Excelファイル読み込み成功")
        
        # カラム名に 'Mark5' または 'Mark6' が含まれるものを抽出
        mark_columns = [col for col in df.columns if "Mark5" in col or "Mark6" in col]
        
        if not mark_columns:
            print("Mark5/Mark6関連のカラムは見つかりませんでした。")
            return
        
        print(f"検出されたMark5/Mark6関連カラム: {', '.join(mark_columns)}")
        
        # Mark5/Mark6のサンプルを表示
        print("\n--- Mark5/Mark6データのサンプル --- ")
        sample_df = df[mark_columns].head(20)
        print(sample_df.to_string())
        
        print(f"\n=== {file_path.name} データ確認完了 ===")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    target_file = Path(r"C:\my_project_folder\envs\cursor\my_keiba\yDate\20250201.xlsx")
    check_excel_marks_data_specific_file(target_file)




