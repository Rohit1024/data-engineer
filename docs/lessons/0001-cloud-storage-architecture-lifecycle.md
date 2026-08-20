---
icon: lucide/hard-drive
---

# Cloud Storage architecture, storage classes, and lifecycle management

Google Cloud Storage (GCS) is an object store backed by Google's global Colossus file system. Unlike POSIX file systems with hierarchical inode trees, GCS uses a flat namespace where slashes in object names are just string prefixes. Understanding this flat namespace and how Colossus distributes shards across storage clusters is essential when designing high-throughput data pipelines.

---

## Internal architecture and consistency

GCS provides strong global consistency for all read-after-write, read-after-update, and read-after-delete operations. When you upload an object, the request hits a Google Front End (GFE) proxy, routes to the GCS metadata service (Spanner-backed), and chunks the payload across Colossus disk blocks with Reed-Solomon erasure coding.

``` mermaid
flowchart TD
    Client["Client / Pipeline Writer"] --> GFE["Google Front End (GFE)"]
    GFE --> Meta["Metadata Layer (Spanner)"]
    GFE --> DataLayer["Colossus Storage Engine"]
    DataLayer --> Chunk1["Chunk 1 (Erasure Coded)"]
    DataLayer --> Chunk2["Chunk 2 (Erasure Coded)"]
    DataLayer --> Chunk3["Chunk 3 (Erasure Coded)"]
```

Because GCS is an object store:
- Renaming a directory requires renaming every object with that prefix sequentially. A rename of a 10 TB folder containing 50,000 files is an O(N) operation that takes minutes and costs metadata operations.
- Appending bytes to an existing object is not supported. You must upload a new object or compose objects using the compose API.

---

## Storage classes and pricing dynamics

GCS offers four storage classes. All four share identical throughput, latency (first-byte latency under 100ms), and API surface. The differences lie in cost, minimum storage duration, and data retrieval fees.

| Storage class | Minimum storage duration | Retrieval fees | Primary data engineering use case |
| :--- | :--- | :--- | :--- |
| **Standard** | None | Free | Hot landing zones, active Spark/Dataflow working directories |
| **Nearline** | 30 days | $0.01 per GB | Monthly reporting raw extracts, 30-day raw event staging |
| **Coldline** | 90 days | $0.02 per GB | Quarterly audit logs, historical snapshots accessed once per quarter |
| **Archive** | 365 days | $0.05 per GB | Regulatory cold storage, compliance archives |

!!! warning "Early deletion penalties"
    If you overwrite or delete an object in Coldline after 15 days, GCP charges you for the remaining 75 days at the Coldline rate. Do not use Nearline or Coldline for transient pipeline landing zones that get wiped daily.

---

## Object lifecycle management

Object Lifecycle Management runs asynchronous evaluation sweeps once per day. You define rules in a JSON configuration and apply them to the bucket.

### Lifecycle rule definition

Save this rule as `lifecycle.json`:

```json
{
  "rule": [
    {
      "action": {
        "type": "SetStorageClass",
        "storageClass": "NEARLINE"
      },
      "condition": {
        "age": 30,
        "matchesPrefix": ["raw/events/"]
      }
    },
    {
      "action": {
        "type": "SetStorageClass",
        "storageClass": "COLDLINE"
      },
      "condition": {
        "age": 90,
        "matchesPrefix": ["raw/events/"]
      }
    },
    {
      "action": {
        "type": "Delete"
      },
      "condition": {
        "age": 365,
        "matchesPrefix": ["raw/events/"]
      }
    }
  ]
}
```

Apply the policy with `gcloud`:

```bash
gcloud storage buckets update gs://my-lakehouse-bucket \
    --lifecycle-file=lifecycle.json
```

---

## High-throughput write patterns and naming

GCS automatically splits index ranges as request volume increases. Each partition can handle approximately 1,000 write requests per second and 5,000 read requests per second before autoscaling.

If your ingestion pipeline writes thousands of objects per second, avoid sequential timestamp prefixes like `gs://bucket/2026-08-20/0001.parquet`. Sequential naming routes all initial traffic to a single backend shard.

``` mermaid
flowchart TD
    subgraph AntiPattern["Anti-Pattern: Sequential Timestamps"]
        Seq1["ts_1000.parquet"] --> ShardA["Single GCS Shard (Throttled at 1,000 req/s)"]
        Seq2["ts_1001.parquet"] --> ShardA
        Seq3["ts_1002.parquet"] --> ShardA
    end

    subgraph BestPractice["Best Practice: Hash or Distributed Prefix"]
        Hash1["a8f1_ts_1000.parquet"] --> Shard1["Shard 1"]
        Hash2["3b0c_ts_1001.parquet"] --> Shard2["Shard 2"]
        Hash3["f9e2_ts_1002.parquet"] --> Shard3["Shard 3"]
    end

    AntiPattern ~~~ BestPractice
```

---

## Hands-on exercise: Bucket configuration and verification

Create a dual-region bucket with uniform bucket-level access, object versioning, and an automated lifecycle policy:

```bash
# 1. Create a dual-region bucket for high availability in europe-west1 and europe-west4
gcloud storage buckets create gs://de-landing-zone-prod-01 \
    --location=EUROPE-WEST1 \
    --placement=europe-west1,europe-west4 \
    --default-storage-class=STANDARD \
    --uniform-bucket-level-access

# 2. Enable object versioning to protect against accidental deletes
gcloud storage buckets update gs://de-landing-zone-prod-01 \
    --versioning

# 3. Verify bucket configuration
gcloud storage buckets describe gs://de-landing-zone-prod-01 --format="yaml(name, location, storageClass, versioning)"
```

---

## Key takeaways and operational heuristics

1. GCS offers strong global read-after-write consistency, but directory renames are slow client-side batch copy-and-delete operations.
2. Match storage class minimum durations to pipeline retention periods. Standard is the right default for any data modified within 30 days.
3. For streaming pipelines writing more than 1,000 files per second, prepend hash prefixes or distribute keys to avoid hotspotting storage index ranges.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| *None (First Lesson)* | [All Lessons (Index)](index.md) | [0002: Bigtable vs Spanner vs Cloud SQL](0002-bigtable-spanner-cloudsql-selection.md) |
