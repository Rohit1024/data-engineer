---
icon: lucide/workflow
---

# Cloud Dataflow and Apache Beam cheatsheet

Quick reference syntax for Apache Beam transforms, windowing, triggers, and Cloud Dataflow CLI operations.

---

## Dataflow streaming pipeline flow

``` mermaid
flowchart TD
    Source["ReadFromPubSub (Subscription)"] --> Timestamp["Extract Event Time & Assign Watermark"]
    Timestamp --> Windowing["WindowInto (Fixed / Sliding / Session) + Triggers"]
    Windowing --> KeyBy["Key by Entity (Map to KV)"]
    KeyBy --> Combine["CombinePerKey (Associative Partial Reduction)"]
    Combine --> Sink["WriteToBigQuery (Storage Write API)"]
```

---

## Core Apache Beam transforms

| Transform | Signature / Usage | Purpose |
| :--- | :--- | :--- |
| `beam.Map` | `beam.Map(lambda x: x * 2)` | 1-to-1 element mapping |
| `beam.FlatMap` | `beam.FlatMap(lambda line: line.split())` | 1-to-many element generation |
| `beam.Filter` | `beam.Filter(lambda rec: rec["status"] == "ACTIVE")` | Boolean predicate filtering |
| `beam.ParDo` | `beam.ParDo(CustomDoFn())` | Custom lifecycle logic and stateful processing |
| `beam.CombinePerKey` | `beam.CombinePerKey(sum)` | Associative and commutative key reduction |
| `beam.GroupByKey` | `beam.GroupByKey()` | Group values by key into iterable list |
| `beam.WindowInto` | `beam.WindowInto(FixedWindows(60))` | Assign elements into temporal windows |
| `beam.Reshuffle` | `beam.Reshuffle()` | Break unwanted stage fusion and balance load |

---

## Streaming windowing and trigger template

```python
import apache_beam as beam
from apache_beam.transforms.window import FixedWindows, Duration
from apache_beam.transforms.trigger import (
    AfterWatermark,
    AfterProcessingTime,
    AfterCount,
    Repeatedly,
    AccumulationMode
)

windowed_pcol = raw_pcol | "ApplyWindowing" >> beam.WindowInto(
    FixedWindows(60), # 1-minute fixed windows
    trigger=Repeatedly(
        AfterWatermark(
            early=AfterProcessingTime(10), # Early speculative firing every 10s
            late=AfterCount(1)             # Immediate firing for late records
        )
    ),
    allowed_lateness=Duration(seconds=300), # 5 minutes allowed lateness
    accumulation_mode=AccumulationMode.ACCUMULATING
)
```

---

## Deploying Dataflow pipelines

### Running via DataflowRunner

```bash
python3 main.py \
    --runner=DataflowRunner \
    --project=my-gcp-project \
    --region=us-central1 \
    --temp_location=gs://my-pipeline-bucket/temp \
    --staging_location=gs://my-pipeline-bucket/staging \
    --enable_streaming_engine \
    --max_num_workers=20 \
    --worker_machine_type=n2-standard-4
```

### Building and running Flex Templates

```bash
# 1. Build and push container to Artifact Registry
gcloud builds submit --tag=us-central1-docker.pkg.dev/my-gcp-project/data-pipelines/beam-ingest:v1 .

# 2. Build Flex Template spec on GCS
gcloud dataflow flex-template build gs://my-pipeline-bucket/templates/beam-ingest.json \
    --image=us-central1-docker.pkg.dev/my-gcp-project/data-pipelines/beam-ingest:v1 \
    --sdk-language=PYTHON \
    --metadata-file=metadata.json

# 3. Launch Flex Template job
gcloud dataflow flex-template run "ingest-job-$(date +%s)" \
    --template-file-gcs-location=gs://my-pipeline-bucket/templates/beam-ingest.json \
    --region=us-central1 \
    --enable-streaming-engine \
    --parameters \
input_subscription="projects/my-gcp-project/subscriptions/orders-sub",\
output_table="my-gcp-project:analytics.orders"
```

---

## Dataflow operational metrics

| Metric | Health indicator | Troubleshooting action |
| :--- | :--- | :--- |
| `data_watermark_age` | Under 30s | If climbing, check for slow DoFn or partition skew |
| `system_lag` | Under 10s | If rising, increase `max_num_workers` |
| `cpu_utilization` | 70% to 85% | Under 20% means thread I/O lock; over 90% triggers auto-scale |

---

| Previous Cheatsheet | All Cheatsheets | Next Cheatsheet |
| :--- | :---: | ---: |
| [03: BigQuery SQL & Optimization](03-bigquery-sql-optimization.md) | [Cheatsheets Index](index.md) | [05: Dataproc & PySpark](05-dataproc-pyspark.md) |
