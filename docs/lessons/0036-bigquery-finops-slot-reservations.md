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

BigQuery allows you to choose how storage is billed per dataset:

| Storage model | Price (Active) | Price (Long-term > 90 days) | Best suited for |
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

# Fail query immediately if it scans more than 50 GB ($0.31)
job_config.maximum_bytes_billed = 50 * 1024 * 1024 * 1024

query = """
SELECT customer_id, SUM(order_amount)
FROM `my_project.analytics_mart.fact_order_events`
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
  (total_bytes_billed / (1024 * 1024 * 1024 * 1024)) * 6.25 AS estimated_cost_usd,
  total_slot_ms / (1000 * 60) AS slot_minutes,
  query
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND job_type = 'QUERY'
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
        Q2["WITH base AS (SELECT id FROM t) SELECT * FROM base b1 JOIN base b2 ..."]
    end

    AntiPattern1 ~~~ BestPractice1
```

1. **Avoid `ORDER BY` without `LIMIT` in subqueries**: BigQuery sorts intermediate stages in memory; sort only in the outermost query.
2. **Filter early before joining**: Place partition filters in `WHERE` clauses instead of filtering after joining multi-million-row dimension tables.
3. **Use `APPROX_COUNT_DISTINCT`**: On multi-billion-row datasets, `APPROX_COUNT_DISTINCT()` is orders of magnitude faster and consumes a fraction of the slot memory compared to `COUNT(DISTINCT)`.

---

## Summary heuristics

1. Switch large analytical datasets with high compression ratios to **Physical Storage Billing** to cut storage costs.
2. Set `maximum_bytes_billed` on all automated BI dashboard service accounts to prevent single queries from scanning multi-terabyte datasets accidentally.
3. Monitor `INFORMATION_SCHEMA.JOBS_BY_PROJECT` weekly to identify un-clustered queries and train team members on partition pruning.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0035: End-to-End Pipeline Observability](0035-pipeline-observability-lineage.md) | [All Lessons (Index)](index.md) | *None (Course Complete)* |
