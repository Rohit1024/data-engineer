DECLARE repair_day DATE DEFAULT DATE '2026-10-25';

-- Materialize the observation once. Freeze writers before relying on it.
CREATE TEMP TABLE expected AS
SELECT * FROM `YOUR_PROJECT_ID.recovery_lab.expected_events`
WHERE event_day = repair_day;
CREATE TEMP TABLE observed AS
SELECT * FROM `YOUR_PROJECT_ID.recovery_lab.actual_events`
WHERE event_day = repair_day;

-- First result: counts alone do not establish equality.
SELECT 'source' AS side, COUNT(*) AS physical_rows,
       COUNT(DISTINCT event_id) AS distinct_ids, SUM(amount_cents) AS cents
FROM expected
UNION ALL
SELECT 'target', COUNT(*), COUNT(DISTINCT event_id), SUM(amount_cents)
FROM observed;

-- Second result: duplicate event IDs and whether their payloads disagree.
SELECT event_id, COUNT(*) AS copies,
       COUNT(DISTINCT TO_JSON_STRING(STRUCT(order_id, version, amount_cents, status))) AS payload_variants,
       ARRAY_AGG(ingest_attempt ORDER BY ingest_attempt) AS attempts
FROM observed
GROUP BY event_id
HAVING COUNT(*) > 1;

-- Third result: expected IDs with no target representation.
SELECT e.* FROM expected e
WHERE NOT EXISTS (SELECT 1 FROM observed o WHERE o.event_id = e.event_id)
ORDER BY event_id;

-- Fourth result: unexpected target IDs.
SELECT o.* FROM observed o
WHERE NOT EXISTS (SELECT 1 FROM expected e WHERE e.event_id = o.event_id)
ORDER BY event_id;

-- Fifth result: matching IDs with incorrect values.
SELECT e.event_id, e.amount_cents AS expected_cents, o.amount_cents AS observed_cents,
       o.ingest_attempt
FROM expected e JOIN observed o USING (event_id)
WHERE TO_JSON_STRING(STRUCT(e.order_id, e.version, e.amount_cents, e.status))
   != TO_JSON_STRING(STRUCT(o.order_id, o.version, o.amount_cents, o.status));

-- Sixth result: IDs needing insertion OR correction, not just missing IDs.
SELECT e.* FROM expected e
WHERE NOT EXISTS (
  SELECT 1 FROM observed o
  WHERE e.event_id = o.event_id
    AND TO_JSON_STRING(STRUCT(e.order_id, e.version, e.amount_cents, e.status))
      = TO_JSON_STRING(STRUCT(o.order_id, o.version, o.amount_cents, o.status))
)
ORDER BY event_id;
