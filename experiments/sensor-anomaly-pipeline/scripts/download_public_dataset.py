from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DATASET_URL = "https://archive.ics.uci.edu/static/public/357/occupancy+detection.zip"
RAW_DIR = ROOT_DIR / "data" / "raw" / "uci_occupancy_detection"
OUTPUT_PATH = ROOT_DIR / "data" / "processed" / "sensor_readings.csv"


def download_zip() -> ZipFile:
    print(f"downloading {DATASET_URL}")
    with urlopen(DATASET_URL, timeout=60) as response:
        return ZipFile(BytesIO(response.read()))


def load_dataset(zip_file: ZipFile, files: list[str]) -> pd.DataFrame:
    frames = []
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for file_name in files:
        raw_bytes = zip_file.read(file_name)
        (RAW_DIR / file_name).write_bytes(raw_bytes)
        # The UCI files contain an unnamed row id before the date column.
        frame = pd.read_csv(BytesIO(raw_bytes), index_col=0)
        frame["source_file"] = file_name
        frames.append(frame)

    return pd.concat(frames, ignore_index=True)


def to_sensor_readings(df: pd.DataFrame, limit: int | None) -> pd.DataFrame:
    df = df.rename(
        columns={
            "date": "measured_at",
            "Temperature": "temperature",
            "Humidity": "humidity",
        }
    )
    df["measured_at"] = pd.to_datetime(df["measured_at"], errors="coerce")
    df = df.dropna(subset=["measured_at", "temperature", "humidity"])
    df = df.sort_values("measured_at")

    processed = pd.DataFrame(
        {
            "device_id": "office-occupancy-sensor-001",
            "temperature": df["temperature"].astype(float).round(3),
            "humidity": df["humidity"].astype(float).round(3),
            # The source data has no battery value. Keep a stable synthetic battery field
            # so the rest of the pipeline can use one common message schema.
            "battery": 100.0,
            "measured_at": df["measured_at"].dt.strftime("%Y-%m-%dT%H:%M:%S"),
        }
    )

    if limit is not None:
        processed = processed.head(limit)
    return processed


def inject_demo_faults(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if len(df) < 180:
        return df

    df.loc[df.index[80:83], "temperature"] = 44.0
    df.loc[df.index[140:143], "humidity"] = 12.0
    df.loc[df.index[170:175], ["temperature", "humidity"]] = [22.2, 31.1]
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and prepare UCI Occupancy Detection sensor data.")
    parser.add_argument(
        "--files",
        nargs="+",
        default=["datatraining.txt", "datatest.txt", "datatest2.txt"],
        help="UCI files to merge.",
    )
    parser.add_argument("--limit", type=int, default=5000, help="Maximum processed rows to keep.")
    parser.add_argument(
        "--inject-demo-faults",
        action="store_true",
        help="Add a few obvious faults so rule-based detection produces demo events.",
    )
    args = parser.parse_args()

    zip_file = download_zip()
    raw_df = load_dataset(zip_file, args.files)
    processed = to_sensor_readings(raw_df, args.limit)
    if args.inject_demo_faults:
        processed = inject_demo_faults(processed)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(OUTPUT_PATH, index=False)
    print(f"wrote {len(processed)} rows to {OUTPUT_PATH}")
    print(f"raw files saved under {RAW_DIR}")


if __name__ == "__main__":
    main()
