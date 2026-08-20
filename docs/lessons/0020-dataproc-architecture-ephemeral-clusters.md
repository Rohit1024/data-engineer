---
icon: lucide/server
---

# Cloud Dataproc architecture: Master/worker topology and ephemeral clusters

Cloud Dataproc is Google Cloud's managed Apache Spark and Hadoop service. It allows teams to spin up dedicated distributed compute clusters in 90 seconds, run batch transformation workloads, and automatically tear down clusters to eliminate idle infrastructure costs.

---

## Node topology: Master, primary, and secondary workers

``` mermaid
flowchart TD
    subgraph MasterNode["Master Node (YARN ResourceManager & HDFS NameNode)"]
        YARNMaster["YARN ResourceManager"]
        SparkDriver["Spark Driver (Cluster Mode)"]
    end

    subgraph PrimaryWorkers["Primary Workers (Standard Persistent Compute)"]
        P1["Primary Worker 1 (DataNode + NodeManager)"]
        P2["Primary Worker 2 (DataNode + NodeManager)"]
    end

    subgraph SecondaryWorkers["Secondary Workers (Spot / Preemptible Task Nodes)"]
        S1["Secondary Worker 1 (NodeManager Only - Compute Only)"]
        S2["Secondary Worker 2 (NodeManager Only - Compute Only)"]
        S3["Secondary Worker 3 (NodeManager Only - Compute Only)"]
    end

    MasterNode --> PrimaryWorkers
    MasterNode --> SecondaryWorkers
```

1. **Master node**: Runs YARN ResourceManager, HDFS NameNode, and coordinates job execution. In High Availability (HA) mode, Dataproc provisions three master nodes with ZooKeeper quorum.
2. **Primary workers**: Run YARN NodeManagers and HDFS DataNodes. They store persistent intermediate data and cannot be preemptible.
3. **Secondary workers (Task nodes)**: Run compute-only NodeManagers without HDFS DataNodes. If a Spot/Preemptible secondary node is terminated by GCP, no HDFS blocks are lost; YARN simply reschedules tasks on remaining nodes.

---

## Ephemeral vs Long-running cluster model

``` mermaid
flowchart TD
    subgraph EphemeralPattern["Ephemeral Cluster Pattern (Recommended)"]
        Airflow["Airflow / Composer"] -->|"1. Create 90s Cluster"| NewCluster["Ephemeral Dataproc Cluster"]
        NewCluster -->|"2. Run PySpark Job"| RunJob["Execute Spark Transformation"]
        RunJob -->|"3. Auto-Delete on Finish"| Destroy["Cluster Deleted (Zero Idle Cost)"]
    end
```

Running persistent, 24/7 Spark clusters incurs massive idle VM and disk overhead. The best practice on GCP is **ephemeral job-scoped clusters** provisioned automatically by Cloud Composer for specific heavy transformation jobs and deleted immediately upon completion.

---

## Provisioning an ephemeral cluster with gcloud

```bash
# Provision cluster with auto-deletion after 30 minutes of idle time and Spot secondary workers
gcloud dataproc clusters create batch-transform-cluster \
    --region=us-central1 \
    --zone=us-central1-a \
    --single-node=false \
    --master-machine-type=n2-standard-4 \
    --master-boot-disk-size=100GB \
    --num-workers=2 \
    --worker-machine-type=n2-standard-8 \
    --worker-boot-disk-size=200GB \
    --num-secondary-workers=8 \
    --secondary-worker-type=spot \
    --max-idle=30m \
    --initialization-actions=gs://my-bucket/scripts/install-pip-deps.sh
```

---

## Submitting and monitoring a PySpark job

```bash
gcloud dataproc jobs submit pyspark gs://my-bucket/jobs/transform_orders.py \
    --cluster=batch-transform-cluster \
    --region=us-central1 \
    --jars=gs://spark-lib/bigquery/spark-bigquery-with-dependencies_2.12-0.34.0.jar \
    -- --input_path=gs://lake-bronze/orders/ \
       --output_path=gs://lake-silver/orders/
```

---

## Summary heuristics

1. Use **Secondary Spot Workers** for 70% to 80% of cluster worker capacity to reduce compute costs.
2. Always set `--max-idle=15m` or `--auto-delete-ttl` so failed pipeline runs don't leave forgotten clusters billing continuously.
3. Decouple storage from compute by reading from and writing to Cloud Storage (`gs://`) rather than local HDFS.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0019: Flex Templates & Cloud Build](0019-dataflow-flex-templates-cloud-build.md) | [All Lessons (Index)](index.md) | [0021: Dataproc Serverless for Spark](0021-dataproc-serverless-spark.md) |
