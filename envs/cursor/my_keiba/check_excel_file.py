import pandas as pd
import os
import sys
import io
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_latest_excel():
    ydate_dir = r"C:\my_project_folder\envs\cursor\my_keiba\yDate"
    latest_file = "20251005.xlsx"
    file_path = os.path.join(ydate_dir, latest_file)
    
    print(f"=== {latest_file} の確認 ===\n")
    
    if not os.path.exists(file_path):
        print(f"[ERROR] ファイルが見つかりません: {file_path}")
        return
    
    try:
        # Excelファイルを読み込み
        df = pd.read_excel(file_path)
        
        print(f"[OK] ファイル読み込み成功")
        print(f"行数: {len(df)} 行")
        print(f"列数: {len(df.columns)} 列")
        
        # 列名の確認
        print(f"\n列名一覧:")
        for i, col in enumerate(df.columns):
            print(f"  {i+1:2d}. {col}")
        
        # 馬印関連の列を探す
        mark_columns = []
        for col in df.columns:
            if '馬印' in str(col) or 'mark' in str(col).lower():
                mark_columns.append(col)
        
        print(f"\n馬印関連の列:")
        for col in mark_columns:
            print(f"  - {col}")
        
        # サンプルデータの表示
        print(f"\nサンプルデータ（最初の3行）:")
        print(df.head(3).to_string())
        
        # 馬印1のデータ確認
        mark1_col = None
        for col in df.columns:
            if '馬印1' in str(col) or 'mark1' in str(col).lower():
                mark1_col = col
                break
        
        if mark1_col:
            print(f"\n馬印1列 ({mark1_col}) のデータ確認:")
            mark1_data = df[mark1_col].dropna()
            print(f"  非空データ数: {len(mark1_data)} 件")
            print(f"  データ例: {mark1_data.head(10).tolist()}")
        else:
            print(f"\n[ERROR] 馬印1列が見つかりません")
        
    except Exception as e:
        print(f"[ERROR] エラー: {e}")

if __name__ == '__main__':
    check_latest_excel()
