# GCP Data Engineering Resources

## Knowledge

- [Google Cloud Official Documentation](https://cloud.google.com/docs)
  Authoritative specification, reference manuals, and architecture guides across BigQuery, Dataflow, Dataproc, Pub/Sub, and Composer.
- [Google Cloud Architecture Center](https://docs.cloud.google.com/architecture)
  Reference architectures and validated designs for enterprise lakehouses and streaming systems.
- [Apache Beam Documentation & Programming Guide](https://beam.apache.org/documentation/programming-guide/)
  Definitive guide to Beam primitives, windowing, pipelines, and runners.
- [Dataform Documentation](https://cloud.google.com/dataform/docs)
  Authoritative guide for developing and orchestrating SQL-based ELT workflows in BigQuery.
- [dbt Documentation for BigQuery](https://docs.getdbt.com/docs/core/connect-data-platform/bigquery-setup)
  Best practices for data modeling, testing, and documentation with dbt-bigquery.

## Wisdom (Communities)

- [Google Cloud Community - Data Analytics](https://www.googlecloudcommunity.com/gc/Data-Analytics/bd-p/cloud-data-analytics)
  High-signal community for architecture discussions, BigQuery optimization, and GCP data challenges.
- [r/dataengineering on Reddit](https://www.reddit.com/r/dataengineering/)
  Active practitioner subreddit with real-world architecture reviews, tool comparisons, and best practices.
- [Apache Beam Slack / Mailing List](https://beam.apache.org/community/contact-us/)
  Community discussions on stream processing, Beam Python/Java SDKs, and Dataflow runner specifics.

## BigQuery ingestion and transformation lab

Official sources checked for lesson 0037 on 2026-10-26.

- [Load JSON from Cloud Storage](https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-json)
- [Configure Cloud Storage transfers](https://cloud.google.com/bigquery/docs/cloud-storage-transfer)
- [Cloud Storage transfer ingestion behavior](https://cloud.google.com/bigquery/docs/cloud-storage-transfer-overview)
- [Create Pub/Sub BigQuery subscriptions](https://cloud.google.com/pubsub/docs/create-bigquery-subscription)
- [BigQuery subscription delivery behavior](https://cloud.google.com/pubsub/docs/bigquery)
- [Pub/Sub dead-letter topics](https://cloud.google.com/pubsub/docs/dead-letter-topics)
- [Dataflow Pub/Sub-to-BigQuery template](https://cloud.google.com/dataflow/docs/guides/templates/provided/pubsub-to-bigquery)
- [Datastream replication quickstart](https://cloud.google.com/datastream/docs/quickstart-replication-to-bigquery)
- [Prepare Cloud SQL PostgreSQL for CDC](https://cloud.google.com/datastream/docs/configure-cloudsql-psql)
- [Datastream connectivity options](https://cloud.google.com/datastream/docs/network-connectivity-options)
- [Configure a BigQuery destination](https://cloud.google.com/datastream/docs/configure-bigquery-destination)
- [Cloud Storage external tables](https://cloud.google.com/bigquery/docs/external-data-cloud-storage)
- [Storage Write API gRPC semantics](https://cloud.google.com/bigquery/docs/write-api-grpc)
- [Schedule BigQuery queries](https://cloud.google.com/bigquery/docs/scheduling-queries)
- [Dataform assertions](https://cloud.google.com/dataform/docs/assertions)

## BigQuery architecture and load-transform-export

Sources checked for lesson 0038 on 2026-10-26. The 2017 article supplies historical architecture context; current product documentation supports the implementation.

- [Designing ETL architecture for a cloud-native data warehouse, May 11, 2017](https://cloud.google.com/blog/products/bigquery/designing-etl-architecture-for-a-cloud-native-data-warehouse-on-google-cloud-platform)
- [Introduction to loading, transforming and exporting data](https://docs.cloud.google.com/bigquery/docs/load-transform-export-intro)
- [GoogleSQL DML and MERGE](https://cloud.google.com/bigquery/docs/reference/standard-sql/dml-syntax)
- [BigQuery transactions](https://cloud.google.com/bigquery/docs/transactions)
- [EXPORT DATA statement](https://cloud.google.com/bigquery/docs/reference/standard-sql/export-statements)
- [Exporting table data and required permissions](https://cloud.google.com/bigquery/docs/exporting-data)

## Managed Airflow environment and DAG lab

Official sources checked for lesson 0039 on 2026-10-26. Examples target Airflow 2.11-style APIs; use provider documentation matching the selected managed image.

- [Create Managed Service for Apache Airflow environments](https://docs.cloud.google.com/composer/docs/composer-3/create-environments)
- [Gen 3 environment architecture](https://docs.cloud.google.com/composer/docs/composer-3/environment-architecture)
- [Add and update DAGs](https://docs.cloud.google.com/composer/docs/composer-3/manage-dags)
- [Airflow 2.11 TaskFlow](https://airflow.apache.org/docs/apache-airflow/2.11.0/tutorial/taskflow.html)
- [Airflow 2.11 best practices](https://airflow.apache.org/docs/apache-airflow/2.11.0/best-practices.html)
- [DAG runs and data intervals](https://airflow.apache.org/docs/apache-airflow/2.10.5/core-concepts/dag-run.html)
- [Dynamic task mapping](https://airflow.apache.org/docs/apache-airflow/2.10.5/authoring-and-scheduling/dynamic-task-mapping.html)
- [Google provider GCS sensors](https://airflow.apache.org/docs/apache-airflow-providers-google/stable/_api/airflow/providers/google/cloud/sensors/gcs/index.html)
- [Google provider BigQuery operators](https://airflow.apache.org/docs/apache-airflow-providers-google/stable/operators/cloud/bigquery.html)

## BigQuery failed-job recovery and backfill

Official sources checked for lesson 0040 on 2026-10-26.

- [Manage BigQuery jobs](https://docs.cloud.google.com/bigquery/docs/managing-jobs)
- [JOBS metadata](https://docs.cloud.google.com/bigquery/docs/information-schema-jobs)
- [Batch load atomicity and retries](https://docs.cloud.google.com/bigquery/docs/batch-loading-data)
- [Transactions](https://docs.cloud.google.com/bigquery/docs/transactions)
- [Create table snapshots](https://docs.cloud.google.com/bigquery/docs/table-snapshots-create)
- [insertAll API and row-indexed errors](https://docs.cloud.google.com/bigquery/docs/reference/rest/v2/tabledata/insertAll)
- [REST streaming behavior](https://docs.cloud.google.com/bigquery/docs/write-api-rest)
- [Storage Write API gRPC](https://docs.cloud.google.com/bigquery/docs/write-api-grpc)
- [DML syntax](https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/dml-syntax)
- [DML limitations](https://docs.cloud.google.com/bigquery/docs/data-manipulation-language)
- [Airflow 2.11 DAG runs and re-runs](https://airflow.apache.org/docs/apache-airflow/2.11.0/core-concepts/dag-run.html)

## Curriculum audit source additions

Source review on 2026-10-28 covered changed service guidance, API shapes and the five added lessons. Links below are primary documentation; version-specific Beam, Spark, Airflow and serialization references support the stated example versions. Source-page reachability is checked separately from cloud execution.


### Storage and operational data

- [Consistency](https://docs.cloud.google.com/storage/docs/consistency)
- [Hierarchical namespace](https://docs.cloud.google.com/storage/docs/hns-overview)
- [Storage-class documentation](https://docs.cloud.google.com/storage/docs/storage-classes)
- [Request preconditions](https://docs.cloud.google.com/storage/docs/request-preconditions)
- [Lifecycle management](https://docs.cloud.google.com/storage/docs/lifecycle)
- [Spanner schema design](https://docs.cloud.google.com/spanner/docs/schema-design)
- [Bigtable schema design](https://docs.cloud.google.com/bigtable/docs/schema-design)
- [Spanner change-stream guide](https://docs.cloud.google.com/spanner/docs/change-streams)
- [BigLake access delegation](https://docs.cloud.google.com/bigquery/docs/biglake-intro)
- [Managed Iceberg tables](https://docs.cloud.google.com/bigquery/docs/biglake-iceberg-tables-in-bigquery)
- [External Iceberg guide](https://docs.cloud.google.com/bigquery/docs/iceberg-external-tables)
- [Parquet format](https://parquet.apache.org/docs/file-format/)
- [External Hive partitions](https://docs.cloud.google.com/bigquery/docs/hive-partitioned-queries)


### Messaging and CDC

- [Exactly-once delivery](https://docs.cloud.google.com/pubsub/docs/exactly-once-delivery)
- [Replay](https://docs.cloud.google.com/pubsub/docs/replay-overview)
- [Subscriber flow control](https://docs.cloud.google.com/pubsub/docs/subscribe-best-practices)
- [Official notice](https://docs.cloud.google.com/pubsub/docs/pubsub-lite-documentation)
- [Messaging-model comparison and retirement notice](https://docs.cloud.google.com/pubsub/docs/choosing-pubsub-or-lite)
- [Managed Kafka overview](https://docs.cloud.google.com/managed-service-for-apache-kafka/docs/overview)
- [Destination metadata](https://docs.cloud.google.com/datastream/docs/destination-bigquery)
- [Event-ordering documentation](https://docs.cloud.google.com/datastream/docs/events-and-streams)
- [Notifications](https://docs.cloud.google.com/storage/docs/pubsub-notifications)


### BigQuery execution and capacity

- [Query-plan explanation](https://docs.cloud.google.com/bigquery/docs/query-plan-explanation)
- [Compute optimization](https://docs.cloud.google.com/bigquery/docs/best-practices-performance-compute)
- [Partitioned tables](https://docs.cloud.google.com/bigquery/docs/partitioned-tables)
- [Clustered tables](https://docs.cloud.google.com/bigquery/docs/clustered-tables)
- [Search indexes](https://docs.cloud.google.com/bigquery/docs/search-intro)
- [Retry guidance](https://docs.cloud.google.com/bigquery/docs/write-api-best-practices)
- [Official Protobuf example](https://docs.cloud.google.com/bigquery/docs/samples/bigquerystorage-append-rows-raw-proto2)
- [Pending-stream batch loading](https://docs.cloud.google.com/bigquery/docs/write-api-batch-load)
- [BI Engine reservation guide](https://docs.cloud.google.com/bigquery/docs/bi-engine-reserve-capacity)
- [Materialized-view creation](https://docs.cloud.google.com/bigquery/docs/materialized-views-create)
- [Smart tuning and use](https://docs.cloud.google.com/bigquery/docs/materialized-views-use)
- [BI Engine overview](https://docs.cloud.google.com/bigquery/docs/bi-engine-intro)
- [Workload management](https://docs.cloud.google.com/bigquery/docs/reservations-workload-management)
- [Reservation tasks](https://docs.cloud.google.com/bigquery/docs/reservations-tasks)
- [JOBS_TIMELINE](https://docs.cloud.google.com/bigquery/docs/information-schema-jobs-timeline)
- [Reservation timelines](https://docs.cloud.google.com/bigquery/docs/information-schema-reservation-timeline)


### Beam and Dataflow

- [Pipeline testing](https://beam.apache.org/documentation/pipelines/test-your-pipeline/)
- [Execution behavior](https://beam.apache.org/documentation/runtime/model/)
- [TestStream](https://beam.apache.org/releases/pydoc/current/apache_beam.testing.test_stream.html)
- [Exactly-once processing](https://docs.cloud.google.com/dataflow/docs/concepts/exactly-once)
- [Streaming Engine](https://docs.cloud.google.com/dataflow/docs/streaming-engine)
- [FlexRS](https://docs.cloud.google.com/dataflow/docs/guides/flexrs)
- [Flex Template configuration](https://docs.cloud.google.com/dataflow/docs/guides/templates/configuring-flex-templates)
- [Custom SDK containers](https://docs.cloud.google.com/dataflow/docs/guides/run-custom-container)
- [Template troubleshooting](https://docs.cloud.google.com/dataflow/docs/guides/troubleshoot-templates)


### Spark

- [Cluster architecture](https://docs.cloud.google.com/dataproc/docs/concepts/overview)
- [Secondary workers](https://docs.cloud.google.com/dataproc/docs/concepts/compute/secondary-vms)
- [Scheduled deletion](https://docs.cloud.google.com/dataproc/docs/concepts/configuring-clusters/scheduled-deletion)
- [Runtime versions](https://docs.cloud.google.com/managed-spark/docs/concepts/versions/serverless-versions)
- [Batch submission](https://docs.cloud.google.com/managed-spark/docs/quickstarts/spark-batch)
- [Spark properties](https://docs.cloud.google.com/managed-spark/docs/concepts/spark-properties-serverless)
- [Custom-container guide](https://docs.cloud.google.com/managed-spark/docs/guides/custom-containers)
- [Official Spark BigQuery connector README and compatibility matrix](https://github.com/GoogleCloudDataproc/spark-bigquery-connector)
- [Spark SQL tuning](https://spark.apache.org/docs/3.5.6/sql-performance-tuning.html)
- [Memory tuning](https://spark.apache.org/docs/3.5.6/tuning.html)
- [Monitoring](https://spark.apache.org/docs/3.5.6/monitoring.html)


### Transformation development and CI

- [Repository settings](https://docs.cloud.google.com/dataform/docs/manage-repository)
- [The CLI guide](https://docs.cloud.google.com/dataform/docs/use-dataform-cli)
- [Compilation configuration](https://docs.cloud.google.com/dataform/docs/configure-compilation)
- [Incremental tables](https://docs.cloud.google.com/dataform/docs/create-tables)
- [Assertion dependencies](https://docs.cloud.google.com/dataform/docs/dependencies)
- [Incremental models](https://docs.getdbt.com/docs/build/incremental-models)
- [Seeds](https://docs.getdbt.com/docs/build/seeds)
- [Snapshots](https://docs.getdbt.com/docs/build/snapshots)
- [State selection](https://docs.getdbt.com/reference/node-selection/methods#state)
- [Deferral](https://docs.getdbt.com/reference/node-selection/defer)
- [Deployment-pipeline federation](https://docs.cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines)
- [Dataform workflow creation](https://docs.cloud.google.com/dataform/docs/quickstart-create-workflow)


### Orchestration

- [Official backend configuration](https://airflow.apache.org/docs/apache-airflow-providers-common-io/stable/xcom_backend.html)
- [Airflow 2.11 dynamic mapping](https://airflow.apache.org/docs/apache-airflow/2.11.0/authoring-and-scheduling/dynamic-task-mapping.html)
- [Connector reference](https://docs.cloud.google.com/workflows/docs/reference/googleapis/bigquery/v2/jobs/insert)
- [Workflows error handling](https://docs.cloud.google.com/workflows/docs/reference/syntax/catching-errors)


### Governance, privacy and operations

- [Transition guide](https://docs.cloud.google.com/knowledge-catalog/docs/transition-dataplex-universal-catalog)
- [Quality scans](https://docs.cloud.google.com/knowledge-catalog/docs/use-auto-data-quality)
- [CLI reference](https://docs.cloud.google.com/sdk/gcloud/reference/dataplex/datascans/create/data-quality)
- [Row policy management](https://docs.cloud.google.com/bigquery/docs/managing-row-level-security)
- [Masking guide](https://docs.cloud.google.com/bigquery/docs/column-data-masking)
- [Column security](https://docs.cloud.google.com/bigquery/docs/column-level-security-intro)
- [Masking](https://docs.cloud.google.com/bigquery/docs/column-data-masking-intro)
- [Row-security best practices](https://docs.cloud.google.com/bigquery/docs/best-practices-row-level-security)
- [Structured de-identification](https://docs.cloud.google.com/sensitive-data-protection/docs/deidentify-sensitive-data)
- [Tokenization and re-identification](https://docs.cloud.google.com/sensitive-data-protection/docs/inspect-sensitive-text-de-identify)
- [Transformation semantics](https://docs.cloud.google.com/sensitive-data-protection/docs/transformations-reference)
- [Audit-log documentation](https://docs.cloud.google.com/bigquery/docs/reference/auditlogs)
- [Cloud Monitoring metric catalog](https://docs.cloud.google.com/monitoring/api/metrics_gcp)
- [Data lineage](https://docs.cloud.google.com/dataplex/docs/about-data-lineage)
- [Storage billing](https://docs.cloud.google.com/bigquery/docs/storage_overview)
- [Time travel](https://docs.cloud.google.com/bigquery/docs/time-travel)
- [Cost controls](https://docs.cloud.google.com/bigquery/docs/best-practices-costs)
- [Billing export](https://docs.cloud.google.com/billing/docs/how-to/export-data-bigquery)


### Modeling, contracts and platform reliability

- [Nested/repeated fields](https://docs.cloud.google.com/bigquery/docs/best-practices-performance-nested)
- [Query syntax](https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax)
- [GoogleSQL data types](https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/data-types)
- [Unenforced keys](https://docs.cloud.google.com/bigquery/docs/primary-foreign-keys)
- [Pub/Sub schemas](https://docs.cloud.google.com/pubsub/docs/schemas)
- [Avro specification](https://avro.apache.org/docs/1.12.0/specification/)
- [Protobuf evolution](https://protobuf.dev/programming-guides/proto3/#updating)
- [BigQuery schema management](https://docs.cloud.google.com/bigquery/docs/managing-table-schemas)
- [Service-account impersonation](https://docs.cloud.google.com/iam/docs/service-account-impersonation)
- [Official Google provider resources](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Private Google Access](https://docs.cloud.google.com/vpc/docs/private-google-access)
- [VPC Service Controls](https://docs.cloud.google.com/vpc-service-controls/docs/overview)
- [Disaster recovery guide](https://docs.cloud.google.com/bigquery/docs/managed-disaster-recovery)
- [Dataset replication](https://docs.cloud.google.com/bigquery/docs/data-replication)
- [Table snapshots](https://docs.cloud.google.com/bigquery/docs/table-snapshots-intro)
- [Pub/Sub reliability](https://docs.cloud.google.com/pubsub/docs/reliability-intro)
- [S3 connector guide](https://docs.cloud.google.com/bigquery/docs/s3-transfer)


| Previous | References | Next |
| --- | :---: | ---: |
| [Reference index](index.md) | [All references](index.md) | [Curriculum audit](curriculum-audit.md) |
