---
icon: lucide/bug
---

# Debugging BigQuery slot starvation, query queuing, and memory spilling

Diagnostic playbook for troubleshooting BigQuery query latency spikes, queries queued in `PENDING` status, slot contention between workloads, and `Resources exceeded during query execution` errors caused by disk spilling.

---

## Failure sequence diagram

``` mermaid
sequenceDiagram
    autonumber
    actor Analyst as Ad-hoc BI User
    actor Airflow as Production Airflow DAG
    participant Router as BigQuery Query Coordinator
    participant Reservation as Enterprise Slot Reservation (500 Slots)
    participant Dremel as Dremel Slot Workers

    Analyst->>Router: Submit Unfiltered Cross Join (Scans 50 TB)
    Router->>Reservation: Request all 500 Slots
    Reservation->>Dremel: Assign 500/500 Slots to Analyst Query
    Airflow->>Router: Submit Mission-Critical Daily Fact Merge
    Router->>Reservation: Request 100 Slots for Production Job
    Note over Reservation: No Available Slots (100% Starvation)
    Reservation-->>Airflow: Queue Job (State: PENDING, wait_ms: 120,000)
    Note over Dremel: Worker RAM full -> Spill intermediate shuffle to disk (10x slow)
```

---

## Symptoms and diagnostic signals

| Symptom | Diagnostic signal in Cloud Console | Root cause |
| :--- | :--- | :--- |
| **`Resources exceeded during query execution`** | Query fails after several minutes with memory error | Massive Cartesian product or sorting millions of unpartitioned rows in a single stage |
| **High `wait_ms` in `INFORMATION_SCHEMA`** | Queries remain in `PENDING` state for minutes before starting | Slot starvation: total concurrent slot demand exceeds reservation cap |
| **High shuffle bytes spilled to disk** | Query execution graph shows gigabytes spilled to disk | Intermediate stage data exceeded in-memory shuffle buffer RAM |
| **Slot contention between teams** | Production ETL pipelines miss SLA during business hours | Production and ad-hoc BI queries share the same reservation without concurrency bounds |

---

## Diagnostic SQL queries

### 1. Identifying queued queries and slot starvation

```sql
SELECT
  job_id,
  user_email,
  state,
  creation_time,
  TIMESTAMP_DIFF(start_time, creation_time, SECOND) AS queue_wait_seconds,
  total_slot_ms / NULLIF(TIMESTAMP_DIFF(end_time, start_time, MILLISECOND), 0) AS avg_slots_used,
  query
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 6 HOUR)
  AND job_type = 'QUERY'
  AND TIMESTAMP_DIFF(start_time, creation_time, SECOND) > 30
ORDER BY queue_wait_seconds DESC
LIMIT 10;
```

### 2. Finding queries spilling shuffle data to disk

```sql
SELECT
  project_id,
  job_id,
  user_email,
  total_slot_ms / (1000 * 60) AS slot_minutes,
  query
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
  AND error_result.reason = 'resourcesExceeded'
ORDER BY total_slot_ms DESC
LIMIT 10;
```

---

## Resolution playbook

### 1. Isolating workloads with separate slot reservations
Separate production automated pipelines from interactive BI users by creating distinct reservation pools:

```bash
# 1. Create dedicated production reservation with guaranteed baseline slots
gcloud bigquery reservations create prod-pipeline-reservation \
    --project=my-admin-project \
    --location=us-central1 \
    --edition=ENTERPRISE \
    --slots=300 \
    --autoscale-max-slots=600 \
    --ignore-idle-slots=false

# 2. Assign production pipeline project strictly to this reservation
gcloud bigquery reservations assignments create \
    --project=my-admin-project \
    --location=us-central1 \
    --reservation=prod-pipeline-reservation \
    --job-type=QUERY \
    --assignee-id=my-prod-etl-project \
    --assignee-type=PROJECT
```

### 2. Eliminating Cartesian join spills in SQL
Replace accidental Cartesian joins or full cross-joins with filtered equality keys:

```sql
-- Anti-pattern causing memory spill
SELECT *
FROM `my_project.analytics.large_orders` a
JOIN `my_project.analytics.large_events` b
  ON a.region = b.region; -- Very low cardinality key creates massive join explosion

-- Fixed: Join on specific high-cardinality foreign key and partition filter
SELECT *
FROM `my_project.analytics.large_orders` a
JOIN `my_project.analytics.large_events` b
  ON a.order_id = b.order_id
  AND DATE(a.event_timestamp) = '2026-08-20'
  AND DATE(b.event_timestamp) = '2026-08-20';
```

### 3. Enforcing query guardrails
Set `maximum_bytes_billed` on client configurations or configure project-level custom quotas in the Google Cloud Console to reject queries scanning multi-terabyte datasets without filters.

---

## Prevention checklist

- [ ] Set `require_partition_filter = true` on all tables larger than 100 GB.
- [ ] Separate ETL service accounts and Looker/Tableau dashboards into distinct reservation assignments.
- [ ] Avoid `ORDER BY` in subqueries; sort only on final output rows.

---

| Previous Guide | All Debugging Guides | Next Guide |
| :--- | :---: | ---: |
| [01: Dataflow Bottlenecks & OOM](01-dataflow-bottlenecks-skew-oom.md) | [Debugging Index](index.md) | [03: Pub/Sub Unacked Messages](03-pubsub-unacked-messages-throttling.md) |
