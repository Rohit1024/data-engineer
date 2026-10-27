---
icon: lucide/zap
---

# Materialized views, BI Engine, and query acceleration in BigQuery

Materialized views can avoid repeated computation, while BI Engine can accelerate supported queries using reserved memory. Measure their benefit against the dashboard's freshness and latency requirements.

---

## Materialized Views: Automatic query rewrite and incremental refresh

A materialized view stores a query result. Eligible incremental definitions can process supported changes without recomputing the entire result. SQL shape and base-table mutations determine whether incremental maintenance and smart tuning are available.

``` mermaid
flowchart TD
    BaseTable["Base Table (100 Billion Rows)"] --> MV["Materialized View (Precomputed Aggregates)"]
    NewInserts["New Appends (Last 10 mins)"] --> BaseTable

    Query["User Query on Base Table"] --> Optimizer["Dremel Cost-Based Optimizer"]
    Optimizer --> SmartRewrite{"Can Smart Query Rewrite Apply?"}
    SmartRewrite -- "Yes" --> Combine["Combine MV Aggregates + Delta from New Inserts"]
    SmartRewrite -- "No" --> FullScan["Full Scan on Base Table"]
    Combine --> FastResult["Eligible accelerated result"]
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
  DATE(event_timestamp) AS order_date,
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
    Match -- "Full Match" --> InMemEval["Vectorized in-memory execution"]
    Match -- "Partial / Miss" --> DremelFallback["Fallback to Dremel On-Demand Slots"]
```

### Sizing and provisioning BI Engine reservations

BI Engine is provisioned per region and charges a flat hourly fee per GB of reserved RAM:

In the BigQuery console, open **BI Engine → Create reservation**, select the project and region, and choose capacity after measuring the dashboard's active data. Configure preferred tables if the workload needs them. Creating a reservation consumes billable capacity. Follow the [BI Engine reservation guide](https://docs.cloud.google.com/bigquery/docs/bi-engine-reserve-capacity) for supported API or console steps.

---

## Diagnostic monitoring with INFORMATION_SCHEMA

Check whether queries are being accelerated by BI Engine or hitting Dremel fallback:

```sql
SELECT
  job_id,
  query,
  bi_engine_statistics.bi_engine_mode,
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

## Decide which acceleration mechanism solves the problem

The result cache reuses eligible query results. A materialized view stores a maintained result that can reduce repeated aggregation work. BI Engine accelerates supported operations using reserved memory. These mechanisms have different eligibility, freshness and cost boundaries; they do not guarantee every dashboard query finishes in less than a second.

For 100 million order rows grouped into 10,000 merchant/day combinations, an eligible materialized view can avoid repeatedly processing the full aggregation. A new append can be combined with maintained data when supported. Updates, deletes, join shape or unsupported SQL can prevent incremental maintenance or smart tuning. Inspect the execution plan and materialized-view statistics rather than assuming the optimizer used the view.

`max_staleness` is a deliberate freshness allowance when querying the view. It does not make an arbitrary base-table query stale, and a refresh interval is not a strict freshness SLA. The example's 30-minute refresh interval and 15-minute staleness allowance can require base-data work when a refresh is older than the allowance. Align those settings with the dashboard's actual freshness requirement.

## Exercise with expected evidence

Run a base-table aggregate with result caching disabled, then an equivalent eligible query after creating the materialized view. Record bytes, slot-ms, refresh state and rewrite evidence. Next run a query that requires a column absent from the view and explain the fallback. With BI Engine, inspect `FULL`, `PARTIAL` or `DISABLED` and the reason fields; a reservation alone proves no acceleration.

??? note "Recall answer"
    A faster repeated query might be result-cache reuse, materialized-view reuse, BI Engine, or a different execution plan. Use job statistics to identify the mechanism before attributing the improvement.

Sources: [materialized-view creation](https://docs.cloud.google.com/bigquery/docs/materialized-views-create), [smart tuning and use](https://docs.cloud.google.com/bigquery/docs/materialized-views-use), and [BI Engine overview](https://docs.cloud.google.com/bigquery/docs/bi-engine-intro).

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0011: BigQuery Storage Write API](0011-bigquery-storage-write-api.md) | [All Lessons (Index)](index.md) | [0013: Slot Management & Editions](0013-bigquery-slot-management-editions.md) |
