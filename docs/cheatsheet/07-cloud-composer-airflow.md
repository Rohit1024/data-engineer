---
icon: lucide/network
---

# Cloud Composer and Apache Airflow cheatsheet

Quick reference for Cloud Composer 2 provisioning, DAG deployment, Google Cloud operators, and deferrable execution syntax.

---

## Composer 2 environment architecture

``` mermaid
flowchart TD
    GCS["GCS DAG Bucket (gs://.../dags/)"] -->|"gcsfuse 30s Sync"| GKE["GKE Autopilot Environment"]
    GKE --> Scheduler["Airflow Scheduler"]
    Scheduler --> Triggerer["Airflow Triggerer (Async Deferrable Loop)"]
    Scheduler --> CeleryQueue["Redis Broker"]
    CeleryQueue --> Workers["Celery Worker Pods (Autoscaling)"]
    Workers --> BQJob["Submit Remote BigQuery / Dataflow Jobs"]
```

---

## Cloud Composer CLI operations

```bash
# Provision Composer 2 environment with autoscaling
gcloud composer environments create prod-composer \
    --location=us-central1 \
    --image-version=composer-2.8.5-airflow-2.7.3 \
    --environment-size=medium \
    --scheduler-count=2 \
    --triggerer-count=2 \
    --min-workers=2 \
    --max-workers=8

# Retrieve environment GCS DAG bucket prefix
DAG_BUCKET=$(gcloud composer environments describe prod-composer \
    --location=us-central1 \
    --format="value(config.nodeConfig.dagGcsPrefix)")

# Deploy DAGs folder to Composer
gcloud storage rsync ./dags ${DAG_BUCKET} --delete-unmatched-destination-objects

# Install PyPI dependencies
gcloud composer environments update prod-composer \
    --location=us-central1 \
    --update-pypi-packages-from-file=requirements.txt
```

---

## Resilient DAG template with deferrable operators

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.operators.empty import EmptyOperator

default_args = {
    "owner": "data-platform",
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True
}

with DAG(
    dag_id="resilient_bigquery_pipeline",
    default_args=default_args,
    schedule_interval="0 4 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["production", "bigquery"]
) as dag:

    start = EmptyOperator(task_id="start")

    run_query = BigQueryInsertJobOperator(
        task_id="run_query",
        configuration={
            "query": {
                "query": "CALL `my_project.analytics.sp_refresh_marts`();",
                "useLegacySql": False
            }
        },
        deferrable=True # Releases worker slot while query executes
    )

    end = EmptyOperator(task_id="end")

    start >> run_query >> end
```

---

## Dynamic Task Mapping (AIP-42) syntax

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(dag_id="dynamic_fan_out_pipeline", start_date=datetime(2026, 1, 1), schedule=None)
def dynamic_dag():

    @task
    def get_shards() -> list[str]:
        return ["shard_01", "shard_02", "shard_03", "shard_04"]

    @task(max_active_tis_per_dag=2) # Concurrency cap
    def process_shard(shard_id: str) -> str:
        return f"Processed {shard_id}"

    shards = get_shards()
    process_shard.expand(shard_id=shards)

dynamic_dag()
```

---

| Previous Cheatsheet | All Cheatsheets | Next Cheatsheet |
| :--- | :---: | ---: |
| [06: Dataform & dbt](06-dataform-dbt.md) | [Cheatsheets Index](index.md) | [08: Dataplex, Security & FinOps](08-dataplex-security-finops.md) |
