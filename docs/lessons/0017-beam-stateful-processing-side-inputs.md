---
icon: lucide/box
---

# Stateful processing, timers, and side inputs in Apache Beam

While standard Apache Beam transforms operate statelessly per element, complex event processing requires persisting state across records and broadcasting reference data. Beam achieves this via the State & Timer API and Side Inputs.

---

## State and Timers architecture

State in Beam is scoped strictly **per key and per window**. You cannot access state across different keys or across different windows.

``` mermaid
flowchart TD
    Stream["Keyed Stream (Key = user_id)"] --> DoFn["Stateful DoFn Worker"]
    DoFn <--> StateStore["Persistent State Backend (Streaming Engine / RocksDB)"]
    DoFn <--> TimerService["Timer Service (Event Time / Processing Time)"]

    StateStore --- VState["ValueStateSpec: Single value"]
    StateStore --- BState["BagStateSpec: Unordered list"]
    StateStore --- MState["MapStateSpec: Key-value map"]
```

---

## Python implementation: State-driven deduplication and threshold alerts

This DoFn tracks the running transaction total per customer. If spending exceeds $1,000 within a 1-hour window, it triggers an alert and resets:

```python
import apache_beam as beam
from apache_beam.transforms.userstate import (
    ValueStateSpec,
    ReadModifyWriteStateSpec,
    TimerSpec,
    on_timer
)
from apache_beam.coders import VarIntCoder, FloatCoder

class ThresholdMonitorDoFn(beam.DoFn):
    TOTAL_SPEND_STATE = ValueStateSpec("total_spend", FloatCoder())
    EXPIRY_TIMER = TimerSpec("expiry_timer", beam.TimeDomain.WATERMARK)

    def process(
        self,
        element,
        total_spend_state=beam.DoFn.StateParam(TOTAL_SPEND_STATE),
        timer=beam.DoFn.TimerParam(EXPIRY_TIMER)
    ):
        user_id, amount = element
        current_total = total_spend_state.read() or 0.0
        new_total = current_total + amount
        total_spend_state.write(new_total)

        # Set or extend timer for 1 hour past current watermark
        timer.set(beam.transforms.window.Timestamp.now() + 3600)

        if new_total > 1000.0:
            yield {
                "user_id": user_id,
                "total_spend": new_total,
                "status": "THRESHOLD_EXCEEDED"
            }
            # Reset after alerting
            total_spend_state.clear()

    @on_timer(EXPIRY_TIMER)
    def on_expiry(
        self,
        total_spend_state=beam.DoFn.StateParam(TOTAL_SPEND_STATE)
    ):
        # Clear state when inactivity timer fires
        total_spend_state.clear()
```

---

## Side inputs: Broadcasting reference data

A Side Input passes an auxiliary PCollection (such as reference tables or currency exchange rates) to a `ParDo` transform alongside the main streaming data.

``` mermaid
flowchart TD
    MainStream["High-Volume Orders Stream (10,000 msgs/sec)"] --> MainPCol["Main PCollection"]
    RefData["Slowly Changing Exchange Rates (GCS / BigQuery)"] --> SidePCol["Side Input PCollectionView"]
    MainPCol --> EnrichDoFn["Enrichment ParDo"]
    SidePCol --> EnrichDoFn
    EnrichDoFn --> Out["Enriched USD Orders"]
```

### Python implementation with side inputs

```python
import apache_beam as beam

def enrich_order(order, exchange_rates):
    currency = order["currency"]
    rate = exchange_rates.get(currency, 1.0)
    order["amount_usd"] = order["amount"] * rate
    return order

def run_enrichment_pipeline():
    with beam.Pipeline() as p:
        # 1. Main stream of transactions
        orders = (
            p
            | "ReadOrders" >> beam.io.ReadFromPubSub(subscription="projects/my-proj/subscriptions/orders-sub")
            | "ParseOrders" >> beam.Map(json.loads)
        )

        # 2. Side input: periodic read of exchange rates as a singleton dictionary
        rates_side_input = (
            p
            | "ReadRates" >> beam.io.ReadFromText("gs://my-bucket/rates/latest.csv")
            | "ParseRates" >> beam.Map(lambda line: line.split(",")) # ["EUR", "1.08"]
            | "ToDict" >> beam.combiners.ToDict()
        )

        # 3. Join via ParDo side input
        enriched_orders = (
            orders
            | "ApplyConversion" >> beam.Map(enrich_order, exchange_rates=beam.pvalue.AsSingleton(rates_side_input))
        )
```

---

## Summary heuristics

1. Always attach an expiration timer (`TimerSpec`) to stateful DoFns to prevent state from growing infinitely in long-running streaming pipelines.
2. Keep side inputs small enough to fit inside worker RAM (under 500 MB). For multi-gigabyte dimension lookups, query BigQuery or Cloud Bigtable directly with connection pooling.
3. Key the main PCollection evenly before applying stateful transforms to prevent individual worker node hot-spotting.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0016: Advanced Windowing & Triggers](0016-beam-windowing-triggers.md) | [All Lessons (Index)](index.md) | [0018: Dataflow Execution Internals](0018-dataflow-execution-internals.md) |
