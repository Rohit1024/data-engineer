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

WITH incoming AS (
  SELECT order_id, customer_id, order_amount, status, order_timestamp,
         version, ingested_at
  FROM ${ref("orders_stream")}
  ${when(incremental(), `
    WHERE ingested_at >= COALESCE(
      (SELECT TIMESTAMP_SUB(MAX(ingested_at), INTERVAL 3 DAY) FROM ${self()}),
      TIMESTAMP '1970-01-01'
    )
  `)}
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY order_id ORDER BY version DESC, ingested_at DESC
  ) = 1
)
SELECT source.* FROM incoming source
${when(incremental(), `
  LEFT JOIN ${self()} target USING (order_id)
  WHERE target.order_id IS NULL OR source.version > target.version
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

An assertion passes if the query returns **0 rows**. A returned row fails that assertion. Downstream actions must explicitly depend on the assertion to use it as a publication gate; a model reference alone does not imply a dependency on all its assertions.

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
FROM ${ref("orders_stream")}
```

---

## Summary heuristics

1. Use `type: "incremental"` with `uniqueKey` on high-volume fact tables to perform automated `MERGE` updates.
2. Add `nonNull` and `uniqueKey` assertions on all primary keys in staging and mart models.
3. Keep complex business logic out of JavaScript includes; reserve `.js` files for repetitive boilerplate SQL generators.

---

## State the incremental contract before trusting the merge

The revised example requires source `version` and `ingested_at` columns. `version` increases per order, and `ingested_at` is a retained arrival timestamp. Validate non-null identity/version, immutable payload per key/version and one resolved source winner before running. The target comparison prevents an older replayed version from overwriting newer state. Equal-version conflicts must fail a separate validation; the filter must not silently hide them.

Using `MAX(order_timestamp)` alone misses late-arriving orders and updates to old orders. `MAX(ingested_at)` with a three-day overlap improves arrival coverage and handles an empty target through `COALESCE`, but it is still a bounded recovery allowance. A longer outage or timestamp backdating requires a recorded cursor, explicit backfill or reconciliation. Version safety does not prove completeness.

`uniqueKey` configures merge matching; it does not deduplicate an ambiguous source or enforce uniqueness as a database constraint. Source filtering and target partition pruning are separate. If you use `updatePartitionFilter`, verify it cannot exclude an existing matching key and cause another insert. Deletes need sequenced tombstones and explicit mutation logic, not an assumption that absent source rows vanish.

## Make quality a dependency

Use a named assertion such as `assert_no_negative_revenue`, and add an explicit dependency on it in the model or publication action that must wait. For built-in assertions, inspect their generated action names or use documented assertion-dependency configuration. An assertion typically runs after its referenced model has materialized; it does not roll that model back. Build in staging and publish only after the required assertions succeed.

## Exercise and expected outcomes

Load order 101 version 2, then replay version 1 with a later arrival time. Expect version 2 to survive. Insert conflicting version-2 values and require the conflict assertion to fail before publication. Try an empty incremental target and confirm its first delta does not disappear because `MAX` was NULL. Finally submit a source update older than the lookback and explain the explicit backfill needed.

Sources: [incremental tables](https://docs.cloud.google.com/dataform/docs/create-tables), [assertions](https://docs.cloud.google.com/dataform/docs/assertions), and [assertion dependencies](https://docs.cloud.google.com/dataform/docs/dependencies).

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0024: Dataform Foundations](0024-dataform-foundations-workflow-settings.md) | [All Lessons (Index)](index.md) | [0026: dbt Core with dbt-bigquery](0026-dbt-core-bigquery-models-snapshots.md) |
