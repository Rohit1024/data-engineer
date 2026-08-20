---
icon: lucide/compass
---

# Mission: GCP Data Engineering Mastery

## Why

Transition from basic cloud familiarity to architecting, optimizing, and operating production-grade, enterprise data platforms on Google Cloud Platform (GCP). Master the design trade-offs between batch and real-time streaming, serverless vs cluster-based processing, data lakehouse architectures, governance, and cost efficiency (FinOps) to excel as a Senior/Principal GCP Data Engineer.

## Success looks like

- Architecting end-to-end streaming and batch pipelines on GCP (Pub/Sub &rarr; Dataflow &rarr; BigQuery / Cloud Storage).
- Designing high-performance, cost-effective analytical data warehouses and lakehouses in BigQuery (partitioning, clustering, BI Engine, BigLake).
- Writing and optimizing Apache Beam (Python/Java) pipelines with advanced windowing, stateful processing, and exact-once semantics.
- Building distributed PySpark and Spark SQL workloads on Dataproc (managed and serverless) with BigQuery connectors.
- Implementing modern SQL-based ELT transformations using Dataform (SQLX) and dbt-bigquery with automated assertions.
- Orchestrating complex multi-cloud and cross-service data workflows using Cloud Composer (Apache Airflow 2.x).
- Enforcing enterprise data security, IAM, fine-grained access control (column/row-level security), and Dataplex data governance.
- Diagnosing pipeline bottlenecks, worker skew, BigQuery slot starvation, and out-of-memory (OOM) failures in production.

## Constraints

- Built bottom-up from first principles (explaining internal mechanics: Dremel, Capacitor, Colossus, Dataflow Shuffle, Beam Runner).
- Every concept backed by runnable code (`gcloud`, Python, SQL, Java), architectural Mermaid diagrams, and real-world system trade-offs.

## Out of scope

- Generic machine learning model training without data engineering pipelines (MLOps covered only at the data ingestion boundary).
- Deprecated legacy services (e.g., legacy BigQuery SQL, Hadoop on Compute Engine without Dataproc).
