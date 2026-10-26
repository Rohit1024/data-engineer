"""Airflow 2.11: map over small, immutable fixture files at runtime."""
from datetime import timedelta
import json
import logging

import pendulum
from airflow.decorators import dag, task
from airflow.exceptions import AirflowFailException
from airflow.providers.google.cloud.hooks.gcs import GCSHook

BUCKET = "YOUR_INPUT_BUCKET"


@dag(
    dag_id="lab_mapped_file_checks",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 1, "retry_delay": timedelta(seconds=30)},
    tags=["lesson-0039", "mapping"],
)
def mapped_file_checks():
    @task
    def discover():
        names = GCSHook(gcp_conn_id="google_cloud_default").list(
            bucket_name=BUCKET, prefix="mapped/"
        )
        files = sorted(name for name in names if name.endswith(".ndjson"))
        if not files:
            raise AirflowFailException("No input files; check the fixture prefix")
        if len(files) > 20:
            raise AirflowFailException("This lab is limited to 20 small files")
        return files

    @task(max_active_tis_per_dag=2)
    def check_file(object_name):
        payload = GCSHook(gcp_conn_id="google_cloud_default").download(
            bucket_name=BUCKET, object_name=object_name
        )
        rows = [json.loads(line) for line in payload.decode("utf-8").splitlines() if line.strip()]
        if not rows:
            raise AirflowFailException(f"Empty file: {object_name}")
        for row in rows:
            if row["amount_cents"] < 0:
                raise AirflowFailException(f"Negative amount in {object_name}")
        return {"object": object_name, "rows": len(rows)}

    @task
    def report(results):
        summaries = list(results)
        logging.info("Validated %s files, %s rows", len(summaries), sum(x["rows"] for x in summaries))

    report(check_file.expand(object_name=discover()))


mapped_file_checks()
