# GCP Data Engineering Resources

## Knowledge

- [Google Cloud Official Documentation](https://cloud.google.com/docs)
  Authoritative specification, reference manuals, and architecture guides across BigQuery, Dataflow, Dataproc, Pub/Sub, and Composer.
- [Google Cloud Architecture Center - Data Analytics](https://cloud.google.com/architecture/data-analytics)
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
