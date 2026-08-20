---
icon: lucide/network
---

# Cloud Composer architecture and GKE environments

Google Cloud Composer 2 is a managed workflow orchestration service built on Apache Airflow 2.x and Google Kubernetes Engine (GKE) Autopilot. It coordinates cross-service data pipelines across BigQuery, Dataflow, Dataproc, and external systems.

---

## Composer 2 internal architecture

Composer 2 separates the Airflow control plane from customer compute resources using GKE Autopilot:

``` mermaid
flowchart TD
    subgraph StorageLayer["GCS Bucket (Environment Storage)"]
        DAGs["gs://composer-bucket/dags/"]
        Plugins["gs://composer-bucket/plugins/"]
        Data["gs://composer-bucket/data/"]
    end

    subgraph ComposerGKE["GKE Autopilot Environment"]
        Webserver["Airflow Webserver (UI)"]
        Scheduler["Airflow Scheduler (1 to N replicas)"]
        Triggerer["Airflow Triggerer (Async event loop)"]
        Workers["Celery Workers (Autoscaling Pods)"]
        RedisQueue["Redis Broker"]
    end

    subgraph ManagedGCP["Managed Google Infrastructure"]
        MetadataDB["Cloud SQL (PostgreSQL Metadata DB)"]
    end

    StorageLayer <-->|"gcsfuse Sync"| ComposerGKE
    Scheduler <--> RedisQueue
    RedisQueue --> Workers
    Scheduler <--> MetadataDB
    Workers <--> MetadataDB
    Triggerer <--> MetadataDB
```

1. **Storage synchronization**: The environment's Cloud Storage bucket syncs DAG files to Airflow pods using `gcsfuse`. Modifying a DAG file in GCS updates all scheduler and worker pods within 30 to 60 seconds.
2. **Dynamic worker autoscaling**: Celery workers scale up automatically based on queue backlog and CPU/memory pressure, scaling down to minimum configured workers when queues are empty.
3. **Airflow Triggerer**: Runs an asynchronous Python `asyncio` loop to monitor sensors and deferrable tasks without blocking Celery worker slots.

---

## Private IP environments and security

In enterprise environments, Cloud Composer must be provisioned with **Private IP**:
- Airflow UI and GKE nodes have no public IP addresses.
- Access routes through internal VPC Peering and Cloud NAT.
- Direct connectivity to on-prem databases via Cloud VPN or Interconnect.

---

## Provisioning a Composer 2 environment with gcloud

```bash
gcloud composer environments create prod-orchestrator-01 \
    --location=us-central1 \
    --image-version=composer-2.8.5-airflow-2.7.3 \
    --environment-size=medium \
    --service-account="composer-sa@my-gcp-project.iam.gserviceaccount.com" \
    --scheduler-count=2 \
    --scheduler-cpu=2 \
    --scheduler-memory=4GB \
    --triggerer-count=2 \
    --triggerer-cpu=1 \
    --triggerer-memory=2GB \
    --min-workers=2 \
    --max-workers=10 \
    --worker-cpu=2 \
    --worker-memory=8GB
```

---

## Managing Python packages and DAG deployment

### 1. Installing custom PyPI dependencies

```bash
gcloud composer environments update prod-orchestrator-01 \
    --location=us-central1 \
    --update-pypi-packages-from-file=requirements.txt
```

### 2. Deploying DAGs to the environment bucket

Retrieve the environment's DAG bucket location:

```bash
DAG_BUCKET=$(gcloud composer environments describe prod-orchestrator-01 \
    --location=us-central1 \
    --format="value(config.nodeConfig.dagGcsPrefix)")

# Sync local DAGs folder to Composer GCS bucket
gcloud storage rsync ./dags ${DAG_BUCKET} --delete-unmatched-destination-objects
```

---

## Summary heuristics

1. Always provision at least 2 schedulers and 2 triggerers for production high availability.
2. Avoid heavy data processing inside Airflow worker processes; workers should only trigger and monitor external compute engines (BigQuery, Dataflow, Dataproc).
3. Use CI/CD to run `gcloud storage rsync` to deploy DAG files into the environment bucket.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0027: Transformation CI/CD & Testing](0027-transformation-pipelines-cicd.md) | [All Lessons (Index)](index.md) | [0029: Resilient DAGs & Deferrable Operators](0029-resilient-dags-deferrable-operators.md) |
