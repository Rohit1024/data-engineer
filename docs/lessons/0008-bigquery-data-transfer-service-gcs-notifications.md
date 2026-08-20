---
icon: lucide/arrow-left-right
---

# BigQuery Data Transfer Service and GCS notifications

Automating scheduled and event-driven data ingestion into BigQuery can be achieved without managing custom servers. BigQuery Data Transfer Service (DTS) provides managed scheduled transfers from SaaS platforms, cloud object stores, and data warehouses, while Cloud Storage Object Change Notifications enable event-driven, real-time file ingestion.

---

## BigQuery Data Transfer Service (DTS) architecture

DTS runs serverless managed batch import jobs into target BigQuery datasets on a recurring schedule or on-demand.

``` mermaid
flowchart TD
    subgraph Sources["Supported DTS Sources"]
        S3["AWS S3 / Azure Blob"]
        SaaS["Google Ads / Salesforce / YouTube"]
        DW["Teradata / Amazon Redshift"]
        GCS["Cloud Storage Batch Files"]
    end

    Sources --> DTSEngine["BigQuery Data Transfer Service"]
    DTSEngine --> Stage["Staging Decryption & Validation"]
    Stage --> BQTarget["BigQuery Destination Dataset"]
```

---

## Configuring a scheduled transfer from Cloud Storage

Use the `bq` CLI to configure a daily transfer that loads partition-formatted Parquet files:

```bash
bq mk --transfer_config \
    --project_id=my-gcp-project \
    --data_source=google_cloud_storage \
    --display_name="Daily Customer Orders Ingest" \
    --target_dataset=raw_staging \
    --params='{
      "data_path_template":"gs://my-inbound-bucket/orders/{run_time|%Y/%m/%d}/*.parquet",
      "destination_table_name_template":"customer_orders",
      "file_data_type":"PARQUET",
      "write_disposition":"APPEND"
    }' \
    --schedule="every 24 hours"
```

DTS replaces `{run_time|%Y/%m/%d}` with the execution timestamp, guaranteeing that each scheduled run loads only the files intended for that time window.

---

## Event-driven ingestion with GCS notifications and Eventarc

Scheduled batch runs introduce latency. For immediate loading when a file lands in GCS, wire GCS bucket notifications to Pub/Sub or Eventarc, triggering a Cloud Function or Cloud Run service.

``` mermaid
flowchart TD
    GCSBucket["GCS Landing Bucket (File Upload)"] --> Notification["GCS Pub/Sub Notification (OBJECT_FINALIZE)"]
    Notification --> Topic["gcs-file-events Topic"]
    Topic --> Function["Cloud Function / Cloud Run Loader"]
    Function --> BQLoad["BigQuery Load Job (api.tables.insert / bq load)"]
    BQLoad --> BQTable["Target Table"]
```

### Setting up Pub/Sub notifications on a bucket

```bash
# 1. Create event topic
gcloud pubsub topics create gcs-file-events

# 2. Add notification configuration to bucket
gcloud storage buckets notifications create gs://my-inbound-bucket \
    --topic=gcs-file-events \
    --event-types=OBJECT_FINALIZE \
    --object-name-prefix="incoming/orders/"
```

---

## Event handler in Python (Cloud Function v2)

This function receives the GCS finalize event and triggers a serverless BigQuery load job:

```python
from google.cloud import bigquery
import functions_framework
import json
import base64

bq_client = bigquery.Client()

@functions_framework.cloud_event
def process_gcs_event(cloud_event):
    pubsub_message = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
    payload = json.loads(pubsub_message)

    bucket_name = payload["bucket"]
    object_name = payload["name"]
    source_uri = f"gs://{bucket_name}/{object_name}"

    if not object_name.endswith(".parquet"):
        print(f"Skipping non-parquet file: {object_name}")
        return

    table_id = "my-gcp-project.raw_staging.customer_orders"
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND
    )

    load_job = bq_client.load_table_from_uri(
        source_uri,
        table_id,
        job_config=job_config
    )
    print(f"Started BigQuery load job {load_job.job_id} for {source_uri}")
```

BigQuery batch load jobs are **free** on shared slots; you do not consume reservation slots or pay on-demand analysis fees for loading Parquet, CSV, or Avro files from GCS.

---

## Trade-offs: DTS vs Event-driven loading

| Factor | BigQuery DTS | Event-Driven (GCS + Eventarc + Functions) |
| :--- | :--- | :--- |
| **Ingestion latency** | Scheduled (minimum 15 minutes) | Near real-time (seconds) |
| **Infrastructure overhead** | Zero (fully managed configuration) | Minimal (Cloud Function / Cloud Run maintenance) |
| **Transformations** | None (direct load) | Lightweight preprocessing possible before loading |
| **Custom deduplication** | Manual downstream SQL | Built-in logic inside event handler |

---

## Summary heuristics

1. Use BigQuery DTS when loading scheduled extracts from standard external platforms (AWS S3, Google Ads, Salesforce, Redshift).
2. Use GCS notifications with Eventarc and Cloud Functions when latency must be under 30 seconds for incoming files.
3. BigQuery batch load jobs (`load_table_from_uri`) are free of compute charges, making batch loads more cost-effective than continuous streaming writes when micro-second latency is not required.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0007: CDC with Datastream & BigQuery](0007-change-data-capture-datastream-bigquery.md) | [All Lessons (Index)](index.md) | [0009: BigQuery Internal Architecture](0009-bigquery-internal-architecture.md) |
