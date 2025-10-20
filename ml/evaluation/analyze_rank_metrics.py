"""Summarise hit/ROI statistics per rank grade for a date range."""
from __future__ import annotations

import sqlite3
import argparse
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from ml.evaluation.evaluate_predictions import (
    EvalConfig,
    attach_results,
    load_predictions,
)


def grade_summary(df: pd.DataFrame, cfg: EvalConfig) -> pd.DataFrame:
    grades: List[str] = sorted(df["RankGrade"].fillna("UNKNOWN").unique().tolist())
    records = []
    for grade in grades:
        grade_df = df[df["RankGrade"].fillna("UNKNOWN") == grade].copy()
        invest_df = grade_df[grade_df["InvestFlag"] >= cfg.min_invest_flag].copy()
        joined_df = invest_df.dropna(subset=["Finish"])

        total = len(grade_df)
        invest_total = len(invest_df)
        joined_total = len(joined_df)

        win_hits = (joined_df["Finish"] == 1).sum()
        place_hits = joined_df["Finish"].apply(lambda x: 1 if pd.notna(x) and x <= 3 else 0).sum()
        win_rate = float(win_hits / joined_total) if joined_total else None
        place_rate = float(place_hits / joined_total) if joined_total else None

        odds = joined_df["Odds"].fillna(0.0).clip(lower=0.0)
        stakes = cfg.stake
        returns = np.where(joined_df["Finish"] == 1, odds * stakes, 0.0)
        total_return = float(returns.sum())
        total_stake = stakes * joined_total
        win_roi = float((total_return - total_stake) / total_stake) if total_stake > 0 else None

        records.append(
            {
                "RankGrade": grade,
                "rows": total,
                "invest_rows": invest_total,
                "joined_rows": joined_total,
                "win_hits": int(win_hits),
                "win_hit_rate": win_rate,
                "place_hit_rate": place_rate,
                "win_roi": win_roi,
                "avg_win_score": float(grade_df["WinScore"].mean()) if not grade_df.empty else None,
                "median_win_score": float(grade_df["WinScore"].median()) if not grade_df.empty else None,
                "avg_m5": float(grade_df["M5Value"].mean()) if "M5Value" in grade_df else None,
                "median_m5": float(grade_df["M5Value"].median()) if "M5Value" in grade_df else None,
                "avg_trainer_win": float(grade_df["TrainerScore"].mean())
                if "TrainerScore" in grade_df
                else None,
            }
        )

    summary_df = pd.DataFrame(records)
    summary_df.sort_values(by="RankGrade", inplace=True)
    return summary_df


def format_percentage(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value*100:.1f}%"


def format_ratio(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.2f}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyse prediction performance per rank grade.")
    parser.add_argument("--date-from", type=str, required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--date-to", type=str, required=True, help="End date YYYY-MM-DD")
    parser.add_argument("--scenario", type=str, default="PRE")
    parser.add_argument("--pred-db", type=Path, default=Path("envs/cursor/my_keiba/predictions.db"))
    parser.add_argument("--ecore", type=Path, default=Path("envs/cursor/my_keiba/ecore.db"))
    parser.add_argument("--stake", type=float, default=100.0)
    parser.add_argument("--output-csv", type=Path, help="Optional path to export the summary CSV.")
    args = parser.parse_args()

    cfg = EvalConfig(
        predictions_db=args.pred_db,
        ecore_db=args.ecore,
        scenario=args.scenario.upper(),
        date_from=args.date_from,
        date_to=args.date_to,
        stake=args.stake,
    )

    with sqlite3.connect(cfg.predictions_db) as conn:  # type: ignore[name-defined]
        preds = load_predictions(conn, cfg)
    preds_with_results = attach_results(preds, cfg)
    if preds_with_results.empty:
        print("[WARN] No prediction rows found for the specified range.")
        return

    summary_df = grade_summary(preds_with_results, cfg)
    display_df = summary_df.copy()
    display_df["win_hit_rate"] = display_df["win_hit_rate"].apply(format_percentage)
    display_df["place_hit_rate"] = display_df["place_hit_rate"].apply(format_percentage)
    display_df["win_roi"] = display_df["win_roi"].apply(format_ratio)

    print("=== Rank Grade Summary ===")
    print(display_df.to_string(index=False))

    if args.output_csv:
        args.output_csv.parent.mkdir(parents=True, exist_ok=True)
        summary_df.to_csv(args.output_csv, index=False, encoding="utf-8")
        print(f"[OK] summary written -> {args.output_csv}")


if __name__ == "__main__":
    main()
