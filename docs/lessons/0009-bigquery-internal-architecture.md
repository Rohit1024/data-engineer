---
icon: lucide/cpu
---

# BigQuery internal architecture: Dremel, Capacitor, Colossus, and Jupiter

BigQuery executes queries across petabytes of data in seconds by decoupling compute from storage through Google's internal infrastructure components: Dremel (the compute execution engine), Capacitor (the columnar file format), Colossus (the distributed file system), and Jupiter (the petabit bisection-bandwidth network).

---

## The four core internal systems

``` mermaid
flowchart TD
    subgraph DremelCompute["Dremel Compute Engine"]
        Root["Root Server (Coordinator)"]
        Mixer1["Mixer Tier 1"]
        Mixer2["Mixer Tier 2"]
        Leaf1["Leaf Slot Worker 1"]
        Leaf2["Leaf Slot Worker 2"]
        Leaf3["Leaf Slot Worker 3"]
        Leaf4["Leaf Slot Worker 4"]

        Root --> Mixer1
        Root --> Mixer2
        Mixer1 --> Leaf1
        Mixer1 --> Leaf2
        Mixer2 --> Leaf3
        Mixer2 --> Leaf4
    end

    subgraph Network["Jupiter Network Fabric (Petabit Network)"]
        Jup["In-Memory Distributed Shuffle & Data Routing"]
    end

    subgraph ColossusStorage["Colossus Distributed Storage"]
        C1["Capacitor Shard A"]
        C2["Capacitor Shard B"]
        C3["Capacitor Shard C"]
    end

    DremelCompute <--> Network
    Network <--> ColossusStorage
```

---

## 1. Dremel: Dynamic execution tree

When you submit a SQL query, BigQuery allocates a dynamic tree of workers called **slots** (a virtual CPU plus memory unit):
1. **Root server**: Parses SQL, expands views, optimizes the execution plan, and acts as the top-level aggregator.
2. **Mixers**: Intermediate aggregation nodes that merge partial results from lower tiers and coordinate distributed shuffle operations.
3. **Leaf slots**: Read columnar chunks directly from Colossus over the Jupiter network, apply predicate filters, evaluate projection expressions, and emit intermediate records.

---

## 2. Capacitor: Columnar storage format

BigQuery stores native tables in Capacitor, an evolution of Apache Parquet and ORC formats.
- **Nested and repeated structures**: Capacitor represents hierarchical data using record shredding and reconstruction algorithms without flattening or data duplication.
- **Encoding and dictionary compression**: Columns are encoded based on data distribution (Run-Length Encoding, Bit-vector encoding, Frame-of-Reference, and Dictionary Encoding).
- **Embedded statistics**: File headers store exact min/max bounds and null counts per column per row group, enabling Dremel to skip irrelevant blocks before reading bytes off disk.

---

## 3. Colossus and Jupiter: Decoupled storage and shuffle

Traditional data warehouses co-locate CPU and disks on the same physical nodes. When a node fails or queries scale, data must be rebalanced across disks.

BigQuery separates compute and storage:
- **Colossus**: Handles multi-zone replication, automated disk repair, and snapshot isolation.
- **Jupiter network**: Delivers more than 1 Petabit per second of bisection bandwidth, allowing compute slots to read from Colossus at line-rate.
- **In-memory shuffle**: Joins and `GROUP BY` operations shuffle intermediate hash partitions across slots in RAM via Jupiter, avoiding slow disk writes.

---

## Inspecting execution stages with INFORMATION_SCHEMA

Inspect query plan stages, slot utilization, and shuffle bytes using `INFORMATION_SCHEMA.JOBS_BY_PROJECT`:

```sql
SELECT
  job_id,
  user_email,
  total_bytes_billed / (1024 * 1024 * 1024) AS gigabytes_billed,
  total_slot_ms / (1000 * 60) AS slot_minutes_consumed,
  total_slot_ms / NULLIF(TIMESTAMP_DIFF(end_time, start_time, MILLISECOND), 0) AS average_slots_used,
  query
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
  AND job_type = 'QUERY'
ORDER BY total_slot_ms DESC
LIMIT 10;
```

---

## Query execution stages inside the BigQuery console

When you inspect a query execution graph in the console or API:
- **Input (S00)**: Leaf workers read from Colossus and filter rows.
- **Shuffle (S01)**: Intermediate workers repartition data across hash keys in memory.
- **Output (S02)**: Mixers perform final aggregations, sorting, and return results to the root node.

``` mermaid
flowchart TD
    S00["Stage 0: Read from Colossus & Filter (Leaf Slots)"] --> Shuffle["In-Memory Shuffle (Jupiter)"]
    Shuffle --> S01["Stage 1: Partial Aggregation & Join (Mixers)"]
    S01 --> S02["Stage 2: Final Order By & Limit (Root)"]
```

---

## Summary heuristics

1. Queries scan only the specific columns referenced in the `SELECT`, `WHERE`, and `JOIN` clauses due to Capacitor columnar storage. Avoid `SELECT *`.
2. Compute slots scale dynamically per query. A query running against 100 TB can scale to thousands of leaf slots for seconds, then drop to zero.
3. High `total_slot_ms` relative to elapsed wall-clock time indicates effective parallelization across many Dremel slots.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0008: DTS & GCS Change Notifications](0008-bigquery-data-transfer-service-gcs-notifications.md) | [All Lessons (Index)](index.md) | [0010: Partitioning, Clustering & Indexes](0010-partitioning-clustering-search-indexes.md) |
