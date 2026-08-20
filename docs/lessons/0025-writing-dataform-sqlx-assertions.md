---
icon: lucide/code
---

# Writing Dataform SQLX: Declarations, incremental tables, and assertions

Dataform uses SQLX files to combine declarative SQL with metadata configuration and JavaScript logic. It automatically calculates dependency order by analyzing `ref()` calls across models.

---

## The SQLX structure

A `.sqlx` file consists of a `config {}` block followed by standard BigQuery SQL:

``` mermaid
flowchart TD
    ConfigBlock["config { type: 'table', dependencies: [...], assertions: {...} }"]
    SQLBody["SELECT ... FROM ${ref('source_table')} WHERE ..."]

    ConfigBlock --> Compiler["Dataform Engine"]
    SQLBody --> Compiler
    Compiler --> ExecutableSQL["Generated BigQuery DDL / DML Query"]
```

---

## 1. Declaring external data sources

Create `definitions/sources/raw_orders.sqlx`:

```sql
config {
  type: "declaration",
  database: "my-gcp-project",
  schema: "raw_landing",
  name: "orders_stream",
  description: "Raw ingested orders streamed from Pub/Sub"
}
```

---

## 2. Incremental tables with `when(incremental(), ...)`

Incremental tables update existing target tables by querying only new or modified rows since the last execution run, avoiding full table scans.

Create `definitions/marts/fact_orders_incremental.sqlx`:

```sql
config {
  type: "incremental",
  schema: "analytics_mart",
  uniqueKey: ["order_id"],
  bigquery: {
    partitionBy: "DATE(order_timestamp)",
    clusterBy: ["customer_id", "status"]
  },
  assertions: {
    uniqueKey: ["order_id"],
    nonNull: ["order_id", "customer_id", "order_amount"]
  }
}

SELECT
  order_id,
  customer_id,
  order_amount,
  status,
  order_timestamp,
  CURRENT_TIMESTAMP() AS updated_at
FROM ${ref("orders_stream")}

${when(incremental(), `
  WHERE order_timestamp > (
    SELECT MAX(order_timestamp) FROM ${self()}
  )
`)}
```

- `${ref("orders_stream")}` establishes the dependency relationship in the DAG.
- `${self()}` resolves to the current destination table.
- `uniqueKey: ["order_id"]` forces Dataform to generate an automatic `MERGE` statement instead of a simple append, updating matching existing rows.

---

## 3. Data quality assertions

Dataform supports built-in assertions inside `config {}` and custom assertion files.

### Built-in assertions
- `uniqueKey`: Asserts column or composite columns are globally unique.
- `nonNull`: Asserts specified columns contain zero null values.
- `rowConditions`: Evaluates arbitrary boolean SQL predicates (e.g. `order_amount > 0`).

### Custom assertion file
Create `definitions/assertions/assert_no_negative_revenue.sqlx`:

```sql
config {
  type: "assertion",
  schema: "dataform_assertions",
  description: "Asserts that total daily merchant revenue is never negative"
}

SELECT
  merchant_id,
  SUM(order_amount) AS total_revenue
FROM ${ref("fact_orders_incremental")}
GROUP BY merchant_id
HAVING total_revenue < 0
```

An assertion passes if the query returns **0 rows**. If any row is returned, the assertion fails and halts downstream pipeline execution.

---

## JavaScript helpers inside `includes/`

Create `includes/date_helpers.js`:

```javascript
function formatAuditTimestamp() {
  return "CURRENT_TIMESTAMP() AS ingested_at";
}

function truncateMonth(columnName) {
  return `DATE_TRUNC(DATE(${columnName}), MONTH)`;
}

module.exports = {
  formatAuditTimestamp,
  truncateMonth
};
```

Use in SQLX models:

```sql
config { type: "table" }

SELECT
  order_id,
  ${date_helpers.truncateMonth("order_timestamp")} AS order_month,
  ${date_helpers.formatAuditTimestamp()}
FROM ${ref("raw_orders")}
```

---

## Summary heuristics

1. Use `type: "incremental"` with `uniqueKey` on high-volume fact tables to perform automated `MERGE` updates.
2. Add `nonNull` and `uniqueKey` assertions on all primary keys in staging and mart models.
3. Keep complex business logic out of JavaScript includes; reserve `.js` files for repetitive boilerplate SQL generators.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0024: Dataform Foundations](0024-dataform-foundations-workflow-settings.md) | [All Lessons (Index)](index.md) | [0026: dbt Core with dbt-bigquery](0026-dbt-core-bigquery-models-snapshots.md) |
