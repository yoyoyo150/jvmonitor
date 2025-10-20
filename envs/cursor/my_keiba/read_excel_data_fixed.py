import sqlite3
import os
import pandas as pd
import sys
from datetime import datetime

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def read_excel_data_fixed():
    """文字化けを修正したExcelデータ読み取り"""
    
    print("=== 文字化け修正版Excelデータ読み取り ===")
    
    # yDateフォルダのファイル一覧
    ydate_files = []
    if os.path.exists('yDate'):
        for file in os.listdir('yDate'):
            if file.endswith(('.xlsx', '.xls', '.csv')) and not file.startswith('25025'):
                ydate_files.append(file)
    
    ydate_files.sort()
    print(f"処理対象ファイル数: {len(ydate_files)}")
    
    # 最新5ファイルをテスト
    test_files = ydate_files[-5:]
    print(f"\nテスト対象ファイル: {test_files}")
    
    for file in test_files:
        file_path = os.path.join('yDate', file)
        print(f"\n--- {file} の読み取り ---")
        
        try:
            # Excelファイルの読み取り（文字化け対策）
            if file.endswith('.csv'):
                # CSVファイル
                df = pd.read_csv(file_path, encoding='utf-8-sig')
            else:
                # Excelファイル
                df = pd.read_excel(file_path, engine='openpyxl')
            
            print(f"行数: {len(df)}")
            print(f"列数: {len(df.columns)}")
            
            # 最初の5行を表示
            print("最初の5行:")
            for i, row in df.head().iterrows():
                print(f"  行{i+1}: {dict(row)}")
            
            # 馬名のサンプル（文字化けチェック）
            if 'HorseName' in df.columns or '馬名' in df.columns:
                horse_col = 'HorseName' if 'HorseName' in df.columns else '馬名'
                horse_names = df[horse_col].dropna().head(3).tolist()
                print(f"馬名サンプル: {horse_names}")
            
            # Mark5/Mark6のサンプル
            mark_cols = [col for col in df.columns if 'Mark' in col or 'マーク' in col]
            print(f"Mark列: {mark_cols}")
            
            for col in mark_cols[:2]:  # 最初の2つのMark列
                if col in df.columns:
                    mark_values = df[col].dropna().head(5).tolist()
                    print(f"{col}サンプル: {mark_values}")
            
        except Exception as e:
            print(f"エラー: {e}")
    
    print("\n=== 文字化け修正完了 ===")

if __name__ == "__main__":
    read_excel_data_fixed()




