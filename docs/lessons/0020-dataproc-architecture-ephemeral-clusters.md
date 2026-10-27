---
icon: lucide/server
---

# Cloud Dataproc architecture: Master/worker topology and ephemeral clusters

Cloud Dataproc is Google Cloud's managed Apache Spark and Hadoop service. It allows teams to provision dedicated distributed compute clusters, run batch transformation workloads, and automatically tear down clusters to eliminate idle infrastructure costs.

---

## Node topology: Master, primary, and secondary workers

``` mermaid
flowchart TD
    subgraph MasterNode["Master Node (YARN ResourceManager & HDFS NameNode)"]
        YARNMaster["YARN ResourceManager"]
        ClusterServices["Cluster coordination services"]
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
        Airflow["Airflow / Composer"] -->|"1. Create job-scoped cluster"| NewCluster["Ephemeral Dataproc Cluster"]
        NewCluster -->|"2. Run PySpark Job"| RunJob["Execute Spark Transformation"]
        RunJob -->|"3. Auto-Delete on Finish"| Destroy["Cluster Deleted (Zero Idle Cost)"]
    end
```

Job-scoped clusters can reduce idle VM and disk charges when workloads have long gaps. A shared cluster can amortize startup and dependencies when jobs are frequent. Compare the full lifecycle against serverless batches and the workload deadline.

---

## Provisioning an ephemeral cluster with gcloud

```bash
# Provision cluster with auto-deletion after 30 minutes of idle time and Spot secondary workers
gcloud dataproc clusters create batch-transform-cluster \
    --region=us-central1 \
    --zone=us-central1-a \
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
    -- --input_path=gs://lake-bronze/orders/ \
       --output_path=gs://lake-silver/orders/
```

---

## Summary heuristics

1. Size secondary Spot capacity from interruption tolerance, shuffle behavior and the job deadline. Keep enough stable capacity to recover tasks.
2. Always set `--max-idle=15m` or the supported `--max-age` lifetime option so failed pipeline runs don't leave forgotten clusters billing continuously.
3. Decouple storage from compute by reading from and writing to Cloud Storage (`gs://`) rather than local HDFS.

---

## Trace a Spark job rather than treat the cluster as one machine

The driver builds a logical plan and schedules stages. Executors run tasks over partitions. A shuffle creates a stage boundary and transfers data between tasks. Driver memory, executor heap, Python worker memory, local shuffle disk and durable input storage are different resources.

In YARN cluster mode the driver runs in an application container allocated by YARN; do not assume it always runs on the master node. Inspect the actual application/driver placement when diagnosing memory or connectivity.

Secondary workers can lose local compute and shuffle work when interrupted even though they do not hold HDFS data. Failed tasks must recompute or fetch replacement outputs. For a tight deadline, a high Spot fraction can cost more in repeated work and missed completion than it saves in VM rate. HDFS intermediates also disappear when an ephemeral cluster is deleted; persist required outputs in Cloud Storage or BigQuery.

If startup and dependency installation take five minutes for a two-minute job, repeatedly creating clusters can dominate runtime. Compare serverless batches, grouped jobs on one cluster, or a deliberately managed shared cluster. Ephemeral clusters reduce idle capacity but are not universally optimal.

## Operations and failure exercise

Use a dedicated worker service account, a supported pinned image and subnet connectivity to APIs and artifacts. Check whether the selected image already bundles the BigQuery connector; adding an old incompatible JAR can cause class conflicts. The commands above are infrastructure/submission patterns and require your own `transform_orders.py`, buckets and initialization script. Use the complete local transformation in [0004](0004-data-lake-medallion-gcs.md) as a starting script.

In a disposable cluster, run a bounded job, inspect its Spark UI, and identify driver, executor, stage and shuffle evidence. Make one executor task fail once, then observe retry. Finally verify output row counts before deleting the cluster with `gcloud dataproc clusters delete batch-transform-cluster --region=us-central1`.

??? note "Recall answer"
    Cluster deletion cleans up compute, not a failed publication contract. Retry-safe output requires an immutable input boundary and a staged/idempotent sink write. A successful driver exit and a correct business dataset must both be checked.

Sources: [cluster architecture](https://docs.cloud.google.com/dataproc/docs/concepts/overview), [secondary workers](https://docs.cloud.google.com/dataproc/docs/concepts/compute/secondary-vms), and [scheduled deletion](https://docs.cloud.google.com/dataproc/docs/concepts/configuring-clusters/scheduled-deletion).

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0019: Flex Templates & Cloud Build](0019-dataflow-flex-templates-cloud-build.md) | [All Lessons (Index)](index.md) | [0021: Serverless Spark batches](0021-dataproc-serverless-spark.md) |
