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


def normalize_horse_name(value: str) -> str:
    """Remove all whitespace characters to normalise horse names."""
    return "".join(value.replace(" ", "").replace("　", ""))


def ensure_schema(conn: sqlite3.Connection) -> None:
    """Ensure the target table and index exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS HORSE_MARKS (
            SourceDate TEXT NOT NULL,
            NormalizedHorseName TEXT NOT NULL,
            HorseName TEXT,
            RaceId TEXT,
            RaceName TEXT,
            JyoCD TEXT,
            Kaiji TEXT,
            Nichiji TEXT,
            RaceNum TEXT,
            Umaban TEXT,
            MorningOdds TEXT,
            Mark1 TEXT,
            Mark2 TEXT,
            Mark3 TEXT,
            Mark4 TEXT,
            Mark5 TEXT,
            Mark6 TEXT,
            Mark7 TEXT,
            Mark8 TEXT,
            SourceFile TEXT,
            ImportedAt TEXT NOT NULL,
            PRIMARY KEY (SourceDate, NormalizedHorseName)
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS IDX_HORSE_MARKS_NAME ON HORSE_MARKS (NormalizedHorseName)"
    )


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


def collect_all_excel_data(record: dict[str, str], file_path: Path) -> dict[str, str]:
    data: dict[str, str] = {
        "SourceDate": extract_source_date(file_path, str(record.get("レースID(新)", "") or "").strip()),
        "HorseName": str(record.get("馬名S", "") or "").strip(),
        "NormalizedHorseName": normalize_horse_name(str(record.get("馬名S", "") or "").strip()),
        "RaceId": str(record.get("レースID(新)", "") or "").strip(),
        "RaceName": str(record.get("レース名", "") or "").strip(),
        "JyoCD": parse_race_id(str(record.get("レースID(新)", "") or "").strip()).get("jyo_cd", ""),
        "Kaiji": parse_race_id(str(record.get("レースID(新)", "") or "").strip()).get("kaiji", ""),
        "Nichiji": parse_race_id(str(record.get("レースID(新)", "") or "").strip()).get("nichiji", ""),
        "RaceNum": parse_race_id(str(record.get("レースID(新)", "") or "").strip()).get("race_num", ""),
        "Umaban": str(record.get("馬番", "") or "").strip() or str(record.get("枠番", "") or "").strip(),
        "MorningOdds": find_morning_odds(record),
        "Mark1": str(record.get("馬印1", "") or "").strip(),
        "Mark2": str(record.get("馬印2", "") or "").strip(),
        "Mark3": str(record.get("馬印3", "") or "").strip(),
        "Mark4": str(record.get("馬印4", "") or "").strip(),
        "Mark5": str(record.get("馬印5", "") or "").strip(),
        "Mark6": str(record.get("馬印6", "") or "").strip(),
        "Mark7": str(record.get("馬印7", "") or "").strip(),
        "Mark8": str(record.get("馬印8", "") or "").strip(),
        "SourceFile": file_path.name,
        "ImportedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ZI_INDEX": str(record.get("ZI指数", "") or "").strip(), # V列
        "ZM_VALUE": str(record.get("馬印7", "") or "").strip(),     # P列からZMを取得
        "SHIBA_DA": str(record.get("芝ダ", "") or "").strip(),
        "KYORI_M": str(record.get("距離", "") or "").strip(),
        "R_MARK1": str(record.get("R印1", "") or "").strip(),
        "R_MARK2": str(record.get("レース印2", "") or "").strip(),
        "R_MARK3": str(record.get("レース印3", "") or "").strip(),
        "RACE_CLASS_C": str(record.get("Ｃ", "") or "").strip(),
        "CHAKU": str(record.get("着", "") or "").strip(),
        "SEX": str(record.get("性", "") or "").strip(),
        "AGE": str(record.get("齢", "") or "").strip(),
        "JOCKEY": str(record.get("騎手", "") or "").strip(),
        "KINRYO": str(record.get("斤量", "") or "").strip(),
        "PREV_KYAKUSHITSU": str(record.get("前脚質", "") or "").strip(),
        "PREV_MARK1": str(record.get("前馬印1", "") or "").strip(),
        "PREV_MARK2": str(record.get("前印2", "") or "").strip(),
        "PREV_MARK3": str(record.get("前印3", "") or "").strip(),
        "PREV_MARK4": str(record.get("前印4", "") or "").strip(),
        "PREV_MARK5": str(record.get("前印5", "") or "").strip(),
        "PREV_MARK6": str(record.get("前印6", "") or "").strip(),
        "PREV_MARK7": str(record.get("前印7", "") or "").strip(),
        "PREV_MARK8": str(record.get("前印8", "") or "").strip(),
        "PREV_NINKI": str(record.get("前人気", "") or "").strip(),
        "INDEX_RANK1": str(record.get("指数順位1", "") or "").strip(),
        "ACCEL_VAL": str(record.get("加速", "") or "").strip(),
        "INDEX_RANK2": str(record.get("指数順位2", "") or "").strip(),
        "INDEX_DIFF2": str(record.get("指差2", "") or "").strip(),
        "ORIGINAL_VAL": str(record.get("オリジナル", "") or "").strip(),
        "INDEX_RANK3": str(record.get("指数順位3", "") or "").strip(),
        "INDEX_RANK4": str(record.get("指数順位4", "") or "").strip(),
        "PREV_CHAKU_JUNI": str(record.get("前着順", "") or "").strip(),
        "PREV_CHAKU_SA": str(record.get("前着差", "") or "").strip(),
        "TANSHO_ODDS": str(record.get("単勝", "") or "").strip(),
        "ZI_RANK": str(record.get("指数順位4", "") or "").strip(), # AQ ZI指数の順位
        "FUKUSHO_ODDS": str(record.get("複勝", "") or "").strip(),
        "INDEX_DIFF4": str(record.get("指差4", "") or "").strip(),
        "INDEX_DIFF1": str(record.get("指差1", "") or "").strip(),
        "PREV_TSUKA1": str(record.get("前通過1", "") or "").strip(),
        "PREV_TSUKA2": str(record.get("前通過2", "") or "").strip(),
        "PREV_TSUKA3": str(record.get("前通過3", "") or "").strip(),
        "PREV_TSUKA4": str(record.get("前通過4", "") or "").strip(),
        "PREV_3F_JUNI": str(record.get("前3F順", "") or "").strip(),
        "PREV_TOSU": str(record.get("前頭数", "") or "").strip(),
        "PREV_RACE_MARK": str(record.get("前レース印", "") or "").strip(),
        "PREV_RACE_MARK2": str(record.get("前レース印2", "") or "").strip(),
        "PREV_RACE_MARK3": str(record.get("前レース印3", "") or "").strip(),
        "FATHER_TYPE_NAME": str(record.get("父タイプ名", "") or "").strip(),
        "TOTAL_HORSES": str(record.get("頭", "") or "").strip(),
        "WORK1": str(record.get("ワーク1", "") or "").strip(),
        "WORK2": str(record.get("ワーク2", "") or "").strip(),
        "PREV_TRACK_NAME": str(record.get("前場所", "") or "").strip(),
        "SAME_TRACK_FLAG": str(record.get("同場", "") or "").strip(),
        "PREV_KINRYO": str(record.get("前斤量", "") or "").strip(),
        "PREV_BATAIJU": str(record.get("前馬体重", "") or "").strip(),
        "PREV_BATAIJU_ZOGEN": str(record.get("前馬体重増減", "") or "").strip(),
        "AGE_AT_RACE": str(record.get("年齢", "") or "").strip(),
        "INTERVAL": str(record.get("間隔", "") or "").strip(),
        "KYUMEI_SENME": str(record.get("休明戦目", "") or "").strip(),
        "KINRYO_SA": str(record.get("斤量差", "") or "").strip(),
        "KYORI_SA": str(record.get("距離差", "") or "").strip(),
        "PREV_SHIBA_DA": str(record.get("前芝ダ", "") or "").strip(),
        "PREV_KYORI_M": str(record.get("前距離", "") or "").strip(),
        "CAREER_TOTAL": str(record.get("キャリア(当時/取消等含)", "") or "").strip(),
        "CAREER_LATEST": str(record.get("キャリア(最新)", "") or "").strip(),
        "CLASS_C": str(record.get("クラスC", "") or "").strip(),
        "PREV_UMABAN": str(record.get("前番", "") or "").strip(),
        "CURRENT_SHIBA_DA": str(record.get("今芝ダ", "") or "").strip(),
        "PREV_BABA_JOTAI": str(record.get("前馬場状態", "") or "").strip(),
        "PREV_CLASS": str(record.get("前ｸﾗｽ", "") or "").strip(),
        "DAMSIRE_TYPE_NAME": str(record.get("母父タイプ名", "") or "").strip(),
        "T_MARK_DIFF": str(record.get("Tﾏ差", "") or "").strip(),
        "MATCHUP_MINING_VAL": str(record.get("対戦型マイニング値", "") or "").strip(),
        "MATCHUP_MINING_RANK": str(record.get("対戦型マイニング順位", "") or "").strip(),
        "KOKYUSEN_FLAG": str(record.get("降級戦", "") or "").strip(),
        "B_COL_FLAG": str(record.get("B", "") or "").strip(),
        "SYOZOKU": str(record.get("所属", "") or "").strip(),
        "CHECK_TRAINER_TYPE": str(record.get("チェック調教師タイプ", "") or "").strip(),
        "CHECK_JOCKEY_TYPE": str(record.get("チェック騎手タイプ", "") or "").strip(),
        "TRAINER_NAME": str(record.get("調教師", "") or "").strip(),
        "FUKUSHO_ODDS_LOWER": str(record.get("複勝オッズ下", "") or "").strip(),
        "FUKUSHO_ODDS_UPPER": str(record.get("上", "") or "").strip(),
        "TAN_ODDS": str(record.get("単オッズ", "") or "").strip(),
        "WAKUBAN": str(record.get("枠番", "") or "").strip(),
        "COURSE_GROUP_COUNT": str(record.get("コースグループ数", "") or "").strip(),
        "COURSE_GROUP_NAME1": str(record.get("コースグループ名1", "") or "").strip(),
        "NINKI_RANK": str(record.get("人気", "") or "").strip(),
        "NORIKAE_FLAG": str(record.get("乗替", "") or "").strip(),
        "PREV_RACE_ID": str(record.get("前レースID(新)", "") or "").strip(),
    }
    # 辞書内の空文字やNoneの値をNoneに変換
    for key, value in data.items():
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
