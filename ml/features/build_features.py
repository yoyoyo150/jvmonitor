"""Feature extraction for the racing prediction pipeline.

This module pulls data from `ecore.db` (公式データ) と `excel_data.db`
(馬印/M5情報) を突合し、学習・推論で使用する特徴量セットを生成する。

主な特徴量:
- レース基本情報: コース、距離、馬場、発走時刻など
- オッズ情報: `N_ODDS_TANPUKU` の単勝オッズ/人気
- 馬印情報: HORSE_MARKS から M5/M6、ZI、ZM 等を抽出
- 調教師成績: 登録数、勝率、連対率、平均着順
- ラベル: `WinLabel` (1着) と `PlaceLabel` (1〜3着)
"""
from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


@dataclass
class FeatureConfig:
    ecore_db: Path
    excel_db: Optional[Path] = None
    output_path: Optional[Path] = None
    target_date: Optional[str] = None  # YYYY-MM-DD


def normalize_horse_name(series: pd.Series) -> pd.Series:
    """Remove whitespace characters from horse names."""
    return series.fillna("").astype(str).str.replace(r"\s+", "", regex=True)


def load_base_frame(conn: sqlite3.Connection, config: FeatureConfig) -> pd.DataFrame:
    """Pull core race-entry rows from N_UMA_RACE + N_RACE."""
    query = """
        SELECT
            U.Year,
            U.MonthDay,
            U.JyoCD,
            U.RaceNum,
            U.Umaban,
            U.KettoNum,
            U.Bamei,
            U.ChokyosiCode,
            U.ChokyosiRyakusyo,
            U.KisyuCode,
            U.KisyuRyakusyo,
            U.SexCD,
            U.Barei,
            U.KakuteiJyuni,
            U.TimeDiff,
            U.HaronTimeL3,
            R.TrackCD,
            R.Kyori,
            R.Hondai AS RaceName,
            R.HassoTime
        FROM N_UMA_RACE U
        JOIN N_RACE R
          ON U.Year = R.Year
         AND U.MonthDay = R.MonthDay
         AND U.JyoCD = R.JyoCD
         AND U.RaceNum = R.RaceNum
        WHERE 1 = 1
    """
    params: tuple = ()
    if config.target_date:
        year, month, day = config.target_date.split("-")
        mmdd = f"{month}{day}"
        query += " AND U.Year = ? AND U.MonthDay = ?"
        params = (year, mmdd)

    df = pd.read_sql_query(query, conn, params=params)
    if df.empty:
        return df

    df["Umaban"] = df["Umaban"].astype(str).str.lstrip("0")
    df["RaceKey"] = (
        df["Year"].astype(str)
        + df["MonthDay"].astype(str).str.zfill(4)
        + df["JyoCD"].astype(str).str.zfill(2)
        + df["RaceNum"].astype(str).str.zfill(2)
    )
    df["RaceDate"] = pd.to_datetime(
        df["Year"].astype(str) + df["MonthDay"].astype(str).str.zfill(4),
        format="%Y%m%d",
        errors="coerce",
    )
    df["NormalizedHorseName"] = normalize_horse_name(df["Bamei"])

    # ラベル: 1着 -> WinLabel, 1〜3着 -> PlaceLabel
    def _safe_int(x: str) -> Optional[int]:
        return int(x) if x and x.isdigit() else None

    numeric_finish = df["KakuteiJyuni"].apply(_safe_int)
    df["WinLabel"] = (numeric_finish == 1).astype(int)
    df["PlaceLabel"] = numeric_finish.apply(lambda x: 1 if x and x <= 3 else 0)
    return df


def load_odds_frame(conn: sqlite3.Connection, config: FeatureConfig) -> pd.DataFrame:
    """Load単勝オッズ情報."""
    query = """
        SELECT Year, MonthDay, JyoCD, RaceNum, Umaban, TanOdds, TanNinki
        FROM N_ODDS_TANPUKU
    """
    params: tuple = ()
    if config.target_date:
        year, month, day = config.target_date.split("-")
        mmdd = f"{month}{day}"
        query += " WHERE Year = ? AND MonthDay = ?"
        params = (year, mmdd)
    odds = pd.read_sql_query(query, conn, params=params)
    if odds.empty:
        return odds
    odds["Umaban"] = odds["Umaban"].astype(str).str.lstrip("0")
    odds["TanOdds"] = pd.to_numeric(odds["TanOdds"], errors="coerce").div(10.0)
    odds["TanNinki"] = pd.to_numeric(odds["TanNinki"], errors="coerce")
    odds.rename(
        columns={"TanOdds": "PreTanOdds", "TanNinki": "PreTanPopularity"},
        inplace=True,
    )
    return odds


def load_trainer_stats(conn: sqlite3.Connection) -> pd.DataFrame:
    """Aggregate trainer performance statistics from historical data."""
    query = """
        SELECT
            ChokyosiCode,
            COUNT(*) AS TrainerStarts,
            SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS TrainerWins,
            SUM(CASE WHEN KakuteiJyuni IN ('01','02','03') THEN 1 ELSE 0 END) AS TrainerTop3,
            AVG(
                CASE
                    WHEN KakuteiJyuni GLOB '[0-9][0-9]' THEN CAST(KakuteiJyuni AS INTEGER)
                    ELSE NULL
                END
            ) AS TrainerAvgFinish
        FROM N_UMA_RACE
        WHERE IFNULL(ChokyosiCode,'') <> ''
        GROUP BY ChokyosiCode
    """
    stats = pd.read_sql_query(query, conn)
    if stats.empty:
        return stats
    stats["TrainerWinRate"] = stats["TrainerWins"] / stats["TrainerStarts"].replace(0, np.nan)
    stats["TrainerTop3Rate"] = stats["TrainerTop3"] / stats["TrainerStarts"].replace(0, np.nan)
    return stats


def attach_marks(df: pd.DataFrame, config: FeatureConfig) -> pd.DataFrame:
    """Attach horse mark (M5/M6) information from excel_data.db."""
    if config.excel_db is None or not config.excel_db.exists() or df.empty:
        df["M5Value"] = pd.NA
        df["M6Value"] = pd.NA
        df["ZI_INDEX"] = pd.NA
        df["ZM_VALUE"] = pd.NA
        df["MarkSourceDate"] = pd.NaT
        df["MarkTrainerName"] = pd.NA
        return df

    with sqlite3.connect(config.excel_db) as excel_conn:
        marks = pd.read_sql_query(
            """
            SELECT
                NormalizedHorseName,
                Umaban,
                SourceDate,
                Mark5,
                Mark6,
                ZI_INDEX,
                ZM_VALUE,
                TRAINER_NAME
            FROM HORSE_MARKS
            """,
            excel_conn,
        )

    if marks.empty:
        df["M5Value"] = pd.NA
        df["M6Value"] = pd.NA
        df["ZI_INDEX"] = pd.NA
        df["ZM_VALUE"] = pd.NA
        df["MarkSourceDate"] = pd.NaT
        df["MarkTrainerName"] = pd.NA
        return df

    marks["NormalizedHorseName"] = normalize_horse_name(marks["NormalizedHorseName"])
    marks["Umaban"] = marks["Umaban"].astype(str).str.lstrip("0")
    marks["SourceDate_dt"] = pd.to_datetime(marks["SourceDate"], format="%Y%m%d", errors="coerce")
    marks["Mark5"] = pd.to_numeric(marks["Mark5"], errors="coerce")
    marks["Mark6"] = pd.to_numeric(marks["Mark6"], errors="coerce")

    enriched = df.copy()
    enriched["Umaban"] = enriched["Umaban"].astype(str).str.lstrip("0")
    enriched["RowId"] = np.arange(len(enriched))

    merged = enriched.merge(
        marks,
        how="left",
        on=["NormalizedHorseName", "Umaban"],
        suffixes=("", "_mark"),
    )

    merged["DaysDiff"] = (merged["RaceDate"] - merged["SourceDate_dt"]).dt.days
    valid_mask = merged["DaysDiff"].between(0, 2)
    merged.loc[~valid_mask, ["Mark5", "Mark6", "ZI_INDEX", "ZM_VALUE", "TRAINER_NAME", "SourceDate_dt"]] = np.nan

    merged.sort_values(["RowId", "SourceDate_dt"], ascending=[True, False], inplace=True)
    merged = merged.drop_duplicates(subset=["RowId"], keep="first")

    merged.rename(columns={"Mark5": "M5Value", "Mark6": "M6Value", "TRAINER_NAME": "MarkTrainerName"}, inplace=True)
    merged["MarkSourceDate"] = merged["SourceDate_dt"]
    merged.drop(columns=["SourceDate_dt", "DaysDiff", "RowId"], inplace=True)
    return merged


def enrich_features(df: pd.DataFrame, config: FeatureConfig) -> pd.DataFrame:
    """Compose all feature blocks."""
    if df.empty:
        return df

    with sqlite3.connect(config.ecore_db) as conn:
        odds = load_odds_frame(conn, config)
        trainer_stats = load_trainer_stats(conn)

    enriched = df.copy()
    if not odds.empty:
        enriched = enriched.merge(
            odds,
            how="left",
            on=["Year", "MonthDay", "JyoCD", "RaceNum", "Umaban"],
        )
    else:
        enriched["PreTanOdds"] = np.nan
        enriched["PreTanPopularity"] = np.nan

    if not trainer_stats.empty:
        enriched = enriched.merge(trainer_stats, how="left", on="ChokyosiCode")
    else:
        enriched["TrainerStarts"] = np.nan
        enriched["TrainerWins"] = np.nan
        enriched["TrainerTop3"] = np.nan
        enriched["TrainerAvgFinish"] = np.nan
        enriched["TrainerWinRate"] = np.nan
        enriched["TrainerTop3Rate"] = np.nan

    enriched = attach_marks(enriched, config)

    # 付加的な派生特徴
    enriched["IsTurf"] = enriched["TrackCD"].astype(str).str.startswith("1").astype(int)
    enriched["RaceDistance"] = pd.to_numeric(enriched["Kyori"], errors="coerce")
    enriched["PreTanOdds"] = pd.to_numeric(enriched["PreTanOdds"], errors="coerce")
    enriched["PreTanPopularity"] = pd.to_numeric(enriched["PreTanPopularity"], errors="coerce")

    return enriched


def build_feature_frame(config: FeatureConfig) -> pd.DataFrame:
    """Convenience helper to build the feature DataFrame."""
    with sqlite3.connect(config.ecore_db) as conn:
        base = load_base_frame(conn, config)
    features = enrich_features(base, config)
    return features


def save_output(df: pd.DataFrame, config: FeatureConfig) -> None:
    if config.output_path is None:
        print(df.head())
        print(f"[INFO] rows: {len(df)} (no output file specified)")
        return
    config.output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(config.output_path, index=False)
    print(f"[OK] features saved -> {config.output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build feature set for racing predictions.")
    parser.add_argument(
        "--ecore",
        type=Path,
        default=Path("envs/cursor/my_keiba/ecore.db"),
        help="Path to ecore.db (default: envs/cursor/my_keiba/ecore.db)",
    )
    parser.add_argument(
        "--excel",
        type=Path,
        default=Path("envs/cursor/my_keiba/excel_data.db"),
        help="Path to excel_data.db (default: envs/cursor/my_keiba/excel_data.db)",
    )
    parser.add_argument("--output", type=Path, help="Where to write features (parquet).")
    parser.add_argument("--date", type=str, help="Target date (YYYY-MM-DD). If omitted, pull all races.")
    args = parser.parse_args()

    config = FeatureConfig(
        ecore_db=args.ecore,
        excel_db=args.excel,
        output_path=args.output,
        target_date=args.date,
    )
    features = build_feature_frame(config)
    save_output(features, config)


if __name__ == "__main__":
    main()
