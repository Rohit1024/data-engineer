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
- **Size policy**: Keep payloads small and enforce a project-specific budget. Limits depend on the Airflow version, backend and serialization; 48 KB is not a universal modern limit.

### GCS XCom backend for large payloads
For exchanging large datasets or complex data structures, configure a custom GCS XCom backend in `airflow.cfg`:

```ini
[core]
xcom_backend = airflow.providers.common.io.xcom.backend.XComObjectStorageBackend

[common.io]
xcom_objectstorage_path = gs://google_cloud_default@my-composer-xcom-bucket/xcom
xcom_objectstorage_threshold = 1048576
```

Airflow automatically serializes outputs to GCS objects and passes URI pointers between tasks.

---

## Summary heuristics

1. Use `.expand()` instead of generating static task loops in global DAG scope, allowing the DAG to handle variable workloads dynamically.
2. Set `max_active_tis_per_dag` on dynamically mapped tasks to prevent downstream databases from being overwhelmed by hundreds of concurrent tasks.
3. Never pass raw data payloads or DataFrames through default database XComs; pass GCS URIs or table IDs instead.

---

## Mapping controls orchestration size as well as service load

`.expand()` creates task instances for runtime inputs; it does not distribute a Python loop inside one task across a data-processing engine. One million files mapped individually can overwhelm scheduler/metadata capacity before workers do useful work. Group files into bounded manifests or partitions and map those batches. Check the installed Airflow mapping limit and use pools plus task/DAG concurrency controls.

`expand(a=[1, 2], b=[3, 4])` maps a Cartesian product, which can create four combinations. Use the supported zip mechanism when the intent is paired inputs. `.partial()` binds constant operator arguments while `.expand()` supplies mapped ones. An empty mapped input can skip tasks; define whether empty input is expected, an error or a reason to preserve previous output.

The example's `record_count=1500` is a fabricated demonstration value, not validation evidence. For a real check, have each task inspect its small fixture or submit an external validation job and return observed counts. [Lesson 0039's mapped DAG](0039-managed-airflow-environments-dags.md#7-dag-3-map-checks-over-a-runtime-file-list) supplies actual parsing, failure behavior and expected totals.

The object-storage backend above requires compatible `common-io`/Google filesystem dependencies and configured credentials; verify it against the managed image before changing environment configuration. It stores large serialized values outside the metadata database, but is not a reason to route bulk analytical data through XCom. Pass a URI/table identifier and a checksum/boundary instead. See the [official backend configuration](https://airflow.apache.org/docs/apache-airflow-providers-common-io/stable/xcom_backend.html).

## Exercise with expected results

Map checks over two three-row fixtures and expect six observed rows. Add a third fixture and expect three mapped instances and nine rows. Then supply an empty list and inspect actual downstream state. Explain how `max_active_tis_per_dag=2` affects scheduling without changing total task count. Finally fail one mapped check and prove the final report cannot falsely publish success.

Source: [Airflow 2.11 dynamic mapping](https://airflow.apache.org/docs/apache-airflow/2.11.0/authoring-and-scheduling/dynamic-task-mapping.html).

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0029: Resilient DAGs & Deferrable Operators](0029-resilient-dags-deferrable-operators.md) | [All Lessons (Index)](index.md) | [0031: Workflows vs Cloud Composer](0031-cloud-workflows-vs-composer.md) |
