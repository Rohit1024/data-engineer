# GCP data engineering masterclass

> **GitHub repository description**: Production-grade curriculum, architecture blueprints, cheatsheets, and diagnostic playbooks for Google Cloud Platform (GCP) data engineering.

Live documentation portal: [https://rohit1024.github.io/data-engineer](https://rohit1024.github.io/data-engineer)

---

## Overview

This repository contains a 36-lesson curriculum, 8 module cheatsheets, and diagnostic playbooks covering end-to-end data platform engineering on Google Cloud.

The material is structured bottom-up from internal mechanics (Dremel, Capacitor, Colossus, Dataflow Streaming Engine, Beam Runner) to distributed implementations and production operations.

---

## Curriculum roadmap

``` mermaid
flowchart TD
    M1["1. Storage Foundations & Lakehouse Architecture"] --> M2["2. Real-Time Ingestion & CDC"]
    M2 --> M3["3. BigQuery Architecture & Lakehouse"]
    M3 --> M4["4. Stream & Batch with Cloud Dataflow"]
    M4 --> M5["5. Distributed Compute with Dataproc & Spark"]
    M5 --> M6["6. Data Transformation with Dataform & dbt"]
    M6 --> M7["7. Enterprise Orchestration with Cloud Composer"]
    M7 --> M8["8. Governance, Security & FinOps"]
```

---

## What is covered

### 1. Storage foundations and lakehouse architecture
- **GCS internals**: Colossus storage, consistency models, and 4-tier lifecycle policies.
- **OLTP / NoSQL engine selection**: Cloud SQL vs Spanner (TrueTime, Paxos) vs Bigtable (row-key design).
- **BigLake and Apache Iceberg**: Open table formats, manifest trees, metadata pruning, and object tables.
- **Medallion architecture on GCS**: Bronze, Silver, and Gold layer partitioning and file compaction.

### 2. Real-time ingestion, messaging, and CDC
- **Cloud Pub/Sub**: Routers, forwarders, dead-letter topics (DLQ), flow control, and direct BigQuery subscriptions.
- **Pub/Sub Lite**: Pre-provisioned partition throughput and cost inflection points.
- **Datastream CDC**: WAL/binlog replication, BigQuery continuous merge, and changelog deduplication SQL.
- **BigQuery DTS and GCS notifications**: Scheduled transfers and Eventarc-triggered serverless loads.

### 3. Serverless data warehousing with BigQuery
- **BigQuery internals**: Dremel execution trees, Capacitor columnar encoding, Colossus, and Jupiter shuffle.
- **Optimization**: Partitioning strategies, 4-column clustering, and inverted search indexes.
- **Storage Write API**: Binary Protocol Buffers over gRPC with committed stream offsets.
- **Acceleration**: Incremental Materialized Views, smart query rewrites, and BI Engine in-memory RAM.
- **Capacity management**: On-Demand vs BigQuery Editions (Standard, Enterprise, Enterprise Plus).

### 4. Stream and batch processing with Apache Beam and Dataflow
- **Beam fundamentals**: Pipelines, PCollections, PTransforms, and the DoFn lifecycle.
- **Streaming mechanics**: Event time vs processing time, heuristic watermarks, and allowed lateness.
- **Windowing and triggers**: Fixed, sliding, and session windows with early/late triggering.
- **State and timers**: User state API, expiration timers, and side input broadcasting.
- **Dataflow internals**: Streaming Engine backend, FlexRS for cost savings, and fusion optimization.
- **CI/CD packaging**: Dockerized Flex Templates and Cloud Build automation.

### 5. Distributed compute with Dataproc and Apache Spark
- **Cluster architecture**: Master/worker topology, Spot task nodes, and auto-deletion TTLs.
- **Dataproc Serverless**: Submitting batch workloads with dynamic DCU allocation.
- **BigQuery connector**: Direct Storage Read API streaming and predicate pushdown.
- **Performance tuning**: Spark JVM memory layout, `memoryOverhead`, and Adaptive Query Execution (AQE).

### 6. Modern data transformation with Dataform and dbt
- **Dataform foundations**: Repositories, workspaces, and `workflow_settings.yaml`.
- **SQLX authoring**: Incremental models (`when(incremental(), ...)`), declarations, and assertions.
- **dbt-bigquery**: Incremental merge models, SCD Type 2 snapshots, and Jinja macros.
- **Slim CI**: Running only modified models with `state:modified+` in GitHub Actions.

### 7. Enterprise orchestration with Cloud Composer and Workflows
- **Composer 2 architecture**: GKE Autopilot, Celery workers, triggerers, and GCS DAG bucket sync.
- **Resilient DAG design**: Deferrable Google Cloud operators and eliminating top-level parsing I/O.
- **Dynamic Task Mapping**: Fan-out and fan-in architectures using `.expand()`.
- **Serverless orchestration**: Google Cloud Workflows vs Cloud Composer decision criteria.

### 8. Data governance, security, observability, and FinOps
- **Dataplex**: Lakes, zones, assets, and automated AutoDQ YAML scans.
- **Fine-grained security**: Policy tags with dynamic data masking (SHA-256) and row-level security (RLS).
- **Sensitive Data Protection (DLP)**: Crypto-deterministic pseudonymization with Cloud KMS.
- **Observability**: Cloud Monitoring alert policies, audit logs, and Dataplex data lineage.
- **FinOps**: Physical vs logical storage billing and query byte limits (`maximum_bytes_billed`).

---

## Diagnostic and debugging playbooks

The repository includes failure sequence diagrams, log queries, and resolution playbooks for common failure modes:

| Failure mode | Playbook |
| :--- | :--- |
| **Dataflow crashes & lag** | [Dataflow Bottlenecks, Key Skew & OOM Failures](docs/debugging/01-dataflow-bottlenecks-skew-oom.md) |
| **BigQuery latency & queueing** | [BigQuery Slot Starvation & Memory Spilling](docs/debugging/02-bigquery-slot-starvation-spilling.md) |
| **Pub/Sub unacked backlogs** | [Pub/Sub Message Accumulation & Throttling](docs/debugging/03-pubsub-unacked-messages-throttling.md) |
| **Spark executor loss** | [Dataproc Spark Executor Failures & OOM](docs/debugging/04-dataproc-spark-executor-oom-shuffle.md) |
| **Airflow task zombies & delays** | [Composer Scheduler Starvation & Zombies](docs/debugging/05-composer-scheduler-starvation-zombies.md) |
| **Transformation DAG cycles** | [Dataform & dbt Cyclic Dependencies & Assertions](docs/debugging/06-dataform-dbt-cyclic-dependencies-assertions.md) |
| **Storage Write API errors** | [BigQuery Storage Write API Errors](docs/debugging/07-bigquery-storage-write-api-errors.md) |
| **IAM & KMS permission issues** | [IAM, Policy Tags & KMS Permissions](docs/debugging/08-iam-policy-tags-kms-permissions.md) |

---

## Local development and verification

This project uses [Zensical](https://zensical.org) for documentation generation and Python tooling for Mermaid diagram validation.

### Prerequisites

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/)
- Node.js (for Mermaid CLI validation)

### Commands

```bash
# 1. Start the local preview server
uv run zensical serve

# 2. Build the documentation site
uv run zensical build --clean

# 3. Validate Mermaid syntax across all markdown files
python3 .agents/skills/teach/scripts/validate_mermaid.py
```

---

## Repository layout

```text
├── docs/
│   ├── index.md                 # Portal homepage
│   ├── mission.md               # Learning mission and success criteria
│   ├── lessons/                 # 36 sequential curriculum lessons
│   │   ├── index.md             # Curriculum catalog
│   │   └── 0001-*.md            # Individual lesson files
│   ├── cheatsheet/              # 8 module reference cheatsheets
│   │   ├── index.md             # Cheatsheet catalog
│   │   └── 01-*.md              # Individual cheatsheets
│   ├── debugging/               # 8 diagnostic and troubleshooting playbooks
│   │   ├── index.md             # Debugging catalog
│   │   └── 01-*.md              # Individual playbooks
│   ├── interview/               # Senior technical and system design question bank
│   └── references/              # Official documentation and glossary
├── zensical.toml                # Zensical site configuration
└── pyproject.toml               # Project dependencies
```

---

## License

Copyright &copy; 2026. All rights reserved.
