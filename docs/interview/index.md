---
icon: lucide/help-circle
---

# Senior GCP Data Engineer & System Design Interview Questions

Curated, high-signal technical and architectural interview questions for Senior and Lead Google Cloud Data Engineering roles.

---

## 🏛️ Storage Foundations & Architecture
- **Storage Tiering & Lakehouse**: How do you architect an enterprise data lake on Cloud Storage and BigLake to support both BI and ad-hoc Spark processing with zero copy?
- **NoSQL vs NewSQL Trade-offs**: Compare Cloud Bigtable, Cloud Spanner, and Firestore for high-throughput time-series vs globally distributed transactional workloads.

---

## 🌐 Real-Time Ingestion & Streaming
- **Exactly-Once vs At-Least-Once**: Walk through how Cloud Pub/Sub, Dataflow, and BigQuery Storage Write API achieve end-to-end exactly-once processing.
- **Handling Late and Out-of-Order Data**: Explain how Apache Beam watermarks, allowed lateness, and accumulation modes handle late-arriving IoT telemetry.

---

## 💾 BigQuery Architecture & Optimization
- **Dremel & Capacitor Under the Hood**: Explain how BigQuery separates compute from storage, executes tree-structured query execution, and optimizes columnar storage compression.
- **Partitioning vs Clustering**: How would you optimize a 100TB event table queried primarily by `timestamp` and filtered by `user_id` and `event_type`?

---

## ⚡ Distributed Processing (Dataflow vs Spark)
- **Engine Selection**: When would you choose Cloud Dataflow (Apache Beam) over Cloud Dataproc (Spark/PySpark) or BigQuery SQL?
- **Dataflow Hotkey Mitigation**: How do you diagnose and resolve a hot key bottleneck causing pipeline lag in a GroupByKey step?

---

## 🧩 Orchestration & Governance
- **Composer DAG Scaling**: How do you structure Airflow DAGs in Cloud Composer to handle 10,000+ daily task executions without scheduler degradation?
- **Enterprise Governance with Dataplex**: How do you implement data mesh governance, column-level security tags, and automated PII redaction across multi-project GCP environments?
