---
icon: lucide/workflow
---

# Apache Beam fundamentals: Pipelines, PCollections, and PTransforms

Apache Beam is an open-source, unified programming model for defining parallel batch and streaming data processing pipelines. It decouples pipeline logic from execution runtimes, allowing the same pipeline code to execute on Google Cloud Dataflow, Apache Flink, Apache Spark, or local DirectRunner.

---

## Core abstractions in Apache Beam

``` mermaid
flowchart TD
    Driver["Driver Program (Pipeline definition)"] --> ReadSource["Source PTransform (ReadFromText / ReadFromPubSub)"]
    ReadSource --> PCol1["PCollection 1 (Distributed Dataset)"]
    PCol1 --> Transform1["ParDo / Map / Filter PTransform"]
    PCol1 --> Transform2["GroupByKey / Combine PTransform"]
    Transform1 --> PCol2["PCollection 2"]
    Transform2 --> PCol3["PCollection 3"]
    PCol2 --> WriteSink["Sink PTransform (WriteToBigQuery / WriteToGCS)"]
    PCol3 --> WriteSink
```

1. **Pipeline**: Encapsulates the entire directed acyclic graph (DAG) of transformations and execution options.
2. **PCollection**: An immutable, distributed dataset representing bounded (batch) or unbounded (streaming) records.
3. **PTransform**: An operation that takes one or more PCollections as input, applies computation, and produces one or more output PCollections.

---

## DoFn lifecycle methods

The fundamental building block for custom transformations is `beam.DoFn`. Workers execute methods according to this lifecycle:

``` mermaid
flowchart TD
    Setup["setup(): Initialize heavy resources once per worker (e.g. database client pool)"] --> StartBundle["start_bundle(): Executed before processing a micro-batch bundle"]
    StartBundle --> Process["process(element): Executed for every single record in the PCollection"]
    Process --> Process
    Process --> FinishBundle["finish_bundle(): Flush buffered writes or commit transactions"]
    FinishBundle --> Teardown["teardown(): Clean up sockets and connections on worker shutdown"]
```

---

## Complete Python batch pipeline example

This pipeline reads raw server logs from Cloud Storage, extracts status codes using a custom `DoFn`, aggregates counts by HTTP status, and writes summary Parquet files:

```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions, StandardOptions
import re

class ParseLogLineDoFn(beam.DoFn):
    def setup(self):
        # Compiled regex for fast parsing across worker threads
        self.pattern = re.compile(r'^(\S+) \S+ \S+ \[(.*?)\] "(\S+) (\S+) \S+" (\d{3}) (\d+)')

    def process(self, element: str):
        match = self.pattern.match(element)
        if match:
            ip, timestamp, method, endpoint, status_code, bytes_sent = match.groups()
            yield {
                "endpoint": endpoint,
                "status_code": int(status_code),
                "bytes": int(bytes_sent)
            }
        else:
            # Drop or route bad records to dead-letter tags
            pass

def run():
    options = PipelineOptions()
    google_cloud_options = options.view_as(GoogleCloudOptions)
    google_cloud_options.project = "my-gcp-project"
    google_cloud_options.region = "us-central1"
    google_cloud_options.temp_location = "gs://my-pipeline-bucket/temp"
    google_cloud_options.staging_location = "gs://my-pipeline-bucket/staging"
    options.view_as(StandardOptions).runner = "DataflowRunner"

    with beam.Pipeline(options=options) as p:
        (
            p
            | "ReadLogs" >> beam.io.ReadFromText("gs://my-pipeline-bucket/logs/*.log")
            | "ParseLogs" >> beam.ParDo(ParseLogLineDoFn())
            | "FilterErrors" >> beam.Filter(lambda rec: rec["status_code"] >= 400)
            | "ExtractEndpoint" >> beam.Map(lambda rec: (rec["endpoint"], 1))
            | "CountErrorsPerEndpoint" >> beam.CombinePerKey(sum)
            | "FormatOutput" >> beam.Map(lambda kv: f"{kv[0]}: {kv[1]} errors")
            | "WriteSummary" >> beam.io.WriteToText("gs://my-pipeline-bucket/output/error_counts")
        )

if __name__ == "__main__":
    run()
```

---

## DirectRunner vs DataflowRunner

- **DirectRunner**: Executes locally on your development machine using multi-threading. Use for unit tests and verifying logic on small test fixtures before deploying to the cloud.
- **DataflowRunner**: Packages the Python environment, spins up autoscaling Compute Engine worker VMs or Streaming Engine backend nodes, and coordinates distributed shuffle operations across petabytes.

```bash
# Run locally with DirectRunner
python3 pipeline.py --runner=DirectRunner

# Deploy to Google Cloud Dataflow
python3 pipeline.py \
    --runner=DataflowRunner \
    --project=my-gcp-project \
    --region=us-central1 \
    --temp_location=gs://my-pipeline-bucket/temp
```

---

## Summary heuristics

1. Keep DoFn instances stateless unless using explicit Beam State API markers.
2. Initialize expensive external clients (database connections, HTTP session pools) inside `setup()`, not inside `process()`.
3. Use `beam.CombinePerKey` instead of `beam.GroupByKey` followed by a map reduce; `CombinePerKey` applies partial associative reduction on worker nodes before shuffling over the network.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0013: Slot Management & Editions](0013-bigquery-slot-management-editions.md) | [All Lessons (Index)](index.md) | [0015: Event Time & Watermarks](0015-beam-event-time-watermarks.md) |
