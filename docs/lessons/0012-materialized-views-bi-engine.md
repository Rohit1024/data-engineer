---
icon: lucide/zap
---

# Materialized views, BI Engine, and query acceleration in BigQuery

BigQuery provides two native acceleration technologies to achieve sub-second dashboard latencies without moving data to caching clusters: Materialized Views (MVs) and BigQuery BI Engine.

---

## Materialized Views: Automatic query rewrite and incremental refresh

A Materialized View precomputes aggregations and joins on disk. When the base table receives new inserts, BigQuery updates the materialized view incrementally in the background without scanning the entire historical table.

``` mermaid
flowchart TD
    BaseTable["Base Table (100 Billion Rows)"] --> MV["Materialized View (Precomputed Aggregates)"]
    NewInserts["New Appends (Last 10 mins)"] --> BaseTable

    Query["User Query on Base Table"] --> Optimizer["Dremel Cost-Based Optimizer"]
    Optimizer --> SmartRewrite{"Can Smart Query Rewrite Apply?"}
    SmartRewrite -- "Yes" --> Combine["Combine MV Aggregates + Delta from New Inserts"]
    SmartRewrite -- "No" --> FullScan["Full Scan on Base Table"]
    Combine --> FastResult["Sub-Second Result (Scanned 5 MB instead of 5 TB)"]
```

### Smart query rewrite
You do not need to query the materialized view directly. If a user submits a query against `base_table`, the BigQuery query optimizer automatically rewrites the query execution plan to read from the materialized view if it produces identical results at lower cost.

---

## Creating an incremental materialized view

```sql
CREATE MATERIALIZED VIEW `my_project.analytics_mart.mv_daily_merchant_sales`
OPTIONS (
  enable_refresh = true,
  refresh_interval_minutes = 30,
  max_staleness = INTERVAL "15" MINUTE
) AS
SELECT
  merchant_id,
  DATE(order_timestamp) AS order_date,
  COUNT(1) AS total_orders,
  SUM(order_amount) AS gross_revenue,
  AVG(order_amount) AS average_order_value
FROM `my_project.analytics_mart.fact_order_events`
GROUP BY merchant_id, order_date;
```

---

## BI Engine: In-memory query acceleration

BigQuery BI Engine is a built-in in-memory analysis service. It stores frequently accessed table columns and partition chunks in distributed RAM and evaluates SQL expressions using a vectorized in-memory query engine.

``` mermaid
flowchart TD
    Dashboard["Looker / Tableau / Connected Sheets"] --> BIQuery["SQL Dashboard Query"]
    BIQuery --> BIEngine["BI Engine In-Memory Cache (RAM)"]
    BIEngine --> Match{"Data Cached in BI RAM?"}
    Match -- "Full Match" --> InMemEval["Sub-100ms In-Memory Vector Execution"]
    Match -- "Partial / Miss" --> DremelFallback["Fallback to Dremel On-Demand Slots"]
```

### Sizing and provisioning BI Engine reservations

BI Engine is provisioned per region and charges a flat hourly fee per GB of reserved RAM:

```bash
# Reserve 50 GB of BI Engine in-memory cache in us-central1
gcloud bigquery bi-reservation create \
    --project=my-gcp-project \
    --location=us-central1 \
    --size=50G
```

You can target specific tables or schemas to ensure BI memory is not occupied by ad-hoc queries:

```bash
# Verify BI Engine reservation
gcloud bigquery bi-reservation describe \
    --project=my-gcp-project \
    --location=us-central1
```

---

## Diagnostic monitoring with INFORMATION_SCHEMA

Check whether queries are being accelerated by BI Engine or hitting Dremel fallback:

```sql
SELECT
  job_id,
  query,
  bi_engine_statistics.bi_engine_mode,
  bi_engine_statistics.acceleration_mode,
  bi_engine_statistics.bi_engine_reasons
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
  AND bi_engine_statistics IS NOT NULL
ORDER BY creation_time DESC
LIMIT 10;
```

Possible `bi_engine_mode` statuses:
- `FULL`: Query ran entirely inside BI Engine in-memory cache.
- `PARTIAL`: Part of the query ran in RAM; remaining stages ran on Dremel slots.
- `DISABLED`: Query contained unsupported functions (e.g. specific user-defined functions or unsupported joins).

---

## Summary heuristics

1. Create Materialized Views for large fact tables with heavy aggregation patterns (`SUM`, `COUNT`, `AVG`) accessed by recurring reporting dashboards.
2. Enable BI Engine for interactive dashboards (Looker, Tableau) where end users demand sub-second query response times on filtered dimensional queries.
3. Use `max_staleness` on Materialized Views to allow BigQuery to serve fast cached results without blocking on recent unmaterialized streaming inserts.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0011: BigQuery Storage Write API](0011-bigquery-storage-write-api.md) | [All Lessons (Index)](index.md) | [0013: Slot Management & Editions](0013-bigquery-slot-management-editions.md) |
