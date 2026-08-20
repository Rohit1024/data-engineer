---
icon: lucide/eye-off
---

# Automated PII masking with Sensitive Data Protection (Cloud DLP)

Google Cloud Sensitive Data Protection (formerly Cloud DLP) provides automated discovery, classification, and de-identification of sensitive Personally Identifiable Information (PII) across structured and unstructured data. Integrating DLP with Dataflow or BigQuery remote functions protects sensitive data before it reaches analytics layers.

---

## De-identification architecture

``` mermaid
flowchart TD
    RawData["Raw Ingestion Stream (Contains PII: Names, SSNs, Emails)"] --> DLPInspection["Sensitive Data Protection Inspection Engine"]
    DLPInspection --> Detect{"Match infoTypes (e.g. EMAIL_ADDRESS, US_SSN)"}

    Detect --> Redaction["Transform 1: Redaction (Replaces with '[REDACTED]')"]
    Detect --> Tokenize["Transform 2: Deterministic Encryption (Reversible Tokenization via KMS)"]
    Detect --> Bucketing["Transform 3: Bucketing / Generalization (e.g. Age 34 -> '30-40')"]

    Redaction --> DeIdentifiedStream["De-Identified Output PCollection"]
    Tokenize --> DeIdentifiedStream
    Bucketing --> DeIdentifiedStream

    DeIdentifiedStream --> Target["Secure BigQuery Dataset / GCS Silver Layer"]
```

---

## InfoTypes and transformation methods

1. **Built-in infoTypes**: Over 150 predefined global detectors (e.g. `EMAIL_ADDRESS`, `PHONE_NUMBER`, `CREDIT_CARD_NUMBER`, `IP_ADDRESS`, `US_SOCIAL_SECURITY_NUMBER`).
2. **Crypto-deterministic tokenization**: Encrypts values with a Cloud KMS key using AES-SIV. The same plain-text value yields the identical encrypted surrogate token across all tables, allowing analysts to perform `JOIN` operations on de-identified customer IDs without knowing real identities.
3. **Bucketing & generalization**: Groups continuous numerical or temporal values into discrete intervals to reduce re-identification risk.

---

## Configuring a de-identification template with JSON

Save as `dlp_crypto_template.json`:

```json
{
  "deidentifyTemplate": {
    "displayName": "Tokenize PII with KMS Key",
    "deidentifyConfig": {
      "recordTransformations": {
        "fieldTransformations": [
          {
            "fields": [{"name": "email"}, {"name": "phone_number"}],
            "primitiveTransformation": {
              "cryptoDeterministicConfig": {
                "cryptoKey": {
                  "kmsWrapped": {
                    "wrappedKey": "CiQA8x...",
                    "cryptoKeyName": "projects/my-gcp-project/locations/global/keyRings/dlp-ring/cryptoKeys/pii-key"
                  }
                },
                "surrogateInfoType": {
                  "name": "TOKENIZED_ID"
                }
              }
            }
          },
          {
            "fields": [{"name": "ssn"}],
            "primitiveTransformation": {
              "characterMaskConfig": {
                "maskingCharacter": "*",
                "numberToMask": 5,
                "charactersToIgnore": [{"charactersToSkip": "-"}]
              }
            }
          }
        ]
      }
    }
  }
}
```

---

## Integrating Cloud DLP inside an Apache Beam pipeline

Use the official `apache_beam.ml.gcp.cloud_dlp` transform for high-throughput batch and streaming tokenization:

```python
import apache_beam as beam
from apache_beam.ml.gcp.cloud_dlp import MaskUserFacingData

def run_dlp_pipeline():
    with beam.Pipeline() as p:
        (
            p
            | "ReadPubSub" >> beam.io.ReadFromPubSub(subscription="projects/my-proj/subscriptions/raw-user-events")
            | "ParseJSON" >> beam.Map(json.loads)
            | "MaskPIIWithDLP" >> MaskUserFacingData(
                project="my-gcp-project",
                deidentify_template_name="projects/my-gcp-project/locations/global/deidentifyTemplates/template-01"
            )
            | "WriteCleanData" >> beam.io.WriteToBigQuery(
                "my-gcp-project:clean_staging.user_events",
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
            )
        )
```

---

## Summary heuristics

1. Use **Crypto-deterministic pseudonymization** for primary/foreign keys (e.g. user IDs) so analytical pipelines can join tables without exposing raw IDs.
2. Tokenize sensitive PII at the ingestion boundary (inside Dataflow) before data lands in shared data lakes.
3. Secure encryption keys in Google Cloud KMS and restrict decryption permissions to compliance escalation roles.

---

| Previous Lesson | Curriculum | Next Lesson |
| :--- | :---: | ---: |
| [0033: Fine-Grained Access Control](0033-fine-grained-access-control-policy-tags-rls.md) | [All Lessons (Index)](index.md) | [0035: End-to-End Pipeline Observability](0035-pipeline-observability-lineage.md) |
