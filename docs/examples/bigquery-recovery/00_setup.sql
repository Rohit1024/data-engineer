-- Run once in a new recovery_lab dataset. Replace YOUR_PROJECT_ID throughout.
CREATE TABLE `YOUR_PROJECT_ID.recovery_lab.expected_events` (
  event_day DATE, event_id STRING, order_id INT64, version INT64,
  amount_cents INT64, status STRING
);
INSERT INTO `YOUR_PROJECT_ID.recovery_lab.expected_events` VALUES
  ('2026-10-25', 'e1', 101, 1, 1000, 'paid'),
  ('2026-10-25', 'e2', 102, 1, 2000, 'paid'),
  ('2026-10-25', 'e3', 103, 1, 3000, 'paid'),
  ('2026-10-25', 'e4', 104, 1, 4000, 'paid'),
  ('2026-10-25', 'e5', 105, 1, 5000, 'paid'),
  ('2026-10-25', 'e6', 106, 1, 6000, 'paid');

CREATE TABLE `YOUR_PROJECT_ID.recovery_lab.actual_events` (
  event_day DATE, event_id STRING, order_id INT64, version INT64,
  amount_cents INT64, status STRING, ingest_attempt STRING
) PARTITION BY event_day CLUSTER BY event_id;
-- A different day's row must survive the repair.
INSERT INTO `YOUR_PROJECT_ID.recovery_lab.actual_events`
VALUES ('2026-10-24', 'keep-me', 999, 1, 999, 'paid', 'earlier-run');

CREATE TABLE `YOUR_PROJECT_ID.recovery_lab.recovery_audit` (
  recovery_id STRING, event_day DATE, source_boundary STRING,
  verified_rows INT64, verified_cents INT64, verified_at TIMESTAMP
);
