---
icon: lucide/database
---

# Bigtable vs Spanner vs Cloud SQL: Selecting the right database

Choosing the right transactional or operational store dictates how downstream pipelines ingest, replicate, and serve analytics. On GCP, the three primary transactional and operational engines are Cloud SQL, Cloud Spanner, and Cloud Bigtable. Each solves a distinct operational constraint.

---

## Architectural decision framework

Use this decision flow to identify the target database based on volume, consistency requirements, and access patterns:

``` mermaid
flowchart TD
    Start["New Operational Workload"] --> Q1{"Data Volume > 10 TB or Millions of IOPS?"}
    Q1 -- "No" --> RelCheck{"Strict ACID & Traditional SQL Relational?"}
    RelCheck -- "Yes" --> CS["Cloud SQL (PostgreSQL / MySQL / SQL Server)"]
    RelCheck -- "No" --> Q1
    Q1 -- "Yes" --> Q2{"Access Pattern?"}
    Q2 -- "Single Key Lookup / Time-Series / Wide-Column" --> BT["Cloud Bigtable (Sub-10ms, No Multi-Row ACID)"]
    Q2 -- "Global Relational / Multi-Row Transactions" --> SP["Cloud Spanner (TrueTime, External Consistency)"]
```

---

## Comparative technical matrix

| Capability | Cloud SQL | Cloud Spanner | Cloud Bigtable |
| :--- | :--- | :--- | :--- |
| **Data model** | Relational (RDBMS) | Relational (ANSI SQL) | NoSQL Wide-column |
| **Max storage** | 64 TB per instance | Practically unlimited (Petabytes) | Practically unlimited (Petabytes) |
| **Scaling** | Vertical (read replicas horizontal) | Horizontal (compute & storage decouple) | Horizontal (linear scaling per node) |
| **Consistency** | Strong (Single-master) | Strong globally (TrueTime + Paxos) | Eventual across replications (strong single-cluster) |
| **Read latency** | 10 to 50ms | 10 to 20ms | 1 to 6ms |
| **Write latency** | 10 to 50ms | 15 to 30ms (two-phase commit) | 1 to 5ms (appends to commit log) |
| **Analytics ingestion** | CDC (Datastream) or Batch export | Change Streams & Dataflow connector | Beam BigtableIO & BigQuery federation |

---

## Deep dive: Engine internals

### 1. Cloud SQL
Runs managed MySQL, PostgreSQL, or SQL Server instances on Compute Engine VMs with persistent disks.
- **Limitation**: Writes route to a single primary instance. Read replicas handle read-only traffic asynchronously, introducing replication lag.
- **Pipeline use case**: Reference dimensions, customer metadata, and transactional lookups under 10,000 queries per second.

### 2. Cloud Spanner
Splits data into splits (shards) distributed across Paxos groups. It uses Google's hardware TrueTime API (GPS receivers and atomic clocks) to provide external consistency without central lock managers.
- **Interleaving**: Spanner allows child tables to physically co-locate on the same splits as parent tables, avoiding distributed network joins.
- **Pipeline use case**: Globally distributed ledger entries, core billing engines, and high-frequency inventory tracking.

### 3. Cloud Bigtable
A sparse, distributed multi-dimensional sorted map. Data is indexed by a single row key, column family, column qualifier, and timestamp.
- **Row key design**: Bigtable orders keys lexicographically. Sequential keys cause hotspotting on a single tablet server.
- **Pipeline use case**: IoT telemetry, financial ticker feeds, and clickstream ingestion pushing hundreds of thousands of events per second.

---

## Hotspotting prevention in Bigtable

``` mermaid
flowchart TD
    subgraph BadKey["Anti-Pattern: Sequential Key (Hotspotting)"]
        K1["2026-08-20#sensor_01"] --> NodeA["Tablet 1 (100% CPU Load)"]
        K2["2026-08-20#sensor_02"] --> NodeA
        K3["2026-08-20#sensor_03"] --> NodeA
    end

    subgraph GoodKey["Best Practice: Salted / Reversed Key"]
        K4["sensor_01#2026-08-20"] --> Node1["Tablet 1"]
        K5["sensor_99#2026-08-20"] --> Node2["Tablet 2"]
        K6["sensor_42#2026-08-20"] --> Node3["Tablet 3"]
    end

    BadKey ~~~ GoodKey
```

---

## Hands-on exercise: Creating a Spanner instance and table with change streams

Spanner Change Streams capture real-time inserts, updates, and deletes, feeding downstream Dataflow and BigQuery pipelines.

```bash
# 1. Create a regional Spanner instance
gcloud spanner instances create prod-spanner-01 \
    --config=regional-us-central1 \
    --description="Core Production Ledger" \
    --nodes=1

# 2. Create database
gcloud spanner databases create orders_db \
    --instance=prod-spanner-01

# 3. Create table with change stream enabled using DDL
gcloud spanner databases ddl update orders_db \
    --instance=prod-spanner-01 \
    --ddl='
      CREATE TABLE Orders (
        OrderId STRING(36) NOT NULL,
        CustomerId STRING(36) NOT NULL,
        OrderAmount NUMERIC NOT NULL,
        CreatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true)
      ) PRIMARY KEY (OrderId);

      CREATE CHANGE STREAM OrdersStream FOR Orders;
    '
```

---

## Summary heuristics

1. Use Cloud SQL when you need standard SQL relational features, have less than 10 TB of data, and can tolerate single-node write limits.
2. Use Cloud Spanner when you require relational consistency, multi-table transactions, and global horizontal scale.
3. Use Cloud Bigtable when you have petabytes of semi-structured data, need sub-10ms single-key reads and writes, and access data strictly through row keys.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0001: Cloud Storage Architecture](0001-cloud-storage-architecture-lifecycle.md) | [All Lessons (Index)](index.md) | [0003: BigLake & Apache Iceberg Catalogs](0003-biglake-iceberg-catalogs.md) |
