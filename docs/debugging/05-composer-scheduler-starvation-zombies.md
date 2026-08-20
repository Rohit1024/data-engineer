---
icon: lucide/bug
---

# Debugging Cloud Composer scheduler starvation, zombie tasks, and DAG deadlocks

Diagnostic playbook for troubleshooting Cloud Composer (Apache Airflow 2.x) scheduler heartbeats, tasks stuck in `QUEUED` state, `Detected zombie job` errors, and slow DAG parsing.

---

## Failure sequence diagram

``` mermaid
sequenceDiagram
    autonumber
    participant Scheduler as Airflow Scheduler
    participant DB as Cloud SQL (Metadata DB)
    participant Worker as Celery Worker Pod
    actor User as DAG Developer

    User->>Scheduler: Add DAG with top-level SQL query: 'SELECT * FROM huge_table'
    loop Every 30s DAG Parsing Sweep
        Scheduler->>DB: Parse DAG & Execute top-level query over network
        Note over Scheduler: Query takes 25 seconds! Scheduler loop blocked
    end
    Note over Scheduler: Misses heartbeat deadline (scheduler_heartbeat_sec: 5s)
    Worker->>DB: Task finishes execution
    Scheduler->>DB: Run zombie detection sweep
    Scheduler->>DB: Mark task as FAILED: "Detected zombie job (worker stopped responding)"
    Note over DB: Downstream tasks blocked in upstream_failed state
```

---

## Symptoms and diagnostic signals

| Symptom | Log error / Diagnostic indicator | Root cause |
| :--- | :--- | :--- |
| **Zombie task errors** | `Detected zombie job: TaskInstance ... was marked as running but not found in Celery` | Worker pod was OOM-killed silently, or scheduler heartbeat lag caused false positive zombie detection |
| **Tasks stuck in `QUEUED`** | Tasks remain queued for hours with available worker capacity | Scheduler CPU saturation preventing task scheduling, or Celery Redis broker connection drop |
| **Slow DAG parsing** | `DAG parsing time > 30s` in Airflow UI metrics | Top-level network requests, BigQuery queries, or heavy file reads in `dags/` Python scripts |
| **Scheduler restart loops** | `Scheduler heartbeat timeout` | Cloud SQL metadata database connection pool exhaustion or GKE pod memory limits reached |

---

## Diagnostic commands

### 1. Identifying slow-parsing DAG files

Run the Airflow CLI command inside the Composer environment:

```bash
# Test parse time of all DAG files
gcloud composer environments run prod-composer \
    --location=us-central1 \
    dags report
```

Look at the **Duration (seconds)** column; any file taking more than **1.0 second** is causing scheduler starvation.

### 2. Querying zombie detection logs in Cloud Logging

```bash
gcloud logging read '
  resource.type="cloud_composer_environment"
  textPayload=~"Detected zombie job"
' --limit=15 --format="table(timestamp, textPayload)"
```

---

## Resolution playbook

### 1. Removing top-level code anti-patterns
Move all database connections, API calls, and heavy variable lookups inside tasks:

```python
# Anti-pattern: Executed every 30 seconds by the Scheduler!
from google.cloud import bigquery
bq = bigquery.Client()
latest_partition = bq.query("SELECT MAX(date) FROM dataset.table").result()

# Best practice: Executed only when worker runs the task
from airflow.decorators import task

@task
def fetch_latest_partition():
    bq = bigquery.Client()
    return list(bq.query("SELECT MAX(date) FROM dataset.table").result())[0][0]
```

### 2. Sizing scheduler and triggerer capacity in Composer 2
If your environment runs more than 50 active DAGs, upgrade scheduler compute resources:

```bash
gcloud composer environments update prod-composer \
    --location=us-central1 \
    --scheduler-count=2 \
    --scheduler-cpu=2 \
    --scheduler-memory=4GB
```

### 3. Converting blocking tasks to deferrable operators
When tasks wait on long-running BigQuery or Dataproc jobs, standard operators hold Celery worker slots open. Replace with `deferrable=True` to eliminate worker slot exhaustion.

---

## Prevention checklist

- [ ] Ensure all DAG files parse in under 0.5 seconds (`dags report`).
- [ ] Never place `Variable.get()` or SQL queries at the root level of a Python file.
- [ ] Set `scheduler-count=2` for high availability in production environments.

---

| Previous Guide | All Debugging Guides | Next Guide |
| :--- | :---: | ---: |
| [04: Dataproc Spark Executor OOM](04-dataproc-spark-executor-oom-shuffle.md) | [Debugging Index](index.md) | [06: Dataform & dbt Cyclic Dependencies](06-dataform-dbt-cyclic-dependencies-assertions.md) |
