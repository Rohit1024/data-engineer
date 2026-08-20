---
icon: lucide/file-code
---

# Dataform and dbt-bigquery cheatsheet

Quick reference syntax for Dataform SQLX, dbt Core models, snapshot configurations, and Slim CI execution patterns.

---

## Transformation framework comparison

``` mermaid
flowchart TD
    subgraph Dataform["Google Cloud Dataform (GCP Native)"]
        D1["SQLX Files (config + SQL + JS)"] --> D2["Compiled via @dataform/cli or API"]
        D2 --> D3["Direct Serverless BigQuery Execution"]
    end

    subgraph dbtCore["dbt Core + dbt-bigquery (Open Source)"]
        B1["SQL Models + Jinja + YAML"] --> B2["Compiled via dbt CLI"]
        B2 --> B3["Orchestrated via Airflow / dbt Cloud"]
    end

    Dataform ~~~ dbtCore
```

---

## Dataform SQLX patterns

### Incremental table with assertions

```sql
config {
  type: "incremental",
  schema: "analytics_mart",
  uniqueKey: ["order_id"],
  bigquery: {
    partitionBy: "DATE(event_timestamp)",
    clusterBy: ["customer_id", "status"]
  },
  assertions: {
    uniqueKey: ["order_id"],
    nonNull: ["order_id", "order_amount"]
  }
}

SELECT
  order_id,
  customer_id,
  order_amount,
  status,
  event_timestamp,
  CURRENT_TIMESTAMP() AS updated_at
FROM ${ref("raw_orders")}

${when(incremental(), `
  WHERE event_timestamp > (
    SELECT MAX(event_timestamp) FROM ${self()}
  )
`)}
```

### Dataform CLI commands

```bash
# Compile and validate SQLX dependencies locally
dataform compile

# Dry-run execution
dataform run --dry-run

# Run only specific tag and downstream models
dataform run --tags "hourly_marts" --include-dependents
```

---

## dbt-bigquery model patterns

### Incremental model with partition and cluster config

```sql
{{
  config(
    materialized = 'incremental',
    unique_key = 'order_id',
    incremental_strategy = 'merge',
    partition_by = {
      'field': 'event_timestamp',
      'data_type': 'timestamp',
      'granularity': 'day'
    },
    cluster_by = ['merchant_id', 'status']
  )
}}

WITH source_data AS (
  SELECT * FROM {{ source('raw_backend', 'orders') }}
  {% if is_incremental() %}
    WHERE updated_at >= (
      SELECT TIMESTAMP_SUB(MAX(updated_at), INTERVAL 3 DAY)
      FROM {{ this }}
    )
  {% endif %}
)

SELECT * FROM source_data
```

### dbt CLI commands and Slim CI

```bash
# Run and test all models
dbt run
dbt test

# Slim CI: Run only modified models and downstream dependencies
dbt run \
    --select state:modified+ \
    --state ./prod_state_artifacts/

# Execute SCD Type 2 dimension snapshot
dbt snapshot
```

---

| Previous Cheatsheet | All Cheatsheets | Next Cheatsheet |
| :--- | :---: | ---: |
| [05: Dataproc & PySpark](05-dataproc-pyspark.md) | [Cheatsheets Index](index.md) | [07: Cloud Composer & Airflow](07-cloud-composer-airflow.md) |
