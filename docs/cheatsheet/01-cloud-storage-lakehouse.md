---
icon: lucide/hard-drive
---

# Cloud Storage and lakehouse architecture cheatsheet

Quick reference commands, configuration patterns, and SQL snippets for Google Cloud Storage (GCS), BigLake, and open table formats.

---

## Architecture and lifecycle flow

``` mermaid
flowchart TD
    Raw["Landing: gs://lake-bronze/ (Standard Class)"] -->|"Age > 30 Days"| Nearline["Nearline Class ($0.01/GB Retrieval)"]
    Nearline -->|"Age > 90 Days"| Coldline["Coldline Class ($0.02/GB Retrieval)"]
    Coldline -->|"Age > 365 Days"| Archive["Archive Class / Automated Deletion"]
```

---

## Essential `gcloud storage` commands

### Bucket provisioning and management

```bash
# Create dual-region bucket with uniform bucket-level access
gcloud storage buckets create gs://my-lakehouse-bucket \
    --location=EUROPE-WEST1 \
    --placement=europe-west1,europe-west4 \
    --default-storage-class=STANDARD \
    --uniform-bucket-level-access

# Enable object versioning for disaster recovery
gcloud storage buckets update gs://my-lakehouse-bucket --versioning

# Apply lifecycle policy file
gcloud storage buckets update gs://my-lakehouse-bucket --lifecycle-file=lifecycle.json

# Check bucket metadata, retention, and storage class
gcloud storage buckets describe gs://my-lakehouse-bucket --format="yaml(name, location, storageClass, versioning)"
```

### High-throughput sync and transfer

```bash
# Multi-threaded parallel rsync to GCS
gcloud storage rsync ./local_data gs://my-lakehouse-bucket/bronze/ \
    --recursive \
    --delete-unmatched-destination-objects

# Copy large files with parallel composite upload
gcloud storage cp large_file.parquet gs://my-lakehouse-bucket/raw/ \
    --threads=8
```

---

## Lifecycle configuration schema (`lifecycle.json`)

```json
{
  "rule": [
    {
      "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
      "condition": {"age": 30, "matchesPrefix": ["raw/events/"]}
    },
    {
      "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
      "condition": {"age": 90, "matchesPrefix": ["raw/events/"]}
    },
    {
      "action": {"type": "Delete"},
      "condition": {"age": 365, "matchesPrefix": ["raw/events/"]}
    }
  ]
}
```

---

## BigLake and Apache Iceberg DDL snippets

### 1. Create Cloud Resource connection

```bash
bq mk --connection \
    --connection_type=CLOUD_RESOURCE \
    --location=US \
    --project_id=my-gcp-project \
    biglake-conn
```

### 2. BigLake Apache Iceberg table definition

```sql
CREATE EXTERNAL TABLE `my_gcp_project.lakehouse_dw.customer_iceberg`
WITH CONNECTION `us.biglake-conn`
OPTIONS (
  format = 'ICEBERG',
  uris = ['gs://my-lakehouse-bucket/tables/customer/metadata/v1.metadata.json']
);
```

### 3. BigLake Parquet table with Hive partition autodetection

```sql
CREATE EXTERNAL TABLE `my_gcp_project.lakehouse_dw.orders_partitioned`
WITH CONNECTION `us.biglake-conn`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://my-lakehouse-bucket/orders/*'],
  hive_partition_uri_prefix = 'gs://my-lakehouse-bucket/orders/',
  require_hive_partition_filter = true
);
```

---

## Operational rules of thumb

1. Always enforce `--uniform-bucket-level-access` to disable legacy object ACLs and unify access control through IAM.
2. Require partition filters (`require_hive_partition_filter = true`) on external tables to eliminate unpruned full bucket scans.
3. Keep file sizes between 128 MB and 512 MB in Parquet format to optimize read throughput across BigQuery, Spark, and Dataflow.

---

| Previous Cheatsheet | All Cheatsheets | Next Cheatsheet |
| :--- | :---: | ---: |
| *None (First Cheatsheet)* | [Cheatsheets Index](index.md) | [02: Pub/Sub & Datastream](02-pubsub-datastream-cdc.md) |
