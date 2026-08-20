---
icon: lucide/bug
---

# Debugging IAM permission errors, policy tag access denied, and cross-project KMS issues

Diagnostic playbook for troubleshooting Google Cloud IAM permission errors, BigQuery Column-Level Security (`Access Denied on Policy Tag`), Cloud KMS decryption failures, and cross-project BigLake connection errors.

---

## Failure sequence diagram

``` mermaid
sequenceDiagram
    autonumber
    actor Analyst as Analyst / Pipeline SA
    participant BQ as BigQuery Execution Engine
    participant DataCatalog as Data Catalog (Policy Tag Manager)
    participant KMS as Cloud KMS (Encryption Keys)

    Analyst->>BQ: SELECT name, ssn FROM `proj.analytics.customers`
    BQ->>DataCatalog: Check IAM role on Policy Tag 'SSN_Confidential'
    DataCatalog-->>BQ: Access Denied! (Missing 'roles/datacatalog.categoryFineGrainedReader')
    BQ--xAnalyst: 403 Access Denied: User does not have fine-grained reader access to policy tag 'SSN_Confidential'
    Note over Analyst: Query fails immediately without returning partial rows
```

---

## Symptoms and diagnostic signals

| Symptom | Error message | Root cause |
| :--- | :--- | :--- |
| **Policy tag denied** | `Access Denied: User does not have fine-grained reader access to policy tag` | The user or service account has BigQuery dataset access but lacks `roles/datacatalog.categoryFineGrainedReader` on the policy tag |
| **Cross-project KMS failure** | `Permission 'cloudkms.cryptoKeyVersions.useToDecrypt' denied on resource` | The BigQuery service agent in project A lacks decrypter permissions on the KMS key hosted in project B |
| **BigLake GCS access denied** | `Access Denied: BigQuery connection could not read GCS URI` | The auto-generated service account for the Cloud Resource connection lacks `roles/storage.objectViewer` on the target GCS bucket |
| **Row-level security empty result** | Query executes successfully but returns 0 rows | The user is not included in any active Row Access Policy `GRANT TO` clauses |

---

## Diagnostic commands

### 1. Inspecting Policy Tag IAM permissions

```bash
gcloud data-catalog taxonomies policy-tags get-iam-policy \
    projects/my-gcp-project/locations/us-central1/taxonomies/PII_TAXONOMY_ID/policyTags/TAG_SSN_ID
```

### 2. Inspecting BigQuery connection service account

```bash
# Retrieve connection service account email
bq show --format=prettyjson --connection my-gcp-project.US.biglake-conn
```

Look for `serviceAccountId` in the JSON output (e.g. `service-12345678@gcp-sa-bigquery-v2.iam.gserviceaccount.com`).

---

## Resolution playbook

### 1. Granting Fine-Grained Reader role on policy tags
Grant the `Data Catalog Fine-Grained Reader` role directly on the specific policy tag (or entire taxonomy):

```bash
gcloud data-catalog taxonomies policy-tags add-iam-policy-binding \
    projects/my-gcp-project/locations/us-central1/taxonomies/PII_TAXONOMY_ID/policyTags/TAG_SSN_ID \
    --member="group:authorized-hr-analysts@company.com" \
    --role="roles/datacatalog.categoryFineGrainedReader"
```

### 2. Resolving cross-project KMS encryption permissions
When BigQuery in project `data-prod` reads CMEK-encrypted tables whose keys live in `security-prod`:

```bash
# 1. Get BigQuery service agent email from data-prod
PROJECT_NUMBER=$(gcloud projects describe data-prod --format="value(projectNumber)")
BQ_SERVICE_AGENT="service-${PROJECT_NUMBER}@gcp-sa-bigquery.iam.gserviceaccount.com"

# 2. Grant CryptoKey Encrypter/Decrypter in security-prod
gcloud kms keys add-iam-policy-binding data-encryption-key \
    --project=security-prod \
    --location=us-central1 \
    --keyring=lakehouse-keyring \
    --member="serviceAccount:${BQ_SERVICE_AGENT}" \
    --role="roles/cloudkms.cryptoKeyEncrypterDecrypter"
```

### 3. Granting storage access to BigLake connections

```bash
gcloud storage buckets add-iam-policy-binding gs://my-lakehouse-bucket \
    --member="serviceAccount:service-12345678@gcp-sa-bigquery-v2.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"
```

---

## Prevention checklist

- [ ] Grant `roles/datacatalog.categoryFineGrainedReader` via Google Groups rather than individual user accounts.
- [ ] Maintain infrastructure-as-code (Terraform) scripts that bind BigQuery connection service agents to GCS buckets automatically.
- [ ] Add audit logging alerts for `403 Permission Denied` events on KMS keys.

---

| Previous Guide | All Debugging Guides | Next Guide |
| :--- | :---: | ---: |
| [07: BigQuery Storage Write API](07-bigquery-storage-write-api-errors.md) | [Debugging Index](index.md) | *None (All Debugging Guides Complete)* |
