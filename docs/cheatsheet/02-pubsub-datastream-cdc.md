---
icon: lucide/radio
---

# Cloud Pub/Sub, Datastream, and CDC cheatsheet

Quick reference commands, message policies, and CDC operational patterns for Cloud Pub/Sub, Pub/Sub Lite, Datastream, and BigQuery Data Transfer Service.

---

## Real-time ingestion topology

``` mermaid
flowchart TD
    App["Application / IoT Streams"] --> Standard["Pub/Sub Standard (Global / Serverless)"]
    HighVol["Sustained High-Volume (>10 MB/s)"] --> Lite["Pub/Sub Lite (Pre-partitioned)"]
    OLTP["Operational DB (PostgreSQL / MySQL)"] --> Datastream["Datastream CDC (WAL / Binlog)"]

    Standard --> Sub1["Pull / Push / Direct BigQuery Subscription"]
    Lite --> Sub2["Dataflow / Kafka Shim Consumer"]
    Datastream --> BQCDC["BigQuery Change Tables"]
```

---

## Cloud Pub/Sub Standard CLI commands

### Creating topics, dead-letter topics, and subscriptions

```bash
# 1. Create main and DLQ topics
gcloud pubsub topics create orders-topic
gcloud pubsub topics create orders-dlq-topic

# 2. Create DLQ subscription
gcloud pubsub subscriptions create orders-dlq-sub --topic=orders-dlq-topic

# 3. Create main subscription with dead-letter and exponential backoff
gcloud pubsub subscriptions create orders-main-sub \
    --topic=orders-topic \
    --ack-deadline=60 \
    --min-retry-delay=10s \
    --max-retry-delay=600s \
    --dead-letter-topic=orders-dlq-topic \
    --max-delivery-attempts=5 \
    --enable-exactly-once-delivery
```

### Direct BigQuery and GCS subscriptions (zero-code ingestion)

```bash
# Stream directly into BigQuery without Dataflow
gcloud pubsub subscriptions create orders-bq-sub \
    --topic=orders-topic \
    --bigquery-table=my-project:raw_staging.orders \
    --use-table-schema \
    --write-metadata

# Stream directly into Cloud Storage as Avro/JSON
gcloud pubsub subscriptions create orders-gcs-sub \
    --topic=orders-topic \
    --cloud-storage-bucket=my-landing-bucket \
    --cloud-storage-file-prefix="raw/orders/" \
    --cloud-storage-max-duration=5m \
    --cloud-storage-max-bytes=100000000
```

---

## Cloud Pub/Sub Lite commands

```bash
# Create 4-partition regional Lite topic (2 MiB/s ingress per partition)
gcloud pubsub lite-topics create high-throughput-telemetry \
    --location=us-central1 \
    --partitions=4 \
    --per-partition-publish-capacity=2MiB \
    --per-partition-subscribe-capacity=4MiB \
    --per-partition-retention-period=7d

# Create subscription for Lite topic
gcloud pubsub lite-subscriptions create telemetry-sub \
    --location=us-central1 \
    --topic=high-throughput-telemetry \
    --delivery-requirement=deliver-after-stored
```

---

## Cloud Datastream and CDC SQL patterns

### Setting up Datastream stream with gcloud

```bash
# Create and start CDC stream from Postgres to BigQuery
gcloud datastream streams create pg-orders-cdc \
    --location=us-central1 \
    --source=projects/my-proj/locations/us-central1/connectionProfiles/pg-source-profile \
    --destination=projects/my-proj/locations/us-central1/connectionProfiles/bq-dest-profile \
    --display-name="PostgreSQL Orders CDC"
```

### Deduplicating CDC change log into current state view

```sql
CREATE OR REPLACE VIEW `my_project.analytics.v_orders_current` AS
WITH ranked_changes AS (
  SELECT
    order_id,
    customer_id,
    order_amount,
    status,
    _metadata_timestamp AS updated_at,
    _metadata_deleted,
    ROW_NUMBER() OVER (
      PARTITION BY order_id
      ORDER BY _metadata_timestamp DESC, _metadata_change_sequence_number DESC
    ) AS row_num
  FROM `my_project.raw_cdc.orders_changelog`
)
SELECT
  order_id,
  customer_id,
  order_amount,
  status,
  updated_at
FROM ranked_changes
WHERE row_num = 1
  AND _metadata_deleted IS FALSE;
```

---

## BigQuery Data Transfer Service (DTS) scheduled transfer

```bash
bq mk --transfer_config \
    --project_id=my-gcp-project \
    --data_source=google_cloud_storage \
    --display_name="Daily GCS Parquet Ingest" \
    --target_dataset=raw_staging \
    --params='{
      "data_path_template":"gs://my-bucket/drops/{run_time|%Y/%m/%d}/*.parquet",
      "destination_table_name_template":"daily_events",
      "file_data_type":"PARQUET",
      "write_disposition":"APPEND"
    }' \
    --schedule="every 24 hours"
```

---

| Previous Cheatsheet | All Cheatsheets | Next Cheatsheet |
| :--- | :---: | ---: |
| [01: Cloud Storage & Lakehouse](01-cloud-storage-lakehouse.md) | [Cheatsheets Index](index.md) | [03: BigQuery SQL & Optimization](03-bigquery-sql-optimization.md) |
