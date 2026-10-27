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

Configure `~/.dbt/profiles.yml` using ADC for local development and workload identity or service-account impersonation for automation:

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
      method: oauth
      project: my-gcp-prod-project
      dataset: analytics_mart
      threads: 16
      impersonate_service_account: dbt-prod@my-gcp-prod-project.iam.gserviceaccount.com
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
      SELECT COALESCE(TIMESTAMP_SUB(MAX(updated_at), INTERVAL 3 DAY), TIMESTAMP '1970-01-01')
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

## Complete the source, seed and macro concepts

Declare external sources in `models/sources.yml`; `source()` does not create the upstream tables:

```yaml
version: 2
sources:
  - name: raw_backend
    database: "{{ target.project }}"
    schema: raw_backend
    tables:
      - name: orders
      - name: customers
```

Keep the physical project/schema appropriate to the selected environment. The incremental example assumes its source already resolves one current row per order with reliable `updated_at`. If it is an event log, deduplicate and order versions first. A three-day timestamp lookback is not proof that all late updates/deletes are captured, and `unique_key` does not enforce source uniqueness. For source deletes, use a defined tombstone or snapshot policy.

A seed loads a small versioned CSV reference table. Put `status,recognized` with rows `paid,true` and `cancelled,false` in `seeds/order_status.csv`, run `dbt seed --select order_status`, and query it through `{{ ref('order_status') }}`. Use seeds for small controlled mappings, not million-row extracts. Define explicit seed types when inference could misinterpret identifiers or booleans.

A macro generates SQL at compilation time. Save this as `macros/cents_to_units.sql`:

```sql
{% macro cents_to_units(column) -%}
  CAST({{ column }} AS NUMERIC) / 100
{%- endmacro %}
```

Use `{{ cents_to_units('amount_cents') }}` in a model. The macro does not loop over live database rows on the Python client; BigQuery evaluates its compiled expression. Inspect `target/compiled` to see that boundary.

## Snapshots and tests have limits

A timestamp snapshot captures changes visible when snapshot runs. If a customer changes tier twice between runs, intermediate states can be missed. Configure deletion handling for the installed dbt version and distinguish observed history from a complete CDC log. Join facts to the proper validity interval when reconstructing historical tier, as in [0041](0041-googlesql-data-modeling.md).

`dbt run` materializes models, `dbt test` checks data, and `dbt build` orders selected resources and their tests. A failing post-build test does not automatically undo an already-created table. Protect production publication through staging and an explicit gate.

## Recall exercise

Run the seed and compile the macro model, then predict what a NULL amount returns. Create an empty incremental target and confirm the `COALESCE` permits loading. Finally explain why snapshots every hour cannot prove all source changes were preserved.

Sources: [incremental models](https://docs.getdbt.com/docs/build/incremental-models), [seeds](https://docs.getdbt.com/docs/build/seeds), [snapshots](https://docs.getdbt.com/docs/build/snapshots), and [BigQuery setup/authentication](https://docs.getdbt.com/docs/core/connect-data-platform/bigquery-setup).

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0025: Writing Dataform SQLX & Assertions](0025-writing-dataform-sqlx-assertions.md) | [All Lessons (Index)](index.md) | [0027: Transformation CI/CD & Testing](0027-transformation-pipelines-cicd.md) |
