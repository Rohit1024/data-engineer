---
icon: lucide/git-branch
---

# Dynamic task mapping, XComs, and Airflow best practices

Dynamic Task Mapping (introduced in Airflow 2.3) allows pipelines to generate tasks at runtime based on upstream data results. Combined with the TaskFlow API (`@task`), it simplifies fan-out/fan-in architectures without requiring manual DAG re-parsing or hardcoded task lists.

---

## Dynamic task mapping architecture

``` mermaid
flowchart TD
    UpstreamTask["1. Discover Shards Task (Queries GCS / Database)"] -->|"Returns list of 50 partition paths"| DynamicFanOut

    subgraph DynamicFanOut["Dynamic Task Mapping (expand)"]
        T1["Process Shard [0]"]
        T2["Process Shard [1]"]
        T3["Process Shard [N...]"]
    end

    DynamicFanOut --> DownstreamReduce["3. Aggregate Summaries Task (Fan-in)"]
```

Using `.expand()` generates individual task instances dynamically at runtime, tracking progress, logs, and retries independently for each element.

---

## TaskFlow API and Dynamic Mapping implementation

```python
from datetime import datetime
from airflow.decorators import dag, task
from airflow.providers.google.cloud.hooks.gcs import GCSHook

@dag(
    dag_id="dynamic_gcs_partition_processor",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["taskflow", "dynamic-mapping"]
)
def dynamic_pipeline():

    @task
    def list_inbound_files(bucket_name: str, prefix: str) -> list[str]:
        hook = GCSHook()
        files = hook.list(bucket_name=bucket_name, prefix=prefix)
        return [f for f in files if f.endswith(".parquet")]

    @task(max_active_tis_per_dag=10) # Control concurrency limit across mapped tasks
    def process_single_file(file_path: str) -> dict:
        print(f"Processing inbound partition: {file_path}")
        # Execute validation or lightweight transform
        return {"file": file_path, "status": "VALIDATED", "record_count": 1500}

    @task
    def summarize_results(results: list[dict]) -> None:
        total_records = sum(r["record_count"] for r in results)
        print(f"Successfully processed {len(results)} files containing {total_records} records.")

    # 1. Discover file list dynamically
    files_to_process = list_inbound_files(
        bucket_name="my-inbound-data-bucket",
        prefix="daily_drop/2026-08-20/"
    )

    # 2. Fan-out dynamic workers over the discovered file array
    processed_files = process_single_file.expand(file_path=files_to_process)

    # 3. Fan-in reduction
    summarize_results(processed_files)

dynamic_pipeline()
```

---

## XCom mechanics and custom GCS backends

XCom (cross-communication) allows tasks to exchange small amounts of state (metadata, file paths, record counts).
- **Default behavior**: XCom payloads are serialized as JSON and stored in the Airflow Cloud SQL metadata database. Storing DataFrames or large dictionaries bloats the database and degrades scheduler performance.
- **Size threshold**: Keep database XCom payloads under **48 KB**.

### GCS XCom backend for large payloads
For exchanging large datasets or complex data structures, configure a custom GCS XCom backend in `airflow.cfg`:

```ini
[core]
xcom_backend = airflow.providers.google.cloud.xcom_backends.gcs.GCSXComBackend
xcom_gcs_bucket_name = my-composer-xcom-bucket
```

Airflow automatically serializes outputs to GCS objects and passes URI pointers between tasks.

---

## Summary heuristics

1. Use `.expand()` instead of generating static task loops in global DAG scope, allowing the DAG to handle variable workloads dynamically.
2. Set `max_active_tis_per_dag` on dynamically mapped tasks to prevent downstream databases from being overwhelmed by hundreds of concurrent tasks.
3. Never pass raw data payloads or DataFrames through default database XComs; pass GCS URIs or table IDs instead.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0029: Resilient DAGs & Deferrable Operators](0029-resilient-dags-deferrable-operators.md) | [All Lessons (Index)](index.md) | [0031: Workflows vs Cloud Composer](0031-cloud-workflows-vs-composer.md) |
