---
icon: lucide/radio
---

# Cloud Pub/Sub architecture, subscriptions, and flow control

Google Cloud Pub/Sub is a globally distributed, horizontally scalable asynchronous messaging service. It decouples message producers from consumers with automatic multi-zone replication, message retention up to 31 days, and per-message acknowledgement deadlines.

---

## Internal architecture: Routers, forwarders, and storage

Pub/Sub separates data planes into distinct architectural tiers:

``` mermaid
flowchart TD
    Pub["Publisher Application"] --> Router["Pub/Sub Router Layer"]
    Router --> Colossus["Colossus Log Storage (Replicated across 3 zones)"]
    Colossus --> Forwarder["Forwarder Server"]
    Forwarder --> AckHandler["Ack Tracker / Deadlines"]
    Forwarder --> Sub["Subscriber Client (Pull / Push / Direct BigQuery)"]
```

1. **Router**: Terminates client connections and assigns messages to topic partitions.
2. **Colossus storage**: Persists raw unacknowledged messages across three availability zones.
3. **Forwarder**: Pulls messages from Colossus and streams them to connected subscribers based on subscription leases.
4. **Ack tracker**: Monitors acknowledgement timestamps (`ack_deadline`). If a message is not acknowledged before the deadline expires, the forwarder re-delivers it.

---

## Subscription types and delivery guarantees

Pub/Sub delivers messages **at least once** by default. Duplicates occur during network retries or when subscriber processing exceeds the acknowledgement deadline.

| Subscription type | Delivery mechanism | Max throughput | Best use case |
| :--- | :--- | :--- | :--- |
| **Pull (StreamingPull)** | Consumer opens bidirectional gRPC stream | Tens of GB/s per topic | High-volume Dataflow or custom backend workers |
| **Push** | Pub/Sub issues HTTP POST to webhook URL | Limited by endpoint capacity | Webhooks, Cloud Functions, Cloud Run microservices |
| **BigQuery subscription** | Direct serverless ingest to BigQuery table | Scales with BigQuery limits | Zero-code direct streaming without compute clusters |
| **Cloud Storage subscription** | Direct file writes (JSON, Avro, Text) to GCS | Scales with GCS limits | Raw archive landing zones without running Dataflow |

---

## Dead-letter topics and retry policies

When bad records cause subscriber worker crashes, messages fail acknowledgement repeatedly. Without a Dead-Letter Topic (DLQ), poisoned messages loop indefinitely, consuming quota and compute resources.

``` mermaid
flowchart TD
    Pub["Publishers"] --> MainTopic["orders-topic"]
    MainTopic --> MainSub["orders-sub (Max delivery attempts = 5)"]
    MainSub --> Worker["Subscriber Worker"]
    Worker -- "JSON Parse Error (Nack / Timeout)" --> MainSub
    MainSub -->|"Attempt > 5"| DLQTopic["orders-dlq-topic"]
    DLQTopic --> DLQSub["orders-dlq-sub (Manual triage / Alerting)"]
```

### Configuring a dead-letter subscription

```bash
# 1. Create dead-letter topic and subscription
gcloud pubsub topics create orders-dlq-topic
gcloud pubsub subscriptions create orders-dlq-sub --topic=orders-dlq-topic

# 2. Grant Pub/Sub service agent publishing rights to the DLQ topic
PUBSUB_SERVICE_ACCOUNT="service-$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')@gcp-sa-pubsub.iam.gserviceaccount.com"

gcloud pubsub topics add-iam-policy-binding orders-dlq-topic \
    --member="serviceAccount:${PUBSUB_SERVICE_ACCOUNT}" \
    --role="roles/pubsub.publisher"

# 3. Create main subscription with dead-letter policy and exponential backoff
gcloud pubsub subscriptions create orders-main-sub \
    --topic=orders-topic \
    --min-retry-delay=10s \
    --max-retry-delay=600s \
    --dead-letter-topic=orders-dlq-topic \
    --max-delivery-attempts=5
```

---

## Subscriber flow control in Python

Uncontrolled subscribers can pull thousands of messages into local memory, triggering Out-Of-Memory (OOM) errors before processing completes. Configure `FlowControl` settings in the Google Cloud Python client:

```python
from google.cloud import pubsub_v1
import time

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path("my-gcp-project", "orders-main-sub")

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    try:
        payload = message.data.decode("utf-8")
        # Process record
        print(f"Processing order: {message.message_id}")
        message.ack()
    except Exception as exc:
        print(f"Failed processing {message.message_id}: {exc}")
        message.nack()

# Restrict in-flight messages and total memory
flow_control = pubsub_v1.types.FlowControl(
    max_messages=500,
    max_bytes=100 * 1024 * 1024, # 100 MB max buffer
    limit_exceeded_behavior=pubsub_v1.types.LimitExceededBehavior.BLOCK
)

streaming_pull_future = subscriber.subscribe(
    subscription_path,
    callback=callback,
    flow_control=flow_control
)

print(f"Listening for messages on {subscription_path}...")
try:
    streaming_pull_future.result()
except KeyboardInterrupt:
    streaming_pull_future.cancel()
    streaming_pull_future.result()
```

---

## Exactly-once delivery

Pub/Sub supports **Exactly-Once Delivery** on pull subscriptions within a single cloud region. When enabled:
- Acknowledgement requests are idempotent.
- Redeliveries are prevented if an ack was received before the deadline.
- If processing exceeds the deadline, acknowledgement fails with `DEADLINE_EXCEEDED` so the subscriber knows another worker picked up the message.

Enable it via CLI:

```bash
gcloud pubsub subscriptions update orders-main-sub \
    --enable-exactly-once-delivery
```

---

## Summary heuristics

1. Use BigQuery and GCS direct subscriptions when you don't need custom transformations, saving Dataflow compute costs.
2. Always attach a Dead-Letter Topic with `max-delivery-attempts` (3 to 5) to prevent malformed payloads from causing infinite redelivery loops.
3. Configure `FlowControl` with explicit memory limits on streaming pull consumers to prevent worker OOM crashes.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0004: Medallion Architecture on GCS](0004-data-lake-medallion-gcs.md) | [All Lessons (Index)](index.md) | [0006: Pub/Sub Lite vs Standard](0006-pubsub-lite-vs-standard.md) |
