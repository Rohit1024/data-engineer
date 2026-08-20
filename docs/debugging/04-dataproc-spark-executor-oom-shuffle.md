---
icon: lucide/bug
---

# Debugging Dataproc Spark executor failures, shuffle fetch errors, and OOM

Diagnostic playbook for troubleshooting Apache Spark job crashes on Google Cloud Dataproc, including `Container killed by YARN for exceeding memory limits`, `FetchFailedException`, and executor loss during wide shuffles.

---

## Failure sequence diagram

``` mermaid
sequenceDiagram
    autonumber
    actor Driver as Spark Driver
    participant YARN as YARN NodeManager
    participant Exec1 as Executor 1 (Shuffle Producer)
    participant Exec2 as Executor 2 (Shuffle Consumer)

    Driver->>Exec1: Execute Wide Join Stage
    Exec1->>Exec1: PySpark C bindings allocate memory outside JVM heap
    Note over Exec1: Total memory > spark.executor.memory + overhead!
    YARN->>Exec1: SIGKILL (Container killed for exceeding memory limits)
    Driver->>Exec2: Fetch shuffle partition from Executor 1
    Exec2->>Exec1: HTTP GET /shuffle/block_1002
    Note over Exec1: No response (Process Dead)
    Exec2-->>Driver: FetchFailedException: Connection refused
    Note over Driver: Driver aborts stage and initiates expensive stage retry
```

---

## Symptoms and diagnostic signals

| Symptom | Error message / Diagnostic log | Root cause |
| :--- | :--- | :--- |
| **YARN container killed** | `Container killed by YARN for exceeding memory limits. 10.4 GB of 10.0 GB used.` | PySpark Python processes, JVM overhead, or off-heap allocations exceeded `memoryOverhead` |
| **Shuffle fetch failure** | `org.apache.spark.shuffle.FetchFailedException: Connection refused` | The executor holding shuffle blocks crashed (often due to OOM), breaking consumer reads |
| **Driver OOM error** | `java.lang.OutOfMemoryError: Java heap space` on driver | Calling `.collect()` or `.toPandas()` on multi-million row DataFrames onto the driver node |
| **Executor heartbeat timeout** | `ExecutorLostFailure: Remote RPC client disassociated` | Heavy Garbage Collection (GC) pauses freezing the JVM for longer than `spark.network.timeout` |

---

## Diagnostic commands

### 1. Extracting YARN container kill logs

```bash
gcloud dataproc jobs wait JOB_ID --region=us-central1

# Fetch specific YARN container error logs
yarn logs -applicationId application_1620000000000_0001 | grep -i -E "killed by YARN|OutOfMemoryError|FetchFailed"
```

### 2. Identifying task skew in Spark UI
Look at the **Stages** tab in the Spark History Server:
- Compare the **Max** task duration to the **75th percentile** task duration.
- If 75th percentile is 3 seconds, but Max is 45 minutes, the stage suffers from data skew.

---

## Resolution playbook

### 1. Increasing `spark.executor.memoryOverhead` for PySpark
In PySpark workloads, Python worker processes run alongside the JVM inside the same YARN container. Increase off-heap overhead memory:

```bash
gcloud dataproc jobs submit pyspark gs://my-bucket/jobs/transform.py \
    --cluster=my-cluster \
    --region=us-central1 \
    --properties=\
spark.executor.memory=8g,\
spark.executor.memoryOverhead=3g,\
spark.driver.memory=8g
```

### 2. Tuning shuffle partitions and network timeouts
By default, Spark uses 200 shuffle partitions, which is either too small (causing huge memory spills) or too large for smaller datasets:

```properties
# Enable Adaptive Query Execution to tune partition count dynamically
spark.sql.adaptive.enabled=true
spark.sql.adaptive.coalescePartitions.enabled=true
spark.sql.adaptive.skewJoin.enabled=true

# Extend network timeouts to absorb temporary GC pauses during massive shuffles
spark.network.timeout=800s
spark.executor.heartbeatInterval=60s
```

### 3. Replacing full `.collect()` calls
Never pull distributed datasets to the driver node:

```python
# Anti-pattern: Driver OOM crash
all_records = df.collect()

# Best practice: Write directly to BigQuery or GCS
df.write.format("bigquery").option("writeMethod", "direct").save("my_proj.mart.output")
```

---

## Prevention checklist

- [ ] Always allocate at least 25% of executor memory to `spark.executor.memoryOverhead` in PySpark.
- [ ] Enable `spark.sql.adaptive.enabled=true` by default.
- [ ] Avoid `collect()` or `toPandas()` in driver scripts for datasets larger than 10,000 rows.

---

| Previous Guide | All Debugging Guides | Next Guide |
| :--- | :---: | ---: |
| [03: Pub/Sub Unacked Messages](03-pubsub-unacked-messages-throttling.md) | [Debugging Index](index.md) | [05: Composer Scheduler & Zombies](05-composer-scheduler-starvation-zombies.md) |
