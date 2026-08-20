# GCP Data Engineering Glossary

Canonical nomenclature and standard terminology used across all lessons in this workspace.

## Terms

**BigQuery**:
A fully managed, serverless, highly scalable enterprise data warehouse designed for business agility, separating storage (Capacitor/Colossus) from compute (Dremel).

**Capacitor**:
BigQuery's proprietary columnar storage format optimized for parallel scan performance and highly efficient data compression.

**Dremel**:
Google's distributed query execution engine that turns SQL queries into execution trees capable of querying petabytes in seconds.

**Cloud Dataflow**:
A fully managed, serverless execution service for executing Apache Beam pipelines with automated resource management and dynamic work rebalancing.

**Watermark**:
A Beam abstraction representing the pipeline's notion of event-time completeness, signaling when all data up to a given timestamp is expected to have arrived.

**Cloud Pub/Sub**:
A global, asynchronous messaging service that decouples senders and receivers, providing at-least-once message delivery and dynamic auto-scaling.

**Cloud Dataproc**:
A managed Apache Spark and Apache Hadoop service that allows running big data workloads with rapid cluster provisioning and Dataproc Serverless execution.

**Cloud Composer**:
A fully managed workflow orchestration service built on Apache Airflow, enabling scheduling, monitoring, and orchestrating multi-cloud and GCP pipelines.

**Dataform**:
A serverless service that enables data teams to develop, test, version control, and schedule complex SQL workflows for BigQuery.

**Dataplex**:
An intelligent data fabric that provides unified data management, centralized governance, automated discovery, and data quality monitoring across distributed GCP data.
