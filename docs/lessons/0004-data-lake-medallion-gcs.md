---
icon: lucide/git-merge
---

# Data lake design patterns: Medallion architecture on GCS

The Medallion architecture structures data storage into three distinct quality layers: Bronze (Raw), Silver (Cleaned/Enriched), and Gold (Aggregated/Business-Ready). Implementing this on Cloud Storage (GCS) and BigLake requires careful partition layout design, compaction policies, and schema enforcement.

---

## Medallion layout on Google Cloud

``` mermaid
flowchart TD
    subgraph Sources["Raw Ingestion"]
        API["HTTP Webhooks"]
        DB["RDBMS CDC"]
        IoT["IoT Telemetry"]
    end

    subgraph Bronze["Bronze Layer (Raw Landing)"]
        B1["gs://lake-bronze/events/raw_*.json"]
        B2["Immutable raw append log"]
    end

    subgraph Silver["Silver Layer (Cleaned & Conformed)"]
        S1["gs://lake-silver/events/dt=YYYY-MM-DD/*.parquet"]
        S2["Deduplicated, type-cast, schema-enforced"]
    end

    subgraph Gold["Gold Layer (Business Aggregates)"]
        G1["BigQuery Managed or Iceberg Tables"]
        G2["Star-schema marts, metric summaries"]
    end

    Sources --> Bronze
    Bronze -->|"Dataflow / Dataproc Validation"| Silver
    Silver -->|"Dataform / dbt / Spark Aggregations"| Gold
```

---

## Partition directory structure and Hive layout

BigQuery and Spark parse partition columns directly from GCS URIs when Hive partitioning syntax is used:

```text
gs://lake-silver/customer_orders/
  ├── year=2026/
  │   ├── month=08/
  │   │   ├── day=20/
  │   │   │   ├── part-00000.snappy.parquet
  │   │   │   └── part-00001.snappy.parquet
```

### Autodetecting Hive partitions in BigQuery

When querying external or BigLake tables, configure Hive partition autodetection:

```sql
CREATE EXTERNAL TABLE `my_project.analytics_silver.customer_orders`
WITH CONNECTION `us.biglake-gcs-conn`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://lake-silver/customer_orders/*'],
  hive_partition_uri_prefix = 'gs://lake-silver/customer_orders/',
  require_hive_partition_filter = true
);
```

Setting `require_hive_partition_filter = true` prevents users from executing accidental full-bucket scans without a partition predicate.

---

## Solving the small files problem

Streaming pipelines writing micro-batches can generate millions of 10 KB files. This degrades query performance because every file requires an HTTP GET metadata request and file footer decode.

``` mermaid
flowchart TD
    subgraph SmallFilesIssue["Small Files Anti-Pattern"]
        F1["10KB File 1"] --> Meta["10,000 Metadata GET Requests (High I/O Overhead)"]
        F2["10KB File 2"] --> Meta
        F3["10KB File N"] --> Meta
    end

    subgraph CompactedFiles["Compacted Parquet (Optimal)"]
        Compactor["Compaction Job (Dataproc / Spark)"] --> Output["128MB - 512MB Parquet Files"]
        Output --> Read["Fast Vectorized Columnar Scan"]
    end

    SmallFilesIssue ~~~ CompactedFiles
```

### Heuristics for file sizing
- **Target Parquet file size**: 128 MB to 512 MB.
- **Row group size**: 64 MB to 128 MB.
- **Compression**: Snappy for fast decompression, or Zstandard (zstd) for better compression ratios on cold storage.

---

## Hands-on transformation: PySpark Silver compaction

This PySpark script reads Bronze raw events, validates schema types, deduplicates by event ID, and compacts into partitioned Silver Parquet files:

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, row_number
from pyspark.sql.window import Window

spark = SparkSession.builder \
    .appName("bronze-to-silver-compaction") \
    .getOrCreate()

# 1. Ingest raw JSON from Bronze
raw_df = spark.read.json("gs://lake-bronze/events/raw_*.json")

# 2. Schema conform and timestamp parse
conformed_df = raw_df \
    .withColumn("event_timestamp", to_timestamp(col("raw_time"), "yyyy-MM-dd'T'HH:mm:ss.SSSX")) \
    .withColumn("user_id", col("userId").cast("string")) \
    .withColumn("event_name", col("eventType").cast("string"))

# 3. Deduplicate latest record per event_id
dedup_window = Window.partitionBy("eventId").orderBy(col("event_timestamp").desc())
deduped_df = conformed_df \
    .withColumn("rank", row_number().over(dedup_window)) \
    .filter(col("rank") == 1) \
    .drop("rank", "raw_time", "userId", "eventType")

# 4. Write compacted Parquet to Silver with Hive partitions
deduped_df.write \
    .mode("append") \
    .partitionBy("event_date") \
    .parquet("gs://lake-silver/events/")
```

---

## Summary heuristics

1. Keep Bronze immutable. Do not clean or modify files in Bronze; if logic changes, you must be able to reprocess from raw data.
2. Require partition filters (`require_hive_partition_filter = true`) on external tables to eliminate unpruned full bucket scans.
3. Compact small files in Silver into 128 MB to 512 MB Parquet files using scheduled Dataproc batches.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0003: BigLake & Apache Iceberg Catalogs](0003-biglake-iceberg-catalogs.md) | [All Lessons (Index)](index.md) | [0005: Cloud Pub/Sub Architecture](0005-pubsub-architecture-flow-control.md) |
