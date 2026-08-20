---
icon: lucide/bug
---

# Debugging Dataflow bottlenecks, key skew, and OOM failures

Diagnostic playbook for troubleshooting Cloud Dataflow pipeline worker crashes, hot key skew bottlenecks, rising watermark lag, and Out-Of-Memory (`Exit code 137`) errors.

---

## Failure sequence diagram

``` mermaid
sequenceDiagram
    autonumber
    actor Source as Cloud Pub/Sub / GCS
    participant WorkerSkew as Worker 1 (Hot Key)
    participant WorkerNormal as Worker 2 & 3 (Normal Keys)
    participant Engine as Dataflow Streaming Engine
    participant Driver as Dataflow Coordinator

    Source->>WorkerSkew: Stream 1,000,000 events (Key: 'VENDOR_NULL')
    Source->>WorkerNormal: Stream 100 events (Key: 'VENDOR_102')
    WorkerNormal->>Engine: Process and commit in 200ms (Healthy)
    Note over WorkerSkew: Buffers 5 GB into JVM Heap (GroupByKey)
    WorkerSkew->>WorkerSkew: GC thrashing (CPU 100%, 0 elements processed)
    WorkerSkew--xDriver: OOM Killed (SIGKILL / Exit Code 137)
    Driver->>Driver: Reschedule bundle on new worker
    Note over Driver: Watermark lag climbs from 5s to 45m
```

---

## Symptoms and diagnostic signals

| Symptom | Diagnostic signal in Cloud Console | Root cause |
| :--- | :--- | :--- |
| **Worker OOM crashes** | `Worker process exited with exit code 137` | Unbounded state growth in DoFn, loading large side inputs into memory, or massive key groups |
| **Rising watermark lag** | Watermark lag climbs steadily without plateauing | A single lagging worker bundle prevents the global watermark from advancing |
| **Straggler tasks** | 1 worker at 100% CPU while 19 workers sit at 5% | Hot key skew during `GroupByKey` or `CombinePerKey` |
| **Stuck pipeline after fan-out** | Low overall throughput despite high CPU on 1 VM | Unwanted stage fusion combining a large fan-out step with downstream processing |

---

## Diagnostic commands and log queries

### Querying worker crash logs in Cloud Logging

```bash
gcloud logging read '
  resource.type="dataflow_step"
  severity>=ERROR
  textPayload=~"Exit code 137|OutOfMemoryError|Container killed"
' --limit=20 --format="table(timestamp, textPayload)"
```

### Inspecting hot key warnings

Dataflow automatically logs hot key warnings when a single key processes for more than 20 seconds:

```bash
gcloud logging read '
  resource.type="dataflow_step"
  jsonPayload.message=~"A hot key was detected"
' --limit=10 --format="table(timestamp, jsonPayload.message)"
```

---

## Resolution playbook

### 1. Breaking unwanted stage fusion
If Dataflow fuses an I/O read directly into a high-cardinality expansion step, force stage splitting by inserting a `Reshuffle`:

```python
import apache_beam as beam

(
    p
    | "ReadSource" >> beam.io.ReadFromPubSub(...)
    | "UnpackBatch" >> beam.ParDo(UnpackBatchDoFn())
    | "BreakFusion" >> beam.Reshuffle()  # Forces distributed repartitioning across workers
    | "HeavyTransform" >> beam.ParDo(ProcessItemDoFn())
)
```

### 2. Mitigating hot key skew with salting
If a `GroupByKey` receives millions of elements with the same key (e.g., null values), prepend random salt digits:

```python
import random

def salt_key(element):
    key, value = element
    # Add random salt suffix 0-9 to hot key
    return (f"{key}_{random.randint(0, 9)}", value)

def unsalt_key(element):
    salted_key, value = element
    original_key = salted_key.rsplit("_", 1)[0]
    return (original_key, value)

(
    keyed_pcol
    | "SaltKeys" >> beam.Map(salt_key)
    | "PartialCombine" >> beam.CombinePerKey(sum)
    | "UnsaltKeys" >> beam.Map(unsalt_key)
    | "FinalCombine" >> beam.CombinePerKey(sum)
)
```

### 3. Upgrading worker memory specifications
If the pipeline legitimately requires large in-memory processing buffers, override the default worker machine type:

```bash
--worker_machine_type=n2-highmem-4 \
--experiments=use_runner_v2 \
--enable_streaming_engine
```

---

## Prevention checklist

- [ ] Use `CombinePerKey` instead of `GroupByKey` followed by a custom summing DoFn.
- [ ] Initialize heavy objects (database clients, lookup dictionaries) in `setup()` rather than in `process()`.
- [ ] Set `max_num_workers` to prevent infinite autoscaling during backpressure events.

---

| Previous Guide | All Debugging Guides | Next Guide |
| :--- | :---: | ---: |
| *None (First Guide)* | [Debugging Index](index.md) | [02: BigQuery Slot Starvation & Spilling](02-bigquery-slot-starvation-spilling.md) |
