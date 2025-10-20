"""Utility to create or upgrade the predictions.db schema.

Usage:
    python -m ml.db.create_predictions_db --db ../predictions.db
"""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from textwrap import dedent

SCHEMA_SQL = dedent(
    """
    PRAGMA journal_mode=WAL;
    PRAGMA foreign_keys=ON;

    CREATE TABLE IF NOT EXISTS Predictions (
        Id            INTEGER PRIMARY KEY AUTOINCREMENT,
        Year          TEXT    NOT NULL,
        MonthDay      TEXT    NOT NULL,
        JyoCD         TEXT    NOT NULL,
        RaceNum       TEXT    NOT NULL,
        Umaban        TEXT    NOT NULL,
        Scenario      TEXT    NOT NULL, -- PRE, LIVE, BACKTEST, etc.
        WinScore      REAL,
        PlaceScore    REAL,
        Odds          REAL,
        InvestFlag    INTEGER DEFAULT 0, -- 1=投資対象, 0=除外
        RankGrade     TEXT    DEFAULT 'E',
        M5Value       REAL,
        TrainerScore  REAL,
        FeaturesHash  TEXT,
        ModelVersion  TEXT    NOT NULL,
        CreatedAt     TEXT    NOT NULL DEFAULT (datetime('now')),
        UpdatedAt     TEXT    NOT NULL DEFAULT (datetime('now'))
    );

    CREATE UNIQUE INDEX IF NOT EXISTS idx_predictions_unique
        ON Predictions (Year, MonthDay, JyoCD, RaceNum, Umaban, Scenario, ModelVersion);

    CREATE INDEX IF NOT EXISTS idx_predictions_race
        ON Predictions (Year, MonthDay, JyoCD, RaceNum, Scenario);
    """
).strip()


def initialize_database(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        with conn:
            conn.executescript(SCHEMA_SQL)
            existing_cols = {
                row[1] for row in conn.execute("PRAGMA table_info(Predictions)").fetchall()
            }
            if "RankGrade" not in existing_cols:
                conn.execute("ALTER TABLE Predictions ADD COLUMN RankGrade TEXT DEFAULT 'E'")
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or update predictions.db schema.")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("predictions.db"),
        help="Path to the predictions database file (default: ./predictions.db)",
    )
    args = parser.parse_args()
    db_path: Path = args.db
    db_path.parent.mkdir(parents=True, exist_ok=True)
    initialize_database(db_path)
    print(f"[OK] predictions schema initialized at {db_path.resolve()}")


if __name__ == "__main__":
    main()
