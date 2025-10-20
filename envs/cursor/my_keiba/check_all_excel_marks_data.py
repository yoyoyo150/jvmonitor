#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
yDateディレクトリ内のExcelファイルのMark5/Mark6データ包括的確認スクリプト
"""
import pandas as pd
import sys
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def check_all_excel_marks_data(base_dir: Path, limit_files=None):
    """yDateディレクトリ内のExcelファイルのMark5/Mark6データを包括的にチェック"""
    print(f"=== ディレクトリ {base_dir.name} 内のExcelファイルのMark5/Mark6データ確認を開始します ===")
    
    excel_files = sorted(list(base_dir.glob("*.xlsx")) + list(base_dir.glob("*.csv")))
    if not excel_files:
        print("指定されたディレクトリにExcel/CSVファイルが見つかりませんでした。")
        return

    if limit_files:
        excel_files = excel_files[:limit_files]

    results = []
    
    for file_path in excel_files:
        print(f"\n--- ファイル: {file_path.name} の確認を開始します ---")
        try:
            if file_path.suffix == '.xlsx':
                df = pd.read_excel(file_path, dtype=str, engine='openpyxl').fillna("")
            elif file_path.suffix == '.csv':
                df = pd.read_csv(file_path, dtype=str).fillna("")
            else:
                print(f"  [skip] 未対応のファイル形式です: {file_path.name}")
                continue

            df.columns = [str(col).strip() for col in df.columns]
            
            mark5_col_exists = "馬印5" in df.columns
            mark6_col_exists = "馬印6" in df.columns
            
            mark5_sample = "N/A"
            mark6_sample = "N/A"
            
            if mark5_col_exists:
                # Mark5の非空値のサンプルを抽出。?もカウント
                valid_mark5 = df["馬印5"].loc[df["馬印5"].astype(str).str.strip() != ""]
                if not valid_mark5.empty:
                    mark5_sample = valid_mark5.head(5).tolist()
                
            if mark6_col_exists:
                # Mark6の非空値のサンプルを抽出。?もカウント
                valid_mark6 = df["馬印6"].loc[df["馬印6"].astype(str).str.strip() != ""]
                if not valid_mark6.empty:
                    mark6_sample = valid_mark6.head(5).tolist()
            
            results.append({
                "file": file_path.name,
                "馬印5_exists": mark5_col_exists,
                "馬印6_exists": mark6_col_exists,
                "馬印5_sample": mark5_sample,
                "馬印6_sample": mark6_sample
            })
            
            print(f"  馬印5 カラム: {mark5_col_exists}")
            print(f"  馬印6 カラム: {mark6_col_exists}")
            if mark5_col_exists:
                print(f"  馬印5 サンプル: {mark5_sample}")
            if mark6_col_exists:
                print(f"  馬印6 サンプル: {mark6_sample}")
                
        except Exception as e:
            print(f"  [エラー] ファイル {file_path.name} の読み込み中にエラーが発生しました: {e}")
            results.append({
                "file": file_path.name,
                "error": str(e)
            })
            
    print("\n=== 包括的データ確認完了 ===")
    print("--- 結果サマリー ---")
    for res in results:
        print(res)

if __name__ == "__main__":
    target_dir = Path(r"C:\my_project_folder\envs\cursor\my_keiba\yDate")
    # 全てのファイルを対象とするため、limit_filesはNoneに設定
    check_all_excel_marks_data(target_dir, limit_files=None)




