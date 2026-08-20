---
icon: lucide/bug
---

# Debugging Cloud Pub/Sub message accumulation, deadline timeouts, and throttling

Diagnostic playbook for troubleshooting Cloud Pub/Sub unacknowledged message backlogs (`num_undelivered_messages`), redelivery loops, `DEADLINE_EXCEEDED` errors, and quota throttling (`RESOURCE_EXHAUSTED`).

---

## Failure sequence diagram

``` mermaid
sequenceDiagram
    autonumber
    actor Publisher as High-Volume Publisher (5,000 msg/s)
    participant Topic as Pub/Sub Topic
    participant Sub as Subscription (ack_deadline: 10s)
    participant Worker as Subscriber Worker Pod

    Publisher->>Topic: Publish Message A
    Topic->>Sub: Buffer Message A
    Sub->>Worker: Deliver Message A (Lease timer starts: 10s)
    Note over Worker: Long DB write / HTTP timeout (takes 15s)
    Note over Sub: 10s expires! Message A unacknowledged
    Sub->>Worker: Re-deliver Message A to another thread
    Worker->>Sub: Original thread finishes & calls ack()
    Sub--xWorker: Ack failed: DEADLINE_EXCEEDED (Duplicate in flight)
    Note over Sub: Backlog increases, worker duplicate CPU wasted
```

---

## Symptoms and diagnostic signals

| Symptom | Diagnostic signal in Cloud Console | Root cause |
| :--- | :--- | :--- |
| **Backlog growth** | `pubsub.googleapis.com/subscription/num_undelivered_messages` spikes | Subscriber ingestion rate is lower than publish rate, or messages are failing processing |
| **Rising message age** | `oldest_unacked_message_age` exceeds 600s | Stuck worker threads or poisoned message payloads causing unhandled crashes |
| **`DEADLINE_EXCEEDED` on Ack** | Subscriber logs show ack failures | Processing time per message exceeds the configured subscription `ack_deadline` |
| **`RESOURCE_EXHAUSTED`** | Publisher receives HTTP 429 / gRPC 8 | Project publish throughput exceeds regional quota (default 200 MB/s per region) |

---

## Diagnostic commands

### 1. Inspecting subscription backlog and delivery settings

```bash
gcloud pubsub subscriptions describe orders-main-sub \
    --format="yaml(name, ackDeadlineSeconds, deadLetterPolicy, retryPolicy)"
```

### 2. Querying unacknowledged message backlog metrics

```bash
gcloud monitoring metrics-scopes list

# Check unacknowledged message count via gcloud monitoring
gcloud alpha monitoring time-series list \
    --filter='metric.type="pubsub.googleapis.com/subscription/num_undelivered_messages" AND resource.labels.subscription_id="orders-main-sub"' \
    --interval-duration=300s
```

---

## Resolution playbook

### 1. Attaching a Dead-Letter Topic (DLQ)
Stop infinite redelivery loops caused by unparseable payloads:

```bash
# 1. Create DLQ topic
gcloud pubsub topics create orders-dlq

# 2. Attach DLQ policy with max 5 attempts
gcloud pubsub subscriptions update orders-main-sub \
    --dead-letter-topic=orders-dlq \
    --max-delivery-attempts=5
```

### 2. Extending ack deadline and enabling lease management
If message processing legitimately takes 30 to 45 seconds (e.g. video processing or complex database queries), increase the base deadline:

```bash
gcloud pubsub subscriptions update orders-main-sub \
    --ack-deadline=60
```

In the Python SDK, configure the subscriber to automatically extend the acknowledgement lease in the background while processing is active:

```python
from google.cloud import pubsub_v1

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path("my-gcp-project", "orders-main-sub")

# Configure FlowControl and automatic lease extension
flow_control = pubsub_v1.types.FlowControl(
    max_messages=100,
    max_bytes=50 * 1024 * 1024,
    limit_exceeded_behavior=pubsub_v1.types.LimitExceededBehavior.BLOCK
)

# max_duration_per_lease_extension tells client to keep extending ack deadline up to 10 minutes
future = subscriber.subscribe(
    subscription_path,
    callback=my_callback_fn,
    flow_control=flow_control,
    await_callbacks_on_shutdown=True
)
```

### 3. Requesting publish and subscriber quota increases
If throughput exceeds regional bandwidth quotas:
1. Navigate to **IAM & Admin &rarr; Quotas** in the Cloud Console.
2. Filter by service: `Cloud Pub/Sub API`.
3. Select `Publish operations per minute` or `Regional publish throughput` and submit an increase request.

---

## Prevention checklist

- [ ] Always attach a dead-letter topic to avoid poisoned message processing loops.
- [ ] Configure `FlowControl` to prevent subscribers from taking more messages than worker threads can process within the ack deadline.
- [ ] Set alert policies on `subscription/oldest_unacked_message_age > 300s`.

---

| Previous Guide | All Debugging Guides | Next Guide |
| :--- | :---: | ---: |
| [02: BigQuery Slot Starvation & Spilling](02-bigquery-slot-starvation-spilling.md) | [Debugging Index](index.md) | [04: Dataproc Spark Executor OOM](04-dataproc-spark-executor-oom-shuffle.md) |
