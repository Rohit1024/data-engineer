# GCP Data Engineering Glossary

Canonical nomenclature and standard terminology used across all lessons in this workspace.

## Terms

**BigQuery**:
A managed analytical warehouse that separates storage from query compute. Its native columnar storage and distributed execution support large SQL workloads.

**Capacitor**:
BigQuery's proprietary columnar storage format optimized for parallel scan performance and highly efficient data compression.

**Dremel**:
Google's distributed analytical execution architecture. Query stages read, filter, shuffle and aggregate data across parallel workers.

**Cloud Dataflow**:
A fully managed, serverless execution service for executing Apache Beam pipelines with automated resource management and dynamic work rebalancing.

**Watermark**:
A Beam abstraction representing the pipeline's notion of event-time completeness, signaling when all data up to a given timestamp is expected to have arrived.

**Cloud Pub/Sub**:
A global, asynchronous messaging service that decouples senders and receivers, providing at-least-once message delivery and dynamic auto-scaling.

**Cloud Dataproc**:
A managed Apache Spark and Apache Hadoop service that allows running big data workloads with rapid cluster provisioning and Dataproc Serverless execution.

**Cloud Composer**:
The former name of Managed Service for Apache Airflow. The `composer` CLI/API names remain in use. Managed generation, Airflow version and provider version are separate compatibility choices.

**Dataform**:
A serverless service that enables data teams to develop, test, version control, and schedule complex SQL workflows for BigQuery.

**Dataplex**:
A Google Cloud governance API/product family. Knowledge Catalog is the current name of the former Dataplex Universal Catalog; existing `dataplex` API names remain relevant.

**Grain**:
The meaning of one row, such as one order, one order line, one event or one customer version. A key and an aggregation must match that meaning.

**Data contract**:
The agreed schema, field meaning, identity, ordering, compatibility, quality, ownership and replay rules for a dataset or event.

**Tombstone**:
A sequenced representation of deletion retained so an older replay cannot recreate an entity.

**Pane**:
One emitted result for a Beam key/window under a trigger. A window can emit early, on-time and late panes.

**RPO**:
Recovery point objective. The maximum acceptable data loss relative to a defined source boundary.

**RTO**:
Recovery time objective. The acceptable time to restore the agreed service after an incident.

**Workload Identity Federation**:
An exchange of an authorized external workload identity for Google Cloud access without distributing a long-lived service-account key. Provider trust conditions and resource permissions still control access.

| Previous | References | Next |
| --- | :---: | ---: |
| [Lab conventions](lab-conventions.md) | [Reference index](index.md) | [Curriculum audit](curriculum-audit.md) |
