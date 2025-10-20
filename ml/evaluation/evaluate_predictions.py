"""Evaluate stored predictions against actual race results.

The script reads rows from predictions.db (Predictions table), joins them with
official results in ecore.db (N_UMA_RACE), and computes hit rates / ROI.

Example:
    python -m ml.evaluation.evaluate_predictions \
        --date-from 2025-10-12 --date-to 2025-10-13 --scenario PRE
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Sequence

import pandas as pd
import numpy as np


@dataclass
class EvalConfig:
    predictions_db: Path
    ecore_db: Path
    scenario: str
    date_from: Optional[str]
    date_to: Optional[str]
    min_invest_flag: int = 1
    stake: float = 100.0  # 円
    output_json: Optional[Path] = None


def load_predictions(conn: sqlite3.Connection, cfg: EvalConfig) -> pd.DataFrame:
    query = """
        SELECT
            Year,
            MonthDay,
            JyoCD,
            RaceNum,
            Umaban,
            Scenario,
            WinScore,
            Odds,
            InvestFlag,
            RankGrade,
            ModelVersion
        FROM Predictions
        WHERE Scenario = ?
    """
    params: list = [cfg.scenario]
    if cfg.date_from and cfg.date_to:
        y_from, m_from, d_from = cfg.date_from.split("-")
        y_to, m_to, d_to = cfg.date_to.split("-")
        mmdd_from = f"{m_from}{d_from}"
        mmdd_to = f"{m_to}{d_to}"
        query += " AND (Year || MonthDay) BETWEEN ? AND ?"
        params.extend([f"{y_from}{mmdd_from}", f"{y_to}{mmdd_to}"])
    elif cfg.date_from:
        y, m, d = cfg.date_from.split("-")
        mmdd = f"{m}{d}"
        query += " AND Year = ? AND MonthDay = ?"
        params.extend([y, mmdd])

    try:
        df = pd.read_sql_query(query, conn, params=params)
    except sqlite3.OperationalError as exc:
        if "no such column: RankGrade" not in str(exc):
            raise
        fallback_query = query.replace(",\n            RankGrade", "")
        df = pd.read_sql_query(fallback_query, conn, params=params)
        df["RankGrade"] = pd.NA
    if df.empty:
        return df
    df["RaceDate"] = pd.to_datetime(df["Year"] + df["MonthDay"], format="%Y%m%d")
    df["Umaban"] = df["Umaban"].astype(str).str.lstrip("0")
    df["Odds"] = pd.to_numeric(df["Odds"], errors="coerce")
    return df


def attach_results(predictions: pd.DataFrame, cfg: EvalConfig) -> pd.DataFrame:
    if predictions.empty:
        return predictions

    query = """
        SELECT
            Year,
            MonthDay,
            JyoCD,
            RaceNum,
            Umaban,
            KakuteiJyuni
        FROM N_UMA_RACE
        WHERE Year IN ({years})
          AND MonthDay IN ({mdays})
    """
    years = sorted(predictions["Year"].unique())
    monthdays = sorted(predictions["MonthDay"].unique())
    placeholders_years = ",".join("?" for _ in years)
    placeholders_md = ",".join("?" for _ in monthdays)
    query = query.format(years=placeholders_years or "''", mdays=placeholders_md or "''")
    params: Sequence[str] = [*years, *monthdays]

    with sqlite3.connect(cfg.ecore_db) as conn:
        results = pd.read_sql_query(query, conn, params=params)

    if results.empty:
        predictions["Finish"] = pd.NA
        return predictions

    results["Umaban"] = results["Umaban"].astype(str).str.lstrip("0")

    merged = predictions.merge(
        results,
        how="left",
        on=["Year", "MonthDay", "JyoCD", "RaceNum", "Umaban"],
    )
    merged["Finish"] = merged["KakuteiJyuni"].apply(
        lambda x: int(x) if isinstance(x, str) and x.isdigit() else pd.NA
    )
    merged.drop(columns=["KakuteiJyuni"], inplace=True)
    return merged


def compute_metrics(df: pd.DataFrame, cfg: EvalConfig) -> dict:
    if df.empty:
        return {
            "total_predictions": 0,
            "invest_selections": 0,
            "joined_results": 0,
            "win_hits": 0,
            "win_hit_rate": None,
            "win_roi": None,
            "place_hits": 0,
            "place_hit_rate": None,
            "invest_grade_counts": {},
        }

    invest_df = df[df["InvestFlag"] >= cfg.min_invest_flag].copy()
    joined_df = invest_df.dropna(subset=["Finish"])

    summary = {
        "total_predictions": int(len(df)),
        "invest_selections": int(len(invest_df)),
        "joined_results": int(len(joined_df)),
    }
    if "RankGrade" in invest_df.columns:
        grade_series = invest_df["RankGrade"].fillna("UNKNOWN")
        summary["invest_grade_counts"] = {
            str(grade): int(count) for grade, count in grade_series.value_counts().sort_index().items()
        }
    else:
        summary["invest_grade_counts"] = {}

    if joined_df.empty:
        summary.update(
            {
                "win_hits": 0,
                "win_hit_rate": None,
                "win_roi": None,
                "place_hits": 0,
                "place_hit_rate": None,
            }
        )
        return summary

    win_hits = (joined_df["Finish"] == 1).sum()
    place_hits = joined_df["Finish"].apply(lambda x: 1 if pd.notna(x) and x <= 3 else 0).sum()
    total_bets = len(joined_df)

    summary["win_hits"] = int(win_hits)
    summary["place_hits"] = int(place_hits)
    summary["win_hit_rate"] = float(win_hits / total_bets)
    summary["place_hit_rate"] = float(place_hits / total_bets)

    odds = joined_df["Odds"].fillna(0.0).clip(lower=0.0)
    stakes = cfg.stake
    returns = np.where(joined_df["Finish"] == 1, odds * stakes, 0.0)
    total_return = float(returns.sum())
    total_stake = stakes * total_bets
    summary["win_roi"] = float((total_return - total_stake) / total_stake) if total_stake > 0 else None

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate prediction performance.")
    parser.add_argument("--pred-db", type=Path, default=Path("envs/cursor/my_keiba/predictions.db"))
    parser.add_argument("--ecore", type=Path, default=Path("envs/cursor/my_keiba/ecore.db"))
    parser.add_argument("--scenario", type=str, default="PRE", help="Scenario identifier (e.g., PRE, LIVE)")
    parser.add_argument("--date-from", type=str, help="Start date YYYY-MM-DD")
    parser.add_argument("--date-to", type=str, help="End date YYYY-MM-DD")
    parser.add_argument("--stake", type=float, default=100.0, help="Stake per wager (for ROI calculation)")
    parser.add_argument("--output-json", type=Path, help="Optional path to write metrics as JSON")
    args = parser.parse_args()

    cfg = EvalConfig(
        predictions_db=args.pred_db,
        ecore_db=args.ecore,
        scenario=args.scenario.upper(),
        date_from=args.date_from,
        date_to=args.date_to,
        stake=args.stake,
        output_json=args.output_json,
    )

    with sqlite3.connect(cfg.predictions_db) as conn:
        preds = load_predictions(conn, cfg)

    preds_with_results = attach_results(preds, cfg)
    metrics = compute_metrics(preds_with_results, cfg)

    print("=== Prediction Evaluation ===")
    print(f"Scenario       : {cfg.scenario}")
    if cfg.date_from and cfg.date_to:
        print(f"Date Range     : {cfg.date_from} -> {cfg.date_to}")
    elif cfg.date_from:
        print(f"Date           : {cfg.date_from}")
    else:
        print("Date Range     : (all available)")
    print(f"Total predictions : {metrics['total_predictions']}")
    print(f"Selections (InvestFlag>=1): {metrics['invest_selections']}")
    grade_counts = metrics.get("invest_grade_counts", {})
    if grade_counts:
        grade_summary = ", ".join(f"{grade}:{count}" for grade, count in grade_counts.items())
        print(f"Invest grade breakdown : {grade_summary}")
    print(f"Joined results  : {metrics['joined_results']}")
    print(f"Win hits        : {metrics.get('win_hits', 0)}")
    print(f"Win hit rate    : {metrics.get('win_hit_rate')}")
    print(f"Win ROI         : {metrics.get('win_roi')}")
    print(f"Place hits      : {metrics.get('place_hits', 0)}")
    print(f"Place hit rate  : {metrics.get('place_hit_rate')}")

    if cfg.output_json:
        cfg.output_json.parent.mkdir(parents=True, exist_ok=True)
        cfg.output_json.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        print(f"[OK] metrics written -> {cfg.output_json}")


if __name__ == "__main__":
    main()
