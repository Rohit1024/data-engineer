---
icon: lucide/refresh-cw
---

# Change Data Capture (CDC) with Datastream and BigQuery

Change Data Capture (CDC) extracts row-level changes (inserts, updates, deletes) from operational databases in real time without querying source tables. Google Cloud Datastream is a serverless CDC service that reads database write-ahead logs and streams changes directly into BigQuery or Cloud Storage.

---

## CDC mechanics and log extraction

Datastream connects to source database replication streams rather than polling queries:
- **PostgreSQL**: Logical decoding plugins (`pgoutput` or `wal2json`) via replication slots.
- **MySQL**: Binary log (`binlog`) with `ROW` format.
- **Oracle**: LogMiner or Oracle GoldenGate extracts.

``` mermaid
flowchart TD
    DB["Source PostgreSQL / Cloud SQL (WAL / Logical Slot)"] --> Datastream["Datastream (Serverless Replication Engine)"]
    Datastream --> BQCDC["BigQuery Direct Ingestion (Storage Write API)"]
    BQCDC --> ChangeTable["Change Table (Staging Append Log)"]
    ChangeTable --> BQEngine["BigQuery Continuous Merge Engine"]
    BQEngine --> TargetTable["Target Replicated Table (Up-to-Date State)"]
```

---

## Datastream to BigQuery replication modes

When replicating to BigQuery, Datastream supports two modes:

### 1. Direct BigQuery integration (Continuous SQL Merge)
Datastream streams changes into an internal change table, and BigQuery merges rows into the replica table in near real time (sub-minute latency). No Dataflow pipeline is required.

### 2. GCS intermediate landing (JSON/Avro)
Datastream writes change files to GCS. You trigger custom Dataflow, Spark, or Dataform ELT jobs to apply transformations before loading into final tables.

---

## Metadata columns in BigQuery change tables

When Datastream writes changes, it appends CDC metadata columns to track change order and operations:

| Metadata column | Type | Purpose |
| :--- | :--- | :--- |
| `_metadata_change_type` | `STRING` | Operation: `INSERT`, `UPDATE-INSERT`, `DELETE` |
| `_metadata_change_sequence_number` | `STRING` | Monotonically increasing Log Sequence Number (LSN) |
| `_metadata_timestamp` | `TIMESTAMP` | Time transaction committed on source database |
| `_metadata_deleted` | `BOOLEAN` | `TRUE` if the change represents a deleted row |

---

## Materializing the latest state with SQL

If using GCS landing or raw change tables, create a current-state view over the change log:

```sql
CREATE OR REPLACE VIEW `my_project.analytics_silver.v_customers_current` AS
WITH ranked_changes AS (
  SELECT
    customer_id,
    email,
    plan_tier,
    account_balance,
    _metadata_timestamp AS last_updated_at,
    _metadata_deleted,
    ROW_NUMBER() OVER (
      PARTITION BY customer_id
      ORDER BY _metadata_timestamp DESC, _metadata_change_sequence_number DESC
    ) AS row_num
  FROM `my_project.raw_cdc.customers_changelog`
)
SELECT
  customer_id,
  email,
  plan_tier,
  account_balance,
  last_updated_at
FROM ranked_changes
WHERE row_num = 1
  AND _metadata_deleted IS FALSE;
```

---

## Hands-on configuration: Datastream connection profile

Configure a PostgreSQL connection profile using `gcloud`:

```bash
# 1. Create a private connection profile for source PostgreSQL
gcloud datastream connection-profiles create pg-source-profile \
    --location=us-central1 \
    --type=postgresql \
    --postgresql-host="10.0.0.15" \
    --postgresql-port=5432 \
    --postgresql-username="datastream_cdc_user" \
    --postgresql-password="SafePasswordHere" \
    --postgresql-database="core_app_db"

# 2. Create BigQuery destination profile
gcloud datastream connection-profiles create bq-dest-profile \
    --location=us-central1 \
    --type=bigquery \
    --bigquery-dataset="raw_cdc"

# 3. Create and start the CDC stream
gcloud datastream streams create pg-to-bq-stream \
    --location=us-central1 \
    --source=pg-source-profile \
    --destination=bq-dest-profile \
    --display-name="Postgres Orders CDC Stream"
```

---

## Operational pitfalls and troubleshooting

1. **Unconsumed replication slots**: If Datastream pauses or errors, the PostgreSQL WAL replication slot retains log segments on disk until the database runs out of disk storage. Monitor `pg_replication_slots` disk consumption in Cloud SQL.
2. **DDL changes**: Adding a column to the source table is automatically propagated by Datastream to BigQuery. Renaming or dropping columns requires updating downstream views to prevent query breaks.

---

## Summary heuristics

1. Use Datastream with direct BigQuery integration for zero-code, sub-minute replication of OLTP databases into analytics.
2. Filter deleted rows (`_metadata_deleted IS FALSE`) when querying CDC changelog tables to prevent ghost records.
3. Monitor source database disk space and replication lag alerts when CDC streams are active.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0006: Pub/Sub Lite vs Standard](0006-pubsub-lite-vs-standard.md) | [All Lessons (Index)](index.md) | [0008: DTS & GCS Change Notifications](0008-bigquery-data-transfer-service-gcs-notifications.md) |
