import pandas as pd
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def get_all_excel_headers(base_dir: Path):
    print(f"=== ディレクトリ {base_dir.name} 内の全Excelファイルからヘッダーを取得します ===")

    excel_files = sorted(list(base_dir.glob("*.xlsx")) + list(base_dir.glob("*.csv")))
    if not excel_files:
        print("指定されたディレクトリにExcel/CSVファイルが見つかりませんでした。")
        return

    all_unique_columns = set()
    processed_files = 0

    for file_path in excel_files:
        try:
            if file_path.suffix == '.xlsx':
                df = pd.read_excel(file_path, dtype=str, engine='openpyxl').fillna("")
            elif file_path == '.csv':
                df = pd.read_csv(file_path, dtype=str).fillna("")
            else:
                print(f"  [skip] 未対応のファイル形式です: {file_path.name}")
                continue

            df.columns = [str(col).strip() for col in df.columns]
            all_unique_columns.update(df.columns.tolist())
            processed_files += 1

        except Exception as e:
            print(f"  [エラー] ファイル {file_path.name} の読み込み中にエラーが発生しました: {e}")

    print(f"\n=== {processed_files} 個のファイルからヘッダーの取得が完了しました ===")
    print("--- 全てのユニークなカラム名 ---")
    for col in sorted(list(all_unique_columns)):
        print(col)

if __name__ == "__main__":
    target_dir = Path(r"C:\my_project_folder\envs\cursor\my_keiba\yDate")
    get_all_excel_headers(target_dir)




