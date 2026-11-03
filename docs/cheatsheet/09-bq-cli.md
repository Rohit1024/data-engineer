---
icon: lucide/terminal
---

# bq command cheatsheet

Use `bq` to inspect BigQuery resources, run SQL, move data, and investigate failed jobs. For daily work, start with the [frequently used commands](#frequently-used-commands).

Checked on 2026-11-03 against Google's [bq reference](https://docs.cloud.google.com/bigquery/docs/reference/bq-cli-reference) and installed BigQuery CLI `2.1.39`. The command catalog covers all 26 commands listed by that installation's `bq help`. The flag tables cover common options. Run `bq help COMMAND` for the full set supported by your version.

## Setup and command syntax

Commands follow `bq GLOBAL_FLAGS COMMAND COMMAND_FLAGS ARGUMENTS`. Put global flags before the command.

| Task | Command | What it does |
| --- | --- | --- |
| Sign in locally | `gcloud auth login` | Selects the account that `bq` uses through the Google Cloud CLI. Cloud Shell already has a signed-in account. |
| Set the default project | `gcloud config set project PROJECT_ID` | Sets the project used when a command omits a project ID and no `bq` configuration overrides it. |
| Check the installed version | `bq version` | Prints the BigQuery CLI version. |
| List commands | `bq help` | Shows the commands available in your installation. |
| Read global flags | `bq --help` | Shows project, location, output, and other global options. |
| Read one command's flags | `bq help load` | Shows arguments and options for a command. |

Replace uppercase placeholders before running examples. Your account needs permission to use the resources involved. Supply the named local files for file-based examples.

| Identifier or input | Example form | Meaning |
| --- | --- | --- |
| CLI dataset ID | `PROJECT_ID:DATASET` | A dataset in a particular project. |
| CLI table ID | `PROJECT_ID:DATASET.TABLE` | A table or view. Examples also use `DATASET.TABLE` after setting a default project. |
| GoogleSQL table path | `` `PROJECT_ID.DATASET.TABLE` `` | SQL uses dots between all three parts and backticks around the path. |
| Job ID | `JOB_ID` | Copy the ID from job output or `bq ls --jobs`. Supply its project and location when inspecting it. |
| Cloud Storage URI | `gs://BUCKET/path/*.parquet` | Quote wildcard URIs so your shell passes the `*` to `bq`. |
| Local inputs | `query.sql`, `schema.json`, `rows.json` | A SQL file, a JSON schema array, and newline-delimited JSON rows. |
| Location | `US` | An example location. Replace it with the location used by your data or reservation. |

!!! tip "Quote SQL at the shell"
    Wrap inline SQL in single quotes so the shell preserves SQL backticks. For longer queries, use `bq query --use_legacy_sql=false < query.sql`. Set `--use_legacy_sql=false` explicitly in query and view commands.

## Every top-level command

Resource types such as datasets, connections, and reservations are flags on these commands. For example, `bq mk --dataset` creates a dataset, and `bq mk --reservation` creates a reservation.

| Command | What it does | Example or help |
| --- | --- | --- |
| `add-iam-policy-binding` | Adds one member and role binding to a table or view's IAM policy. | `bq add-iam-policy-binding --member=user:USER_EMAIL --role=roles/bigquery.dataViewer DATASET.TABLE` |
| `cancel` | Requests cancellation of a job. The job can finish before cancellation takes effect. | `bq --project_id=PROJECT_ID --location=US cancel JOB_ID` |
| `cp` | Copies tables. Flags also create clones and snapshots. | `bq cp --no_clobber DATASET.TABLE DATASET.TABLE_COPY` |
| `extract` | Exports a table to Cloud Storage. `--model` exports a supported BigQuery ML model. | `bq extract --destination_format=PARQUET DATASET.TABLE 'gs://BUCKET/export/*.parquet'` |
| `get-iam-policy` | Prints a supported resource's IAM policy as JSON. | `bq get-iam-policy DATASET.TABLE` |
| `head` | Reads table rows without running a SQL query job. | `bq head --max_rows=10 DATASET.TABLE` |
| `help` | Prints command documentation. | `bq help query` |
| `info` | Prints information about the CLI's execution environment. | `bq info` |
| `init` | Legacy authentication and configuration setup. Google Cloud CLI installations direct you to `gcloud auth` instead. | Use `gcloud auth login`. |
| `insert` | Sends newline-delimited JSON rows through streaming inserts. Google documents this command for testing. | `bq insert DATASET.TABLE rows.json` |
| `load` | Loads a local file or Cloud Storage objects into a table. | `bq load --source_format=PARQUET DATASET.TABLE 'gs://BUCKET/input/*.parquet'` |
| `ls` | Lists projects, datasets, tables, jobs, or other resource collections. | `bq ls PROJECT_ID:DATASET` |
| `mk` | Creates a resource selected by its type flag. | `bq --location=US mk --dataset PROJECT_ID:DATASET` |
| `mkdef` | Writes an external table definition as JSON. | `bq mkdef --source_format=PARQUET 'gs://BUCKET/input/*.parquet' > external.json` |
| `partition` | Copies date-sharded tables into an ingestion-time partitioned table. | `bq partition --no_clobber DATASET.events_ DATASET.events_partitioned` |
| `query` | Runs GoogleSQL, including queries, DDL, DML, and scripts. | `bq query --use_legacy_sql=false 'SELECT 1 AS ok'` |
| `remove-iam-policy-binding` | Removes one member and role binding from a table or view's IAM policy. | `bq remove-iam-policy-binding --member=user:USER_EMAIL --role=roles/bigquery.dataViewer DATASET.TABLE` |
| `rm` | Deletes a resource. Choose its type with a flag. | `bq rm --table DATASET.TABLE` |
| `set-iam-policy` | Applies a JSON IAM policy to a supported resource. Preserve the policy's current `etag`. | `bq set-iam-policy DATASET.TABLE policy.json` |
| `shell` | Starts an interactive `bq` session. | `bq shell` |
| `show` | Prints metadata for a dataset, table, job, or other resource. | `bq --format=prettyjson show DATASET.TABLE` |
| `truncate` | Copies tables at a recovery timestamp. It can process a table, dataset, or project for replication recovery. | `bq help truncate` |
| `undelete` | Restores a deleted dataset within its time travel window. | `bq --location=US undelete PROJECT_ID:DATASET` |
| `update` | Changes resource properties, such as descriptions, labels, expiration, or schemas. | `bq update --description='Daily order events' DATASET.TABLE` |
| `version` | Prints the CLI version. | `bq version` |
| `wait` | Waits for a job to reach a state, usually `DONE`. The optional seconds argument limits the wait. | `bq --project_id=PROJECT_ID --location=US wait --fail_on_error=true JOB_ID 60` |

`info`, `init`, `shell`, `truncate`, and `undelete` appear in the installed CLI's help but lack their own sections in the web reference checked above. For `truncate`, read local help and start with `--dry_run` to inspect the recovery plan. To empty a table while retaining its schema, run SQL `TRUNCATE TABLE` through `bq query`.

## Frequently used commands

### Inspect datasets, tables, and schemas

| Task | Command | Result |
| --- | --- | --- |
| List accessible projects | `bq ls --projects` | Projects your account can list. |
| List datasets | `bq --project_id=PROJECT_ID ls` | Datasets visible in the project. |
| Include hidden datasets | `bq --project_id=PROJECT_ID ls --all` | Also includes hidden datasets your account can access. |
| List tables and views | `bq ls --max_results=100 PROJECT_ID:DATASET` | Up to 100 resources in the dataset. Use `--page_token` for another page. |
| Inspect a dataset | `bq --format=prettyjson show --dataset PROJECT_ID:DATASET` | Location, access entries, defaults, and other dataset metadata. |
| Inspect a table | `bq --format=prettyjson show PROJECT_ID:DATASET.TABLE` | Schema, size, partitioning, clustering, and other table metadata. |
| Save a schema | `bq --format=prettyjson show --schema PROJECT_ID:DATASET.TABLE > schema.json` | A local schema file for review or reuse. |
| Preview selected columns | `bq head --max_rows=10 --selected_fields=order_id,amount PROJECT_ID:DATASET.orders` | Up to 10 rows. Row order is unspecified. |

### Run queries and control scanned bytes

These examples follow Google's [query execution guide](https://docs.cloud.google.com/bigquery/docs/running-queries). `query.sql` must use tables accessible to the selected account.

| Task | Command | Result |
| --- | --- | --- |
| Run inline SQL | ``bq --project_id=PROJECT_ID --location=US query --use_legacy_sql=false 'SELECT order_id, amount FROM `PROJECT_ID.DATASET.orders` WHERE event_ts >= TIMESTAMP("2026-11-01") LIMIT 10'`` | Filters by event time and prints up to 10 rows. `LIMIT` alone does not cap scanned bytes. |
| Run a SQL file | `bq --project_id=PROJECT_ID --location=US query --use_legacy_sql=false < query.sql` | Executes the file as a query or SQL script. |
| Validate and estimate bytes | `bq --project_id=PROJECT_ID --location=US query --use_legacy_sql=false --dry_run < query.sql` | Validates the query and estimates bytes without executing it. |
| Set a bytes billed limit | `bq --project_id=PROJECT_ID --location=US query --use_legacy_sql=false --maximum_bytes_billed=10737418240 < query.sql` | Sets a 10 GiB billed-bytes ceiling. This is a per-query control, not a project budget. |
| Bind a named parameter | `bq --project_id=PROJECT_ID --location=US query --use_legacy_sql=false --parameter='order_id:INT64:42' 'SELECT @order_id AS order_id'` | Binds a typed value. Parameters cannot replace table or column names. |
| Write to a new table | `bq --project_id=PROJECT_ID --location=US query --use_legacy_sql=false --destination_table=PROJECT_ID:DATASET.RESULTS < query.sql` | Saves a `SELECT` result. Fails if the destination already contains data unless a write flag allows it. |
| Append query results | `bq --project_id=PROJECT_ID --location=US query --use_legacy_sql=false --destination_table=PROJECT_ID:DATASET.RESULTS --append_table < query.sql` | Adds the result rows to the destination. |
| Replace query results | `bq --project_id=PROJECT_ID --location=US query --use_legacy_sql=false --destination_table=PROJECT_ID:DATASET.RESULTS --replace < query.sql` | Overwrites the destination with the result. |
| Submit without waiting | `bq --project_id=PROJECT_ID --location=US --synchronous_mode=false query --use_legacy_sql=false < query.sql` | Returns after submitting a job. Save its job ID to check completion. |
| Use batch priority | `bq --project_id=PROJECT_ID --location=US --synchronous_mode=false query --use_legacy_sql=false --batch < query.sql` | Submits a batch-priority query and returns without waiting. Batch priority does not make a query free. |
| Save output as CSV | `bq --project_id=PROJECT_ID --location=US --format=csv query --use_legacy_sql=false --max_rows=1000 < query.sql > results.csv` | Saves at most 1,000 result rows locally. Use an extract or `EXPORT DATA` for a full large export. |

### Create and maintain tables

| Task | Command | Result |
| --- | --- | --- |
| Create a dataset | `bq --location=US mk --dataset PROJECT_ID:DATASET` | Creates the dataset in `US`. |
| Create a table with a schema file | `bq mk --table PROJECT_ID:DATASET.orders schema.json` | Creates an empty table. `schema.json` is a JSON array of field definitions. |
| Create a partitioned, clustered table | `bq mk --table --time_partitioning_type=DAY --time_partitioning_field=event_ts --clustering_fields=customer_id --require_partition_filter PROJECT_ID:DATASET.orders order_id:INT64,event_ts:TIMESTAMP,customer_id:STRING,amount:NUMERIC` | Partitions by `event_ts`, clusters within each partition by `customer_id`, and requires a partition filter. |
| Create a logical view | ``bq mk --use_legacy_sql=false --view='SELECT order_id, amount FROM `PROJECT_ID.DATASET.orders`' PROJECT_ID:DATASET.orders_view`` | Stores the query definition. |
| Add a description | `bq update --description='Daily order events' PROJECT_ID:DATASET.orders` | Updates table metadata. |
| Add a label | `bq update --set_label=team:analytics PROJECT_ID:DATASET.orders` | Sets a table label for ownership or billing analysis. |
| Set table expiration | `bq update --expiration=604800 PROJECT_ID:DATASET.orders` | Sets expiration to seven days after the update. `0` removes expiration. |
| Set a dataset's default table lifetime | `bq update --dataset --default_table_expiration=604800 PROJECT_ID:DATASET` | Applies a seven-day default to newly created tables. |
| Update a schema | `bq update --schema=schema.json PROJECT_ID:DATASET.orders` | Applies supported schema changes. Keep existing fields and their order in the file. |

### Load and export data

The [Parquet load guide](https://docs.cloud.google.com/bigquery/docs/loading-data-cloud-storage-parquet) and [export guide](https://docs.cloud.google.com/bigquery/docs/exporting-data) describe format and location restrictions. Use a compatible Cloud Storage bucket location for load and extract jobs.

| Task | Command | Result |
| --- | --- | --- |
| Append Parquet objects | `bq --location=US load --source_format=PARQUET --replace=false PROJECT_ID:DATASET.orders 'gs://BUCKET/orders/*.parquet'` | Loads objects and appends to an existing table. Parquet supplies the schema. |
| Load a local CSV with a header | `bq --location=US load --source_format=CSV --skip_leading_rows=1 PROJECT_ID:DATASET.orders orders.csv schema.json` | Loads the file with an explicit schema. |
| Load newline-delimited JSON | `bq --location=US load --source_format=NEWLINE_DELIMITED_JSON PROJECT_ID:DATASET.orders rows.json schema.json` | Loads one JSON object per line. |
| Infer a CSV schema | `bq --location=US load --source_format=CSV --autodetect PROJECT_ID:DATASET.orders orders.csv` | Infers a schema. Review inferred types before using them in a production pipeline. |
| Replace a table during a load | `bq --location=US load --source_format=PARQUET --replace PROJECT_ID:DATASET.orders 'gs://BUCKET/orders/*.parquet'` | Overwrites the destination table. |
| Export Parquet | `bq --location=US extract --destination_format=PARQUET --compression=SNAPPY PROJECT_ID:DATASET.orders 'gs://BUCKET/export/orders-*.parquet'` | Writes table data to Cloud Storage objects. |
| Export JSON | `bq --location=US extract --destination_format=NEWLINE_DELIMITED_JSON PROJECT_ID:DATASET.orders 'gs://BUCKET/export/orders-*.json'` | Writes newline-delimited JSON, including nested fields. |
| Export CSV | `bq --location=US extract --destination_format=CSV --compression=GZIP PROJECT_ID:DATASET.orders 'gs://BUCKET/export/orders-*.csv.gz'` | Writes compressed CSV. CSV cannot represent nested or repeated fields. |
| Write an external table definition | `bq mkdef --source_format=PARQUET 'gs://BUCKET/orders/*.parquet' > external.json` | Creates a local JSON definition. It does not load data into BigQuery storage. |
| Create the external table | `bq mk --table --external_table_definition=external.json PROJECT_ID:DATASET.orders_external` | Creates a table that reads the Cloud Storage objects. |

### Copy, snapshot, and recover

| Task | Command | Result |
| --- | --- | --- |
| Copy without overwriting | `bq cp --no_clobber PROJECT_ID:DATASET.orders PROJECT_ID:DATASET.orders_copy` | Creates an independent table copy and refuses to overwrite an existing destination. |
| Append one table to another | `bq cp --append_table PROJECT_ID:DATASET.orders_delta PROJECT_ID:DATASET.orders` | Appends compatible source rows. |
| Create a clone | `bq cp --clone --no_clobber PROJECT_ID:DATASET.orders PROJECT_ID:DATASET.orders_clone` | Creates a writable clone. Storage charges depend on data that differs from the base table. |
| Create a snapshot | `bq cp --snapshot --no_clobber PROJECT_ID:DATASET.orders PROJECT_ID:DATASET.orders_snapshot` | Creates a read-only point-in-time snapshot. |
| Restore a table from one hour ago | `bq cp --no_clobber 'PROJECT_ID:DATASET.orders@-3600000' PROJECT_ID:DATASET.orders_restored` | Copies historical data within the table's time travel window. For a deleted table, choose a time before deletion. |
| Restore a deleted dataset | `bq --location=US undelete PROJECT_ID:DATASET` | Restores a dataset within its time travel window. Check view authorizations and refresh materialized views afterward. |
| Consolidate daily shards | `bq partition --no_clobber PROJECT_ID:DATASET.events_ PROJECT_ID:DATASET.events_partitioned` | Copies shards such as `events_20261101` into ingestion-time partitions. |

See [table recovery](https://docs.cloud.google.com/bigquery/docs/restore-deleted-tables) and [dataset recovery](https://docs.cloud.google.com/bigquery/docs/restore-deleted-datasets) for permissions and recovery limits. A table clone or snapshot must use a supported destination location and organization.

### Inspect and cancel jobs

| Task | Command | Result |
| --- | --- | --- |
| List your recent jobs | `bq --project_id=PROJECT_ID ls --jobs --max_results=20` | Lists up to 20 jobs submitted by your account. |
| List jobs from all users | `bq --project_id=PROJECT_ID ls --jobs --all --max_results=20` | Includes other users' jobs when your permissions allow it. |
| Inspect a job | `bq --project_id=PROJECT_ID --location=US --format=prettyjson show --job JOB_ID` | Shows status, errors, and job statistics. |
| Read query job results | `bq --project_id=PROJECT_ID --location=US head --job=JOB_ID --max_rows=20` | Reads up to 20 result rows. |
| Wait up to 60 seconds | `bq --project_id=PROJECT_ID --location=US wait --fail_on_error=true JOB_ID 60` | Returns an error if the job fails or still runs when the wait expires. |
| Request cancellation | `bq --project_id=PROJECT_ID --location=US cancel JOB_ID` | Requests cancellation and waits by default. Work already performed can still incur charges. |

Google's [job guide](https://docs.cloud.google.com/bigquery/docs/managing-jobs) distinguishes completion from success. `DONE` means the job stopped. Check `status.errorResult` for failure.

### Inspect access and delete resources

| Task | Command | Result |
| --- | --- | --- |
| Save a table's IAM policy | `bq get-iam-policy PROJECT_ID:DATASET.orders > policy.json` | Saves the resource policy and its `etag`. |
| Grant table read access | `bq add-iam-policy-binding --member=group:GROUP_EMAIL --role=roles/bigquery.dataViewer PROJECT_ID:DATASET.orders` | Adds a table-level binding. Query execution also requires job-creation permission in the project that runs the query. |
| Remove that table binding | `bq remove-iam-policy-binding --member=group:GROUP_EMAIL --role=roles/bigquery.dataViewer PROJECT_ID:DATASET.orders` | Removes that binding. Access inherited through other policies can remain. |
| Apply an edited table policy | `bq set-iam-policy PROJECT_ID:DATASET.orders policy.json` | Replaces the resource policy with the edited file. Keep the current `etag` and bindings you still need. |
| Inspect dataset access entries | `bq --format=prettyjson show --dataset PROJECT_ID:DATASET` | Prints dataset metadata, including the `access` entries. |
| Delete a table | `bq rm --table PROJECT_ID:DATASET.TABLE` | Prompts, then deletes the table. |
| Delete an empty dataset | `bq rm --dataset PROJECT_ID:DATASET` | Prompts, then deletes the dataset if it has no contents. |
| Delete a dataset and its contents | `bq rm --recursive --dataset PROJECT_ID:DATASET` | Prompts, then deletes the dataset and everything it contains. |

!!! note "IAM support varies by resource and version"
    Table and view policy commands are covered in the web reference. CLI `2.1.39` also exposes dataset, routine, connection, and reservation flags for `get-iam-policy` and `set-iam-policy`. Check `bq help get-iam-policy` and `bq help set-iam-policy` before applying them to another resource type. The add and remove binding commands above target tables or views.

## Other resource operations

These examples cover less frequent administrative tasks. Enable the APIs and grant the permissions required by each resource before creating it.

| Resource or task | Command | What it does |
| --- | --- | --- |
| Materialized view | ``bq mk --materialized_view='SELECT customer_id, SUM(amount) AS total FROM `PROJECT_ID.DATASET.orders` GROUP BY customer_id' PROJECT_ID:DATASET.sales_mv`` | Creates a materialized view over an eligible query. |
| Models | `bq ls --models PROJECT_ID:DATASET` | Lists BigQuery ML models. Create models with `CREATE MODEL` through `bq query`. |
| Routines | `bq ls --routines PROJECT_ID:DATASET` | Lists persistent functions and procedures. Create routines with SQL DDL through `bq query`. |
| Row access policies | `bq ls --row_access_policies PROJECT_ID:DATASET.TABLE` | Lists policies on the table. SQL DDL through `bq query` creates or changes them. |
| Cloud resource connection | `bq --project_id=PROJECT_ID --location=US mk --connection --connection_type=CLOUD_RESOURCE CONNECTION_ID` | Creates a connection with a service account. Grant that account access to the external storage before querying it. |
| Connections | `bq --project_id=PROJECT_ID --location=US ls --connection` | Lists connections in the location. |
| Reservation | `bq --project_id=ADMIN_PROJECT --location=us mk --reservation --edition=ENTERPRISE --slots=100 --autoscale_max_slots=300 RESERVATION` | Creates 100 baseline slots with up to 300 additional autoscaling slots. This allocates paid capacity. |
| Reservation assignment | `bq --project_id=ADMIN_PROJECT --location=us mk --reservation_assignment --reservation_id=ADMIN_PROJECT:us.RESERVATION --job_type=QUERY --assignee_type=PROJECT --assignee_id=WORKLOAD_PROJECT` | Routes the workload project's query jobs in that location to the reservation. |
| Reservation group | `bq --project_id=ADMIN_PROJECT --location=us mk --reservation_group GROUP_NAME` | Creates a reservation group where the feature is available. |
| Capacity commitments | `bq --project_id=ADMIN_PROJECT --location=us ls --capacity_commitment` | Lists slot commitments. Use `bq help mk` to review purchase options before creating one. |
| Transfer configurations | `bq --project_id=PROJECT_ID ls --transfer_config --transfer_location=us` | Lists Data Transfer Service configurations, including scheduled queries. |
| Create a transfer configuration | `bq --project_id=PROJECT_ID --location=us mk --transfer_config --target_dataset=DATASET --display_name='Storage import' --data_source=google_cloud_storage --params='{"data_path_template":"gs://BUCKET/input/*.parquet","destination_table_name_template":"orders","file_format":"PARQUET","write_disposition":"APPEND"}'` | Creates a recurring Cloud Storage transfer that appends to `orders`. Reruns can append the same data again. |
| Start a transfer run | `bq mk --transfer_run --run_time=RUN_TIME CONFIG_NAME` | Requests a manual run for an existing configuration. Use an RFC3339 UTC timestamp for `RUN_TIME`. |
| Transfer run history | `bq ls --transfer_run CONFIG_NAME` | Lists runs under `projects/PROJECT_ID/locations/LOCATION/transferConfigs/CONFIG_ID`. |
| Transfer logs | `bq ls --transfer_log RUN_NAME` | Lists messages under `CONFIG_NAME/runs/RUN_ID`. |
| Migration workflows | `bq --project_id=PROJECT_ID --location=US ls --migration_workflow` | Lists BigQuery migration workflows. |

Use the resource's matching `show`, `update`, or `rm` flag where supported. Read the [reservation guide](https://docs.cloud.google.com/bigquery/docs/reservations-tasks) and [Cloud Storage transfer guide](https://docs.cloud.google.com/bigquery/docs/cloud-storage-transfer) before creating those resources.

## Flags worth remembering

### Global flags

| Flag | What it does | Example |
| --- | --- | --- |
| `--project_id` | Sets the default project for the command. For query jobs, this selects the job project. | `--project_id=PROJECT_ID` |
| `--location` | Sets the job or resource location. Match it to the operation and data involved. | `--location=US` |
| `--dataset_id` | Sets a default dataset for unqualified names. | `--dataset_id=PROJECT_ID:DATASET` |
| `--format` | Chooses output such as `prettyjson`, `json`, `csv`, or `pretty`. | `--format=prettyjson` |
| `--synchronous_mode=false` | Returns after job submission instead of waiting for completion. | `bq --synchronous_mode=false query --use_legacy_sql=false 'SELECT 1'` |
| `--job_id` | Supplies a job ID for job-creating commands. Reusing an ID does not create another job in the same project and location. | `--job_id=orders_load_20261103` |
| `--headless=true` | Disables interactive prompts for scripts. | `--headless=true` |
| `--bigqueryrc` | Reads defaults from a chosen configuration file. | `--bigqueryrc=./.bigqueryrc` |

### Command flags

| Flag | Used with | What it does |
| --- | --- | --- |
| `--use_legacy_sql=false` | `query`, view creation or update | Selects GoogleSQL. |
| `--dry_run` | `query` | Validates SQL and estimates bytes without running the query. |
| `--maximum_bytes_billed=N` | `query` | Sets a per-query billed-bytes ceiling. |
| `--parameter=name:type:value` | `query` | Supplies a typed query parameter. Repeat for multiple parameters. |
| `--destination_table=PROJECT_ID:DATASET.TABLE` | `query` | Saves query results to a named table. |
| `--append_table` | `query`, `cp` | Appends rows to an existing destination. |
| `--replace` | `query`, `load` | Overwrites the destination table. |
| `--replace=false` | `load` | Appends to an existing table. Repeating the load can duplicate rows. |
| `--batch` | `query` | Selects batch priority. |
| `--use_cache=false` | `query` | Disables reuse of cached query results. |
| `--label=key:value` | Job-creating commands that support labels | Adds a job label. Use `--set_label` with `update` to change resource labels. |
| `--max_rows=N`, `-n N` | `query`, `head` | Limits returned rows. It does not limit query bytes scanned. |
| `--max_results=N`, `-n N` | `ls` | Limits the number of listed resources or jobs. |
| `--page_token=TOKEN` | `ls` | Fetches a later page of results. |
| `--source_format=FORMAT` | `load`, `mkdef` | Sets the input format, such as `PARQUET`, `CSV`, or `NEWLINE_DELIMITED_JSON`. |
| `--autodetect` | `load`, `mkdef` | Infers schema and supported format options. |
| `--skip_leading_rows=N` | CSV `load` | Skips header or other leading rows. |
| `--schema_update_option=ALLOW_FIELD_ADDITION` | `load`, `query` | Allows new fields during supported writes. Repeat with `ALLOW_FIELD_RELAXATION` when needed. |
| `--destination_format=FORMAT` | `extract` | Sets the export format. |
| `--compression=CODEC` | `extract` | Sets compression. Supported codecs depend on the format. |
| `--schema` | `show` | Prints only a table's schema. |
| `--schema=schema.json` | `update` | Reads a schema to apply to a table. |
| `--time_partitioning_field=FIELD` | `mk --table`, `load`, `query` | Chooses the time partitioning column for a destination table. |
| `--time_partitioning_type=DAY` | `mk --table`, `load`, `query`, `partition` | Chooses time partition granularity. |
| `--clustering_fields=a,b` | `mk --table`, `load`, `query`, `update` | Sets clustering columns. |
| `--require_partition_filter` | Table creation or update | Requires queries to include a filter usable for partition elimination. |
| `--expiration=SECONDS` | `mk`, `update`, `cp` where supported | Sets the destination's expiration relative to now. Check the command's resource-specific rules. |
| `--no_clobber`, `-n` | `cp`, `partition` | Refuses to overwrite an existing destination table or partition. |
| `--recursive`, `-r` | `rm --dataset` | Deletes the dataset's contents as well as the dataset. |
| `--force`, `-f` | `mk`, `cp`, `rm` | Meaning depends on the command. `mk` ignores an existing resource, `cp` permits overwrite without prompting, and `rm` suppresses confirmation. |

## Common mistakes

| Symptom or assumption | Check or correction |
| --- | --- |
| A job exists but `show --job` cannot find it | Supply the project and location that created the job. |
| SQL backticks trigger a shell error | Enclose the SQL in single quotes or read it from a file. |
| `LIMIT 10` should make a query cheap | `LIMIT` caps result rows. Use partition filters, a dry run, and `--maximum_bytes_billed` to control scanned bytes. |
| A repeated load doubles the data | Loads append by default. Use a staging table and an idempotent merge when retries must avoid duplicates. |
| A schema update drops or reorders fields | Supply the existing fields in their current order, then append supported new fields. Use SQL DDL for changes the schema-update API cannot apply. |
| `-n` always means a row limit | It means `--max_rows` for `query` and `head`, `--max_results` for `ls`, and `--no_clobber` for `cp` and `partition`. |
| An export should include query logic | `extract` exports a table. Materialize query results first or run SQL `EXPORT DATA` through `bq query`. |
| A copy is a dataset copy | `bq cp` copies tables. Dataset copies use Data Transfer Service. |
| A job says `DONE`, so it succeeded | Inspect `status.errorResult` or use `bq wait --fail_on_error=true`. |

## Recall check

| Prompt | Answer |
| --- | --- |
| Which command previews rows without a query job? | `bq head`. |
| Which command estimates query bytes without executing? | `bq query --use_legacy_sql=false --dry_run`. |
| Which load flag explicitly appends? | `--replace=false`. |
| How do you copy a table while refusing overwrite? | `bq cp --no_clobber SOURCE DESTINATION`. |
| What must accompany a job ID when project or location differs from your defaults? | The correct `--project_id` and `--location`. |

The [source catalog](../references/resources.md#bq-command-line-reference) records the official references and local verification scope. For SQL tuning and slot diagnostics, see the [BigQuery SQL and optimization cheatsheet](03-bigquery-sql-optimization.md).

| Previous cheatsheet | All cheatsheets | Next cheatsheet |
| --- | :---: | ---: |
| [08: Dataplex, security, and FinOps](08-dataplex-security-finops.md) | [Cheatsheet index](index.md) | None |
