---
icon: lucide/terminal
---

# Dataproc Serverless for Spark: Submitting interactive and batch workloads

Dataproc Serverless runs Apache Spark workloads without requiring you to manage, configure, or tune underlying Compute Engine clusters. You submit Spark code or SQL scripts, and GCP dynamically provisions, scales, and deallocates compute capacity measured in Dataproc Compute Units (DCUs).

---

## Dataproc Serverless architecture

``` mermaid
flowchart TD
    Submit["User / Airflow: gcloud dataproc batches submit"] --> ControlPlane["Dataproc Serverless Control Plane"]
    ControlPlane --> AutoScale["Dynamic DCU Autoscaler (Executors 2 .. 50)"]
    AutoScale --> SparkDriver["Managed Driver Container"]
    AutoScale --> SparkExec["Managed Executor Containers"]
    SparkDriver <--> SparkExec
    SparkExec <--> Storage["Cloud Storage / BigQuery Storage API / Iceberg"]
    SparkDriver --> Cleanup["Auto-Decommission upon Batch Completion"]
```

---

## Submitting a PySpark batch workload

Submit a batch job directly from the terminal without creating a cluster:

```bash
gcloud dataproc batches submit pyspark gs://my-code-bucket/scripts/clean_transactions.py \
    --project=my-gcp-project \
    --region=us-central1 \
    --deps-bucket=gs://my-staging-bucket \
    --subnet=projects/my-gcp-project/regions/us-central1/subnetworks/data-subnet \
    --version=2.1 \
    --properties=spark.dynamicAllocation.maxExecutors=20,spark.driver.cores=4,spark.executor.memory=16g
```

---

## Custom container images for Python dependencies

When pipelines depend on third-party C extensions or specialized Python libraries (e.g. `scikit-learn`, `geopandas`), build a custom container image using the Dataproc Serverless base image:

```dockerfile
FROM gcr.io/dataproc-serverless/spark:latest

USER root
RUN apt-get update && apt-get install -y libspatialindex-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

USER spark
```

Submit batches referencing the custom container:

```bash
gcloud dataproc batches submit pyspark gs://my-code-bucket/scripts/geo_aggregation.py \
    --region=us-central1 \
    --container-image=us-central1-docker.pkg.dev/my-gcp-project/containers/spark-geo:v1
```

---

## Comparison: Managed clusters vs Dataproc Serverless

| Dimension | Dataproc Managed Clusters | Dataproc Serverless |
| :--- | :--- | :--- |
| **Cluster provisioning time** | 90 to 180 seconds | 10 to 30 seconds |
| **Infrastructure management** | Machine types, disk sizes, autoscaling policies | None (fully managed DCUs) |
| **Billing metric** | Compute Engine VM vCPU/RAM + Dataproc premium | DCU-hours ($0.06 per DCU-hour) |
| **Custom open source tooling** | Full root SSH access to VMs, custom daemons (Presto, Flink) | Standard Spark runtime container only |
| **Best fit** | Long-running multi-framework clusters with custom networking | Independent batch ETL workloads and scheduled Airflow tasks |

---

## Summary heuristics

1. Choose **Dataproc Serverless** for scheduled Spark batch workloads to eliminate cluster startup overhead and infrastructure tuning.
2. Ensure the VPC subnet has **Private Google Access** enabled and adequate IP address space for dynamically allocated executor containers.
3. Build custom container images instead of passing large zip packages when Python dependencies exceed a few lightweight packages.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0020: Cloud Dataproc Architecture](0020-dataproc-architecture-ephemeral-clusters.md) | [All Lessons (Index)](index.md) | [0022: PySpark BigQuery Connector](0022-pyspark-bigquery-connector.md) |
