---
icon: lucide/shield
---

# Dataplex architecture: Lakes, zones, assets, and data quality tasks

Google Cloud Dataplex is an intelligent data fabric management platform. It allows organizations to centrally discover, manage, monitor, and govern distributed data assets stored across Cloud Storage buckets and BigQuery datasets without moving data.

---

## Dataplex organizational hierarchy

``` mermaid
flowchart TD
    Org["Google Cloud Organization"] --> Lake["Dataplex Lake: 'finance_analytics_lake'"]
    Lake --> RawZone["Raw Data Zone (Landing & Ingestion Storage)"]
    Lake --> CuratedZone["Curated Data Zone (Cleaned & Conformed)"]

    RawZone --> Asset1["Asset 1: gs://lake-bronze-finance/"]
    RawZone --> Asset2["Asset 2: BigQuery Dataset 'raw_transactions'"]

    CuratedZone --> Asset3["Asset 3: BigQuery Dataset 'gold_financial_marts'"]
    CuratedZone --> Asset4["Asset 4: gs://lake-silver-finance/ (Parquet)"]
```

1. **Lake**: A logical container representing a business domain or data domain (e.g. Sales, Marketing, Supply Chain).
2. **Zone**: Categorizes data within a lake by readiness or security tier:
   - **Raw zone**: Unstructured or semi-structured data with loose formatting rules.
   - **Curated zone**: Uniform, schema-enforced, and conformed data ready for analytical consumption.
3. **Asset**: Binds an underlying physical Cloud Storage bucket or BigQuery dataset into the zone.

---

## Automated metadata discovery and cataloging

When you attach an asset to a Dataplex zone, Dataplex runs discovery jobs that:
- Scan GCS buckets for Parquet, Avro, ORC, CSV, and JSON files.
- Infer schemas and partition layouts automatically.
- Register external tables in the central Data Catalog and BigQuery metastore.

---

## Dataplex Auto Data Quality (AutoDQ)

Dataplex AutoDQ runs serverless data quality validation rules defined in YAML against BigQuery tables, logging test results directly to Cloud Monitoring and BigQuery.

### AutoDQ rule specification

Save as `data_quality_rules.yaml`:

```yaml
metadata:
  table: projects/my-gcp-project/datasets/analytics_mart/tables/fact_order_events

ruleDimensions:
  - completeness
  - validity
  - uniqueness

rules:
  - dimension: uniqueness
    name: unique_order_id
    table: fact_order_events
    column: order_id
    unique: true

  - dimension: completeness
    name: non_null_customer
    table: fact_order_events
    column: customer_id
    nonNull: true

  - dimension: validity
    name: positive_order_amount
    table: fact_order_events
    column: order_amount
    rangeExpectation:
      minValue: 0.01

  - dimension: validity
    name: valid_order_status
    table: fact_order_events
    column: order_status
    setExpectation:
      values:
        - "PENDING"
        - "COMPLETED"
        - "CANCELLED"
        - "REFUNDED"
```

### Running the Data Quality scan with gcloud

```bash
# 1. Create the data quality scan task
gcloud dataplex datascans create data-quality orders-dq-scan \
    --location=us-central1 \
    --data-source-table="projects/my-gcp-project/datasets/analytics_mart/tables/fact_order_events" \
    --data-quality-spec-file="data_quality_rules.yaml"

# 2. Run the scan immediately
gcloud dataplex datascans run orders-dq-scan \
    --location=us-central1
```

---

## Summary heuristics

1. Structure Dataplex lakes by domain (e.g. Sales, Logistics) rather than by environment, creating Raw and Curated zones within each domain lake.
2. Use Dataplex AutoDQ YAML rules for automated, scheduled data quality checks instead of maintaining custom query scripts.
3. Leverage Dataplex discovery to automatically register Hive-partitioned GCS files as external BigLake tables without manual DDL maintenance.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0031: Workflows vs Cloud Composer](0031-cloud-workflows-vs-composer.md) | [All Lessons (Index)](index.md) | [0033: Fine-Grained Access Control](0033-fine-grained-access-control-policy-tags-rls.md) |
