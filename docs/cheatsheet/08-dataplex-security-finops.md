---
icon: lucide/shield-check
---

# Dataplex, security, observability, and FinOps cheatsheet

Quick reference for Dataplex data quality rules, BigQuery column/row-level security, Cloud DLP masking, and FinOps cost controls.

---

## Governance and security controls flow

``` mermaid
flowchart TD
    Data["Data Lake / BigQuery Tables"] --> Dataplex["Dataplex Lakes & Zones (Automated Discovery & Cataloging)"]
    Data --> DQ["Dataplex AutoDQ (Declarative YAML Quality Scans)"]
    Data --> Security["Security Layer (Policy Tags, Masking & Row Access Policies)"]
    Data --> Observability["Observability (Audit Logs & Cloud Monitoring Alerts)"]
    Data --> FinOps["FinOps (Physical Storage Billing & Query Quotas)"]
```

---

## Policy tags and dynamic data masking DDL

```sql
-- Attach policy tag to sensitive column
ALTER TABLE `my_project.analytics.dim_customers`
ALTER COLUMN ssn
SET POLICY TAGS = ('projects/my-proj/locations/us-central1/taxonomies/PII_TAXONOMY/policyTags/TAG_SSN');

-- Define dynamic data masking policy
CREATE OR REPLACE MASKING POLICY `my_project.us.ssn_mask`
OPTIONS (masking_expression = 'SHA256(ssn)')
TO ('group:analysts@company.com');
```

---

## Row-level access policies

```sql
-- Restrict rows by region based on caller group
CREATE OR REPLACE ROW ACCESS POLICY regional_sales_filter
ON `my_project.analytics.fact_sales`
GRANT TO ('group:emea-sales@company.com')
FILTER USING (region = 'EMEA');

-- Full access for admins
CREATE OR REPLACE ROW ACCESS POLICY admin_full_access
ON `my_project.analytics.fact_sales`
GRANT TO ('group:admin-team@company.com')
FILTER USING (TRUE);
```

---

## Dataplex Auto Data Quality YAML spec

Save as `data_quality.yaml`:

```yaml
metadata:
  table: projects/my-gcp-project/datasets/analytics/tables/fact_orders

rules:
  - dimension: uniqueness
    name: unique_order_id
    column: order_id
    unique: true

  - dimension: completeness
    name: non_null_amount
    column: order_amount
    nonNull: true

  - dimension: validity
    name: positive_amount
    column: order_amount
    rangeExpectation:
      minValue: 0.01
```

Run scan with `gcloud`:

```bash
gcloud dataplex datascans create data-quality orders-dq \
    --location=us-central1 \
    --data-source-table="projects/my-gcp-project/datasets/analytics/tables/fact_orders" \
    --data-quality-spec-file="data_quality.yaml"
```

---

## BigQuery FinOps and storage billing optimization

```sql
-- Switch dataset storage billing model to PHYSICAL to cut costs on compressed data
ALTER SCHEMA `my_project.analytics`
SET OPTIONS(
  storage_billing_model = 'PHYSICAL'
);
```

### Python query budget safeguard

```python
from google.cloud import bigquery

client = bigquery.Client()
job_config = bigquery.QueryJobConfig()

# Fail query if scanned data exceeds 100 GB ($0.62)
job_config.maximum_bytes_billed = 100 * 1024 * 1024 * 1024

query_job = client.query("SELECT * FROM `my_project.analytics.fact_orders`", job_config=job_config)
```

---

| Previous Cheatsheet | All Cheatsheets | Next Cheatsheet |
| :--- | :---: | ---: |
| [07: Cloud Composer & Airflow](07-cloud-composer-airflow.md) | [Cheatsheets Index](index.md) | *None (All Cheatsheets Complete)* |
