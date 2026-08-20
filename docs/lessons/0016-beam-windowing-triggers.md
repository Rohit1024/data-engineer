---
icon: lucide/calendar
---

# Advanced windowing and triggers in Apache Beam

Windowing subdivides unbounded PCollections into bounded chunks for aggregation based on temporal bounds. Triggers determine exactly when the results of a window are emitted to downstream consumers.

---

## Windowing strategies

``` mermaid
flowchart TD
    subgraph Fixed["Fixed (Tumbling) Windows: Non-overlapping, fixed size (e.g. 5 min)"]
        F1["[12:00 - 12:05]"] --- F2["[12:05 - 12:10]"] --- F3["[12:10 - 12:15]"]
    end

    subgraph Sliding["Sliding (Hopping) Windows: Overlapping, fixed size + period (e.g. 10 min window every 2 min)"]
        S1["[12:00 - 12:10]"]
        S2["[12:02 - 12:12]"]
        S3["[12:04 - 12:14]"]
    end

    subgraph Sessions["Session Windows: Dynamic gaps per key based on inactivity"]
        UserA["User A: [12:01..12:04] -> [Session 1]"]
        UserB["User B: [12:02..12:20] -> [Session 2 (Long Active)]"]
    end

    Fixed ~~~ Sliding ~~~ Sessions
```

1. **Fixed (Tumbling) windows**: Consistent, non-overlapping time slices (e.g., hourly sales rollups).
2. **Sliding (Hopping) windows**: Overlapping time intervals (e.g., 5-minute moving averages calculated every 30 seconds). Elements are assigned to multiple windows simultaneously.
3. **Session windows**: Data-driven, dynamic duration windows bounded by an inactivity gap (e.g., user web session tracking).
4. **Global windows**: A single infinite window covering all event time. Used in batch jobs or streaming jobs with explicit data-driven triggers.

---

## Triggers: Deciding when to emit results

A trigger controls when the accumulated state for a window is fired. Triggers evaluate three temporal domains:
- **Event-time triggers**: Fire when the watermark passes the window end.
- **Processing-time triggers**: Fire based on wall-clock time passing (e.g. emit partial updates every 10 seconds).
- **Data-driven triggers**: Fire when an element count is reached (e.g. emit every 100 elements).

---

## Accumulation modes: Accumulating vs Discarding

``` mermaid
flowchart TD
    subgraph AccumulatingMode["ACCUMULATING: Each firing includes all past data"]
        F1A["Firing 1 (Early at count 100): Total = 100"] --> F2A["Firing 2 (On Watermark): Total = 150 (100 + 50)"]
    end

    subgraph DiscardingMode["DISCARDING: Each firing emits only new delta"]
        F1D["Firing 1 (Early at count 100): Delta = 100"] --> F2D["Firing 2 (On Watermark): Delta = 50"]
    end

    AccumulatingMode ~~~ DiscardingMode
```

- **ACCUMULATING**: Emits cumulative totals. Downstream sinks must overwrite or upsert by window key.
- **DISCARDING**: Emits only the delta since the previous firing. Downstream sinks sum values across firings.

---

## Python implementation: Session window with early and late triggers

This pipeline groups user clickstream events into sessions with a 10-minute gap, emitting early speculative updates every minute and late arriving updates:

```python
import apache_beam as beam
from apache_beam.transforms.window import Sessions, Duration
from apache_beam.transforms.trigger import (
    AfterWatermark,
    AfterProcessingTime,
    AfterCount,
    Repeatedly,
    AccumulationMode
)

def run_session_pipeline():
    options = beam.options.pipeline_options.PipelineOptions(streaming=True)

    with beam.Pipeline(options=options) as p:
        (
            p
            | "ReadPubSub" >> beam.io.ReadFromPubSub(subscription="projects/my-proj/subscriptions/clickstream-sub")
            | "ParseJSON" >> beam.Map(lambda raw: json.loads(raw.decode("utf-8")))
            | "AddTimestamps" >> beam.Map(lambda rec: beam.window.TimestampedValue(rec, rec["timestamp_epoch"]))
            | "ApplySessionWindow" >> beam.WindowInto(
                Sessions(gap_size=600), # 10 minutes inactivity gap
                trigger=Repeatedly(
                    AfterWatermark(
                        early=AfterProcessingTime(60), # Speculative firing every 1 minute
                        late=AfterCount(1)             # Fire immediately on every late record
                    )
                ),
                allowed_lateness=Duration(seconds=1800), # 30 minutes lateness
                accumulation_mode=AccumulationMode.ACCUMULATING
            )
            | "KeyByUser" >> beam.Map(lambda rec: (rec["user_id"], 1))
            | "CountClicksPerSession" >> beam.CombinePerKey(sum)
            | "Format" >> beam.Map(lambda kv: {"user_id": kv[0], "click_count": kv[1]})
            | "WriteToBigQuery" >> beam.io.WriteToBigQuery(
                "my-proj:analytics.user_session_counts",
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
            )
        )
```

---

## Summary heuristics

1. Use **Fixed Windows** for financial accounting and metrics that map to calendar boundaries.
2. Use **Session Windows** for behavioral and user-journey analytics where events naturally group around bursts of activity.
3. Combine `AfterWatermark` with early `AfterProcessingTime` triggers to provide real-time visibility in dashboards before the watermark officially closes long windows.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0015: Event Time & Watermarks](0015-beam-event-time-watermarks.md) | [All Lessons (Index)](index.md) | [0017: Stateful Processing & Side Inputs](0017-beam-stateful-processing-side-inputs.md) |
