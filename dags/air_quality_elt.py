from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import requests
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
ANALYTICS_DIR = BASE_DIR / "data" / "analytics"

RAW_DIR.mkdir(parents=True, exist_ok=True)
ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)

def extract_raw():
    """Extracts raw JSON data from OpenAQ API with NO modifications."""
    try:
        url = "https://api.openaq.org/v2/measurements?country=MX&limit=1000&page=1"
        response = requests.get(url, timeout=30)
        raw_data = response.json()["results"]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        raw_path = RAW_DIR / f"air_quality_raw_{timestamp}.csv"

        df = pd.json_normalize(raw_data)
        df.to_csv(raw_path, index=False)

        logging.info(f"[ELT] RAW saved: {raw_path}")
    except Exception as e:
        logging.error(f"[ERROR] Extract failed: {e}")
        raise

def transform_analytics():
    """Transforms raw data INTO analytics layer without touching raw."""
    try:
        # Read most recent raw file
        raw_files = sorted(RAW_DIR.glob("air_quality_raw_*.csv"))
        if not raw_files:
            raise FileNotFoundError("No raw files found")

        df = pd.read_csv(raw_files[-1])

        # REQUIRED TRANSFORMATIONS
        df.dropna(subset=["value"], inplace=True)

        # Fix types
        if "value" in df.columns:
            df["value"] = df["value"].astype(float)

        # Feature creation
        if "date.utc" in df.columns:
            df["date.utc"] = pd.to_datetime(df["date.utc"])
            df["hour"] = df["date.utc"].dt.hour

        # Aggregation for dashboard
        analytics = df.groupby(["parameter"], as_index=False)["value"].mean()
        analytics.rename(columns={"value": "avg_value"}, inplace=True)

        # Save analytics layer
        analytics_path = ANALYTICS_DIR / "air_quality_analytics.csv"
        analytics.to_csv(analytics_path, index=False)

        logging.info(f"[ELT] ANALYTICS saved: {analytics_path}")

    except Exception as e:
        logging.error(f"[ERROR] Transform failed: {e}")
        raise


default_args = {
    "owner": "rogelio",
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="air_quality_elt",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    description="Full ELT pipeline using OpenAQ data"
) as dag:

    extract_task = PythonOperator(
        task_id="extract_raw_task",
        python_callable=extract_raw
    )

    transform_task = PythonOperator(
        task_id="transform_analytics_task",
        python_callable=transform_analytics
    )

    # ELT ORDER
    extract_task >> transform_task
