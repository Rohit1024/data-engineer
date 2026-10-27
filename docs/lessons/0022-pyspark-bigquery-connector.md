---
icon: lucide/database-zap
---

# PySpark ETL workloads and the BigQuery Storage connector

The Spark-BigQuery Connector enables Apache Spark applications to read directly from and write to BigQuery at scale. It utilizes the BigQuery Storage Read and Write APIs, using parallel read streams and either direct Storage Write API writes or indirect Cloud Storage staging, depending on the configured write method.

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

spark = SparkSession.builder.appName("spark-bigquery-optimized-read").getOrCreate()
# Use the connector bundled with the selected runtime, or install a compatible pinned version.

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
    .option("table", "my-gcp-project.analytics_staging.orders_projection") \
    .mode("append") \
    .save()
```

### 2. Indirect write method (GCS staging)
Writes intermediate Parquet or Avro files to a temporary GCS bucket, then triggers a BigQuery batch load job. Useful when writing tens of terabytes where free batch load jobs are preferred.

```python
projected_df.write \
    .format("bigquery") \
    .option("writeMethod", "indirect") \
    .option("temporaryGcsBucket", "my-staging-bucket") \
    .option("table", "my-gcp-project.analytics_staging.orders_projection") \
    .mode("overwrite") \
    .save()
```

---

## Complete ETL transformation pipeline

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, avg, count, to_date

spark = SparkSession.builder \
    .appName("merchant-daily-aggregation") \
    .getOrCreate()

# 1. Read source fact table using direct Storage Read API
orders_df = spark.read.format("bigquery") \
    .option("table", "my-gcp-project.analytics_mart.fact_order_events") \
    .option("filter", "DATE(event_timestamp) = '2026-08-20'") \
    .load()

# 2. Compute business aggregations
merchant_summary_df = orders_df.withColumn("business_date", to_date("event_timestamp")) \
    .groupBy("business_date", "merchant_id") \
    .agg(
        count("order_id").alias("total_orders"),
        _sum("order_amount").alias("gross_revenue"),
        avg("order_amount").alias("avg_order_value")
    )

# 3. Replace this dedicated run's staging result; publication is a separate step.
merchant_summary_df.write \
    .format("bigquery") \
    .option("writeMethod", "direct") \
    .option("table", "my-gcp-project.analytics_staging.merchant_summary_run_20260820") \
    .mode("overwrite") \
    .save()
```

---

## Summary heuristics

1. Use `option("filter", "...")` on BigQuery reads to enforce predicate pushdown and prune scanned bytes before data travels across the network.
2. Use `writeMethod="direct"` for low-latency pipeline steps; use `writeMethod="indirect"` with `temporaryGcsBucket` when writing large bulk historical snapshots.
3. Configure `maxParallelism` when reading massive tables to control the number of gRPC streams allocated across Spark worker tasks.

---

## Connector guarantees do not make whole-job retries unique

Direct and indirect writes use different protocols. Indirect writes stage files and run a load job; direct writes use the Storage Write API. Connector/version options affect retry behavior. Even when one job's task retries are handled correctly, starting the whole aggregation again in append mode can add another daily summary.

The complete example groups by business date and merchant and replaces a dedicated run-specific staging table. It assumes a fixed source day and one owner of that staging output. Validate `(business_date, merchant_id)` uniqueness, then transactionally replace the intended reporting partition. Staging success alone does not publish the mart. See [0039](0039-managed-airflow-environments-dags.md#6-dag-2-wait-load-validate-and-publish-to-bigquery).

Predicate/projection pushdown reduces transferred data only for supported expressions and paths. Inspect `df.explain("formatted")`, connector logs and read/query metrics. A Python UDF filter usually runs after reading rather than being translated into a Storage Read predicate. Query-based reads may create BigQuery work and temporary results, so a filter in Spark is not proof of zero warehouse cost.

## A connector exercise with expected results

Create three orders for two merchants using the fixture from lesson 0014. Read selected columns, filter one recorded business date, aggregate integer cents and write to a sandbox staging table. Expect two merchant rows totaling 7,700 cents. Rerun append and observe four physical rows; then switch to bounded partition publication and prove a rerun preserves two business rows.

Ensure the identity can create read sessions and read source tables. Writes need target data permissions and, for indirect mode, appropriate staging-object and load-job permissions. Clean up staging files after success and failure; do not assume a failed Spark application removed every temporary object.

Source: the [official Spark BigQuery connector README and compatibility matrix](https://github.com/GoogleCloudDataproc/spark-bigquery-connector).

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0021: Serverless Spark batches](0021-dataproc-serverless-spark.md) | [All Lessons (Index)](index.md) | [0023: Spark Optimization on GCP](0023-spark-optimization-memory-tuning-gcp.md) |
