---
icon: lucide/grid
---

# Partitioning, clustering, and search indexes in BigQuery

Partitioning and clustering are the two primary physical layout optimizations in BigQuery. Partitioning segments data into distinct storage blocks based on date, timestamp, or integer values. Clustering sorts data within those partitions by up to four columns, enabling block-level pruning.

---

## Physical layout: Partitioning vs clustering

``` mermaid
flowchart TD
    subgraph Partitioning["Partitioning: Divides Table into Physical Slices"]
        P1["Partition: 2026-08-18"]
        P2["Partition: 2026-08-19"]
        P3["Partition: 2026-08-20"]
    end

    subgraph Clustering["Clustering: Sorts Blocks Inside Each Partition"]
        P3 --> C1["Block 1: customer_id [100..499] | status: 'ACTIVE'"]
        P3 --> C2["Block 2: customer_id [500..899] | status: 'ACTIVE'"]
        P3 --> C3["Block 3: customer_id [900..999] | status: 'PENDING'"]
    end

    Partitioning ~~~ Clustering
```

1. **Partition pruning**: BigQuery eliminates entire partitions during query planning before execution begins. This reduces both scanned bytes (cost on on-demand pricing) and slot consumption.
2. **Cluster pruning**: Dremel workers check min/max metadata on Capacitor blocks during query execution, skipping unneeded blocks. This reduces slot-milliseconds and wall-clock execution time.

---

## Partitioning strategies

BigQuery supports three partitioning mechanisms:

| Type | Syntax | Limits | Use case |
| :--- | :--- | :--- | :--- |
| **Time-unit column** | `PARTITION BY DATE(created_at)` | Max 10,000 partitions (Daily/Hourly/Monthly/Yearly) | Event timestamps, audit logs, order dates |
| **Ingestion-time** | `PARTITION BY _PARTITIONDATE` | Max 10,000 partitions | Raw append logs lacking explicit timestamp column |
| **Integer range** | `PARTITION BY RANGE_BUCKET(org_id, GENERATE_ARRAY(0, 100000, 1000))` | Max 10,000 partitions | Multi-tenant tenant IDs, customer ID shards |

---

## Clustering best practices

- You can specify up to **4 columns** in `CLUSTER BY`.
- **Column order matters**: Place high-cardinality columns used in equality filters first, followed by columns used in range filters.
- BigQuery automatically re-clusters data in the background at no cost as new data is appended.

---

## Creating an optimized table with DDL

```sql
CREATE TABLE `my_project.analytics_mart.fact_order_events` (
  order_id STRING NOT NULL,
  customer_id INT64 NOT NULL,
  merchant_id INT64 NOT NULL,
  order_status STRING,
  order_amount NUMERIC,
  event_timestamp TIMESTAMP NOT NULL
)
PARTITION BY DATE(event_timestamp)
CLUSTER BY merchant_id, customer_id, order_status
OPTIONS (
  partition_expiration_days = 730,
  require_partition_filter = true,
  description = "Partitioned daily by event_timestamp and clustered by merchant and customer"
);
```

Setting `require_partition_filter = true` forces analysts and BI tools to include a `WHERE event_timestamp >= ...` filter, preventing multi-terabyte query scan accidents.

---

## BigQuery search indexes

Standard clustering works on structured equality and range filters. For high-cardinality unstructured text or semi-structured JSON search (e.g., searching error logs for specific exception trace strings), create a **Search Index**:

```sql
-- Create text search index on log messages and JSON payloads
CREATE SEARCH INDEX idx_logs_message
ON `my_project.raw_logs.server_events` (log_message, payload);
```

Query with the native `SEARCH()` function:

```sql
SELECT event_timestamp, host_name, log_message
FROM `my_project.raw_logs.server_events`
WHERE SEARCH(log_message, '`NullPointerException`')
  AND DATE(event_timestamp) = '2026-08-20';
```

BigQuery uses an inverted index to pinpoint matching Capacitor blocks, scanning fractions of the bytes required by `LIKE '%NullPointerException%'`.

---

## Verifying query cost and scan reduction

Run an explain query with `dry_run` using Python to verify byte pruning:

```python
from google.cloud import bigquery

client = bigquery.Client()

query = """
SELECT order_id, order_amount
FROM `my_project.analytics_mart.fact_order_events`
WHERE event_timestamp >= '2026-08-01' AND event_timestamp < '2026-08-02'
  AND merchant_id = 4921
"""

job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
query_job = client.query(query, job_config=job_config)

print(f"Bytes to be scanned: {query_job.total_bytes_processed / (1024 * 1024):.2f} MB")
```

---

## Summary heuristics

1. Always partition on a high-granularity date column (`DATE(timestamp)`) and set `require_partition_filter = true` on tables larger than 100 GB.
2. Put the most selective filter column first in `CLUSTER BY`.
3. Use Search Indexes on log and JSON tables to accelerate point lookups without full string table scans.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0009: BigQuery Internal Architecture](0009-bigquery-internal-architecture.md) | [All Lessons (Index)](index.md) | [0011: BigQuery Storage Write API](0011-bigquery-storage-write-api.md) |
