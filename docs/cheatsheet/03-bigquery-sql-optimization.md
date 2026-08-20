---
icon: lucide/database
---

# BigQuery SQL and optimization cheatsheet

Condensed reference for `bq` CLI operations, table optimization DDL, slot reservations, BI Engine tuning, and `INFORMATION_SCHEMA` diagnostic queries.

---

## BigQuery query execution architecture

``` mermaid
flowchart TD
    Query["Client SQL Query"] --> Root["Dremel Root / Parser & Optimizer"]
    Root --> BIEngine{"Cached in BI Engine RAM?"}
    BIEngine -- "Yes" --> Sub100ms["Sub-100ms In-Memory Vector Execution"]
    BIEngine -- "No" --> Slots["Dremel Slots (Leaf Workers via Jupiter Network)"]
    Slots --> Pruning{"Evaluate Capacitor Min/Max Metadata"}
    Pruning --> Read["Read Pruned Partition/Cluster Blocks from Colossus"]
    Read --> IntermediateShuffle["In-Memory Intermediate Shuffle"]
    IntermediateShuffle --> Result["Return Aggregated Result"]
```

---

## Table optimization DDL syntax

### Partitioning, clustering, and expiration

```sql
CREATE OR REPLACE TABLE `my_project.analytics.fact_orders` (
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
  description = "Daily partitioned and clustered fact table"
);
```

### Creating an incremental Materialized View

```sql
CREATE MATERIALIZED VIEW `my_project.analytics.mv_daily_merchant_sales`
OPTIONS (
  enable_refresh = true,
  refresh_interval_minutes = 30,
  max_staleness = INTERVAL "15" MINUTE
) AS
SELECT
  merchant_id,
  DATE(event_timestamp) AS order_date,
  COUNT(1) AS order_count,
  SUM(order_amount) AS total_revenue
FROM `my_project.analytics.fact_orders`
GROUP BY merchant_id, order_date;
```

---

## Essential `bq` CLI operations

```bash
# Dry run query to estimate scanned bytes and costs before executing
bq query --use_legacy_sql=false --dry_run \
    'SELECT * FROM `my_project.analytics.fact_orders` WHERE DATE(event_timestamp) = "2026-08-20"'

# Free zero-cost batch load from GCS Parquet files
bq load --source_format=PARQUET \
    --replace=false \
    my_project:analytics.fact_orders \
    "gs://my-bucket/orders/*.parquet"

# Export query results directly to compressed Parquet files on GCS
bq extract --destination_format=PARQUET \
    --compression=SNAPPY \
    my_project:analytics.fact_orders \
    "gs://my-bucket/exports/orders_*.parquet"
```

---

## Slot reservations and BI Engine management

```bash
# Create Enterprise edition reservation with autoscaling
gcloud bigquery reservations create prod-etl-reservation \
    --project=my-admin-project \
    --location=us-central1 \
    --edition=ENTERPRISE \
    --slots=100 \
    --autoscale-max-slots=400 \
    --ignore-idle-slots=false

# Assign project to the reservation
gcloud bigquery reservations assignments create \
    --project=my-admin-project \
    --location=us-central1 \
    --reservation=prod-etl-reservation \
    --job-type=QUERY \
    --assignee-id=my-data-engineering-project \
    --assignee-type=PROJECT

# Provision 50 GB BI Engine in-memory acceleration
gcloud bigquery bi-reservation create \
    --project=my-data-engineering-project \
    --location=us-central1 \
    --size=50G
```

---

## `INFORMATION_SCHEMA` diagnostic queries

### Top 10 most expensive queries (last 7 days)

```sql
SELECT
  job_id,
  user_email,
  DATE(creation_time) AS query_date,
  total_bytes_billed / (1024 * 1024 * 1024 * 1024) AS terabytes_billed,
  (total_bytes_billed / (1024 * 1024 * 1024 * 1024)) * 6.25 AS estimated_cost_usd,
  total_slot_ms / (1000 * 60) AS slot_minutes,
  query
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND job_type = 'QUERY'
ORDER BY total_bytes_billed DESC
LIMIT 10;
```

### Checking BI Engine acceleration mode

```sql
SELECT
  job_id,
  bi_engine_statistics.bi_engine_mode,
  bi_engine_statistics.acceleration_mode,
  bi_engine_statistics.bi_engine_reasons
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
  AND bi_engine_statistics IS NOT NULL
ORDER BY creation_time DESC;
```

---

| Previous Cheatsheet | All Cheatsheets | Next Cheatsheet |
| :--- | :---: | ---: |
| [02: Pub/Sub & Datastream](02-pubsub-datastream-cdc.md) | [Cheatsheets Index](index.md) | [04: Dataflow & Apache Beam](04-dataflow-apache-beam.md) |
