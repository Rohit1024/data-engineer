---
icon: lucide/cpu
---

# Cloud Dataflow execution internals: Streaming Engine, FlexRS, and Shuffle

Cloud Dataflow is the managed execution runner for Apache Beam pipelines on Google Cloud. Understanding how Dataflow compiles execution graphs, optimizes pipeline stages, and offloads state and shuffle operations allows you to debug bottlenecks and cut compute costs.

---

## Graph optimizations: Fusion and combiner lifting

Before deploying workers, Dataflow translates the Beam pipeline DAG into an optimized physical execution graph:

``` mermaid
flowchart TD
    subgraph BeamDAG["User Pipeline DAG (Logical)"]
        Read["ReadFromGCS"] --> Parse["ParseJSON"]
        Parse --> FilterOp["FilterValid"]
        FilterOp --> WriteSink["WriteToBigQuery"]
    end

    subgraph FusedStage["Fused Stage (Physical)"]
        Fused["Fused Execution Step: Read + Parse + Filter in a Single Worker Loop"]
    end

    BeamDAG -->|"Fusion Optimization"| FusedStage
```

1. **Fusion optimization**: Combines adjacent `DoFn` and `Map` operations into a single execution step, eliminating network and serialization overhead between operations.
2. **Preventing accidental fusion**: If a pipeline stage produces massive fan-out, fusion can force downstream processing onto a single worker. Break unwanted fusion by inserting a `Reshuffle()` transform.
3. **Combiner lifting**: Moves partial aggregations ahead of the GroupByKey operation to reduce shuffle data volume.

---

## Streaming Engine vs Appliance mode

In legacy **Appliance mode**, worker VMs store streaming state and execute shuffle operations on local persistent disks attached to the Compute Engine VMs.

In **Dataflow Streaming Engine**, state storage and shuffle are offloaded to dedicated, specialized Google backend services:

``` mermaid
flowchart TD
    subgraph StreamingEngineArch["Dataflow Streaming Engine"]
        Worker1["Lightweight Worker VM 1"] <--> BackingEngine["Dataflow Streaming Engine Backend"]
        Worker2["Lightweight Worker VM 2"] <--> BackingEngine
        BackingEngine <--> PersistentState["Persistent State & High-Speed Shuffle"]
    end
```

### Benefits of Streaming Engine
- Worker VMs consume less CPU and memory because the managed backend handles streaming state and shuffle; do not assume a specific local state-store implementation.
- Autoscaling is fast and responsive because scaling down a worker does not require copying gigabytes of local state to another VM.
- Worker disk requirements can be reduced for suitable workloads. Use the selected runner/job configuration's supported sizing rather than assuming one universal minimum.

Enable via CLI:

```bash
--enable_streaming_engine
```

---

## Dataflow Shuffle for batch jobs

For batch workloads, **Dataflow Shuffle Service** moves the shuffle operation off worker disks and into a multi-tenant shuffle service.

- Solves worker disk exhaustion (`No space left on device`) during multi-terabyte `GROUP BY` operations.
- Reduces batch worker VM core and memory sizing requirements.

---

## Flexible Resource Scheduling (FlexRS)

FlexRS reduces batch pipeline compute costs by up to 40% by pairing regular Compute Engine VMs with Spot/Preemptible VMs and deferring execution within a 6-hour scheduling window.

```bash
python batch_pipeline.py --runner=DataflowRunner \
    --project=YOUR_PROJECT_ID --region=us-central1 \
    --temp_location=gs://YOUR_BUCKET/temp \
    --flexrs_goal=COST_OPTIMIZED
```

---

## Diagnostic metrics in the Dataflow monitoring console

| Metric name | Healthy state | Troubleshooting trigger |
| :--- | :--- | :--- |
| **System latency** | Meets the pipeline freshness objective | Rising latency indicates worker CPU saturation or downstream sink throttling |
| **Watermark age** | Consistent with source timestamps and window policy | Growing watermark lag means unclosed windows or stuck DoFn loops |
| **Throughput (elements/sec)** | Steady or matching source rate | Sudden drops point to backpressure from slow external API calls |
| **CPU utilization** | Interpret with backlog, parallelism and I/O | Low CPU can mean I/O or limited parallelism; high CPU alone does not guarantee autoscaling |

---

## Summary heuristics

1. Evaluate Streaming Engine for supported streaming workloads to offload state/shuffle and improve scaling behavior. Confirm the processing mode, regional support and cost model.
2. Use FlexRS (`--flexrs_goal=COST_OPTIMIZED`) for non-urgent daily or weekly batch pipelines to slash compute costs.
3. Insert `beam.Reshuffle()` when a single worker becomes a bottleneck after a high fan-out transform.

---

## Exactly-once processing and external effects

Dataflow's processing mode and a sink's delivery contract are separate. A `DoFn` that calls an external payment API can execute again after a retry. Use supported connectors and idempotent external operation IDs; do not infer global exactly-once business behavior from a runner setting. Compare at-least-once streaming mode only when your workload can tolerate or explicitly resolve repeat processing.

For diagnosis, consider a pipeline receiving 20,000 events/s but writing 15,000 events/s. Backlog grows by 5,000 events/s, or 18 million/hour. Adding workers helps only if worker capacity is the bottleneck. A serialized hot key, BigQuery quota or slow external service can limit throughput regardless of the maximum worker setting.

Fusion eliminates unnecessary materialization but can constrain parallelism after a fan-out. `Reshuffle` can create a redistribution boundary; it adds serialization/shuffle overhead and does not split state for one hot key. Inspect the physical stages before inserting it.

Drain and cancel also differ. Drain processes buffered work under the runner's drain semantics and can advance/close windows; cancel stops work without that completion behavior. Test state compatibility before a streaming job update and retain source replay coverage before replacement.

## Exercise with expected evidence

Inject a slow external call into a disposable pipeline. Record source rate, backlog growth, worker CPU and sink throughput. Predict whether more workers help, then compare. Repeat with a single hot key. Explain why the second case can remain slow despite idle capacity.

Sources: [exactly-once processing](https://docs.cloud.google.com/dataflow/docs/concepts/exactly-once), [Streaming Engine](https://docs.cloud.google.com/dataflow/docs/streaming-engine), and [FlexRS](https://docs.cloud.google.com/dataflow/docs/guides/flexrs).

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0017: Stateful Processing & Side Inputs](0017-beam-stateful-processing-side-inputs.md) | [All Lessons (Index)](index.md) | [0019: Flex Templates & Cloud Build](0019-dataflow-flex-templates-cloud-build.md) |
