---
icon: lucide/trending-down
---

# BigQuery FinOps: Cost monitoring, storage optimization, and query tuning

Managing data platform costs at scale requires applying FinOps practices to BigQuery compute, storage, and ingestion. Optimizing storage compression, setting byte safeguards, and diagnosing expensive query patterns cuts cloud spend without impacting query performance.

---

## BigQuery cost allocation architecture

``` mermaid
flowchart TD
    subgraph BigQuerySpend["BigQuery Total Cost"]
        ComputeSpend["Compute (On-Demand Scans vs Slot Editions)"]
        StorageSpend["Storage (Active vs Long-Term | Logical vs Physical)"]
        IngestionSpend["Ingestion (Storage Write API vs Batch Loads)"]
    end

    subgraph FinOpsGovernance["FinOps Controls & Guardrails"]
        Quotas["Project & User Query Byte Quotas"]
        PhysicalBilling["Physical Storage Billing Model (Compressed)"]
        SlotReservations["Autoscaled Slot Baseline Reservations"]
        FreeLoads["Zero-Cost Batch Loads from GCS"]
    end

    FinOpsGovernance --> BigQuerySpend
```

---

## Physical vs Logical storage billing models

BigQuery allows you to choose how storage is billed per dataset. The following rates are hypothetical arithmetic inputs, not current regional prices:

| Storage model | Hypothetical active rate per GB-month | Hypothetical long-term rate | Evaluation consideration |
| :--- | :--- | :--- | :--- |
| **Logical storage** | $0.020 per GB | $0.010 per GB | Uncompressed small tables, heavily mutated tables |
| **Physical storage** | $0.040 per GB | $0.020 per GB | Tables with high compression ratios (Parquet/Capacitor 5x-10x compression) |

If a table is 10 TB uncompressed (logical) but compresses to 1 TB on disk (physical):
- **Logical cost**: 10,000 GB * $0.020 = **$200/month**.
- **Physical cost**: 1,000 GB * $0.040 = **$40/month** (an 80% cost reduction).

### Enabling physical storage billing on a dataset

```sql
ALTER SCHEMA `my_project.analytics_mart`
SET OPTIONS(
  storage_billing_model = 'PHYSICAL'
);
```

---

## Query guardrails and cost controls

Prevent runaway queries by setting hard byte limits in client requests or configuring user-level quotas:

```python
from google.cloud import bigquery

client = bigquery.Client()
job_config = bigquery.QueryJobConfig()

# Bound eligible analysis bytes; current pricing is a separate input.
job_config.maximum_bytes_billed = 50 * 1024 * 1024 * 1024

query = """
SELECT customer_id, SUM(order_amount)
FROM `my_project.analytics_mart.fact_order_events`
WHERE event_timestamp >= TIMESTAMP '2026-08-20'
  AND event_timestamp < TIMESTAMP '2026-08-21'
GROUP BY customer_id
"""

query_job = client.query(query, job_config=job_config)
```

---

## Identifying top 10 most expensive queries

Query `INFORMATION_SCHEMA.JOBS_BY_PROJECT` to find expensive queries across the organization:

```sql
SELECT
  job_id,
  user_email,
  DATE(creation_time) AS query_date,
  total_bytes_billed / (1024 * 1024 * 1024 * 1024) AS terabytes_billed,
  total_slot_ms / (1000 * 60) AS slot_minutes,
  query
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND job_type = 'QUERY'
  AND (statement_type IS NULL OR statement_type != 'SCRIPT')
ORDER BY total_bytes_billed DESC
LIMIT 10;
```

---

## Query tuning anti-patterns and solutions

``` mermaid
flowchart TD
    subgraph AntiPattern1["Anti-Pattern: Multiple Repeated Subqueries"]
        Q1["SELECT * FROM (SELECT id FROM t) JOIN (SELECT id FROM t)"]
    end

    subgraph BestPractice1["Best Practice: CTE / Temporary Table"]
        Q2["Materialize expensive reused results when measurement justifies it"]
    end

    AntiPattern1 ~~~ BestPractice1
```

1. **Avoid `ORDER BY` without `LIMIT` in subqueries**: BigQuery sorts intermediate stages in memory; sort only in the outermost query.
2. **Filter early before joining**: Place partition filters in `WHERE` clauses instead of filtering after joining multi-million-row dimension tables.
3. Use approximate aggregates only when the metric tolerates approximation. Compare error and resource use on representative data; there is no universal speedup guarantee.

---

## Summary heuristics

1. Switch large analytical datasets with high compression ratios to **Physical Storage Billing** to cut storage costs.
2. Set `maximum_bytes_billed` on all automated BI dashboard service accounts to prevent single queries from scanning multi-terabyte datasets accidentally.
3. Monitor `INFORMATION_SCHEMA.JOBS_BY_PROJECT` weekly to identify un-clustered queries and train team members on partition pruning.

---

## Count the costs the compression example omits

Physical storage billing includes relevant time-travel and fail-safe bytes as well as active stored bytes. Frequently overwritten tables can retain several historical versions. A 10:1 compression ratio does not by itself prove physical billing is cheaper. Compare measured active, long-term and retained historical bytes at actual regional rates before changing the dataset billing model. See [storage billing](https://docs.cloud.google.com/bigquery/docs/storage_overview) and [time travel](https://docs.cloud.google.com/bigquery/docs/time-travel).

Query bytes are useful for on-demand analysis attribution, while reservation spend follows capacity/scaling and commitments. Do not multiply every project's job bytes by one public rate and call that the invoice. Account for cache hits, script-parent/child duplication, pricing tiers, storage, ingestion, transfer and supporting services. Use billing export for spend and job metrics for its causes.

CTEs improve query organization but are not guaranteed materialization. Referencing a costly CTE twice can evaluate work more than once. A temporary/materialized table can avoid repeated evaluation when its extra write/storage cost is justified. Compare execution plans and results rather than asserting that a `WITH` clause caches data.

## Worked unit-economics exercise

Assume a pipeline costs 120 units/day and delivers 60 million valid unique events. Its cost is 2 units per million delivered events. If a cheaper configuration costs 100 but loses 20 million events, the cost is 2.5 units per million valid events and correctness is worse. Track cost per accepted event, per published partition or per reconciled business transaction alongside the SLO.

For query guardrails, `maximum_bytes_billed` can reject an expensive eligible analysis request; it does not cap every capacity or storage charge. Budget alerts notify rather than acting as universal hard spending stops. Use dataset/table expiration for sandbox data and scoped retention for raw/history. Avoid deleting replay sources needed to meet recovery objectives merely to improve today's bill.

## Recall and review

Identify the three most expensive real workload groups using labels, billing export and job metrics. Propose one change, predict its cost and freshness/correctness impact, and compare measured results after a controlled trial. Preserve identical business boundaries for the comparison.

Sources: [compute best practices](https://docs.cloud.google.com/bigquery/docs/best-practices-performance-compute), [cost controls](https://docs.cloud.google.com/bigquery/docs/best-practices-costs), and [billing export](https://docs.cloud.google.com/billing/docs/how-to/export-data-bigquery).

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0035: End-to-End Pipeline Observability](0035-pipeline-observability-lineage.md) | [All Lessons (Index)](index.md) | [0037: BigQuery ingestion and ETL/ELT lab](0037-bigquery-ingestion-etl-elt-lab.md) |
