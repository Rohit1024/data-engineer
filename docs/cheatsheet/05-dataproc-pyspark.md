---
icon: lucide/server
---

# Cloud Dataproc and PySpark cheatsheet

Quick reference commands, cluster provisioning parameters, Spark tuning flags, and BigQuery connector integration for Apache Spark on Google Cloud.

---

## Dataproc deployment modes

``` mermaid
flowchart TD
    Airflow["Orchestrator (Cloud Composer / Airflow)"] --> Decision{"Batch Job Execution Mode"}
    Decision -- "Serverless (No Cluster Ops)" --> Serverless["Dataproc Serverless Batches (DCUs)"]
    Decision -- "Ephemeral Cluster (Full Control)" --> Ephemeral["Ephemeral Cluster (Preemptible Workers + Auto-Delete)"]

    Serverless --> ReadWrite["Read & Write to GCS / BigQuery via Storage API"]
    Ephemeral --> ReadWrite
```

---

## Provisioning and submitting jobs

### 1. Ephemeral cluster with Spot workers and auto-delete

```bash
gcloud dataproc clusters create batch-cluster-01 \
    --region=us-central1 \
    --master-machine-type=n2-standard-4 \
    --master-boot-disk-size=100GB \
    --num-workers=2 \
    --worker-machine-type=n2-standard-8 \
    --worker-boot-disk-size=200GB \
    --num-secondary-workers=6 \
    --secondary-worker-type=spot \
    --max-idle=15m
```

### 2. Submitting PySpark job to managed cluster

```bash
gcloud dataproc jobs submit pyspark gs://my-code-bucket/scripts/etl_orders.py \
    --cluster=batch-cluster-01 \
    --region=us-central1 \
    --jars=gs://spark-lib/bigquery/spark-bigquery-with-dependencies_2.12-0.34.0.jar \
    --properties=spark.sql.adaptive.enabled=true,spark.executor.memory=10g,spark.executor.memoryOverhead=3g
```

### 3. Submitting to Dataproc Serverless (Zero-cluster)

```bash
gcloud dataproc batches submit pyspark gs://my-code-bucket/scripts/etl_orders.py \
    --region=us-central1 \
    --version=2.1 \
    --deps-bucket=gs://my-staging-bucket \
    --properties=spark.dynamicAllocation.maxExecutors=16,spark.driver.cores=4
```

---

## PySpark with BigQuery Storage connector

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("pyspark-bigquery-etl") \
    .config("spark.jars.packages", "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.34.0") \
    .getOrCreate()

# 1. Read from BigQuery with pushdown filtering
df = spark.read.format("bigquery") \
    .option("table", "my-project.analytics.fact_orders") \
    .option("filter", "DATE(event_timestamp) = '2026-08-20'") \
    .load()

# 2. Transform in Spark
summary_df = df.groupBy("merchant_id").count()

# 3. Direct write via BigQuery Storage Write API
summary_df.write \
    .format("bigquery") \
    .option("writeMethod", "direct") \
    .option("table", "my-project.analytics.daily_merchant_counts") \
    .mode("append") \
    .save()
```

---

## Essential Spark tuning properties

| Property | Recommended value | Purpose |
| :--- | :--- | :--- |
| `spark.sql.adaptive.enabled` | `true` | Enables Adaptive Query Execution (AQE) |
| `spark.sql.adaptive.coalescePartitions.enabled` | `true` | Merges tiny post-shuffle partitions automatically |
| `spark.sql.adaptive.skewJoin.enabled` | `true` | Splits skewed partition tasks automatically |
| `spark.sql.autoBroadcastJoinThreshold` | `67108864` (64 MB) | Broadcasts tables under 64 MB to avoid network shuffles |
| `spark.executor.memoryOverhead` | `2g` to `4g` | Prevents YARN container memory killed errors in PySpark |
| `spark.dynamicAllocation.enabled` | `true` | Scales executors based on task backlog |

---

| Previous Cheatsheet | All Cheatsheets | Next Cheatsheet |
| :--- | :---: | ---: |
| [04: Dataflow & Apache Beam](04-dataflow-apache-beam.md) | [Cheatsheets Index](index.md) | [06: Dataform & dbt](06-dataform-dbt.md) |
