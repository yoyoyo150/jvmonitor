import sqlite3
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import re

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def normalize_horse_name(value: str) -> str:
    """Remove all whitespace characters to normalise horse names."""
    return "".join(value.replace(" ", "").replace("　", ""))

def extract_source_date(file_path: Path) -> str:
    """Extract date from filename (YYYYMMDD format)."""
    match = re.search(r"(20\d{6})", file_path.stem)
    if match:
        return match.group(1)
    return datetime.now().strftime("%Y%m%d") # Fallback if no date in filename

def extract_race_num_from_ba_r(ba_r_value: str) -> str:
    """Extracts race number from '場 R' column (e.g., '中11' -> '11')."""
    match = re.search(r'\d+', ba_r_value)
    if match:
        return match.group(0)
    return ""

# Excelカラム名とDBカラム名のマッピング
# ここに全カラムのマッピングを記述。不足分は随時追加。
COLUMN_MAPPING = {
    "レースID(新)": "RaceID_New",
    "馬名S": "HorseNameS",
    "場 R": "Ba_R_Raw",
    "レース名": "RaceName",
    "芝ダ": "Shiba_Da",
    "距離": "Kyori_M",
    "R印1": "R_Mark1",
    "レース印2": "Race_Mark2",
    "レース印3": "Race_Mark3",
    "馬番": "Umaban",
    "馬印1": "Mark1",
    "馬印2": "Mark2",
    "馬印3": "Mark3",
    "馬印4": "Mark4",
    "馬印5": "Mark5",
    "馬印6": "Mark6",
    "馬印7": "Mark7",
    "馬印8": "Mark8",
    "Ｃ": "C_Flag",
    "着": "Chaku",
    "性": "Sex",
    "齢": "Age",
    "騎手": "Jockey",
    "斤量": "Kinryo",
    "前脚質": "Prev_Kyakushitsu",
    "前馬印1": "Prev_Mark1",
    "前印2": "Prev_Mark2",
    "前印3": "Prev_Mark3",
    "前印4": "Prev_Mark4",
    "前印5": "Prev_Mark5",
    "前印6": "Prev_Mark6",
    "前印7": "Prev_Mark7",
    "前印8": "Prev_Mark8",
    "前人気": "Prev_Ninki",
    "ZM": "ZM_Value",
    "指数順位1": "Index_Rank1",
    "加速": "Accel_Val",
    "指数順位2": "Index_Rank2",
    "指差2": "Index_Diff2",
    "オリジナル": "Original_Val",
    "指数順位3": "Index_Rank3",
    "ZI指数": "ZI_Index",
    "指数順位4": "Index_Rank4",
    "前着順": "Prev_Chaku_Juni",
    "前着差": "Prev_Chaku_Sa",
    "単勝": "Tansho_Odds",
    "複勝": "Fukusho_Odds",
    "指差4": "Index_Diff4",
    "指差1": "Index_Diff1",
    "前通過1": "Prev_Tsuka1",
    "前通過2": "Prev_Tsuka2",
    "前通過3": "Prev_Tsuka3",
    "前通過4": "Prev_Tsuka4",
    "前3F順": "Prev_3F_Juni",
    "前頭数": "Prev_Tosu",
    "前レース印": "Prev_Race_Mark",
    "前レース印2": "Prev_Race_Mark2",
    "前レース印3": "Prev_Race_Mark3",
    "父タイプ名": "Father_Type_Name",
    "頭": "Total_Horses",
    "ワーク1": "Work1",
    "ワーク2": "Work2",
    "前場所": "Prev_Track_Name",
    "同場": "Same_Track_Flag",
    "前斤量": "Prev_Kinryo",
    "前馬体重": "Prev_Bataiju",
    "前馬体重増減": "Prev_Bataiju_Zogen",
    "年齢": "Age_At_Race",
    "間隔": "Interval",
    "休明戦目": "Kyumei_Senme",
    "斤量差": "Kinryo_Sa",
    "距離差": "Kyori_Sa",
    "前芝ダ": "Prev_Shiba_Da",
    "前距離": "Prev_Kyori_M",
    "キャリア(当時/取消等含)": "Career_Total",
    "キャリア(最新)": "Career_Latest",
    "クラスC": "Class_C",
    "前番": "Prev_Umaban",
    "前芝ダ.1": "Prev_Shiba_Da_1",
    "今芝ダ": "Current_Shiba_Da",
    "前馬場状態": "Prev_Baba_Jotai",
    "前ｸﾗｽ": "Prev_Class",
    "母父タイプ名": "Damsire_Type_Name",
    "Tﾏ差": "T_Mark_Diff",
    "対戦型マイニング値": "Matchup_Mining_Val",
    "対戦型マイニング順位": "Matchup_Mining_Rank",
    "降級戦": "Kokyusen_Flag",
    "B": "B_Flag",
    "所属": "Syozoku",
    "チェック調教師タイプ": "Check_Trainer_Type",
    "チェック騎手タイプ": "Check_Jockey_Type",
    "所属.1": "Syozoku_1",
    "調教師": "Trainer_Name",
    "複勝オッズ下": "Fukusho_Odds_Lower",
    "上": "Fukusho_Odds_Upper",
    "単オッズ": "Tan_Odds",
    "枠番": "Wakuban",
    "コースグループ数": "Course_Group_Count",
    "コースグループ名1": "Course_Group_Name1",
    "人気": "Ninki_Rank",
    "乗替": "Norikae_Flag",
    "前レースID(新)": "Prev_Race_ID_New"
}

def import_excel_data_to_dedicated_db(excel_dir: Path, db_path: Path):
    print(f"=== Excelデータを専用DB '{db_path.name}' にインポートします ===")

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        excel_files = sorted(list(excel_dir.glob("*.xlsx")) + list(excel_dir.glob("*.csv")))
        if not excel_files:
            print("指定されたディレクトリにExcel/CSVファイルが見つかりませんでした。")
            return
        
        total_imported_rows = 0

        for file_path in excel_files:
            print(f"--- ファイル: {file_path.name} のインポートを開始します ---")
            try:
                if file_path.suffix == '.xlsx':
                    df = pd.read_excel(file_path, dtype=str, engine='openpyxl').fillna("")
                elif file_path.suffix == '.csv':
                    df = pd.read_csv(file_path, dtype=str).fillna("")
                else:
                    print(f"  [skip] 未対応のファイル形式です: {file_path.name}")
                    continue

                df.columns = [str(col).strip() for col in df.columns] # カラム名を整形

                records_to_insert = []
                source_file_name = file_path.name
                imported_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                source_date = extract_source_date(file_path)

                for index, row_series in df.iterrows():
                    row_data = row_series.to_dict()
                    processed_data = {
                        "SourceDate": source_date,
                        "ImportedAt": imported_at,
                        "SourceFile": source_file_name,
                        "NormalizedHorseName": normalize_horse_name(str(row_data.get("馬名S", "") or "")),
                        "Ba_R_Raw": str(row_data.get("場 R", "") or ""), # '場 R'の生データを保持
                    }
                    
                    # 他のカラムをマッピングに基づいて追加
                    for excel_col, db_col in COLUMN_MAPPING.items():
                        if excel_col in row_data:
                            processed_data[db_col] = str(row_data.get(excel_col, "") or "")
                        else:
                            processed_data[db_col] = None # ExcelにないカラムはNULLに

                    # NULL値の正規化（空文字列をNoneにする）
                    for key, value in processed_data.items():
                        if value == "":
                            processed_data[key] = None

                    records_to_insert.append(processed_data)

                if records_to_insert:
                    # カラム名リストとプレースホルダーを作成
                    columns = ', '.join(records_to_insert[0].keys())
                    placeholders = ', '.join([f':{key}' for key in records_to_insert[0].keys()])
                    insert_sql = f"INSERT OR REPLACE INTO excel_marks ({columns}) VALUES ({placeholders})"
                    
                    cursor.executemany(insert_sql, records_to_insert)
                    conn.commit()
                    total_imported_rows += len(records_to_insert)
                    print(f"  [OK] {len(records_to_insert)} 件のレコードをインポートしました。")

            except Exception as e:
                print(f"  [エラー] ファイル {file_path.name} のインポート中にエラーが発生しました: {e}")
                if conn:
                    conn.rollback()

        print(f"\n=== 全てのExcelファイルのインポートが完了しました。合計インポート数: {total_imported_rows} 件 ===")

    except sqlite3.Error as e:
        print(f"[エラー] SQLiteデータベースの操作中にエラーが発生しました: {e}")
    except Exception as e:
        print(f"[エラー] 予期せぬエラーが発生しました: {e}")
    finally:
        if conn:
            conn.close()
            print("データベース接続を閉じました。")

if __name__ == "__main__":
    excel_data_dir = Path(r"C:\my_project_folder\envs\cursor\my_keiba\yDate")
    dedicated_db_path = Path("trainer_prediction_system/excel_data.db")
    
    import_excel_data_to_dedicated_db(excel_data_dir, dedicated_db_path)




