---
icon: lucide/shield-check
---

# Designing resilient DAGs: Google Cloud operators and deferrable execution

Building production data pipelines in Apache Airflow requires writing resilient DAGs that handle transient network drops, avoid blocking worker slots during long-running cloud jobs, and eliminate top-level code execution anti-patterns.

---

## Deferrable operators and the Triggerer process

Standard Airflow operators consume a continuous Celery worker slot while waiting for a remote BigQuery or Dataflow job to finish. **Deferrable operators** release the worker slot immediately after submitting the job, handing off monitoring to the lightweight Airflow Triggerer process.

``` mermaid
flowchart TD
    subgraph StandardOperator["Standard Blocking Operator"]
        Worker1["Celery Worker Pod (1 Slot)"] --> Submit1["Submit BigQuery Job"]
        Submit1 --> Block["Blocked in time.sleep() (Consumes 100% of 1 Worker Slot for 45 mins)"]
        Block --> Done1["Job Finished"]
    end

    subgraph DeferrableOperator["Deferrable Operator (deferrable=True)"]
        Worker2["Celery Worker Pod"] --> Submit2["Submit BigQuery Job"]
        Submit2 --> Yield["Yield TriggerEvent & Release Worker Slot"]
        Yield --> Triggerer["Airflow Triggerer (Monitors 1,000+ jobs on 1 async thread)"]
        Triggerer -->|"Job Finished Event"| Resume["Resume Worker (Post-processing)"]
    end

    StandardOperator ~~~ DeferrableOperator
```

---

## Eliminating top-level code anti-patterns

The Airflow Scheduler parses every Python file in the `dags/` folder every 30 seconds:
- **Anti-pattern**: Running SQL queries, `Variable.get()`, or `gcloud` requests at the root level of a Python file. This forces the scheduler to make dozens of network calls every 30 seconds, causing scheduler heartbeats to freeze.
- **Best practice**: Keep the global scope strictly declarative. Wrap all API connections and data access inside operator `execute()` methods or Python callables.

---

## Complete resilient Airflow DAG implementation

Save as `dags/ecommerce_daily_mart.py`:

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryInsertJobOperator,
    BigQueryCheckOperator
)
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator
from airflow.operators.empty import EmptyOperator

default_args = {
    "owner": "data-platform",
    "depends_on_past": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=15)
}

with DAG(
    dag_id="ecommerce_daily_mart_pipeline",
    default_args=default_args,
    description="Daily resilient ELT pipeline with deferrable operators",
    schedule_interval="0 3 * * *", # 03:00 UTC daily
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["production", "ecommerce", "bigquery"]
) as dag:

    start = EmptyOperator(task_id="start")

    # 1. Transform Bronze to Silver using Deferrable BigQuery job
    run_silver_transformation = BigQueryInsertJobOperator(
        task_id="run_silver_transformation",
        configuration={
            "query": {
                "query": """
                  MERGE `my-proj.silver.orders` T
                  USING (
                    SELECT * FROM `my-proj.bronze.orders_raw`
                    WHERE DATE(event_timestamp) = '{{ ds }}'
                  ) S
                  ON T.order_id = S.order_id
                  WHEN MATCHED THEN UPDATE SET
                    T.amount = S.amount,
                    T.status = S.status,
                    T.updated_at = CURRENT_TIMESTAMP()
                  WHEN NOT MATCHED THEN INSERT ROW;
                """,
                "useLegacySql": False
            }
        },
        deferrable=True # Releases Celery worker slot while query executes
    )

    # 2. Data quality check
    verify_record_count = BigQueryCheckOperator(
        task_id="verify_record_count",
        sql="""
          SELECT COUNT(1) > 0
          FROM `my-proj.silver.orders`
          WHERE DATE(updated_at) = '{{ ds }}'
        """,
        use_legacy_sql=False
    )

    end = EmptyOperator(task_id="end")

    start >> run_silver_transformation >> verify_record_count >> end
```

---

## Summary heuristics

1. Set `deferrable=True` on all Google Cloud operators (`BigQueryInsertJobOperator`, `DataprocSubmitJobOperator`, `DataflowCreateJavaJobOperator`) to avoid worker slot starvation.
2. Configure `retries=3` with `retry_exponential_backoff=True` on every production DAG to automatically absorb intermittent network blips.
3. Keep DAG files free of top-level network I/O and dynamic variable lookups to protect scheduler stability.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0028: Cloud Composer Architecture](0028-cloud-composer-architecture-gke.md) | [All Lessons (Index)](index.md) | [0030: Dynamic Task Mapping & XComs](0030-dynamic-task-mapping-airflow-best-practices.md) |
