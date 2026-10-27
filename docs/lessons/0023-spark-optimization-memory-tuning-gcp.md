---
icon: lucide/sliders-horizontal
---

# Spark optimization on GCP: Memory tuning, dynamic allocation, and partition sizing

Tuning Apache Spark applications on Google Cloud Dataproc prevents driver/executor Out-Of-Memory (`OOM`) crashes, eliminates data skew bottlenecks, and cuts cluster compute costs.

---

## Spark JVM memory layout

An executor JVM divides its heap into distinct memory pools:

``` mermaid
flowchart TD
    subgraph TotalContainerMemory["Total YARN / Container Memory (spark.executor.memory + spark.executor.memoryOverhead)"]
        subgraph JVMHeap["JVM Heap (spark.executor.memory)"]
            Reserved["Reserved Memory (300 MB)"]
            UserMem["User Memory (40%: UDFs, custom data structures)"]
            subgraph SparkUnifiedMemory["Spark Unified Memory Pool (60%: spark.memory.fraction)"]
                ExecMem["Execution Memory (Shuffles, Joins, Aggregations)"]
                StorageMem["Storage Memory (Cached RDDs, DataFrames, Broadcasts)"]
            end
        end
        Overhead["Memory Overhead (10% min 384 MB: PySpark C bindings, off-heap)"]
    end
```

If your PySpark job crashes with `Container killed by YARN for exceeding memory limits`, increase `spark.executor.memoryOverhead` to give Python worker processes adequate off-heap memory.

---

## Memory sizing formula for Dataproc nodes

When configuring 8-core, 32 GB RAM worker VMs (`n2-standard-8`):
- Leave 1 core and 4 GB RAM for the OS and YARN NodeManager.
- Run 2 executors per node (3 vCPUs and 13 GB RAM per executor).
- Recommended configuration:
  - `spark.executor.cores = 3`
  - `spark.executor.memory = 10g`
  - `spark.executor.memoryOverhead = 3g`

---

## Partition sizing heuristics

Use **128 MiB to 200 MiB** of shuffle/input data per partition as an initial experiment, then measure decoded memory, skew and task duration:
- **Too many small partitions**: High task scheduling overhead on the Spark driver and millions of tiny files written to GCS.
- **Too few large partitions**: Risk of executor OOMs during shuffle and underutilized CPU cores.

```python
# Sizing partitions after a massive filter
filtered_df = large_df.filter("active = true")

# Use coalesce to reduce partition count without triggering a full network shuffle
optimized_df = filtered_df.coalesce(50)

# Use repartition only when increasing partitions or redistributing by a specific hash key
reshuffled_df = filtered_df.repartition(200, "customer_id")
```

---

## Data skew mitigation and join optimization

Data skew occurs when one key (e.g. `null` or a massive vendor ID) contains 80% of all rows, forcing one executor task to process for hours while others finish in seconds.

``` mermaid
flowchart TD
    subgraph SkewedJoin["Skewed Join (Hot Executor Bottleneck)"]
        SkewK1["Key: 'DEFAULT' (10,000,000 rows)"] --> ExecSlow["Executor 1 (OOM or Runs for 2 hours)"]
        NormalK2["Key: 'V102' (100 rows)"] --> ExecFast["Executor 2 (Finishes in 1s)"]
    end

    subgraph SaltingSolution["Salting Strategy (Uniform Distribution)"]
        Salted1["Key: 'DEFAULT_0' (1M rows)"] --> Ex1["Executor 1"]
        Salted2["Key: 'DEFAULT_1' (1M rows)"] --> Ex2["Executor 2"]
        Salted3["Key: 'DEFAULT_9' (1M rows)"] --> Ex3["Executor 3"]
    end

    SkewedJoin ~~~ SaltingSolution
```

### Salting technique in PySpark

```python
from pyspark.sql.functions import array, col, concat, explode, lit, rand, floor

# 1. Add random salt (0-9) to the skewed large table
skewed_df_salted = skewed_df.withColumn(
    "salted_key",
    concat(col("customer_id"), lit("_"), floor(rand() * 10).cast("string"))
)

# 2. Replicate dimension rows 10 times to match all possible salt keys
lookup_replicated = lookup_df.withColumn("salt", explode(array([lit(i) for i in range(10)]))) \
    .withColumn("salted_key", concat(col("customer_id"), lit("_"), col("salt").cast("string")))

# 3. Join on the evenly distributed salted key
joined_df = skewed_df_salted.join(lookup_replicated, "salted_key")
```

---

## Enabling Adaptive Query Execution (AQE)

Enable AQE in Spark 3.x to automatically coalesce shuffle partitions and optimize skewed joins at runtime:

```bash
spark.sql.adaptive.enabled=true
spark.sql.adaptive.coalescePartitions.enabled=true
spark.sql.adaptive.skewJoin.enabled=true
spark.sql.adaptive.skewJoin.skewedPartitionFactor=5
spark.sql.autoBroadcastJoinThreshold=67108864
```

---

## Summary heuristics

1. Set `spark.sql.adaptive.enabled=true` by default on all Dataproc Spark workloads.
2. If PySpark tasks crash with YARN container memory violations, increase `spark.executor.memoryOverhead` rather than just `spark.executor.memory`.
3. Broadcast a lookup only after checking decoded size, driver/executor memory and join semantics. A 64 MiB serialized input is not a universal safe memory limit.

---

## Measure before changing memory

Spark evaluates transformations lazily. A `select`, filter or join builds a plan; an action such as a write or count triggers execution. Use `explain("formatted")` and the Spark UI to locate scans, exchanges and join strategies. Cache only reused work, and unpersist it when finished. Caching every intermediate can increase pressure without improving runtime.

If a 32 GiB worker has two executors configured with 10 GiB heap plus 3 GiB overhead each, they reserve roughly 26 GiB before other runtime/OS needs. Python workers, Arrow buffers, native libraries and shuffle all matter. Increasing heap while leaving the same container/node limit can make the process exceed its memory budget. A driver failure caused by `collect()` is a different problem from executor skew.

For a 100 GiB shuffle with 200 partitions, the average is about 512 MiB per partition. If one key owns half the rows, the average hides a roughly 50 GiB hot partition. AQE can help supported skewed joins, but ordinary hash repartitioning by the same hot key cannot split its logical group.

The salting example expands every dimension key to ten variants. That is a cost, and it preserves joins only if matching keys/types and dimension grain are correct. Null join keys need an explicit policy. For replay-sensitive transforms, derive salts from a stable event identifier rather than depending on random assignment.

## Exercise with a useful correctness check

Build a local fixture with one hot customer and a unique lookup table. Compare an ordinary join, an eligible broadcast join and a correctly salted join. Assert identical row counts and total integer amounts before comparing shuffle bytes or runtime. Then duplicate a lookup key. All three can multiply revenue; performance tuning does not fix the data model.

??? note "Recall answer"
    `coalesce` reduces partitions without a general redistribution and can preserve skew. `repartition` redistributes, but hashing the same hot grouping key still sends it together. Use the query's semantics to decide whether salting or partial aggregation is valid.

Sources: [Spark SQL tuning](https://spark.apache.org/docs/3.5.6/sql-performance-tuning.html), [memory tuning](https://spark.apache.org/docs/3.5.6/tuning.html), and [monitoring](https://spark.apache.org/docs/3.5.6/monitoring.html).

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0022: PySpark BigQuery Connector](0022-pyspark-bigquery-connector.md) | [All Lessons (Index)](index.md) | [0024: Dataform Foundations](0024-dataform-foundations-workflow-settings.md) |
