---
icon: lucide/flask-conical
---

# Running the curriculum examples

The curriculum teaches the production-platform mission in [mission.md](../mission.md). Reading or building the documentation does not run its cloud commands. Cloud examples are exercises for a disposable billing-enabled project, with explicit identities and cleanup.

## Choose the right execution environment

| Example | Requirements | What success establishes |
| --- | --- | --- |
| Standalone Python | Stated Python version and dependencies | Local fixture behavior |
| Python Beam fixtures | Python 3.11 and Beam 2.69.0 in the pinned example environment | Transform and TestStream assertions on DirectRunner |
| Java Beam fixture | JDK 17, Maven and the supplied POM | Java graph and expected aggregate assertions |
| PySpark | Compatible Spark/Python/JVM versions or selected managed runtime | Bounded distributed transformation behavior |
| GoogleSQL | BigQuery editor or `bq query --use_legacy_sql=false` | Service execution against the selected fixtures |
| Airflow DAG | Matching Airflow 2.11 image and Google provider for the provided labs | Parsing plus separate runtime integration checks |
| Dataform/dbt | Matching pinned compiler/adapter and a sandbox target | Compilation plus separately executed data assertions |

The repository's documentation Python version does not imply every data SDK supports that interpreter. `uv run --no-project --python 3.11 --with apache-beam==2.69.0 ...` creates a separate example environment. SDK pins are reproducibility choices for these local fixtures, not instructions to deploy an unreviewed old runtime to production.

For the Java fixture, select JDK 17 with your Java version manager before running `mvn compile exec:java` in `docs/examples/beam-java`. On macOS, `/usr/libexec/java_home -v 17` locates an installed JDK 17.

## Cloud setup and identifiers

Use an authenticated Cloud Shell or local Google Cloud CLI with `gcloud` and `bq`. A client library generally uses Application Default Credentials, which is separate from the CLI's active login. For local client examples, use `gcloud auth application-default login` or an approved impersonation flow. Managed jobs should use their runtime service account rather than a downloaded key file.

Set `PROJECT_ID` to your disposable project. Replace every `YOUR_PROJECT_ID`, `YOUR_BUCKET`, service account, group and existing source/table identifier before execution. Bucket names must be globally unique. Most short examples assume the named dataset/table or service account already exists; their surrounding prose states those prerequisites. Lessons 0037–0040 contain full cloud setup and cleanup sequences.

Choose compatible locations. A `region-us-central1` metadata query must execute in `us-central1`; `US` multi-region is different. Use the source, destination, worker and artifact locations supported by the actual service combination. GoogleSQL in an editor does not expand shell variables.

## Distinguish a full program from a configuration fragment

A complete local fixture has explicit input, executable code, assertions and an expected result. A connection, YAML snippet, transform class or build command can be a component requiring the named surrounding resources. Do not execute a configuration fragment as if it provisioned an entire platform. Keep arguments and runtime versions aligned with the official source linked in that lesson.

For every cloud lab, record input identity/boundary, code revision, runtime versions, effective principal, location, external job IDs and observed business results. Include the failure/retry case. A successful API submission is less evidence than a terminal successful job; neither alone proves the output is correct.

## Cleanup and learning records

Stop producers and continuous jobs before deleting their sinks. Remove only the dedicated lab resources after checking project/name/scope. Deletion and resource expiry can leave recoverable or retained bytes according to storage settings. Keep incident evidence until the exercise is complete.

Do not mark a learning record complete merely because a lesson exists or a documentation check passes. Record demonstrated predictions, observed output, corrected reasoning and unresolved questions.

| Previous | References | Next |
| --- | :---: | ---: |
| [Source catalog](resources.md) | [Reference index](index.md) | [Glossary](glossary.md) |
