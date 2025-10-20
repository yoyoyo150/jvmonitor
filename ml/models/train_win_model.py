"""Baseline training script for win probability models.

Currently a scaffold:
1. Loads feature parquet from `ml/features`.
2. Splits into train/validation.
3. Fits a logistic regression (placeholder).
4. Writes model + metadata into `ml/model_artifacts/`.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def main() -> None:
    parser = argparse.ArgumentParser(description="Train baseline win probability model.")
    parser.add_argument("--features", type=Path, required=True, help="Parquet file with engineered features.")
    parser.add_argument("--output-dir", type=Path, default=Path("ml/model_artifacts"),
                        help="Directory to store model artifacts.")
    parser.add_argument("--model-version", type=str, default=None,
                        help="Manual model version tag; defaults to timestamp.")
    args = parser.parse_args()

    df = pd.read_parquet(args.features)
    if "WinLabel" not in df.columns:
        raise ValueError("Feature set must include 'WinLabel' column (1=win,0=lose).")

    default_features = [
        "PreTanOdds",
        "PreTanPopularity",
        "TrainerStarts",
        "TrainerWins",
        "TrainerTop3",
        "TrainerAvgFinish",
        "TrainerWinRate",
        "TrainerTop3Rate",
        "M5Value",
        "M6Value",
        "IsTurf",
        "RaceDistance",
    ]
    feature_columns = [c for c in default_features if c in df.columns]
    if not feature_columns:
        raise ValueError("No usable numeric features found in the feature set.")

    numeric_df = df[feature_columns].copy()
    numeric_df = numeric_df.astype(float).fillna(0.0)

    X = numeric_df.to_numpy(dtype=float)
    y = df["WinLabel"].astype(int).to_numpy(dtype=int)

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)

    model = LogisticRegression(max_iter=1000, n_jobs=-1)
    model.fit(X_train_scaled, y_train)
    val_pred = model.predict_proba(X_val_scaled)[:, 1]
    val_logloss = log_loss(y_val, val_pred)

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    version = args.model_version or datetime.utcnow().strftime("win-%Y%m%d%H%M%S")

    joblib.dump(model, output_dir / f"{version}.joblib")
    joblib.dump(scaler, output_dir / f"{version}_scaler.joblib")
    metadata = {
        "version": version,
        "trained_at": datetime.utcnow().isoformat(),
        "features": feature_columns,
        "logloss": float(val_logloss),
        "n_samples": len(df),
    }
    (output_dir / f"{version}.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"[OK] model stored at {output_dir}, version={version}, val_logloss={val_logloss:.4f}")


if __name__ == "__main__":
    main()
