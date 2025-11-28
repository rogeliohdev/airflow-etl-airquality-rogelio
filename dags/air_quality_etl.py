from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import logging
import requests
import pandas as pd
from pathlib import Path

# ==== Paths (data folder inside the repo) ====
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_PATH = DATA_DIR / "air_quality_raw.csv"
CLEAN_PATH = DATA_DIR / "air_quality_clean.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============ EXTRACT ============
def extract_air_quality(**context):
    """
    Extract: download air quality data from OpenAQ API
    and save raw CSV into data/air_quality_raw.csv
    """
    try:
        url = "https://api.openaq.org/v2/measurements?country=MX&limit=1000&page=1"
        logging.info(f"Requesting data from {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()["results"]
        df = pd.json_normalize(data)
        df.to_csv(RAW_PATH, index=False)

        logging.info(f"EXTRACT: downloaded {len(df)} rows to {RAW_PATH}")

    except Exception as e:
        logging.error(f"[ERROR] Extract step failed: {e}")
        # This makes Airflow mark the task as failed and apply retries
        raise


# ============ TRANSFORM ============
def transform_data(**context):
    """
    Transform: cleaning + aggregation.
    - Removes duplicates and null values
    - Filters high-volume raw data to a subset of pollutants (scaling improvement)
    - Aggregates mean value by city and parameter
    - Saves cleaned data to data/air_quality_clean.csv
    """
    try:
        chunks = []
        # Chunk processing (scaling consideration)
        for chunk in pd.read_csv(RAW_PATH, chunksize=500):
            # Cleaning
            chunk = chunk.drop_duplicates()
            chunk = chunk.dropna(subset=["value"])

            if "date.utc" in chunk.columns:
                chunk["date.utc"] = pd.to_datetime(chunk["date.utc"])

            # Filter to main pollutants (scaling improvement)
            if "parameter" in chunk.columns:
                allowed = ["pm25", "pm10", "no2", "o3", "co"]
                chunk = chunk[chunk["parameter"].isin(allowed)]

            chunks.append(chunk)

        if not chunks:
            raise ValueError("No data left after cleaning.")

        df = pd.concat(chunks, ignore_index=True)

        # Aggregation: average value by city and pollutant
        group_cols = []
        if "city" in df.columns:
            group_cols.append("city")
        if "parameter" in df.columns:
            group_cols.append("parameter")

        agg_df = df.groupby(group_cols, as_index=False)["value"].mean()
        agg_df.rename(columns={"value": "avg_value"}, inplace=True)

        agg_df.to_csv(CLEAN_PATH, index=False)
        logging.info(
            f"TRANSFORM: cleaned dataset saved to {CLEAN_PATH} with {len(agg_df)} rows"
        )

    except Exception as e:
        logging.error(f"[ERROR] Transform step failed: {e}")
        raise


# ============ LOAD ============
def load_data(**context):
    """
    Load: simple validation that cleaned data exists and is readable.
    This represents loading into a storage layer (here: local folder).
    """
    try:
        if not CLEAN_PATH.exists():
            raise FileNotFoundError(f"{CLEAN_PATH} not found")

        df = pd.read_csv(CLEAN_PATH)
        logging.info("LOAD: file exists and is readable.")
        logging.info("Sample of cleaned data:\n%s", df.head().to_string())

    except Exception as e:
        logging.error(f"[ERROR] Load step failed: {e}")
        raise


# ============ DAG DEFINITION ============
default_args = {
    "owner": "rogelio",
    "retries": 2,  # Error handling: Airflow retry settings
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="air_quality_etl",
    default_args=default_args,
    description="ETL pipeline for air quality data using OpenAQ (MX)",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",  # Scheduling requirement
    catchup=False,
) as dag:

    extract_task = PythonOperator(
        task_id="extract_task",
        python_callable=extract_air_quality,
    )

    transform_task = PythonOperator(
        task_id="transform_task",
        python_callable=transform_data,
    )

    load_task = PythonOperator(
        task_id="load_task",
        python_callable=load_data,
    )

    # DAG order: Extract -> Transform -> Load
    extract_task >> transform_task >> load_task
