---
icon: lucide/database-zap
---

# PySpark ETL workloads and the BigQuery Storage connector

The Spark-BigQuery Connector enables Apache Spark applications to read directly from and write to BigQuery at scale. It utilizes the BigQuery Storage Read and Write APIs, streaming Apache Arrow and Avro record streams directly into Spark executor memory without writing temporary files to GCS.

---

## Connector architecture and parallel reads

``` mermaid
flowchart TD
    SparkDriver["Spark Driver"] -->|"1. Request Read Session (Filter + Column Projections)"| BQStorageAPI["BigQuery Storage Read API"]
    BQStorageAPI -->|"2. Return N Stream Descriptors"| SparkDriver
    SparkDriver -->|"3. Assign Streams to Partitions"| Exec1["Spark Executor 1"]
    SparkDriver --> Exec2["Spark Executor 2"]
    SparkDriver --> Exec3["Spark Executor 3"]

    Exec1 <-->|"Parallel gRPC / Arrow Stream 1"| BQStorageAPI
    Exec2 <-->|"Parallel gRPC / Arrow Stream 2"| BQStorageAPI
    Exec3 <-->|"Parallel gRPC / Arrow Stream 3"| BQStorageAPI
```

---

## Predicate and projection pushdown

When you apply `.filter()` or `.select()` in PySpark, the connector translates SQL expressions into BigQuery filter predicates:
- Unused columns are skipped before reading from Capacitor storage.
- Filtered rows are excluded at the BigQuery storage tier, avoiding network transfer to Spark workers.

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("spark-bigquery-optimized-read") \
    .config("spark.jars.packages", "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.34.0") \
    .getOrCreate()

# Predicate pushdown happens automatically
df = spark.read.format("bigquery") \
    .option("table", "my-gcp-project.analytics_mart.fact_order_events") \
    .option("filter", "DATE(event_timestamp) >= '2026-08-01' AND order_status = 'COMPLETED'") \
    .load()

# Select only necessary columns
projected_df = df.select("order_id", "customer_id", "merchant_id", "order_amount")
```

---

## Writing data back to BigQuery

The connector supports two write methods:

### 1. Direct write method (Storage Write API)
Streams data directly from Spark executors into BigQuery storage via gRPC. No temporary GCS bucket is required.

```python
projected_df.write \
    .format("bigquery") \
    .option("writeMethod", "direct") \
    .option("table", "my-gcp-project.analytics_mart.aggregated_daily_sales") \
    .mode("append") \
    .save()
```

### 2. Indirect write method (GCS staging)
Writes intermediate Parquet or Avro files to a temporary GCS bucket, then triggers a BigQuery batch load job. Useful when writing tens of terabytes where free batch load jobs are preferred.

```python
projected_df.write \
    .format("bigquery") \
    .option("temporaryGcsBucket", "my-staging-bucket") \
    .option("table", "my-gcp-project.analytics_mart.aggregated_daily_sales") \
    .mode("overwrite") \
    .save()
```

---

## Complete ETL transformation pipeline

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, avg, count

spark = SparkSession.builder \
    .appName("merchant-daily-aggregation") \
    .getOrCreate()

# 1. Read source fact table using direct Storage Read API
orders_df = spark.read.format("bigquery") \
    .option("table", "my-gcp-project.analytics_mart.fact_order_events") \
    .option("filter", "DATE(event_timestamp) = CURRENT_DATE()") \
    .load()

# 2. Compute business aggregations
merchant_summary_df = orders_df.groupBy("merchant_id") \
    .agg(
        count("order_id").alias("total_orders"),
        _sum("order_amount").alias("gross_revenue"),
        avg("order_amount").alias("avg_order_value")
    )

# 3. Write summary directly to BigQuery target table
merchant_summary_df.write \
    .format("bigquery") \
    .option("writeMethod", "direct") \
    .option("table", "my-gcp-project.analytics_mart.daily_merchant_summary") \
    .mode("append") \
    .save()
```

---

## Summary heuristics

1. Use `option("filter", "...")` on BigQuery reads to enforce predicate pushdown and prune scanned bytes before data travels across the network.
2. Use `writeMethod="direct"` for low-latency pipeline steps; use `writeMethod="indirect"` with `temporaryGcsBucket` when writing large bulk historical snapshots.
3. Configure `maxParallelism` when reading massive tables to control the number of gRPC streams allocated across Spark worker tasks.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0021: Dataproc Serverless for Spark](0021-dataproc-serverless-spark.md) | [All Lessons (Index)](index.md) | [0023: Spark Optimization on GCP](0023-spark-optimization-memory-tuning-gcp.md) |
