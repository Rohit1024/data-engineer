---
icon: lucide/git-commit
---

# Cloud Pub/Sub Lite vs Standard: Cost and latency trade-offs

Google Cloud offers two messaging systems: Pub/Sub Standard and Pub/Sub Lite. Standard is a global, fully managed serverless messaging service with automated scaling. Lite is a zonal or regional partition-based service designed for high-volume, cost-sensitive workloads similar to Apache Kafka.

---

## Architectural differences

Pub/Sub Standard automatically shards traffic behind a single endpoint. Pub/Sub Lite requires you to pre-provision topic partitions and reserve ingress/egress bandwidth in MiB/s.

``` mermaid
flowchart TD
    subgraph PubSubStandard["Pub/Sub Standard (Global & Serverless)"]
        StdPub["Publishers"] --> GlobalEndpoint["Global Endpoint (Auto-sharded)"]
        GlobalEndpoint --> DynPart["Dynamic Shards (Managed by GCP)"]
        DynPart --> StdSub["Subscribers (Individual message acks)"]
    end

    subgraph PubSubLite["Pub/Sub Lite (Zonal / Regional Partitioned)"]
        LitePub["Publishers (Partition Routing)"] --> P0["Partition 0 (4 MiB/s Ingress)"]
        LitePub --> P1["Partition 1 (4 MiB/s Ingress)"]
        P0 --> LiteSub0["Consumer Group 0 (Offset cursor tracking)"]
        P1 --> LiteSub1["Consumer Group 1 (Offset cursor tracking)"]
    end

    PubSubStandard ~~~ PubSubLite
```

---

## Feature and cost comparison

| Dimension | Pub/Sub Standard | Pub/Sub Lite |
| :--- | :--- | :--- |
| **Architecture** | Global, serverless, automated routing | Zonal or Regional, pre-partitioned |
| **Capacity management** | Automatic scaling up and down | Manual provisioning (MiB/s per partition) |
| **Pricing basis** | Data volume processed ($40 per TB) | Capacity reserved ($4.50 per MiB/s-month) + storage |
| **Message ordering** | Optional via ordering keys | Strict per partition |
| **Acknowledgement mechanism** | Individual message acknowledgment | Offset-based cursor commits (Kafka-style) |
| **Max message size** | 10 MB | 256 MB |
| **Cross-cloud replication** | Native multi-region | Zonal or Regional replication |
| **Kafka connector compatibility** | Via Kafka Connect Sink/Source | Drop-in Kafka Shim client library |

---

## Cost inflection point

Pub/Sub Lite is approximately 80% to 90% cheaper than Pub/Sub Standard at sustained high throughput because you pay for provisioned capacity rather than raw message volume.

If a pipeline streams 50 MB/s continuously (130 TB/month):
- **Pub/Sub Standard**: 130 TB * $40/TB = **$5,200/month**.
- **Pub/Sub Lite**: 50 MB/s provisioned ingress + egress + 3 days storage = **~$580/month**.

If your traffic is unpredictable with long quiet periods and sudden bursts, Pub/Sub Standard avoids paying for idle reserved capacity.

---

## Hands-on exercise: Creating a Pub/Sub Lite topic and subscription

Create a regional topic with 4 partitions, 8 MiB/s total publish bandwidth, and 7-day retention:

```bash
# 1. Create a 4-partition regional Pub/Sub Lite topic
gcloud pubsub lite-topics create high-throughput-telemetry \
    --location=us-central1 \
    --partitions=4 \
    --per-partition-publish-capacity=2MiB \
    --per-partition-subscribe-capacity=4MiB \
    --per-partition-retention-period=7d \
    --per-partition-retention-storage=100GiB

# 2. Create a Lite subscription with commit cursor delivery
gcloud pubsub lite-subscriptions create telemetry-dataflow-sub \
    --location=us-central1 \
    --topic=high-throughput-telemetry \
    --delivery-requirement=deliver-after-stored

# 3. Inspect provisioned throughput
gcloud pubsub lite-topics describe high-throughput-telemetry \
    --location=us-central1 \
    --format="yaml(name, partitionConfig, retentionConfig)"
```

---

## Kafka shim integration

Pub/Sub Lite includes a Kafka client library that lets existing Kafka applications write to and read from Lite without changing application code:

```xml
<!-- Maven dependency for Kafka shim -->
<dependency>
  <groupId>com.google.cloud</groupId>
  <artifactId>google-cloud-pubsublite-kafka</artifactId>
  <version>1.1.0</version>
</dependency>
```

In your Kafka producer configuration, point to Pub/Sub Lite:

```properties
bootstrap.servers=us-central1.pubsublite.googleapis.com:443
key.serializer=org.apache.kafka.common.serialization.StringSerializer
value.serializer=org.apache.kafka.common.serialization.ByteArraySerializer
pubsublite.project=my-gcp-project
pubsublite.topic=high-throughput-telemetry
```

---

## Decision heuristics

1. Choose **Pub/Sub Standard** when you need a serverless setup, global routing, direct BigQuery/GCS subscriptions, or have spiky, low-to-medium volume traffic.
2. Choose **Pub/Sub Lite** when migrating existing Kafka pipelines, or when continuous streaming volume exceeds 10 MB/s and justifies manual partition management for major cost savings.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0005: Cloud Pub/Sub Architecture](0005-pubsub-architecture-flow-control.md) | [All Lessons (Index)](index.md) | [0007: CDC with Datastream & BigQuery](0007-change-data-capture-datastream-bigquery.md) |
