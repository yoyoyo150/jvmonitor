from pathlib import Path

import pandas as pd


def inspect_excel(file_path: Path) -> None:
    if not file_path.exists():
        print(f"ファイルが見つかりません: {file_path}")
        return

    print(f"読み込み中: {file_path.resolve()}")
    df = pd.read_excel(file_path, sheet_name=0, dtype=str)
    print("列一覧:")
    for idx, col in enumerate(df.columns):
        print(f"  {idx}: {col}")

    print("\n先頭5行:")
    if df.empty:
        print("データがありません")
    else:
        print(df.head().to_string(index=False))


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent / "yDate"
    excel_files = sorted(base_dir.glob("*.xlsx"), reverse=True)
    if not excel_files:
        print("Excelファイルが見つかりません")
    else:
        inspect_excel(excel_files[0])







