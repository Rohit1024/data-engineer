---
icon: lucide/git-pull-request
---

# CI/CD testing and deployment for transformation pipelines

Deploying SQL transformation pipelines requires automated validation, unit testing, and isolated staging runs before code merges to production. Using Slim CI techniques with Cloud Build or GitHub Actions ensures fast feedback cycles while minimizing BigQuery query costs.

---

## Slim CI workflow architecture

``` mermaid
flowchart TD
    PR["Developer Opens Pull Request (Modifies stg_orders.sql)"] --> Trigger["CI Pipeline Triggered (Cloud Build / GitHub Actions)"]
    Trigger --> FetchState["Fetch Production manifest.json from GCS"]
    FetchState --> SlimSelect["Compute Modified Subset: state:modified+"]
    SlimSelect --> CreateSandbox["Create Ephemeral PR Dataset: pr_dataset_1234"]
    CreateSandbox --> RunModels["Execute dbt run --select state:modified+"]
    RunModels --> RunTests["Execute dbt test --select state:modified+"]
    RunTests --> Gate{"Tests Passed?"}
    Gate -- "Yes" --> AllowMerge["Approve PR for Merge to Main"]
    Gate -- "No" --> BlockMerge["Block PR & Emit Failure Report"]
```

---

## Ephemeral PR sandbox creation

In pull request validation:
1. The CI pipeline creates an isolated BigQuery dataset named `pr_sandbox_<pr_number>`.
2. Modified models build inside the ephemeral dataset.
3. Tests run against the newly built tables.
4. On PR merge or closure, a post-action script drops the ephemeral dataset to avoid clutter and storage costs.

---

## GitHub Actions workflow for dbt Slim CI

Save as `.github/workflows/dbt_ci.yml`:

```yaml
name: dbt Slim CI

on:
  pull_request:
    paths:
      - 'models/**'
      - 'snapshots/**'
      - 'tests/**'
      - 'dbt_project.yml'

jobs:
  validate_transformations:
    runs-on: ubuntu-latest
    env:
      DBT_PROFILES_DIR: ./ci
      PR_DATASET: "ci_pr_${{ github.event.number }}"

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_CI_SA_KEY }}

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dbt-bigquery
        run: pip install dbt-bigquery

      - name: Download Production State Manifest
        run: |
          mkdir -p prod_state
          gcloud storage cp gs://my-dbt-artifacts-bucket/production/manifest.json ./prod_state/manifest.json || true

      - name: Run Modified Models and Downstream Dependencies
        run: |
          dbt run \
            --target ci \
            --vars "ci_dataset: $PR_DATASET" \
            --select state:modified+ \
            --state ./prod_state

      - name: Run Data Quality Tests on Modified Models
        run: |
          dbt test \
            --target ci \
            --vars "ci_dataset: $PR_DATASET" \
            --select state:modified+ \
            --state ./prod_state

      - name: Clean Up Ephemeral Dataset
        if: always()
        run: |
          bq rm -r -f -d "my-gcp-dev-project:$PR_DATASET"
```

---

## Dataform CI/CD compilation and release configuration

For Dataform repositories hosted on GCP, configure **Release Configurations** and **Workflow Invocations** using Google Cloud Build:

```bash
# 1. Compile Dataform code against target environment
gcloud dataform compilation-results create \
    --repository=ecommerce-dataform-repo \
    --location=us-central1 \
    --git-commitish=main

# 2. Trigger workflow execution from the latest compilation
gcloud dataform workflow-invocations create \
    --repository=ecommerce-dataform-repo \
    --location=us-central1 \
    --compilation-result="projects/my-gcp-project/locations/us-central1/repositories/ecommerce-dataform-repo/compilationResults/latest"
```

---

## Summary heuristics

1. Use `state:modified+` (Slim CI) to only compile, run, and test models changed in the pull request, cutting CI execution time from 45 minutes to 2 minutes.
2. Store production `manifest.json` artifacts in GCS upon every merge to `main`.
3. Always drop ephemeral PR datasets in CI cleanup steps (`bq rm -r -f -d`) to prevent abandoned datasets from accumulating.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0026: dbt Core with dbt-bigquery](0026-dbt-core-bigquery-models-snapshots.md) | [All Lessons (Index)](index.md) | [0028: Cloud Composer Architecture](0028-cloud-composer-architecture-gke.md) |
