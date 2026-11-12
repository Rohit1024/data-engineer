-- Run in the lab project, with default dataset medallia_lab and named parameters.
-- These tables are replaceable, single-window teaching fixtures.
ASSERT (SELECT COUNT(*) FROM medallia_lab.raw_window) = @expected_rows
  AS 'Raw row count differs from the completed manifest';

ASSERT NOT EXISTS (
  SELECT 1 FROM medallia_lab.raw_window
  WHERE attempt_id != @expected_attempt
) AS 'Staging contains a different attempt';

ASSERT NOT EXISTS (
  SELECT 1 FROM medallia_lab.raw_window
  GROUP BY tenant, feedback_id HAVING COUNT(*) > 1
) AS 'Duplicate feedback identity within the selected snapshot';

CREATE TEMP TABLE typed AS
WITH parsed AS (
  SELECT *,
    SAFE_CAST(JSON_VALUE(payload, '$.source_time.values[0]') AS TIMESTAMP) AS source_time,
    SAFE_CAST(JSON_VALUE(payload, '$.score.values[0]') AS INT64) AS score
  FROM medallia_lab.raw_window
)
SELECT *,
  CASE
    WHEN JSON_VALUE(payload, '$.id') IS DISTINCT FROM feedback_id
      THEN 'Payload identity differs from envelope'
    WHEN COALESCE(ARRAY_LENGTH(JSON_QUERY_ARRAY(payload, '$.source_time.values')), 0) != 1
      OR source_time IS NULL THEN 'Expected one parseable source timestamp'
    WHEN source_time < window_start OR source_time >= window_end
      THEN 'Source timestamp outside requested window'
    WHEN COALESCE(ARRAY_LENGTH(JSON_QUERY_ARRAY(payload, '$.score.values')), 0) != 1
      OR score IS NULL OR score NOT BETWEEN 0 AND 10
      THEN 'Not an eligible 0-to-10 NPS response'
    ELSE NULL
  END AS rejection_reason
FROM parsed;

CREATE OR REPLACE TABLE medallia_lab.quarantine AS
SELECT * FROM typed WHERE rejection_reason IS NOT NULL;

CREATE OR REPLACE TABLE medallia_lab.feedback_snapshot
PARTITION BY DATE(source_time)
CLUSTER BY tenant AS
SELECT tenant, feedback_id, source_time, score, extracted_at, attempt_id
FROM typed WHERE rejection_reason IS NULL;

ASSERT (SELECT COUNT(*) FROM medallia_lab.feedback_snapshot)
     + (SELECT COUNT(*) FROM medallia_lab.quarantine) = @expected_rows
  AS 'Accepted and rejected rows do not reconcile';

SELECT
  DATE(source_time) AS source_date,
  COUNT(*) AS eligible_responses,
  COUNTIF(score >= 9) AS promoters,
  COUNTIF(score <= 6) AS detractors,
  ROUND(100 * SAFE_DIVIDE(
    COUNTIF(score >= 9) - COUNTIF(score <= 6), COUNT(*)
  ), 2) AS nps
FROM medallia_lab.feedback_snapshot
GROUP BY source_date;
