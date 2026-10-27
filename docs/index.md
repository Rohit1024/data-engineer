---
icon: lucide/terminal
---

# GCP data engineering workspace

A hands-on curriculum and architectural reference for Google Cloud Platform (GCP) data engineering.

This workspace covers ingestion, storage, stream and batch processing, transformations, orchestration, security, and FinOps across Google Cloud's data stack.

---

## Quick navigation

- [The mission](mission.md): The guiding compass and outcomes for this workspace.
- [Curriculum and lessons](lessons/index.md): All 45 lessons across 10 modules, with local examples and cloud labs.
- [Curriculum audit](references/curriculum-audit.md): Coverage findings and corrections for every original lesson.
- [Cheatsheets](cheatsheet/index.md): Fast lookups, query snippets, and gcloud/bq CLI references.
- [Debugging guides](debugging/index.md): Practical diagnostic workflows and failure mode resolution.
- [Interview questions](interview/index.md): Senior technical and system design question bank.
- [References and glossary](references/index.md): Canonical terminology and authoritative documentation sources.

---

## Curriculum roadmap

``` mermaid
flowchart TD
    M1["1. Cloud Storage & Storage Foundations"] --> M2["2. Real-Time Ingestion & CDC"]
    M2 --> M3["3. BigQuery Architecture & Lakehouse"]
    M3 --> M4["4. Stream & Batch with Cloud Dataflow"]
    M4 --> M5["5. Distributed Compute with Dataproc & Spark"]
    M5 --> M6["6. Data Transformation with Dataform & dbt"]
    M6 --> M7["7. Enterprise Orchestration with Cloud Composer"]
    M7 --> M8["8. Governance, Security & FinOps"]
    M8 --> M9["9. End-to-end implementation labs"]
    M9 --> M10["10. Modeling, contracts and platform design"]
```

---

## Getting started

Start with Module 1:
[Open Curriculum and Lesson 1](lessons/0001-cloud-storage-architecture-lifecycle.md)
