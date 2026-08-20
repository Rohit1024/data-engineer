---
icon: lucide/file-code
---

# Dataform foundations: Repositories, workspaces, and workflow_settings.yaml

Google Cloud Dataform is a fully managed, serverless orchestration and transformation framework native to BigQuery. It compiles SQLX scripts (SQL with JavaScript extensions) into dependency graphs and executes transformations directly inside BigQuery slots.

---

## Dataform repository architecture

``` mermaid
flowchart TD
    subgraph RepoStructure["Dataform Project Structure"]
        Config["workflow_settings.yaml (or dataform.json)"]
        Definitions["definitions/ (SQLX Models, Operations, Assertions)"]
        Includes["includes/ (Reusable JavaScript Helper Functions)"]
    end

    subgraph CompilePhase["Compilation Phase (Dry Run)"]
        Compiler["Dataform Compiler Engine"] --> Graph["Compiled Directed Acyclic Graph (DAG)"]
    end

    subgraph ExecutionPhase["Execution Phase (BigQuery Engine)"]
        Graph --> Slot1["BigQuery DDL / DML Execution"]
        Slot1 --> TargetDataset["Target BigQuery Tables & Views"]
    end

    RepoStructure --> Compiler
```

---

## Repository configuration: `workflow_settings.yaml`

The `workflow_settings.yaml` file defines default BigQuery projects, target datasets, location, and compilation prefixes.

```yaml
defaultProject: "my-analytics-prod"
defaultDataset: "dataform_analytics"
defaultLocation: "US"
defaultAssertionDataset: "dataform_assertions"
projectConfig:
  vars:
    execution_date: "2026-08-20"
```

---

## Environment isolation: Dev, staging, and prod

To prevent developers from overwriting production tables, Dataform uses **Release Configurations** and **Compilation Overrides**:

``` mermaid
flowchart TD
    GitMain["Git Branch: main"] --> ProdConfig["Production Release Config (dataset: 'analytics_mart')"]
    GitDev["Git Branch: dev_rohit"] --> DevConfig["Development Workspace (schema suffix: '_dev_rohit')"]
    ProdConfig --> ProdTables["`analytics_mart.fact_orders`"]
    DevConfig --> DevTables["`analytics_mart_dev_rohit.fact_orders`"]
```

In development workspaces, Dataform appends workspace prefixes to dataset names automatically so developers test against isolated sandboxes.

---

## Developing locally with the Dataform CLI

You can develop, validate, and compile Dataform projects locally using the npm CLI:

```bash
# 1. Install Dataform CLI globally
npm install -g @dataform/cli

# 2. Initialize a new Dataform repository
dataform init . --default-project=my-gcp-project --default-dataset=analytics_staging

# 3. Test compilation and generate compiled SQL DAG
dataform compile

# 4. Dry-run execute all definitions in development
dataform run --dry-run
```

---

## Summary heuristics

1. Use `workflow_settings.yaml` to enforce strict central defaults for dataset locations and assertion destinations.
2. Structure projects with separate folders for `sources/`, `staging/`, `intermediate/`, and `marts/` under `definitions/`.
3. Test compilation locally with `dataform compile` before committing code to prevent broken dependency graphs in production release configurations.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0023: Spark Optimization on GCP](0023-spark-optimization-memory-tuning-gcp.md) | [All Lessons (Index)](index.md) | [0025: Writing Dataform SQLX & Assertions](0025-writing-dataform-sqlx-assertions.md) |
