---
icon: lucide/sliders
---

# BigQuery slot management: On-Demand vs Editions

BigQuery compute pricing operates under two primary models: On-Demand (per-TB scanned) and BigQuery Editions (capacity-based slot reservations). Sizing and assigning slot reservations correctly controls costs and guarantees query SLA predictability across production pipelines and ad-hoc analysts.

---

## On-Demand vs Editions comparison

``` mermaid
flowchart TD
    subgraph OnDemand["On-Demand Pricing ($6.25 / TB Scanned)"]
        ODQuery["Query Scan (e.g., 2 TB)"] --> ODCost["Billed: $12.50"]
        ODSlots["Shared Multi-Tenant Slot Pool (Up to 2,000 slots per project)"]
    end

    subgraph Editions["BigQuery Editions (Slot Reservations)"]
        EdQuery["Queries scan unlimited TB"] --> Res["Dedicated Reservation (e.g. 100 Baseline + 300 Autoscale)"]
        Res --> EdCost["Billed: $ per slot-hour (Flat or Autoscaled)"]
    end

    OnDemand ~~~ Editions
```

| Edition tier | Target workloads | Key features |
| :--- | :--- | :--- |
| **Standard** | Ad-hoc analytics, dev environments | Slot autoscaling, multi-statement transactions |
| **Enterprise** | Production data platforms | Fine-grained security, BI Engine, continuous queries, dynamic slot sharing |
| **Enterprise Plus** | Regulated, mission-critical enterprise workloads | CMEK, FedRAMP/HIPAA compliance, multi-region disaster recovery |

---

## Slot allocation and reservation architecture

A BigQuery reservation defines a pool of slots. Multiple projects or folders are assigned to reservations with specific job types.

``` mermaid
flowchart TD
    subgraph ReservationPool["Enterprise Capacity Commitment (500 Slots)"]
        ProdRes["Prod ETL Reservation (300 Slots Baseline, Autoscale to 500)"]
        AdhocRes["Ad-hoc BI Reservation (100 Slots Baseline, Autoscale to 200)"]
    end

    subgraph Assignments["Reservation Assignments"]
        ETLJob["Composer / Dataform Pipelines"] -->|"Assigned to"| ProdRes
        Dashboards["Looker / Analysts"] -->|"Assigned to"| AdhocRes
    end

    ProdRes -->|"Idle Slots Shared Automatically"| AdhocRes
```

---

## Configuring reservations and assignments with gcloud

### 1. Create a reservation in Enterprise edition

```bash
# Create an Enterprise reservation with 100 baseline slots and max 400 slots autoscaling
gcloud bigquery reservations create prod-etl-reservation \
    --project=my-admin-project \
    --location=us-central1 \
    --edition=ENTERPRISE \
    --slots=100 \
    --autoscale-max-slots=400 \
    --ignore-idle-slots=false
```

Setting `--ignore-idle-slots=false` enables dynamic idle slot sharing: when the ETL reservation is idle during the day, ad-hoc BI queries can burst into those idle slots at zero additional cost.

### 2. Assign projects to the reservation

```bash
# Assign all queries from the production data engineering project to the reservation
gcloud bigquery reservations assignments create \
    --project=my-admin-project \
    --location=us-central1 \
    --reservation=prod-etl-reservation \
    --job-type=QUERY \
    --assignee-id=my-prod-data-project \
    --assignee-type=PROJECT
```

---

## Detecting slot starvation and concurrency bottlenecks

When total slot demand exceeds provisioned capacity, BigQuery queues queries until slots free up. Monitor slot contention using `INFORMATION_SCHEMA.RESERVATION_USAGE`:

```sql
SELECT
  reservation_name,
  period_start,
  AVG(slots_assigned) AS avg_slots_assigned,
  MAX(slots_assigned) AS peak_slots_assigned,
  AVG(autoscale_slots) AS avg_autoscale_slots,
  AVG(wait_ms) AS avg_query_wait_ms
FROM `region-us`.INFORMATION_SCHEMA.RESERVATION_USAGE
WHERE period_start > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 12 HOUR)
GROUP BY reservation_name, period_start
HAVING avg_query_wait_ms > 1000
ORDER BY period_start DESC;
```

---

## Cost optimization decision heuristics

1. **Use On-Demand** when monthly query scans are under 15 TB or when workloads are unpredictable with long periods of zero activity.
2. **Switch to Editions** when monthly query scan costs exceed $3,000, or when strict slot quotas are needed to prevent rogue `SELECT *` queries from generating large unexpected bills.
3. Enable dynamic idle slot sharing between production pipelines and BI reporting reservations to maximize hardware utilization across different peak hours.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0012: Materialized Views & BI Engine](0012-materialized-views-bi-engine.md) | [All Lessons (Index)](index.md) | [0014: Apache Beam Fundamentals](0014-apache-beam-fundamentals.md) |
