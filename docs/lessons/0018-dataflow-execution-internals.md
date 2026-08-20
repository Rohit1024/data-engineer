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
- Worker VMs consume less CPU and memory since they no longer run local RocksDB state stores.
- Autoscaling is fast and responsive because scaling down a worker does not require copying gigabytes of local state to another VM.
- Persistent disk sizes on worker VMs can be reduced to the minimum 30 GB.

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
gcloud dataflow jobs run monthly-billing-aggregation \
    --gcs-location=gs://my-templates/billing.json \
    --region=us-central1 \
    --parameters=flexRSGoal=COST_OPTIMIZED,tempLocation=gs://my-bucket/temp
```

---

## Diagnostic metrics in the Dataflow monitoring console

| Metric name | Healthy state | Troubleshooting trigger |
| :--- | :--- | :--- |
| **System Latency** | Under 10 seconds | Rising latency indicates worker CPU saturation or downstream sink throttling |
| **Data Watermark Lag** | 2 to 15 seconds | Growing watermark lag means unclosed windows or stuck DoFn loops |
| **Throughput (elements/sec)** | Steady or matching source rate | Sudden drops point to backpressure from slow external API calls |
| **CPU Utilization** | 70% to 85% | Under 20% indicates I/O blocking; over 95% triggers horizontal autoscaling |

---

## Summary heuristics

1. Always enable `--enable_streaming_engine` for streaming production pipelines to reduce VM footprint and enable fast autoscaling.
2. Use FlexRS (`--flexrs_goal=COST_OPTIMIZED`) for non-urgent daily or weekly batch pipelines to slash compute costs.
3. Insert `beam.Reshuffle()` when a single worker becomes a bottleneck after a high fan-out transform.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0017: Stateful Processing & Side Inputs](0017-beam-stateful-processing-side-inputs.md) | [All Lessons (Index)](index.md) | [0019: Flex Templates & Cloud Build](0019-dataflow-flex-templates-cloud-build.md) |
