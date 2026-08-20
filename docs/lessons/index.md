---
icon: lucide/graduation-cap
---

# GCP data engineering curriculum

All concepts from the roadmap are organized into structured, progressive modules. Each lesson is focused, hands-on, and includes architectural diagrams, internal mechanics, and retrieval exercises.

---

## Module 1: Storage foundations and lakehouse architecture
- [x] [0001: Cloud Storage Architecture, Storage Classes & Lifecycle Management](0001-cloud-storage-architecture-lifecycle.md)
- [x] [0002: Bigtable vs Spanner vs Cloud SQL: Selecting the Right Database](0002-bigtable-spanner-cloudsql-selection.md)
- [x] [0003: BigLake & Apache Iceberg Catalogs on Google Cloud](0003-biglake-iceberg-catalogs.md)
- [x] [0004: Data Lake Design Patterns: Medallion Architecture on GCS](0004-data-lake-medallion-gcs.md)

---

## Module 2: Real-time ingestion, messaging and CDC
- [x] [0005: Cloud Pub/Sub Architecture: Topics, Subscriptions & Flow Control](0005-pubsub-architecture-flow-control.md)
- [x] [0006: Cloud Pub/Sub Lite vs Standard: Cost vs Latency Trade-offs](0006-pubsub-lite-vs-standard.md)
- [x] [0007: Change Data Capture (CDC) with Datastream & BigQuery Ingestion](0007-change-data-capture-datastream-bigquery.md)
- [x] [0008: BigQuery Data Transfer Service (DTS) & GCS Object Change Notifications](0008-bigquery-data-transfer-service-gcs-notifications.md)

---

## Module 3: Serverless data warehousing with BigQuery
- [x] [0009: BigQuery Internal Architecture: Dremel, Capacitor, Colossus & Jupiter](0009-bigquery-internal-architecture.md)
- [x] [0010: Partitioning, Clustering & Search Indexes for Performance & Cost](0010-partitioning-clustering-search-indexes.md)
- [x] [0011: BigQuery Storage Write API: Streaming Ingestion & Exactly-Once Semantics](0011-bigquery-storage-write-api.md)
- [x] [0012: Materialized Views, BI Engine & Query Acceleration](0012-materialized-views-bi-engine.md)
- [x] [0013: BigQuery Slot Management: On-Demand vs Editions](0013-bigquery-slot-management-editions.md)

---

## Module 4: Stream and batch processing with Apache Beam and Cloud Dataflow
- [x] [0014: Apache Beam Fundamentals: PCollections, PTransforms & Pipelines](0014-apache-beam-fundamentals.md)
- [x] [0015: Streaming Concepts: Event Time, Processing Time, Watermarks & Allowed Lateness](0015-beam-event-time-watermarks.md)
- [x] [0016: Advanced Windowing: Fixed, Sliding, Session Windows & Triggering](0016-beam-windowing-triggers.md)
- [x] [0017: Stateful Processing, Side Inputs & Schema-Aware PCollections](0017-beam-stateful-processing-side-inputs.md)
- [x] [0018: Cloud Dataflow Execution Internals: Streaming Engine, FlexRS & Shuffle](0018-dataflow-execution-internals.md)
- [x] [0019: Dataflow Flex Templates & CI/CD Packaging with Cloud Build](0019-dataflow-flex-templates-cloud-build.md)

---

## Module 5: Distributed compute with Dataproc and Apache Spark
- [x] [0020: Cloud Dataproc Architecture: Master/Worker Topology & Ephemeral Clusters](0020-dataproc-architecture-ephemeral-clusters.md)
- [x] [0021: Dataproc Serverless for Spark: Submitting Interactive and Batch Workloads](0021-dataproc-serverless-spark.md)
- [x] [0022: PySpark ETL Workloads & BigQuery Storage Connector](0022-pyspark-bigquery-connector.md)
- [x] [0023: Spark Optimization on GCP: Memory Tuning, Dynamic Allocation & Partition Sizing](0023-spark-optimization-memory-tuning-gcp.md)

---

## Module 6: Modern data transformation with Dataform and dbt
- [x] [0024: Dataform Foundations: Repositories, Workspaces & workflow_settings.yaml](0024-dataform-foundations-workflow-settings.md)
- [x] [0025: Writing Dataform SQLX: Declarations, Incremental Tables & Assertions](0025-writing-dataform-sqlx-assertions.md)
- [x] [0026: dbt Core with dbt-bigquery: Models, Seeds, Snapshots & Jinja Macros](0026-dbt-core-bigquery-models-snapshots.md)
- [x] [0027: CI/CD Testing & Deployment for Transformation Pipelines](0027-transformation-pipelines-cicd.md)

---

## Module 7: Enterprise orchestration with Cloud Composer and Workflows
- [x] [0028: Cloud Composer (Apache Airflow 2.x) Architecture & GKE Environments](0028-cloud-composer-architecture-gke.md)
- [x] [0029: Designing Resilient DAGs: Google Cloud Operators & Deferrable Execution](0029-resilient-dags-deferrable-operators.md)
- [x] [0030: Dynamic Task Mapping, XComs & Airflow Best Practices](0030-dynamic-task-mapping-airflow-best-practices.md)
- [x] [0031: Google Cloud Workflows vs Cloud Composer: When to Use Serverless Orchestration](0031-cloud-workflows-vs-composer.md)

---

## Module 8: Data governance, security, observability and FinOps
- [x] [0032: Dataplex Architecture: Lakes, Zones, Assets & Data Quality Tasks](0032-dataplex-architecture-data-quality.md)
- [x] [0033: Fine-Grained Access Control: Column-Level Security & Row-Level Security](0033-fine-grained-access-control-policy-tags-rls.md)
- [x] [0034: Automated PII Masking with Sensitive Data Protection (Cloud DLP)](0034-automated-pii-masking-cloud-dlp.md)
- [x] [0035: End-to-End Pipeline Observability: Cloud Monitoring, Audit Logs & Lineage](0035-pipeline-observability-lineage.md)
- [x] [0036: BigQuery FinOps: Cost Monitoring, Slot Reservations & Query Optimization](0036-bigquery-finops-slot-reservations.md)
