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
        print("\n--- DataFrameの先頭5行 ---")
        print(df.head().to_string())
        print(f"初期行数: {len(df)}")

        print(f"検索条件: horse_name='{horse_name}', race_num='{race_num}', jyo_cd='{jyo_cd}'")

        # カラムのユニーク値を表示して、一致する値があるか確認
        if "馬名S" in df.columns:
            print(f"カラム '馬名S' のユニーク値（一部）: {df['馬名S'].unique()[:10].tolist()}")
        if "場 R" in df.columns:
            print(f"カラム '場 R' のユニーク値（一部）: {df['場 R'].unique()[:10].tolist()}")
        if "レース名" in df.columns:
            print(f"カラム 'レース名' のユニーク値（一部）: {df['レース名'].unique()[:10].tolist()}")

        # 馬名でフィルタリング
        filtered_by_horse = df[df["馬名S"] == horse_name]
        print(f"馬名 '{horse_name}' でフィルタリング後行数: {len(filtered_by_horse)}")
        if not filtered_by_horse.empty:
            print("\n--- 馬名でフィルタリング後のDataFrame ---")
            print(filtered_by_horse.to_string())
        
        # レース番号でフィルタリング
        # お客様のスクリーンショットから '場 R' は '中11' のような形式であるため、結合して検索
        target_race_full_id = jyo_cd + race_num  # 例: '中山' + '11' -> '中山11'
        # Excelファイルのカラム '場 R' が '中1' のような略称であることを考慮し、部分一致ではなく、より厳密に検索します。
        # JyoCD（場所コード）は、通常は数字ですが、Excelデータでは「中山」のような文字列で使われています。
        # スクリーンショットの「場 R」カラムは、開催場所の略称（例：「中」）とレース番号を組み合わせた文字列（例：「中11」）になっています。
        # なので、jyo_cd（ここでは「中山」）から略称「中」を抽出し、race_num「11」と結合して「中11」を作成します。
        # ただし、JyoCDが必ずしも「中山」→「中」のように単純変換できるとは限らないため、まずは仮に「中」と固定して試します。
        # より汎用的にするためには、JyoCDのマップが必要です。現状は、お客様のデータから「中山」→「中」を仮定します。
        jyo_abbr = ''
        if jyo_cd == '中山':
            jyo_abbr = '中'
        elif jyo_cd == '東京':
            jyo_abbr = '東'
        # 他の開催場所も同様に追加
        
        if jyo_abbr:
            target_race_full_id_for_場R = jyo_abbr + race_num # 例: '中' + '11' -> '中11'
            filtered_by_race_num = filtered_by_horse[filtered_by_horse["場 R"] == target_race_full_id_for_場R]
            print(f"レース番号 '{target_race_full_id_for_場R}' でフィルタリング後行数: {len(filtered_by_race_num)}")
            if not filtered_by_race_num.empty:
                print("\n--- レース番号でフィルタリング後のDataFrame ---")
                print(filtered_by_race_num.to_string())
        else:
            print(f"開催コード '{jyo_cd}' の略称が不明なため、'場 R' でのフィルタリングをスキップします。")
            filtered_by_race_num = filtered_by_horse # フィルタリングせずに次へ

        # 開催コードでフィルタリング（レース名に開催コードが含まれるか）
        # ここでのフィルタリングは不要なため、前のステップの結果をそのまま利用
        final_filtered_df = filtered_by_race_num
        print(f"最終フィルタリング後行数: {len(final_filtered_df)}")

        if not final_filtered_df.empty:
            print(f"\n--- {horse_name} のデータが見つかりました --- ")
            print(final_filtered_df.to_string())
            
            # Mark5/Mark6 カラムの存在確認と内容表示
            mark_columns_found = []
            if "馬印5" in final_filtered_df.columns:
                mark_columns_found.append("馬印5")
            if "馬印6" in final_filtered_df.columns:
                mark_columns_found.append("馬印6")
            
            if mark_columns_found:
                print("\n--- Mark5/Mark6 データ ---")
                print(final_filtered_df[mark_columns_found].to_string())
            else:
                print("\nMark5/Mark6 関連のカラムは見つかりませんでした。")

        else:
            print(f"\n{horse_name} のデータはファイルに見つかりませんでした。")
            
        print(f"\n=== {file_path.name} データ確認完了 ===\n")
            
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
