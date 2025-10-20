"""Generate predictions for a specific race day and store them in predictions.db."""
from __future__ import annotations

import argparse
import json
import operator
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import joblib
import pandas as pd

from ml.features.build_features import FeatureConfig, build_feature_frame


CONDITION_DISPATCH: Dict[str, Tuple[str, Any]] = {
    "min_win_score": ("WinScore", operator.ge),
    "max_win_score": ("WinScore", operator.le),
    "min_m5": ("M5Value", operator.ge),
    "max_m5": ("M5Value", operator.le),
    "min_zm": ("ZM_VALUE", operator.ge),
    "max_zm": ("ZM_VALUE", operator.le),
    "min_zi": ("ZI_INDEX", operator.ge),
    "max_zi": ("ZI_INDEX", operator.le),
    "min_trainer_win": ("TrainerWinRate", operator.ge),
    "max_trainer_win": ("TrainerWinRate", operator.le),
    "min_odds": ("PreTanOdds", operator.ge),
    "max_odds": ("PreTanOdds", operator.le),
}

GRADE_ORDER: Tuple[str, ...] = ("S", "A", "B", "C", "D", "E")

DEFAULT_RANK_CONFIG: Dict[str, Any] = {
    "fallback_grade": "E",
    "default_invest_grades": ["S", "A"],
    "scenarios": {
        "PRE": {
            "invest_grades": ["S", "A"],
            "rules": [
                {
                    "grade": "S",
                    "conditions": {
                        "min_win_score": 0.75,
                        "max_m5": 1.5,
                        "min_zm": 60,
                        "min_zi": 55,
                        "min_trainer_win": 0.12,
                    },
                },
                {
                    "grade": "A",
                    "conditions": {
                        "min_win_score": 0.62,
                        "max_m5": 2.0,
                        "min_zm": 55,
                        "min_zi": 50,
                    },
                },
                {
                    "grade": "B",
                    "conditions": {
                        "min_win_score": 0.52,
                        "min_zm": 48,
                    },
                },
                {
                    "grade": "C",
                    "conditions": {
                        "min_win_score": 0.45,
                    },
                },
                {
                    "grade": "D",
                    "conditions": {
                        "min_win_score": 0.35,
                    },
                },
            ],
        },
        "LIVE": {
            "invest_grades": ["S", "A"],
            "rules": [
                {
                    "grade": "S",
                    "conditions": {
                        "min_win_score": 0.78,
                        "max_m5": 1.6,
                        "min_zm": 60,
                        "max_odds": 6.0,
                    },
                },
                {
                    "grade": "A",
                    "conditions": {
                        "min_win_score": 0.65,
                        "max_m5": 2.2,
                        "min_zm": 55,
                        "max_odds": 12.0,
                    },
                },
                {
                    "grade": "B",
                    "conditions": {
                        "min_win_score": 0.55,
                        "min_zm": 50,
                    },
                },
                {
                    "grade": "C",
                    "conditions": {
                        "min_win_score": 0.45,
                    },
                },
                {
                    "grade": "D",
                    "conditions": {
                        "min_win_score": 0.35,
                    },
                },
            ],
        },
    },
}


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = json.loads(json.dumps(base))

    def _merge(dst: Dict[str, Any], src: Dict[str, Any]) -> None:
        for key, value in src.items():
            if isinstance(value, dict) and isinstance(dst.get(key), dict):
                _merge(dst[key], value)
            else:
                dst[key] = value

    _merge(result, override)
    return result


@dataclass
class RankRule:
    grade: str
    conditions: Dict[str, float]

    def matches(self, row: pd.Series) -> bool:
        for key, threshold in self.conditions.items():
            column, comparator = CONDITION_DISPATCH.get(key, (None, None))
            if not column:
                return False
            value = row.get(column, pd.NA)
            if pd.isna(value):
                return False
            try:
                numeric_value = float(value)
            except (TypeError, ValueError):
                return False
            if not comparator(numeric_value, float(threshold)):
                return False
        return True


def load_rank_config(scenario: str, explicit_path: Optional[Path]) -> Tuple[List[RankRule], Set[str], str, str]:
    scenario_key = scenario.upper()
    search_paths: List[Path] = []
    if explicit_path:
        search_paths.append(explicit_path)
    search_paths.extend(
        [
            Path("ml/config/rank_rules.json"),
            Path("config/rank_rules.json"),
        ]
    )

    merged_config = DEFAULT_RANK_CONFIG
    source = "built-in defaults"
    for candidate in search_paths:
        if not candidate.exists():
            continue
        try:
            user_config = json.loads(candidate.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"[WARN] Failed to parse rank rule config at {candidate}: {exc}. Continuing with defaults.")
            continue
        merged_config = _deep_merge(DEFAULT_RANK_CONFIG, user_config)
        source = str(candidate)
        break

    scenario_map = merged_config.get("scenarios", {})
    scenario_data = scenario_map.get(scenario_key) or scenario_map.get("DEFAULT", {})

    default_invest = {grade.upper() for grade in merged_config.get("default_invest_grades", ["S", "A"])}
    invest_grades = {grade.upper() for grade in scenario_data.get("invest_grades", list(default_invest))}
    fallback_grade = scenario_data.get("fallback_grade", merged_config.get("fallback_grade", "E")).upper()

    rules: List[RankRule] = []
    for entry in scenario_data.get("rules", []):
        grade = str(entry.get("grade", fallback_grade)).upper()
        conditions_raw = entry.get("conditions", {})
        conditions: Dict[str, float] = {}
        for key, threshold in conditions_raw.items():
            if key not in CONDITION_DISPATCH:
                raise ValueError(f"Unknown rank condition '{key}' for scenario '{scenario_key}'.")
            conditions[key] = float(threshold)
        rules.append(RankRule(grade=grade, conditions=conditions))

    return rules, invest_grades, fallback_grade, source


def assign_rank_grade(row: pd.Series, cfg: "PredictionConfig") -> str:
    for rule in cfg.rank_rules:
        if rule.matches(row):
            return rule.grade
    return cfg.fallback_grade


def format_grade_distribution(grades: Iterable[str], invest_grades: Set[str]) -> str:
    counts: Dict[str, int] = {}
    for grade in grades:
        counts[grade] = counts.get(grade, 0) + 1
    summary_parts: List[str] = []
    for grade in GRADE_ORDER:
        if grade in counts:
            mark = "*" if grade in invest_grades else ""
            summary_parts.append(f"{grade}:{counts[grade]}{mark}")
    for grade, count in sorted(counts.items()):
        if grade in GRADE_ORDER:
            continue
        mark = "*" if grade in invest_grades else ""
        summary_parts.append(f"{grade}:{count}{mark}")
    return ", ".join(summary_parts)


@dataclass
class PredictionConfig:
    ecore_db: Path
    excel_db: Optional[Path]
    predictions_db: Path
    model_dir: Path
    model_version: Optional[str]
    scenario: str
    target_date: str  # YYYY-MM-DD
    rank_rules: List[RankRule]
    invest_grades: Set[str]
    fallback_grade: str
    rank_config_source: str


def load_model_artifacts(config: PredictionConfig) -> Tuple[object, object, dict]:
    artifacts = sorted(config.model_dir.glob("win-*.json"))
    if not artifacts:
        raise FileNotFoundError(f"No model metadata found in {config.model_dir}")

    if config.model_version:
        metadata_path = config.model_dir / f"{config.model_version}.json"
        if not metadata_path.exists():
            raise FileNotFoundError(f"Specified model version metadata not found: {metadata_path}")
    else:
        metadata_path = artifacts[-1]

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    version = metadata["version"]
    model = joblib.load(config.model_dir / f"{version}.joblib")
    scaler = joblib.load(config.model_dir / f"{version}_scaler.joblib")
    metadata["version"] = version
    return model, scaler, metadata


def upsert_predictions(df: pd.DataFrame, metadata: dict, cfg: PredictionConfig) -> None:
    cfg.predictions_db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(cfg.predictions_db)
    try:
        rows = []
        for _, row in df.iterrows():
            rows.append(
                (
                    row["Year"],
                    row["MonthDay"],
                    row["JyoCD"],
                    row["RaceNum"],
                    row["Umaban"],
                    cfg.scenario,
                    float(row["WinScore"]) if not pd.isna(row["WinScore"]) else None,
                    None,
                    float(row["PreTanOdds"]) if not pd.isna(row["PreTanOdds"]) else None,
                    int(row["InvestFlag"]),
                    str(row["RankGrade"]) if not pd.isna(row["RankGrade"]) else None,
                    float(row["M5Value"]) if not pd.isna(row["M5Value"]) else None,
                    float(row["TrainerWinRate"]) if not pd.isna(row["TrainerWinRate"]) else None,
                    metadata["version"],
                )
            )

        with conn:
            conn.executemany(
                """
                INSERT INTO Predictions
                (Year, MonthDay, JyoCD, RaceNum, Umaban, Scenario,
                 WinScore, PlaceScore, Odds, InvestFlag, RankGrade, M5Value, TrainerScore, ModelVersion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(Year, MonthDay, JyoCD, RaceNum, Umaban, Scenario, ModelVersion)
                DO UPDATE SET
                    WinScore=excluded.WinScore,
                    PlaceScore=excluded.PlaceScore,
                    Odds=excluded.Odds,
                    InvestFlag=excluded.InvestFlag,
                    RankGrade=excluded.RankGrade,
                    M5Value=excluded.M5Value,
                    TrainerScore=excluded.TrainerScore,
                    UpdatedAt=datetime('now')
                """,
                rows,
            )
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict race outcomes and populate predictions.db.")
    parser.add_argument("--date", required=True, help="Target date (YYYY-MM-DD)")
    parser.add_argument("--ecore", type=Path, default=Path("envs/cursor/my_keiba/ecore.db"))
    parser.add_argument("--excel", type=Path, default=Path("envs/cursor/my_keiba/excel_data.db"))
    parser.add_argument("--pred-db", type=Path, default=Path("envs/cursor/my_keiba/predictions.db"))
    parser.add_argument("--model-dir", type=Path, default=Path("ml/model_artifacts"))
    parser.add_argument("--model-version", type=str)
    parser.add_argument("--scenario", type=str, default="PRE")
    parser.add_argument(
        "--rank-rules",
        type=Path,
        help="Optional path to rank rule configuration JSON (defaults to ml/config/rank_rules.json).",
    )
    args = parser.parse_args()

    scenario = args.scenario.upper()
    rank_rules, invest_grades, fallback_grade, rank_source = load_rank_config(scenario, args.rank_rules)

    cfg = PredictionConfig(
        ecore_db=args.ecore,
        excel_db=args.excel,
        predictions_db=args.pred_db,
        model_dir=args.model_dir,
        model_version=args.model_version,
        scenario=scenario,
        target_date=args.date,
        rank_rules=rank_rules,
        invest_grades=invest_grades,
        fallback_grade=fallback_grade,
        rank_config_source=rank_source,
    )

    model, scaler, metadata = load_model_artifacts(cfg)

    feature_cfg = FeatureConfig(
        ecore_db=cfg.ecore_db,
        excel_db=cfg.excel_db if cfg.excel_db.exists() else None,
        output_path=None,
        target_date=cfg.target_date,
    )
    features = build_feature_frame(feature_cfg)
    if features.empty:
        print("[WARN] No entries found for the target date.")
        return

    selected_cols = metadata.get("features", [])
    missing_cols = [c for c in selected_cols if c not in features.columns]
    if missing_cols:
        raise ValueError(f"Missing columns in feature set: {missing_cols}")

    X = features[selected_cols].astype(float).fillna(0.0).to_numpy()
    X_scaled = scaler.transform(X)
    win_scores = model.predict_proba(X_scaled)[:, 1]
    features["WinScore"] = win_scores
    features["RankGrade"] = features.apply(lambda row: assign_rank_grade(row, cfg), axis=1)
    features["InvestFlag"] = features["RankGrade"].isin(cfg.invest_grades).astype(int)

    total_entries = len(features)
    invest_total = int(features["InvestFlag"].sum())
    grade_summary = format_grade_distribution(features["RankGrade"], cfg.invest_grades)
    print(f"[INFO] rank config source: {cfg.rank_config_source}")
    print(f"[INFO] grade distribution: {grade_summary}")
    print(
        f"[INFO] invest selections (grades {', '.join(sorted(cfg.invest_grades))}): "
        f"{invest_total}/{total_entries}"
    )

    upsert_predictions(features, metadata, cfg)
    print(f"[OK] predictions stored for {cfg.target_date} ({cfg.scenario}) using model {metadata['version']}")


if __name__ == "__main__":
    main()
