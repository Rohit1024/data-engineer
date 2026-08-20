---
icon: lucide/git-compare
---

# Google Cloud Workflows vs Cloud Composer: When to use serverless orchestration

Google Cloud offers two primary workflow orchestration tools: Cloud Composer (managed Apache Airflow) and Google Cloud Workflows (a serverless, low-latency JSON/YAML state machine). Sizing complexity and latency requirements determines which engine to deploy.

---

## Architectural and runtime comparison

``` mermaid
flowchart TD
    subgraph CloudWorkflows["Cloud Workflows (Serverless State Machine)"]
        WStep1["Eventarc Trigger / HTTP Call"] --> WStep2["Direct GCP API Call (BigQuery Job)"]
        WStep2 --> WStep3["Cloud Function Invocation"]
        WStep3 --> WDone["Complete in Milliseconds (Billed per Step)"]
    end

    subgraph CloudComposer["Cloud Composer (Airflow 2.x on GKE)"]
        CSched["Airflow Scheduler Loop"] --> CQueue["Celery Redis Queue"]
        CQueue --> CWorker["GKE Worker Pod"]
        CWorker --> CExec["Operator Execution & Deferral"]
    end

    CloudWorkflows ~~~ CloudComposer
```

---

## Feature and cost comparison matrix

| Dimension | Google Cloud Workflows | Cloud Composer (Airflow) |
| :--- | :--- | :--- |
| **Infrastructure** | Fully serverless (zero provisioning) | Managed GKE Autopilot cluster + Cloud SQL |
| **Base cost** | $0/month (5,000 internal steps free/mo) | ~$350 to $700+/month base cluster cost |
| **Startup / Step latency** | Sub-100ms | 10 to 60 seconds (scheduler polling) |
| **Execution model** | Declarative YAML/JSON state machine | Python code DAGs |
| **Cross-cloud connectors** | HTTP REST endpoints | Hundreds of pre-built community providers |
| **Data pipeline UI** | GCP Console execution visualizer | Airflow Web UI (Grid view, Gantt, Graph) |
| **Best use case** | Event-driven microservices, instant alerting | Complex enterprise ELT pipelines with dependencies |

---

## Complete Cloud Workflows YAML definition

Save as `workflows/trigger_bq_and_alert.yaml`:

```yaml
main:
  params: [args]
  steps:
    - init:
        assign:
          - projectId: ${sys.get_env("GOOGLE_CLOUD_PROJECT_NUMBER")}
          - datasetId: "analytics_mart"
          - queryText: "CALL `analytics_mart.sp_refresh_daily_summary`();"

    - runBigQueryJob:
        call: googleapis.bigquery.v2.jobs.insert
        args:
          projectId: ${projectId}
          body:
            configuration:
              query:
                query: ${queryText}
                useLegacySql: false
        result: bqJob

    - waitForQuery:
        call: googleapis.bigquery.v2.jobs.getQueryResults
        args:
          projectId: ${projectId}
          jobId: ${bqJob.jobReference.jobId}
        result: queryResult

    - checkStatus:
        switch:
          - condition: ${queryResult.jobComplete == true}
            next: sendSlackNotification
        next: waitBeforeRetry

    - waitBeforeRetry:
        call: sys.sleep
        args:
          seconds: 5
        next: waitForQuery

    - sendSlackNotification:
        call: http.post
        args:
          url: "https://hooks.slack.com/services/T00/B00/XXXXX"
          body:
            text: "Daily BigQuery stored procedure executed successfully."
        result: slackResponse

    - finish:
        return:
          status: "SUCCESS"
          jobId: ${bqJob.jobReference.jobId}
```

Deploy and execute with `gcloud`:

```bash
# Deploy workflow
gcloud workflows deploy daily-bq-summary-workflow \
    --source=workflows/trigger_bq_and_alert.yaml \
    --location=us-central1

# Execute workflow manually
gcloud workflows run daily-bq-summary-workflow \
    --location=us-central1
```

---

## Decision heuristics

1. Choose **Cloud Workflows** for event-driven pipelines triggered by GCS uploads or Pub/Sub events where immediate execution (sub-second) is required, or when total pipeline volume does not justify the $350+/month cost of a Composer cluster.
2. Choose **Cloud Composer** for scheduled, multi-team data platforms with complex DAG dependencies, cross-cloud data movement (AWS S3, Snowflake, Salesforce), or custom Python logic.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0030: Dynamic Task Mapping & XComs](0030-dynamic-task-mapping-airflow-best-practices.md) | [All Lessons (Index)](index.md) | [0032: Dataplex Architecture](0032-dataplex-architecture-data-quality.md) |
