"""Airflow 2.11: immutable daily file -> staging -> validated partition."""
from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor

PROJECT = "YOUR_PROJECT_ID"
BUCKET = "YOUR_INPUT_BUCKET"
REGION = "us-central1"
DATASET = "airflow_lab"
DAY = "{{ data_interval_start | ds }}"
DAY_ID = "{{ data_interval_start | ds_nodash }}"
RAW_TABLE = f"orders_raw_{DAY_ID}"

SCHEMA = [
    {"name": "order_id", "type": "INTEGER", "mode": "REQUIRED"},
    {"name": "amount_cents", "type": "INTEGER", "mode": "REQUIRED"},
    {"name": "status", "type": "STRING", "mode": "REQUIRED"},
]

with DAG(
    dag_id="lab_daily_orders",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    dagrun_timeout=timedelta(hours=2),
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
        "retry_exponential_backoff": True,
        "execution_timeout": timedelta(minutes=45),
    },
    tags=["lesson-0039", "bigquery"],
) as daily_orders:
    wait_for_file = GCSObjectExistenceSensor(
        task_id="wait_for_file",
        bucket=BUCKET,
        object=f"daily/{DAY}/orders.ndjson",
        google_cloud_conn_id="google_cloud_default",
        mode="reschedule",
        deferrable=False,
        poke_interval=60,
        timeout=1800,
    )

    load_raw = BigQueryInsertJobOperator(
        task_id="load_raw",
        project_id=PROJECT,
        location=REGION,
        gcp_conn_id="google_cloud_default",
        deferrable=True,
        force_rerun=True,
        configuration={
            "load": {
                "sourceUris": [f"gs://{BUCKET}/daily/{DAY}/orders.ndjson"],
                "destinationTable": {
                    "projectId": PROJECT,
                    "datasetId": DATASET,
                    "tableId": RAW_TABLE,
                },
                "sourceFormat": "NEWLINE_DELIMITED_JSON",
                "schema": {"fields": SCHEMA},
                "writeDisposition": "WRITE_TRUNCATE",
                "createDisposition": "CREATE_IF_NEEDED",
                "maxBadRecords": 0,
            }
        },
    )

    validate = BigQueryInsertJobOperator(
        task_id="validate",
        project_id=PROJECT,
        location=REGION,
        deferrable=True,
        configuration={
            "query": {
                "useLegacySql": False,
                "query": f"""
                ASSERT (SELECT COUNT(*) > 0 FROM `{PROJECT}.{DATASET}.{RAW_TABLE}`)
                  AS 'Empty daily file';
                ASSERT (
                  SELECT COUNT(*) = COUNT(DISTINCT order_id)
                  FROM `{PROJECT}.{DATASET}.{RAW_TABLE}`
                ) AS 'Duplicate order IDs';
                ASSERT (
                  SELECT COUNT(*) = 0 FROM `{PROJECT}.{DATASET}.{RAW_TABLE}`
                  WHERE amount_cents < 0 OR status NOT IN ('paid', 'cancelled')
                ) AS 'Invalid order values';
                """,
            }
        },
    )

    publish = BigQueryInsertJobOperator(
        task_id="publish",
        project_id=PROJECT,
        location=REGION,
        deferrable=True,
        force_rerun=True,
        configuration={
            "query": {
                "useLegacySql": False,
                "query": f"""
                CREATE TABLE IF NOT EXISTS `{PROJECT}.{DATASET}.daily_sales` (
                  business_date DATE, paid_orders INT64, paid_amount NUMERIC
                ) PARTITION BY business_date;
                BEGIN TRANSACTION;
                DELETE FROM `{PROJECT}.{DATASET}.daily_sales`
                  WHERE business_date = DATE('{DAY}');
                INSERT INTO `{PROJECT}.{DATASET}.daily_sales`
                SELECT DATE('{DAY}'), COUNT(*),
                       COALESCE(SUM(CAST(amount_cents AS NUMERIC)), 0) / 100
                FROM `{PROJECT}.{DATASET}.{RAW_TABLE}`
                WHERE status = 'paid';
                COMMIT TRANSACTION;
                """,
            }
        },
    )

    wait_for_file >> load_raw >> validate >> publish
