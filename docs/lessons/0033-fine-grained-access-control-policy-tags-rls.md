---
icon: lucide/lock
---

# Fine-grained access control: Column-level security and row-level security in BigQuery

Enterprise data platforms require restricting access to sensitive columns (PII, salary, SSN) and sensitive rows (tenant partitions, regional boundaries) without creating dozens of duplicate physical views. BigQuery enforces fine-grained access control natively via Policy Tags (Column-Level Security) and Row-Level Access Policies.

---

## Access control architecture

``` mermaid
flowchart TD
    User["Analyst Query: SELECT name, ssn, country, revenue FROM customers"] --> PolicyEngine["BigQuery IAM & Governance Policy Engine"]

    subgraph ColumnSecurity["Column-Level Security (Policy Tags)"]
        TagCheck{"Has 'Fine-Grained Reader' Role on 'SSN' Tag?"}
        TagCheck -- "Yes" --> ShowSSN["Expose Raw SSN"]
        TagCheck -- "No (Masking Rule)" --> MaskSSN["Expose Masked: 'XXX-XX-1234' or SHA256"]
    end

    subgraph RowSecurity["Row-Level Security (Row Access Policies)"]
        RowCheck["Filter Predicate: country = SESSION_USER_COUNTRY()"]
    end

    PolicyEngine --> ColumnSecurity
    PolicyEngine --> RowSecurity
    ColumnSecurity --> FilteredResult["Unified Result Set (Filtered Rows + Masked Columns)"]
    RowSecurity --> FilteredResult
```

---

## 1. Column-level security and dynamic data masking

Column-level security assigns policy tags created in Data Catalog taxonomies directly to schema columns.

### Creating a taxonomy and assigning data masking rules

```bash
# 1. Create a policy tag taxonomy
gcloud data-catalog taxonomies create \
    --location=us-central1 \
    --display-name="PII Taxonomy" \
    --activated-policy-types=FINE_GRAINED_ACCESS_CONTROL

# 2. Create child policy tags
gcloud data-catalog taxonomies policy-tags create \
    --location=us-central1 \
    --taxonomy="projects/my-gcp-project/locations/us-central1/taxonomies/PII_TAXONOMY_ID" \
    --display-name="SSN_Confidential"
```

### Applying policy tags and masking rules with SQL

```sql
-- Alter table column to attach policy tag
ALTER TABLE `my_project.analytics_mart.dim_customers`
ALTER COLUMN ssn
SET POLICY TAGS = ('projects/my-project/locations/us-central1/taxonomies/PII_TAXONOMY_ID/policyTags/TAG_SSN');

-- Define dynamic data masking policy on the tag
CREATE OR REPLACE MASKING POLICY `my_project.us.ssn_mask`
OPTIONS (
  masking_expression = 'SHA256(ssn)'
)
TO ('group:business-analysts@company.com');
```

When users in the `business-analysts` group run `SELECT ssn`, they receive the deterministic SHA-256 hash without seeing the plain-text Social Security Number.

---

## 2. Row-level security (Row access policies)

Row access policies restrict visible records based on the identity of the querying user evaluated at query time using `SESSION_USER()`.

```sql
CREATE OR REPLACE ROW ACCESS POLICY regional_sales_filter
ON `my_project.analytics_mart.fact_sales`
GRANT TO ('group:emea-sales@company.com')
FILTER USING (region = 'EMEA');

CREATE OR REPLACE ROW ACCESS POLICY admin_full_access
ON `my_project.analytics_mart.fact_sales`
GRANT TO ('group:executive-leaders@company.com')
FILTER USING (TRUE);
```

When an analyst in `emea-sales@company.com` queries `fact_sales`, BigQuery automatically appends `AND region = 'EMEA'` to the query plan before scanning Capacitor blocks.

---

## Dynamic data masking vs Physical views

| Dimension | Dynamic Policy Tags / RLS | Physical Materialized Views |
| :--- | :--- | :--- |
| **Table maintenance** | Single table (Zero duplicate DDL) | Hundreds of custom views for each user group |
| **Storage cost** | Zero duplication cost | Additional storage cost per materialized replica |
| **Security auditability** | Centralized in Data Catalog | Scattered across SQL view definitions |
| **Query performance** | Direct execution in Dremel engine | Fast, but fragile to view hierarchy changes |

---

## Summary heuristics

1. Use **Policy Tags with Dynamic Data Masking** for sensitive columns (SSN, credit card, email) instead of physically masking data in staging pipelines.
2. Use **Row Access Policies** with `SESSION_USER()` or authorized security mapping tables to enforce multi-tenant isolation on a single fact table.
3. Users without explicit row access policy permissions will see **zero rows** when querying a table protected by row-level security.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0032: Dataplex Architecture](0032-dataplex-architecture-data-quality.md) | [All Lessons (Index)](index.md) | [0034: Automated PII Masking with Cloud DLP](0034-automated-pii-masking-cloud-dlp.md) |
