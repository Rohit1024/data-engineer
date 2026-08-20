---
icon: lucide/upload-cloud
---

# BigQuery Storage Write API: Streaming ingestion and exactly-once semantics

The BigQuery Storage Write API replaces the legacy `tabledata.insertAll` streaming API. It streams records directly into BigQuery storage via bidirectional gRPC connections using Protocol Buffers (Protobuf), providing higher throughput, lower cost (50% cheaper than legacy streaming), and exactly-once delivery guarantees.

---

## Architectural evolution: Legacy streaming vs Storage Write API

``` mermaid
flowchart TD
    subgraph LegacyStreaming["Legacy tabledata.insertAll (Deprecated Pattern)"]
        ClientOld["Client"] -->|"JSON over HTTP POST"| APIOld["REST API Gateway"]
        APIOld -->|"JSON Parsing Overhead"| BufferOld["Streaming Buffer"]
    end

    subgraph StorageWriteAPI["Storage Write API (gRPC + Protobuf)"]
        ClientNew["Client Streamer"] -->|"Binary Protobuf over gRPC"| BQWrite["Storage Write Endpoint"]
        BQWrite -->|"Direct Commit / Append"| Capacitor["Capacitor Storage Blocks"]
    end

    LegacyStreaming ~~~ StorageWriteAPI
```

Key advantages of the Storage Write API:
- **Binary serialization**: Protocol Buffers eliminate JSON encoding and decoding CPU bottlenecks.
- **Stream connection reuse**: A single gRPC connection streams millions of rows continuously.
- **Atomic multi-stream commits**: Transactions can write to multiple streams in parallel and commit atomically in a single RPC.

---

## Stream modes and semantics

| Stream mode | Visibility | Delivery guarantee | Best use case |
| :--- | :--- | :--- | :--- |
| **Committed stream** | Immediate | Exactly-once via explicit stream offsets | Real-time dashboards, low-latency log streams |
| **Pending stream** | Hidden until commit | Exactly-once across distributed workers | Batch ETL jobs, Dataflow streaming pipelines |
| **Buffered stream** | Intermediate flush | Exactly-once via manual flush tokens | Micro-batch applications |
| **Default stream** | Immediate | At-least-once (no stream offsets) | High-volume fire-and-forget ingestion |

---

## Stream offset management and exactly-once guarantees

In **Committed** and **Pending** modes, each write request must include a monotonically increasing 0-indexed stream offset:

``` mermaid
flowchart TD
    Client["Writer Worker"] -->|"Append Rows (Offset: 0..99)"| Stream["Committed Stream"]
    Stream -->|"Ack: Next expected offset = 100"| Client
    Client -->|"Network Failure / Retry (Offset: 0..99)"| Stream
    Stream -->|"Duplicate detected: Rejected (ALREADY_EXISTS)"| Client
    Client -->|"Append Rows (Offset: 100..199)"| Stream
    Stream -->|"Ack: Next expected offset = 200"| Client
```

If a network timeout occurs, re-sending the batch with the identical offset prevents duplicate records from being written.

---

## Streaming rows in Python using default stream

The default stream provides immediate write availability without manually opening and closing stream objects:

```python
from google.cloud.bigquery_storage_v1 import BigQueryWriteClient, types
from google.protobuf import descriptor_pb2

write_client = BigQueryWriteClient()
parent_table = "projects/my-gcp-project/datasets/raw_staging/tables/telemetry"

# Initialize default write stream path
write_stream = f"{parent_table}/streams/_default"

# Define row payload serialized into binary protobuf format
# (In production, generate classes from your .proto schema)
proto_rows = types.ProtoRows()
# Append binary serialized protobuf instances to proto_rows.serialized_rows

request = types.AppendRowsRequest(
    write_stream=write_stream,
    proto_rows=types.AppendRowsRequest.ProtoData(
        rows=proto_rows
    )
)

# Stream requests through gRPC
stream = write_client.append_rows(iter([request]))
for response in stream:
    if response.error.code != 0:
        print(f"Write error: {response.error.message}")
    else:
        print("Batch appended successfully.")
```

---

## Batch atomic commits with pending streams

For multi-worker pipelines (e.g. Spark or Dataflow workers writing distributed shards):
1. The driver creates a parent session with `PENDING` mode.
2. Each worker writes its partition to a dedicated child stream.
3. Once all workers finish successfully, the driver executes `batch_commit_write_streams`. All records become visible to queries in a single millisecond transaction. If any worker fails, no records commit.

```bash
# Verify write metrics on target table
bq show --format=prettyjson my-gcp-project:raw_staging.telemetry
```

---

## Summary heuristics

1. Use the **Default stream** for simplicity when at-least-once delivery is acceptable and downstream views handle deduplication.
2. Use **Pending streams** when replacing batch file loads, ensuring all worker writes commit atomically or abort cleanly.
3. Always migrate from legacy `insertAll` to the Storage Write API to cut streaming ingestion costs in half.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0010: Partitioning, Clustering & Indexes](0010-partitioning-clustering-search-indexes.md) | [All Lessons (Index)](index.md) | [0012: Materialized Views & BI Engine](0012-materialized-views-bi-engine.md) |
