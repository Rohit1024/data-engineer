---
icon: lucide/activity
---

# End-to-end pipeline observability: Cloud Monitoring, audit logs, and data lineage

Production data platforms require comprehensive observability across three operational pillars: Metrics (Cloud Monitoring), Logs (Cloud Logging & Audit Logs), and Metadata/Lineage (Dataplex Data Lineage).

---

## Observability and lineage architecture

``` mermaid
flowchart TD
    subgraph DataPlane["Data Pipelines"]
        PS["Cloud Pub/Sub"] --> DF["Cloud Dataflow Pipeline"]
        DF --> BQ["BigQuery Tables"]
        Airflow["Cloud Composer DAGs"] --> BQ
    end

    subgraph ObservabilityLayer["Central Observability & Governance"]
        Metrics["Cloud Monitoring (Watermark Lag, Slot Usage, Backlog)"]
        AuditLogs["Cloud Audit Logs (Data Access & Admin Activity)"]
        Lineage["Dataplex Data Lineage (Automated Column & Table Lineage Graph)"]
    end

    DataPlane --> Metrics
    DataPlane --> AuditLogs
    DataPlane --> Lineage

    Metrics --> AlertEngine["Cloud Monitoring Alert Policies -> PagerDuty / Slack"]
```

---

## Automated data lineage with Dataplex

Dataplex automatically tracks table-level and column-level lineage relationships for:
- BigQuery queries, copy jobs, and scheduled queries.
- Cloud Dataflow streaming and batch pipelines.
- Cloud Composer Airflow DAG executions via the OpenLineage integration.
- Dataproc Spark jobs using the BigQuery connector.

### Querying table lineage via Dataplex API

```bash
gcloud dataplex entries lookup \
    --project=my-gcp-project \
    --location=us-central1 \
    --entry-group="@bigquery" \
    --entry="projects/my-gcp-project/datasets/analytics_mart/tables/daily_revenue"
```

---

## Critical Cloud Monitoring metrics for data pipelines

| Service | Critical metric | Alert threshold |
| :--- | :--- | :--- |
| **Dataflow** | `dataflow.googleapis.com/job/data_watermark_age` | `> 300s` (Indicates stuck processing or sink bottleneck) |
| **Dataflow** | `dataflow.googleapis.com/job/system_lag` | `> 60s` (Indicates pipeline falling behind source stream) |
| **Pub/Sub** | `pubsub.googleapis.com/subscription/oldest_unacked_message_age` | `> 600s` (Subscriber down or processing stalled) |
| **BigQuery** | `bigquery.googleapis.com/slots/total_available` vs `allocated` | Allocated slots `> 95%` for 10 consecutive minutes |
| **Composer** | `composer.googleapis.com/environment/database_health` | `!= 1` (Airflow metadata database unreachable) |

---

## Defining an automated alert policy for Dataflow lag

Save as `alert_policy_dataflow_lag.json`:

```json
{
  "displayName": "Alert: Dataflow Watermark Lag Exceeds 5 Minutes",
  "combiner": "OR",
  "conditions": [
    {
      "displayName": "Dataflow job watermark age > 300s",
      "conditionThreshold": {
        "filter": "resource.type = \"dataflow_job\" AND metric.type = \"dataflow.googleapis.com/job/data_watermark_age\"",
        "comparison": "COMPARISON_GT",
        "thresholdValue": 300,
        "duration": "180s",
        "aggregations": [
          {
            "alignmentPeriod": "60s",
            "perSeriesAligner": "ALIGN_MEAN"
          }
        ]
      }
    }
  ],
  "notificationChannels": [
    "projects/my-gcp-project/notificationChannels/PAGERDUTY_CHANNEL_ID"
  ]
}
```

Deploy with `gcloud`:

```bash
gcloud alpha monitoring policies create --policy-from-file=alert_policy_dataflow_lag.json
```

---

## Log-based metrics and Cloud Audit Logs

Monitor data exfiltration and large ad-hoc scans by querying BigQuery Audit Logs:

```sql
SELECT
  protopayload_auditlog.authenticationInfo.principalEmail AS user_email,
  protopayload_auditlog.servicedata_v1_33.jobCompletedEvent.job.jobStatistics.totalBilledBytes / (1024 * 1024 * 1024 * 1024) AS terabytes_billed,
  protopayload_auditlog.servicedata_v1_33.jobCompletedEvent.job.jobConfiguration.query.query AS query_text
FROM `my-gcp-project.global._Default._AllLogs`
WHERE resource.type = 'bigquery_project'
  AND protopayload_auditlog.methodName = 'jobservice.jobcompleted'
  AND protopayload_auditlog.servicedata_v1_33.jobCompletedEvent.job.jobStatistics.totalBilledBytes > 1099511627776 -- > 1 TB
ORDER BY timestamp DESC;
```

---

## Summary heuristics

1. Set up alert policies on `oldest_unacked_message_age` for Pub/Sub subscriptions and `data_watermark_age` for Dataflow jobs.
2. Enable Dataplex Data Lineage across all production GCP projects to perform impact analysis before altering table schemas.
3. Use Log-Based Alerts on Cloud Audit Logs to notify on queries scanning more than 1 TB.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0034: Automated PII Masking with Cloud DLP](0034-automated-pii-masking-cloud-dlp.md) | [All Lessons (Index)](index.md) | [0036: BigQuery FinOps & Cost Optimization](0036-bigquery-finops-slot-reservations.md) |
