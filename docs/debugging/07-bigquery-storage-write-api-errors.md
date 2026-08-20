---
icon: lucide/bug
---

# Debugging BigQuery Storage Write API connection failures and rate limits

Diagnostic playbook for troubleshooting BigQuery Storage Write API gRPC errors, quota throttling (`RESOURCE_EXHAUSTED`), stream offset mismatches (`INVALID_ARGUMENT`), and schema drift issues.

---

## Failure sequence diagram

``` mermaid
sequenceDiagram
    autonumber
    actor Writer as Ingestion Service Worker
    participant API as BigQuery Storage Write API
    participant Storage as Capacitor Storage Block

    Writer->>API: AppendRowsRequest (Stream: stream_01, Offset: 100)
    API->>Storage: Commit rows 100-199
    Storage-->>API: Success
    API-->>Writer: Ack: Next expected offset = 200
    Note over Writer: Worker thread restarted / Network glitch
    Writer->>API: AppendRowsRequest (Stream: stream_01, Offset: 150)
    API--xWriter: 400 INVALID_ARGUMENT: Stream offset mismatch (Expected 200, got 150)
    Note over Writer: Ingestion halted to prevent silent data corruption
```

---

## Symptoms and diagnostic signals

| Symptom | Error code / Message | Root cause |
| :--- | :--- | :--- |
| **Offset mismatch** | `INVALID_ARGUMENT: Stream offset mismatch. Expected: X, got: Y` | Attempted to write records out of sequential order on a `COMMITTED` or `PENDING` stream |
| **Throughput exceeded** | `RESOURCE_EXHAUSTED: Exceeded streaming throughput limit` | Ingestion throughput exceeded regional quota (default 3 GB/s per project) |
| **Stream count exceeded** | `RESOURCE_EXHAUSTED: Too many concurrent streams opened` | Application opens a new stream object per batch rather than reusing long-lived streams |
| **Schema validation error** | `INVALID_ARGUMENT: Schema mismatch on column 'field_name'` | The Protocol Buffer descriptor structure does not match the BigQuery destination table schema |

---

## Diagnostic commands

### 1. Checking Storage Write API quotas in Cloud Console

```bash
# Check current Storage Write API regional usage and limits
gcloud services quotas list \
    --service=bigquerystorage.googleapis.com \
    --consumer=projects/my-gcp-project \
    --format="table(metric, displayName, limit)"
```

### 2. Inspecting table streaming errors

```bash
bq show --format=prettyjson my-gcp-project:raw_staging.telemetry
```

---

## Resolution playbook

### 1. Reusing long-lived streams and connection pools
Do not instantiate a new `WriteStream` object for every micro-batch. Open a persistent gRPC bidirectional connection and keep it open across batches:

```python
from google.cloud.bigquery_storage_v1 import BigQueryWriteClient, types

client = BigQueryWriteClient()
parent_table = "projects/my-project/datasets/staging/tables/events"

# Use the default stream for automatic offset handling and connection multiplexing
default_stream_path = f"{parent_table}/streams/_default"
```

### 2. Handling offset mismatches gracefully in COMMITTED mode
When writing to a named `COMMITTED` stream, track the next expected offset returned in the gRPC response headers:

```python
def append_batch_with_offset(write_client, stream_path, proto_rows, current_offset):
    request = types.AppendRowsRequest(
        write_stream=stream_path,
        offset=current_offset,
        proto_rows=types.AppendRowsRequest.ProtoData(rows=proto_rows)
    )

    responses = write_client.append_rows(iter([request]))
    for response in responses:
        if response.error.code != 0:
            if "offset mismatch" in response.error.message.lower():
                # Re-fetch next valid offset from BigQuery or rollback transaction
                print(f"Offset mismatch! Expected: {response.append_result.offset}")
            raise Exception(response.error.message)
        return response.append_result.offset
```

### 3. Resolving schema drift
If the destination BigQuery table adds a new column, update the Protobuf definition and regenerate the `.proto` compiled bindings:

```bash
protoc --python_out=. schema.proto
```

---

## Prevention checklist

- [ ] Use `_default` stream when at-least-once delivery is acceptable to eliminate manual offset bookkeeping.
- [ ] Implement exponential backoff when receiving `RESOURCE_EXHAUSTED` (HTTP 429).
- [ ] Keep gRPC stream objects open across requests rather than opening and closing them per row.

---

| Previous Guide | All Debugging Guides | Next Guide |
| :--- | :---: | ---: |
| [06: Dataform & dbt Cyclic Dependencies](06-dataform-dbt-cyclic-dependencies-assertions.md) | [Debugging Index](index.md) | [08: IAM, Policy Tags & KMS Permissions](08-iam-policy-tags-kms-permissions.md) |
