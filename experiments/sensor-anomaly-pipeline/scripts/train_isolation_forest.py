from __future__ import annotations

import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from common.features import FEATURE_COLUMNS

CSV_PATH = ROOT_DIR / "data" / "processed" / "sensor_readings.csv"
MODEL_PATH = ROOT_DIR / "models" / "isolation_forest.joblib"


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["device_id", "measured_at"]).copy()
    df["measured_at"] = pd.to_datetime(df["measured_at"])
    df["hour"] = df["measured_at"].dt.hour
    df["temp_diff"] = df.groupby("device_id")["temperature"].diff().fillna(0)
    df["humidity_diff"] = df.groupby("device_id")["humidity"].diff().fillna(0)
    df["temp_rolling_mean"] = (
        df.groupby("device_id")["temperature"].rolling(5, min_periods=1).mean().reset_index(level=0, drop=True)
    )
    df["humidity_rolling_mean"] = (
        df.groupby("device_id")["humidity"].rolling(5, min_periods=1).mean().reset_index(level=0, drop=True)
    )
    df["temp_rolling_std"] = (
        df.groupby("device_id")["temperature"].rolling(5, min_periods=1).std().reset_index(level=0, drop=True).fillna(0)
    )
    df["humidity_rolling_std"] = (
        df.groupby("device_id")["humidity"].rolling(5, min_periods=1).std().reset_index(level=0, drop=True).fillna(0)
    )
    return df


def main() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}. Run generate_sample_data.py first.")

    df = pd.read_csv(CSV_PATH)
    df = add_features(df)

    # Remove obvious injected rule anomalies from training data.
    normal_df = df[
        (df["temperature"].between(5, 40))
        & (df["humidity"].between(20, 90))
        & (df["temp_diff"].abs() < 10)
        & (df["humidity_diff"].abs() < 20)
    ]

    model = IsolationForest(n_estimators=150, contamination=0.03, random_state=42)
    model.fit(normal_df[FEATURE_COLUMNS].to_numpy())

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"trained on {len(normal_df)} rows and wrote {MODEL_PATH}")


if __name__ == "__main__":
    main()
