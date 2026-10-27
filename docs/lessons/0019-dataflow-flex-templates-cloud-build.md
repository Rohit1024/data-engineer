---
icon: lucide/package
---

# Dataflow Flex Templates and CI/CD packaging with Cloud Build

Dataflow Flex Templates package Apache Beam pipelines into container images stored in Google Artifact Registry. Unlike legacy templates with fixed execution graphs, Flex Templates dynamically construct the Beam pipeline DAG at runtime based on user-supplied parameters.

---

## Flex Template packaging architecture

``` mermaid
flowchart TD
    Code["Beam Code (pipeline.py) + Dockerfile + metadata.json"] --> CloudBuild["Cloud Build Packaging"]
    CloudBuild --> Image["Artifact Registry: us-central1-docker.pkg.dev/proj/repo/image:v1"]
    CloudBuild --> Spec["Flex Template Spec File (gs://my-bucket/templates/pipeline.json)"]
    Spec --> Trigger["Launch Request (gcloud / Airflow / Cloud Function)"]
    Trigger --> DataflowService["Dataflow Service Coordinator"]
    DataflowService --> Launcher["Launcher VM pulls template image and constructs graph"]
    Launcher --> WorkerVMs["Workers run the selected Beam SDK environment"]
```

---

## Packaging a Python Beam pipeline

### 1. The Dockerfile

```dockerfile
FROM gcr.io/dataflow-templates-base/python311-template-launcher-base:latest

ENV FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE="/template/requirements.txt"
ENV FLEX_TEMPLATE_PYTHON_PY_FILE="/template/main.py"

COPY requirements.txt /template/
COPY main.py /template/

RUN pip install --no-cache-dir -r $FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE
```

### 2. The metadata file (`metadata.json`)

Define parameters exposed to operators and schedulers:

```json
{
  "name": "PubSub to BigQuery Streaming Aggregator",
  "description": "Streams real-time metrics into BigQuery.",
  "parameters": [
    {
      "name": "input_subscription",
      "label": "Input Pub/Sub Subscription",
      "helpText": "Pub/Sub subscription to pull records from.",
      "isOptional": false,
      "regexes": ["^projects\\/[^\\n\\r\\/]+\\/subscriptions\\/[^\\n\\r\\/]+$"]
    },
    {
      "name": "output_table",
      "label": "Output BigQuery Table",
      "helpText": "Destination table in project:dataset.table format.",
      "isOptional": false
    }
  ]
}
```

---

## Building and staging with Cloud Build

Submit the build to Cloud Build to compile the container and upload the template spec file:

```bash
# 1. Build and push container to Artifact Registry
gcloud builds submit --tag=us-central1-docker.pkg.dev/my-gcp-project/data-pipelines/pubsub-to-bq:v1 .

# 2. Build the Flex Template specification JSON on GCS
gcloud dataflow flex-template build gs://my-pipeline-bucket/templates/pubsub-to-bq.json \
    --image=us-central1-docker.pkg.dev/my-gcp-project/data-pipelines/pubsub-to-bq:v1 \
    --sdk-language=PYTHON \
    --metadata-file=metadata.json
```

---

## Running the Flex Template

Run the staged template via `gcloud` or orchestrate it from Airflow:

```bash
gcloud dataflow flex-template run "pubsub-to-bq-prod-$(date +%s)" \
    --template-file-gcs-location=gs://my-pipeline-bucket/templates/pubsub-to-bq.json \
    --region=us-central1 \
    --enable-streaming-engine \
    --max-workers=10 \
    --parameters \
input_subscription="projects/my-gcp-project/subscriptions/orders-sub",\
output_table="my-gcp-project:analytics_mart.realtime_orders"
```

---

## Summary heuristics

1. Package all production pipelines as Flex Templates to standardize CI/CD releases and lock runtime dependency versions in containers.
2. Store custom Docker images in Artifact Registry in the same region as your Dataflow workers to minimize image pull times.
3. Validate parameter types and regex rules in `metadata.json` to catch operator configuration errors before workers boot.

---

## A launcher image is not automatically the worker SDK image

The Flex Template container starts the pipeline launcher. Worker SDK containers run the element-processing code. Installing a package in the launcher does not by itself prove every worker has it. Use supported dependency staging or a compatible custom SDK container, and keep the launch SDK version consistent with the worker environment. See [Flex Template configuration](https://docs.cloud.google.com/dataflow/docs/guides/templates/configuring-flex-templates) and [custom SDK containers](https://docs.cloud.google.com/dataflow/docs/guides/run-custom-container).

The Dockerfile above demonstrates packaging; `main.py` must actually parse `input_subscription` and `output_table`, preserve runner-supplied pipeline options, construct the graph and wait appropriately. A metadata parameter only describes an argument. It does not implement its behavior. The complete service-managed template lab in [0037](0037-bigquery-ingestion-etl-elt-lab.md#6-method-d-dataflow-streaming-etl) is the runnable reference path.

For a reproducible release, pin dependency versions, launcher base image and custom SDK image digest. Use immutable template-spec names such as `templates/orders/REVISION.json`. Replacing one `latest` JSON or image tag can make a rollback run different code from the original job.

Separate the build identity, job launcher, Dataflow service agent and worker service account. The build identity pushes artifacts; the launcher submits/acts as the worker; workers read source data, stage dependencies and write sinks. Private workers also need permitted network access to APIs, artifacts and staged packages.

## Release and rollback exercise

Build a sandbox template, record its image digest/spec generation and run ID, then deliberately supply an invalid subscription path. Expect parameter validation or a visible launch failure, not a running job with silently ignored parameters. Next remove a worker-only dependency and distinguish launcher success from worker import failure.

??? note "Expected reasoning"
    A successful container build proves packaging completed. A successful launch proves graph submission. A healthy worker and reconciled sink prove more of the runtime path. For rollback, use the recorded immutable artifacts and test state/source compatibility; an older image alone does not restore streaming checkpoints.

See [template troubleshooting](https://docs.cloud.google.com/dataflow/docs/guides/troubleshoot-templates) for launch-network and dependency failures.

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0018: Dataflow Execution Internals](0018-dataflow-execution-internals.md) | [All Lessons (Index)](index.md) | [0020: Cloud Dataproc Architecture](0020-dataproc-architecture-ephemeral-clusters.md) |
