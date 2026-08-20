---
icon: lucide/database
---

# dbt Core with dbt-bigquery: Models, seeds, snapshots, and Jinja macros

dbt (data build tool) enables data engineering teams to define, test, document, and version-control SQL transformation pipelines using software engineering best practices. The `dbt-bigquery` adapter leverages BigQuery's native partitioning, clustering, and merge features.

---

## Architecture of dbt with BigQuery

``` mermaid
flowchart TD
    subgraph dbtProject["dbt Project (Code & Configurations)"]
        Sources["sources.yml (Source Declarations)"]
        Models["models/ (SQL + Jinja)"]
        Macros["macros/ (Reusable Jinja Functions)"]
        Snapshots["snapshots/ (SCD Type 2 Historization)"]
        Tests["tests/ (Data Quality Assertions)"]
    end

    subgraph Compiler["dbt Compiler"]
        Graph["DAG Dependency Resolution via ref() & source()"]
    end

    subgraph BigQueryExecution["BigQuery Target Datasets"]
        BQStaging["Staging Views (stg_*)"]
        BQIntermediate["Intermediate Tables (int_*)"]
        BQMarts["Production Marts (fct_*, dim_*)"]
    end

    dbtProject --> Compiler
    Compiler --> BigQueryExecution
```

---

## Authentication and `profiles.yml`

Configure `~/.dbt/profiles.yml` using Google Application Default Credentials (ADC) for local development or service account keys for production CI/CD:

```yaml
ecommerce_analytics:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: oauth
      project: my-gcp-dev-project
      dataset: dbt_rohit
      threads: 8
      location: US
      priority: interactive
      retries: 1
    prod:
      type: bigquery
      method: service-account
      project: my-gcp-prod-project
      dataset: analytics_mart
      threads: 16
      keyfile: /secrets/dbt-service-account.json
      location: US
      priority: interactive
      retries: 2
```

---

## Incremental models in dbt with BigQuery partitioning

Create `models/marts/fct_orders.sql`:

```sql
{{
  config(
    materialized = 'incremental',
    unique_key = 'order_id',
    incremental_strategy = 'merge',
    partition_by = {
      'field': 'order_timestamp',
      'data_type': 'timestamp',
      'granularity': 'day'
    },
    cluster_by = ['merchant_id', 'status']
  )
}}

WITH source_data AS (
  SELECT
    order_id,
    customer_id,
    merchant_id,
    order_amount,
    status,
    order_timestamp,
    updated_at
  FROM {{ source('raw_backend', 'orders') }}
  {% if is_incremental() %}
    -- Lookback 3 days to catch late-arriving updates
    WHERE updated_at >= (
      SELECT TIMESTAMP_SUB(MAX(updated_at), INTERVAL 3 DAY)
      FROM {{ this }}
    )
  {% endif %}
)

SELECT * FROM source_data
```

---

## Slowly Changing Dimensions (SCD Type 2) with dbt Snapshots

dbt Snapshots track historical record changes over time by generating `dbt_valid_from` and `dbt_valid_to` timestamp columns.

Create `snapshots/customers_snapshot.sql`:

```sql
{% snapshot customers_snapshot %}

{{
  config(
    target_database='my-gcp-prod-project',
    target_schema='analytics_snapshots',
    unique_key='customer_id',
    strategy='timestamp',
    updated_at='last_modified_timestamp',
    invalidate_hard_deletes=True
  )
}}

SELECT
  customer_id,
  email,
  subscription_tier,
  shipping_address,
  last_modified_timestamp
FROM {{ source('raw_backend', 'customers') }}

{% endsnapshot %}
```

When a customer changes their `subscription_tier` from "Basic" to "Enterprise", dbt marks the old record's `dbt_valid_to` timestamp and inserts a new active row where `dbt_valid_to IS NULL`.

---

## Testing and running with the dbt CLI

```bash
# 1. Test database connection
dbt debug

# 2. Run models and incremental builds
dbt run --select marts.fct_orders

# 3. Execute generic and singular data quality tests
dbt test

# 4. Take historical snapshot
dbt snapshot
```

---

## Summary heuristics

1. Use `incremental_strategy = 'merge'` for transactional fact tables with updates and `unique_key` identifiers.
2. Use `dbt snapshot` with `strategy='timestamp'` to capture SCD Type 2 dimension histories without writing manual boilerplate SQL.
3. Configure `threads` based on query concurrency limits to prevent BigQuery API quota exhaustion.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0025: Writing Dataform SQLX & Assertions](0025-writing-dataform-sqlx-assertions.md) | [All Lessons (Index)](index.md) | [0027: Transformation CI/CD & Testing](0027-transformation-pipelines-cicd.md) |
