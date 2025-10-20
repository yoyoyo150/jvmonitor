#!/usr/bin/env python3

from __future__ import annotations



import argparse

from datetime import datetime

import re

import sqlite3

from pathlib import Path

from typing import Sequence, Iterable



import pandas as pd

import sys



# Excel̃CNV}NXƃIbỸJ

MARK_COLUMNS = ["馬印1", "馬印2", "馬印3", "馬印4", "馬印5", "馬印6", "馬印7", "馬印8"]

MARK_FIELD_NAMES = [f"Mark{i}" for i in range(1, 9)]

MORNING_ODDS_COLUMNS = ["朝一オッズ", "朝一", "単オッズ", "単勝"]





HORSE_MARKS_COLUMN_DEFS: list[tuple[str, str, str]] = [
    ("SourceDate", "TEXT NOT NULL", "TEXT"),
    ("NormalizedHorseName", "TEXT NOT NULL", "TEXT"),
    ("HorseName", "TEXT", "TEXT"),
    ("RaceId", "TEXT", "TEXT"),
    ("RaceName", "TEXT", "TEXT"),
    ("JyoCD", "TEXT", "TEXT"),
    ("Kaiji", "TEXT", "TEXT"),
    ("Nichiji", "TEXT", "TEXT"),
    ("RaceNum", "TEXT", "TEXT"),
    ("Umaban", "TEXT", "TEXT"),
    ("MorningOdds", "TEXT", "TEXT"),
    ("Mark1", "TEXT", "TEXT"),
    ("Mark2", "TEXT", "TEXT"),
    ("Mark3", "TEXT", "TEXT"),
    ("Mark4", "TEXT", "TEXT"),
    ("Mark5", "TEXT", "TEXT"),
    ("Mark6", "TEXT", "TEXT"),
    ("Mark7", "TEXT", "TEXT"),
    ("Mark8", "TEXT", "TEXT"),
    ("ZI_INDEX", "TEXT", "TEXT"),
    ("ZM_VALUE", "TEXT", "TEXT"),
    ("ZI_RANK", "TEXT", "TEXT"),
    ("SHIBA_DA", "TEXT", "TEXT"),
    ("KYORI_M", "TEXT", "TEXT"),
    ("R_MARK1", "TEXT", "TEXT"),
    ("R_MARK2", "TEXT", "TEXT"),
    ("R_MARK3", "TEXT", "TEXT"),
    ("RACE_CLASS_C", "TEXT", "TEXT"),
    ("CHAKU", "TEXT", "TEXT"),
    ("SEX", "TEXT", "TEXT"),
    ("AGE", "TEXT", "TEXT"),
    ("JOCKEY", "TEXT", "TEXT"),
    ("KINRYO", "TEXT", "TEXT"),
    ("PREV_KYAKUSHITSU", "TEXT", "TEXT"),
    ("PREV_MARK1", "TEXT", "TEXT"),
    ("PREV_MARK2", "TEXT", "TEXT"),
    ("PREV_MARK3", "TEXT", "TEXT"),
    ("PREV_MARK4", "TEXT", "TEXT"),
    ("PREV_MARK5", "TEXT", "TEXT"),
    ("PREV_MARK6", "TEXT", "TEXT"),
    ("PREV_MARK7", "TEXT", "TEXT"),
    ("PREV_MARK8", "TEXT", "TEXT"),
    ("PREV_NINKI", "TEXT", "TEXT"),
    ("INDEX_RANK1", "TEXT", "TEXT"),
    ("ACCEL_VAL", "TEXT", "TEXT"),
    ("INDEX_RANK2", "TEXT", "TEXT"),
    ("INDEX_DIFF2", "TEXT", "TEXT"),
    ("ORIGINAL_VAL", "TEXT", "TEXT"),
    ("INDEX_RANK3", "TEXT", "TEXT"),
    ("INDEX_RANK4", "TEXT", "TEXT"),
    ("PREV_CHAKU_JUNI", "TEXT", "TEXT"),
    ("PREV_CHAKU_SA", "TEXT", "TEXT"),
    ("TANSHO_ODDS", "TEXT", "TEXT"),
    ("FUKUSHO_ODDS", "TEXT", "TEXT"),
    ("INDEX_DIFF4", "TEXT", "TEXT"),
    ("INDEX_DIFF1", "TEXT", "TEXT"),
    ("PREV_TSUKA1", "TEXT", "TEXT"),
    ("PREV_TSUKA2", "TEXT", "TEXT"),
    ("PREV_TSUKA3", "TEXT", "TEXT"),
    ("PREV_TSUKA4", "TEXT", "TEXT"),
    ("PREV_3F_JUNI", "TEXT", "TEXT"),
    ("PREV_TOSU", "TEXT", "TEXT"),
    ("PREV_RACE_MARK", "TEXT", "TEXT"),
    ("PREV_RACE_MARK2", "TEXT", "TEXT"),
    ("PREV_RACE_MARK3", "TEXT", "TEXT"),
    ("FATHER_TYPE_NAME", "TEXT", "TEXT"),
    ("TOTAL_HORSES", "TEXT", "TEXT"),
    ("WORK1", "TEXT", "TEXT"),
    ("WORK2", "TEXT", "TEXT"),
    ("PREV_TRACK_NAME", "TEXT", "TEXT"),
    ("SAME_TRACK_FLAG", "TEXT", "TEXT"),
    ("PREV_KINRYO", "TEXT", "TEXT"),
    ("PREV_BATAIJU", "TEXT", "TEXT"),
    ("PREV_BATAIJU_ZOGEN", "TEXT", "TEXT"),
    ("AGE_AT_RACE", "TEXT", "TEXT"),
    ("INTERVAL", "TEXT", "TEXT"),
    ("KYUMEI_SENME", "TEXT", "TEXT"),
    ("KINRYO_SA", "TEXT", "TEXT"),
    ("KYORI_SA", "TEXT", "TEXT"),
    ("PREV_SHIBA_DA", "TEXT", "TEXT"),
    ("PREV_KYORI_M", "TEXT", "TEXT"),
    ("CAREER_TOTAL", "TEXT", "TEXT"),
    ("CAREER_LATEST", "TEXT", "TEXT"),
    ("CLASS_C", "TEXT", "TEXT"),
    ("PREV_UMABAN", "TEXT", "TEXT"),
    ("CURRENT_SHIBA_DA", "TEXT", "TEXT"),
    ("PREV_BABA_JOTAI", "TEXT", "TEXT"),
    ("PREV_CLASS", "TEXT", "TEXT"),
    ("DAMSIRE_TYPE_NAME", "TEXT", "TEXT"),
    ("T_MARK_DIFF", "TEXT", "TEXT"),
    ("MATCHUP_MINING_VAL", "TEXT", "TEXT"),
    ("MATCHUP_MINING_RANK", "TEXT", "TEXT"),
    ("KOKYUSEN_FLAG", "TEXT", "TEXT"),
    ("B_COL_FLAG", "TEXT", "TEXT"),
    ("SYOZOKU", "TEXT", "TEXT"),
    ("CHECK_TRAINER_TYPE", "TEXT", "TEXT"),
    ("CHECK_JOCKEY_TYPE", "TEXT", "TEXT"),
    ("TRAINER_NAME", "TEXT", "TEXT"),
    ("FUKUSHO_ODDS_LOWER", "TEXT", "TEXT"),
    ("FUKUSHO_ODDS_UPPER", "TEXT", "TEXT"),
    ("TAN_ODDS", "TEXT", "TEXT"),
    ("WAKUBAN", "TEXT", "TEXT"),
    ("COURSE_GROUP_COUNT", "TEXT", "TEXT"),
    ("COURSE_GROUP_NAME1", "TEXT", "TEXT"),
    ("NINKI_RANK", "TEXT", "TEXT"),
    ("NORIKAE_FLAG", "TEXT", "TEXT"),
    ("PREV_RACE_ID", "TEXT", "TEXT"),
    ("SourceFile", "TEXT", "TEXT"),
    ("ImportedAt", "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP", "DATETIME"),
]





def normalize_horse_name(value: str) -> str:

    """Remove all whitespace characters to normalise horse names."""

    return "".join(value.replace(" ", "").replace("　", ""))





def ensure_schema(conn: sqlite3.Connection) -> None:

    """Ensure the HORSE_MARKS schema matches the expected column layout."""

    existing_columns = {row[1] for row in conn.execute("PRAGMA table_info(HORSE_MARKS)")}



    if not existing_columns:

        column_sql = ",\n            ".join(

            f"{name} {definition}" for name, definition, _ in HORSE_MARKS_COLUMN_DEFS

        )

        conn.execute(

            f"""

        CREATE TABLE HORSE_MARKS (

            {column_sql},

            PRIMARY KEY (SourceDate, NormalizedHorseName)

        )

        """

        )

    else:

        for name, _create_def, alter_def in HORSE_MARKS_COLUMN_DEFS:

            if name not in existing_columns:

                conn.execute(f"ALTER TABLE HORSE_MARKS ADD COLUMN {name} {alter_def}")



    conn.execute("CREATE INDEX IF NOT EXISTS IDX_HORSE_MARKS_NAME ON HORSE_MARKS (NormalizedHorseName)")





def parse_race_id(value: str) -> dict[str, str]:

    """Split a 16-digit race id into components."""

    if not value:

        return {}

    digits = value.strip()

    if len(digits) >= 16 and digits[:16].isdigit():

        return {

            "year": digits[:4],

            "month_day": digits[4:8],

            "jyo_cd": digits[8:10],

            "kaiji": digits[10:12],

            "nichiji": digits[12:14],

            "race_num": digits[14:16],

        }

    return {}





def extract_source_date(file_path: Path, race_id: str) -> str:

    """Prefer the race id date, fall back to the first 8 digits in the file name."""

    parts = parse_race_id(race_id)

    if parts:

        return parts["year"] + parts["month_day"]

    match = re.search(r"(20\d{6})", file_path.stem)

    if match:

        return match.group(1)

    return datetime.now().strftime("%Y%m%d")





def read_excel(path: Path) -> pd.DataFrame:

    # engine='openpyxl' を明示的に指定して文字化けを防ぐ

    # CX (ENDLINE) の定義に従い、読み込む列を明確に指定する

    df = pd.read_excel(path, dtype=str, engine='openpyxl', usecols='A:CU').fillna("")

    df.columns = [str(col).strip() for col in df.columns]

    return df





def iter_excel_files(base_dir: Path, names: Sequence[str] | None) -> list[Path]:

    if names:

        return [base_dir / name for name in names]

    return sorted(base_dir.glob("*.xlsx"))





def find_morning_odds(record: dict[str, str]) -> str:

    for column in MORNING_ODDS_COLUMNS:

        value = str(record.get(column, "") or "").strip()

        if value:

            return value

    return ""





def get_first_value(record: dict[str, str], *keys: str) -> str:

    """Return the first non-empty value for the given keys."""

    for key in keys:

        if not key:

            continue

        raw = record.get(key)

        if raw is None:

            continue

        value = str(raw).strip()

        if value:

            return value

    return ""





def collect_marks(record: dict[str, str]) -> dict[str, str]:

    marks: dict[str, str] = {

        "Mark1": str(record.get("馬印1", "") or "").strip(),

        "Mark2": str(record.get("馬印2", "") or "").strip(), # アルゴ

        "Mark3": str(record.get("馬印3", "") or "").strip(),     # スピリット・上がり差

        "Mark4": str(record.get("馬印4", "") or "").strip(),     # 前走ZM順

        "Mark5": str(record.get("馬印5", "") or "").strip(),

        "Mark6": str(record.get("馬印6", "") or "").strip(),

        "Mark7": str(record.get("馬印7", "") or "").strip(), # スクリーンショットではP列、現状確認.txtではZMと解釈されたが、馬印7として明記

        "Mark8": str(record.get("馬印8", "") or "").strip(),

        "ZI_INDEX": str(record.get("ZI指数", "") or "").strip(), # V列

        "ZM_VALUE": str(record.get("ZM", "") or "").strip(),     # T列

    }

    return marks





def collect_all_excel_data(record: dict[str, str], file_path: Path) -> dict[str, str | None]:

    race_id = get_first_value(record, "レースID(新)")

    race_parts = parse_race_id(race_id)

    horse_name = get_first_value(record, "馬名S")

    normalized_name = normalize_horse_name(horse_name)



    data: dict[str, str | None] = {

        "SourceDate": extract_source_date(file_path, race_id),

        "HorseName": horse_name,

        "NormalizedHorseName": normalized_name,

        "RaceId": race_id,

        "RaceName": get_first_value(record, "レース名"),

        "JyoCD": race_parts.get("jyo_cd", ""),

        "Kaiji": race_parts.get("kaiji", ""),

        "Nichiji": race_parts.get("nichiji", ""),

        "RaceNum": race_parts.get("race_num", ""),

        "Umaban": get_first_value(record, "馬番", "枠番"),

        "MorningOdds": find_morning_odds(record),

        "Mark1": get_first_value(record, "馬印1"),

        "Mark2": get_first_value(record, "馬印2"),

        "Mark3": get_first_value(record, "馬印3"),

        "Mark4": get_first_value(record, "馬印4"),

        "Mark5": get_first_value(record, "馬印5"),

        "Mark6": get_first_value(record, "馬印6"),

        "Mark7": get_first_value(record, "馬印7"),

        "Mark8": get_first_value(record, "馬印8"),

        "ZI_INDEX": get_first_value(record, "ZI指数"),

        "ZM_VALUE": get_first_value(record, "ZM", "馬印7"),

        "ZI_RANK": get_first_value(record, "ZI指数順位", "指数順位4"),

        "SHIBA_DA": get_first_value(record, "芝ダ"),

        "KYORI_M": get_first_value(record, "距離"),

        "R_MARK1": get_first_value(record, "R印1", "レース印1"),

        "R_MARK2": get_first_value(record, "レース印2", "R印2"),

        "R_MARK3": get_first_value(record, "レース印3", "R印3"),

        "RACE_CLASS_C": get_first_value(record, "Ｃ", "C"),

        "CHAKU": get_first_value(record, "着", "着順"),

        "SEX": get_first_value(record, "性"),

        "AGE": get_first_value(record, "齢", "年齢"),

        "JOCKEY": get_first_value(record, "騎手"),

        "KINRYO": get_first_value(record, "斤量"),

        "PREV_KYAKUSHITSU": get_first_value(record, "前脚質"),

        "PREV_MARK1": get_first_value(record, "前馬印1"),

        "PREV_MARK2": get_first_value(record, "前印2"),

        "PREV_MARK3": get_first_value(record, "前印3"),

        "PREV_MARK4": get_first_value(record, "前印4"),

        "PREV_MARK5": get_first_value(record, "前印5"),

        "PREV_MARK6": get_first_value(record, "前印6"),

        "PREV_MARK7": get_first_value(record, "前印7"),

        "PREV_MARK8": get_first_value(record, "前印8"),

        "PREV_NINKI": get_first_value(record, "前人気"),

        "INDEX_RANK1": get_first_value(record, "指数順位1"),

        "ACCEL_VAL": get_first_value(record, "加速"),

        "INDEX_RANK2": get_first_value(record, "指数順位2"),

        "INDEX_DIFF2": get_first_value(record, "指差2"),

        "ORIGINAL_VAL": get_first_value(record, "オリジナル"),

        "INDEX_RANK3": get_first_value(record, "指数順位3"),

        "INDEX_RANK4": get_first_value(record, "指数順位4"),

        "PREV_CHAKU_JUNI": get_first_value(record, "前着順"),

        "PREV_CHAKU_SA": get_first_value(record, "前着差"),

        "TANSHO_ODDS": get_first_value(record, "単勝"),

        "FUKUSHO_ODDS": get_first_value(record, "複勝"),

        "INDEX_DIFF4": get_first_value(record, "指差4"),

        "INDEX_DIFF1": get_first_value(record, "指差1"),

        "PREV_TSUKA1": get_first_value(record, "前通過1"),

        "PREV_TSUKA2": get_first_value(record, "前通過2"),

        "PREV_TSUKA3": get_first_value(record, "前通過3"),

        "PREV_TSUKA4": get_first_value(record, "前通過4"),

        "PREV_3F_JUNI": get_first_value(record, "前3F順"),

        "PREV_TOSU": get_first_value(record, "前頭数"),

        "PREV_RACE_MARK": get_first_value(record, "前レース印"),

        "PREV_RACE_MARK2": get_first_value(record, "前レース印2"),

        "PREV_RACE_MARK3": get_first_value(record, "前レース印3"),

        "FATHER_TYPE_NAME": get_first_value(record, "父タイプ名"),

        "TOTAL_HORSES": get_first_value(record, "頭", "頭数"),

        "WORK1": get_first_value(record, "ワーク1"),

        "WORK2": get_first_value(record, "ワーク2"),

        "PREV_TRACK_NAME": get_first_value(record, "前場所"),

        "SAME_TRACK_FLAG": get_first_value(record, "同場"),

        "PREV_KINRYO": get_first_value(record, "前斤量"),

        "PREV_BATAIJU": get_first_value(record, "前馬体重"),

        "PREV_BATAIJU_ZOGEN": get_first_value(record, "前馬体重増減"),

        "AGE_AT_RACE": get_first_value(record, "年齢"),

        "INTERVAL": get_first_value(record, "間隔"),

        "KYUMEI_SENME": get_first_value(record, "休明戦目"),

        "KINRYO_SA": get_first_value(record, "斤量差"),

        "KYORI_SA": get_first_value(record, "距離差"),

        "PREV_SHIBA_DA": get_first_value(record, "前芝ダ", "前芝ダ.1"),

        "PREV_KYORI_M": get_first_value(record, "前距離"),

        "CAREER_TOTAL": get_first_value(record, "キャリア(当時/取消等含)"),

        "CAREER_LATEST": get_first_value(record, "キャリア(最新)"),

        "CLASS_C": get_first_value(record, "クラスC"),

        "PREV_UMABAN": get_first_value(record, "前番"),

        "CURRENT_SHIBA_DA": get_first_value(record, "今芝ダ"),

        "PREV_BABA_JOTAI": get_first_value(record, "前馬場状態"),

        "PREV_CLASS": get_first_value(record, "前ｸﾗｽ", "前クラス"),

        "DAMSIRE_TYPE_NAME": get_first_value(record, "母父タイプ名"),

        "T_MARK_DIFF": get_first_value(record, "Tﾏ差"),

        "MATCHUP_MINING_VAL": get_first_value(record, "対戦型マイニング値"),

        "MATCHUP_MINING_RANK": get_first_value(record, "対戦型マイニング順位"),

        "KOKYUSEN_FLAG": get_first_value(record, "降級戦"),

        "B_COL_FLAG": get_first_value(record, "B"),

        "SYOZOKU": get_first_value(record, "所属", "所属.1"),

        "CHECK_TRAINER_TYPE": get_first_value(record, "チェック調教師タイプ"),

        "CHECK_JOCKEY_TYPE": get_first_value(record, "チェック騎手タイプ"),

        "TRAINER_NAME": get_first_value(record, "調教師"),

        "FUKUSHO_ODDS_LOWER": get_first_value(record, "複勝オッズ下"),

        "FUKUSHO_ODDS_UPPER": get_first_value(record, "複勝オッズ上", "上"),

        "TAN_ODDS": get_first_value(record, "単オッズ", "単勝"),

        "WAKUBAN": get_first_value(record, "枠番"),

        "COURSE_GROUP_COUNT": get_first_value(record, "コースグループ数"),

        "COURSE_GROUP_NAME1": get_first_value(record, "コースグループ名1"),

        "NINKI_RANK": get_first_value(record, "人気"),

        "NORIKAE_FLAG": get_first_value(record, "乗替"),

        "PREV_RACE_ID": get_first_value(record, "前レースID(新)"),

        "SourceFile": file_path.name,

        "ImportedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

    }



    for key, value in list(data.items()):

        if value == "" or value is None:

            data[key] = None



    return data





def collect_source_dates(records: list[dict[str, str]], file_path: Path) -> set[str]:

    dates: set[str] = set()

    for record in records:

        race_id = str(record.get("レースID(新)", "") or "").strip()

        source_date = extract_source_date(file_path, race_id)

        if source_date:

            dates.add(source_date)

    return dates





def _existing_source_dates(conn: sqlite3.Connection, candidate_dates: Iterable[str]) -> set[str]:

    dates = [d for d in candidate_dates if d]

    if not dates:

        return set()

    placeholders = ','.join('?' for _ in dates)

    query = f"SELECT SourceDate FROM HORSE_MARKS WHERE SourceDate IN ({placeholders})"

    return {row[0] for row in conn.execute(query, dates)}



def import_excel(conn: sqlite3.Connection, file_path: Path, skip_existing: bool = False) -> int:

    df = read_excel(file_path)

    if df.empty:

        print(f"[skip] {file_path.name}: no rows")

        return 0



    imported = 0

    records_to_insert = []

    

    all_records_from_excel = df.to_dict(orient="records")

    source_dates = collect_source_dates(all_records_from_excel, file_path)



    if skip_existing and source_dates:

        existing = _existing_source_dates(conn, source_dates)

        if source_dates.issubset(existing):

            joined = ", ".join(sorted(source_dates))

            print(f"[skip existing] {file_path.name}: {joined}")

            return 0

    elif source_dates:

        placeholders = ",".join("?" for _ in source_dates)

        cursor = conn.execute(

            f"DELETE FROM HORSE_MARKS WHERE SourceDate IN ({placeholders})",

            list(source_dates),

        )

        if cursor.rowcount:

            joined = ", ".join(sorted(source_dates))

            print(f"[overwrite] Cleared {cursor.rowcount} rows for dates: {joined}")

    

    for record in all_records_from_excel:

        horse_name = str(record.get("馬名S", "") or "").strip()

        if not horse_name:

            continue

        

        params = collect_all_excel_data(record, file_path)

        

        if not params.get("MorningOdds") and not any(params.get(f"Mark{i}") for i in range(1,9)) and not params.get("ZI_INDEX") and not params.get("ZM_VALUE"):

            continue



        records_to_insert.append(params)



    if not records_to_insert:

        return 0



    column_names = list(records_to_insert[0].keys())

    placeholders = ", ".join(f":{name}" for name in column_names)

    update_assignments = ", ".join(f"{name}=excluded.{name}" for name in column_names if name not in ["SourceDate", "RaceId", "HorseName"])



    sql = f"""

        INSERT INTO HORSE_MARKS ({', '.join(column_names)})

        VALUES ({placeholders})

        ON CONFLICT(SourceDate, NormalizedHorseName) DO UPDATE SET

            {update_assignments}

        ;"""



    cursor = conn.cursor()

    cursor.executemany(sql, records_to_insert)

    imported = cursor.rowcount



    return imported





def main() -> int:

    parser = argparse.ArgumentParser(description="Import yDate Excel horse marks into SQLite")

    parser.add_argument("--db", default="ecore.db", help="Path to SQLite database (default: ecore.db)")

    parser.add_argument("--excel-dir", default="yDate", help="Directory that stores Excel files")

    parser.add_argument("--files", nargs="*", help="Specific Excel file names to import (within excel-dir)")

    parser.add_argument("--skip-existing", action="store_true", help="既に同じ日付のデータが登録済みならスキップする")

    parser.add_argument("--mode", choices=("full", "incremental"), help="Import mode: full reimports all files, incremental skips dates already present.")



    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")

    sys.stderr.reconfigure(encoding="utf-8")



    mode = args.mode

    skip_existing = args.skip_existing

    if mode:

        if mode == "incremental":

            skip_existing = True

        else:

            if skip_existing:

                parser.error("--skip-existing cannot be combined with --mode full")

            skip_existing = False

    else:

        mode = "incremental" if skip_existing else "full"



    db_path = Path(args.db)

    excel_dir = Path(args.excel_dir)



    if not db_path.exists():

        parser.error(f"database not found: {db_path}")

    if not excel_dir.exists():

        parser.error(f"excel directory not found: {excel_dir}")



    conn = sqlite3.connect(db_path)

    try:

        ensure_schema(conn)

        targets = iter_excel_files(excel_dir, args.files)

        if not targets:

            print("No Excel files to import.")

            return 0



        total = 0

        print(f"Import mode: {mode} (skip-existing={skip_existing})")



        for file_path in targets:

            if not file_path.exists():

                print(f"[skip] missing file: {file_path}")

                continue

            count = import_excel(conn, file_path, skip_existing=skip_existing)

            conn.commit()

            print(f"Imported {count:3d} rows from {file_path.name}")

            total += count



        print(f"Done. Total rows upserted: {total}")

        return 0

    finally:

        conn.close()





if __name__ == "__main__":

    raise SystemExit(main())

