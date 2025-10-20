# ML Pipeline Overview

This directory hosts the data science workflow that complements JVMonitor.

Structure (planned):

- `ml/db/` — scripts for creating and maintaining auxiliary SQLite databases such as `predictions.db`.
- `ml/features/` — feature extraction utilities that pull data from `ecore.db`.
- `ml/models/` — training and inference code (scikit-learn / LightGBM, etc.).
- `ml/model_artifacts/` — trained model binaries, scalers, metadata (ignored from Git).
- `ml/logs/` — runtime logs for training and prediction (ignored from Git).

Initial goals:

1. Define and create the `predictions.db` schema.
2. Extract features (M5 指標, 調教師成績, オッズなど) from `ecore.db`.
3. Train baseline models (ロジスティック回帰) and store artifacts.
4. Run `predict_today.py` to populate `Predictions` table for前日/当日シナリオ.
5. Surface predictions in JVMonitor UI via LEFT JOIN.

This file will evolve as the pipeline is implemented.
