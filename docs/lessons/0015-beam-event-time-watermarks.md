---
icon: lucide/clock
---

# Streaming concepts: Event time, processing time, watermarks, and allowed lateness

Processing unbounded streaming data requires handling out-of-order records, network delays, and mobile client offline periods. The Apache Beam streaming model separates **event time** (when the event occurred) from **processing time** (when the data engine observes the event).

---

## Event time vs Processing time

``` mermaid
flowchart TD
    EventGen["Event Occurs on Mobile Client (Event Time: 12:00:00)"] -->|"Device goes offline / Network delay"| Lag["5-Minute Network Lag"]
    Lag --> PubSub["Pub/Sub Ingestion (Ingestion Time: 12:05:00)"]
    PubSub --> Dataflow["Dataflow Worker (Processing Time: 12:05:02)"]
```

- **Event time**: The timestamp embedded within the record payload when the event physically took place on the client device.
- **Processing time**: The wall-clock time of the Dataflow worker processing the record.
- **Watermark**: A monotonically increasing timestamp tracking the system's progress through event time.

---

## The Watermark mechanism

A watermark of timestamp $T$ represents a guarantee (or high-confidence heuristic) that the pipeline does not expect to see any more records with an event timestamp $t < T$.

``` mermaid
flowchart TD
    W1["Current Watermark: 12:04:00"]
    R1["Record A (Event Time: 12:03:50) -> On-Time Data"]
    R2["Record B (Event Time: 12:02:10) -> Late Data (t < Watermark)"]

    W1 --> Check{"Evaluate against Watermark"}
    Check -->|"t >= 12:04:00"| R1
    Check -->|"t < 12:04:00"| R2
```

1. **Perfect watermarks**: Possible when sources have deterministic ordering (e.g. static batch files or partitioned monotonically increasing logs).
2. **Heuristic watermarks**: Used for distributed real-time systems like Cloud Pub/Sub, estimating watermark progression based on message age, backlog, and network latency.

---

## Allowed lateness and late data handling

When a record arrives after the watermark has passed the end of its assigned window:
- If **within allowed lateness**: The window is reopened, re-evaluated, and an updated aggregate is emitted.
- If **past allowed lateness**: The record is permanently dropped by the runner unless routed to a side output.

``` mermaid
flowchart TD
    WindowEnd["Window [12:00 - 12:05] Closes"] --> WatermarkPass["Watermark passes 12:05 (Initial Emit)"]
    WatermarkPass --> AllowedLateWindow["Allowed Lateness Window (e.g., 10 minutes: until 12:15)"]
    AllowedLateWindow --> LateRecord1["Late Record (t = 12:03 arrives at 12:10) -> Processed & Emits Update"]
    AllowedLateWindow --> Expire["Window Garbage Collected at 12:15"]
    Expire --> DroppedRecord["Late Record (t = 12:03 arrives at 12:20) -> DROPPED"]
```

---

## Attaching event timestamps and handling lateness in Python

```python
import apache_beam as beam
from apache_beam.transforms.window import FixedWindows, Duration
import json
import time

class ExtractTimestampDoFn(beam.DoFn):
    def process(self, element: bytes):
        payload = json.loads(element.decode("utf-8"))
        event_time_epoch = payload["event_timestamp_ms"] / 1000.0
        # Yield element with explicit event timestamp
        yield beam.window.TimestampedValue(payload, event_time_epoch)

def run_streaming_pipeline():
    options = beam.options.pipeline_options.PipelineOptions(
        streaming=True,
        runner="DataflowRunner",
        project="my-gcp-project",
        region="us-central1"
    )

    with beam.Pipeline(options=options) as p:
        (
            p
            | "ReadPubSub" >> beam.io.ReadFromPubSub(subscription="projects/my-gcp-project/subscriptions/orders-sub")
            | "AssignEventTime" >> beam.ParDo(ExtractTimestampDoFn())
            | "ApplyWindowAndLateness" >> beam.WindowInto(
                FixedWindows(60), # 1-minute fixed windows
                allowed_lateness=Duration(seconds=300), # 5 minutes allowed lateness
                accumulation_mode=beam.transforms.trigger.AccumulationMode.ACCUMULATING
            )
            | "ExtractMerchantKey" >> beam.Map(lambda rec: (rec["merchant_id"], float(rec["amount"])))
            | "SumRevenuePerMerchant" >> beam.CombinePerKey(sum)
            | "WriteToBigQuery" >> beam.io.WriteToBigQuery(
                "my-gcp-project:analytics_mart.realtime_merchant_revenue",
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
            )
        )
```

---

## Watermark lag and pipeline troubleshooting

In Cloud Dataflow, **Watermark Lag** measures the time difference between current real-world wall clock time and the pipeline watermark.
- **Normal behavior**: Lag stays steady between 2 and 15 seconds.
- **Stuck watermark**: If watermark lag grows linearly (e.g. 30 minutes and climbing), a single slow worker or an unacknowledged partition is holding back the global watermark, preventing windows from closing.

---

## Summary heuristics

1. Always extract and assign timestamps from payload event time rather than relying on Pub/Sub publish timestamps for business metrics.
2. Set `allowed_lateness` based on mobile client connection patterns (e.g. 5 to 15 minutes), balancing accuracy against the cost of retaining window state in memory.
3. Monitor watermark lag in the Dataflow monitoring console; a rising lag indicates pipeline bottlenecks or stuck I/O operations.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0014: Apache Beam Fundamentals](0014-apache-beam-fundamentals.md) | [All Lessons (Index)](index.md) | [0016: Advanced Windowing & Triggers](0016-beam-windowing-triggers.md) |
