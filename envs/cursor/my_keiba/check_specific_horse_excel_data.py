#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excelファイル内の特定馬のMark5/Mark6データ詳細確認スクリプト
"""
import pandas as pd
import sys
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def check_specific_horse_excel_data(file_path: Path, horse_name: str, race_num: str, jyo_cd: str, sheet_name=0):
    """指定されたExcelファイル内の特定馬のMark5/Mark6データを詳細にチェック"""
    print(f"=== Excelファイル {file_path.name} 内の {horse_name} のデータ確認を開始します ===")
    
    try:
        if file_path.suffix == '.xlsx':
            df = pd.read_excel(file_path, dtype=str, engine='openpyxl').fillna("")
        elif file_path.suffix == '.csv':
            df = pd.read_csv(file_path, dtype=str).fillna("")
        else:
            print(f"  [skip] 未対応のファイル形式です: {file_path.name}")
            return

        df.columns = [str(col).strip() for col in df.columns]
        print("Excelファイル読み込み成功。カラム:", df.columns.tolist())
        
        # レースID(新)のフォーマットに合わせて検索条件を構築
        # レースID(新)は YearMonthDayJyoCDKaijiNichijiRaceNum の形式
        # 202509280611 の場合、20250928 (SourceDate), 06 (JyoCD), 11 (RaceNum) に対応
        target_race_id_prefix = file_path.stem # 20250928
        
        # 馬名、レース番号、開催コードでフィルタリング
        filtered_df = df[
            (df["馬名S"] == horse_name) & 
            (df["場 R"] == race_num) & 
            (df["レース名"].str.contains(jyo_cd)) # レース名に開催コード（中山）が含まれるかでフィルタ
        ]

        if not filtered_df.empty:
            print(f"\n--- {horse_name} のデータが見つかりました --- ")
            print(filtered_df.to_string())
        else:
            print(f"\n{horse_name} のデータはファイルに見つかりませんでした。")
            
        print(f"\n=== {file_path.name} データ確認完了 ===")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    target_file = Path(r"C:\my_project_folder\envs\cursor\my_keiba\yDate\20250928.xlsx")
    horse_name = 'トウシンマカオ'
    race_num = '11' # 11R
    jyo_cd = '中山' # 中山
    check_specific_horse_excel_data(target_file, horse_name, race_num, jyo_cd)
