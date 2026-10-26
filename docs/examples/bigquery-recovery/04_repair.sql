DECLARE repair_day DATE DEFAULT DATE '2026-10-25';
DECLARE recovery_key STRING DEFAULT 'orders-20261025-repair-v1';

CREATE TEMP TABLE stage AS
SELECT * FROM `YOUR_PROJECT_ID.recovery_lab.backfill_20261025`;

ASSERT (SELECT COUNT(*) = 6 FROM stage) AS 'Source control row count differs';
ASSERT (SELECT SUM(amount_cents) = 21000 FROM stage) AS 'Source control total differs';
ASSERT (SELECT COUNT(*) = 0 FROM stage
        WHERE event_day IS NULL OR event_day != repair_day
          OR event_id IS NULL OR order_id IS NULL OR version IS NULL
          OR amount_cents IS NULL OR amount_cents < 0 OR status IS NULL)
  AS 'Invalid source contract';
ASSERT (SELECT COUNT(*) = COUNT(DISTINCT event_id) FROM stage)
  AS 'Source keys are not unique';

BEGIN TRANSACTION;
DELETE FROM `YOUR_PROJECT_ID.recovery_lab.actual_events`
WHERE event_day = repair_day;
INSERT INTO `YOUR_PROJECT_ID.recovery_lab.actual_events`
SELECT *, recovery_key FROM stage;

-- Check multiplicity as well as values; EXCEPT DISTINCT alone hides duplicates.
ASSERT (
  SELECT COUNT(*) = 6 AND COUNT(DISTINCT event_id) = 6 AND SUM(amount_cents) = 21000
  FROM `YOUR_PROJECT_ID.recovery_lab.actual_events` WHERE event_day = repair_day
) AS 'Post-repair count/key/amount check failed';
ASSERT (
  SELECT COUNT(*) = 0 FROM (
    SELECT event_day, event_id, order_id, version, amount_cents, status FROM stage
    EXCEPT DISTINCT
    SELECT event_day, event_id, order_id, version, amount_cents, status
    FROM `YOUR_PROJECT_ID.recovery_lab.actual_events` WHERE event_day = repair_day
  )
) AS 'Expected values absent from target';
ASSERT (
  SELECT COUNT(*) = 0 FROM (
    SELECT event_day, event_id, order_id, version, amount_cents, status
    FROM `YOUR_PROJECT_ID.recovery_lab.actual_events` WHERE event_day = repair_day
    EXCEPT DISTINCT
    SELECT event_day, event_id, order_id, version, amount_cents, status FROM stage
  )
) AS 'Unexpected values remain in target';

-- Keep the data repair and its completion record in the same transaction.
DELETE FROM `YOUR_PROJECT_ID.recovery_lab.recovery_audit`
WHERE recovery_id = recovery_key;
INSERT INTO `YOUR_PROJECT_ID.recovery_lab.recovery_audit`
VALUES (recovery_key, repair_day, 'fixture-export-20261025-v1', 6, 21000, CURRENT_TIMESTAMP());
COMMIT TRANSACTION;
