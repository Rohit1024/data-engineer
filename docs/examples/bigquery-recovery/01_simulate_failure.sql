-- Run exactly once. This script deliberately fails AFTER committed writes.
-- There is no explicit transaction around the script.
INSERT INTO `YOUR_PROJECT_ID.recovery_lab.actual_events`
SELECT *, 'attempt-1'
FROM `YOUR_PROJECT_ID.recovery_lab.expected_events`
WHERE event_id IN ('e1', 'e2');

INSERT INTO `YOUR_PROJECT_ID.recovery_lab.actual_events` VALUES
  ('2026-10-25', 'e2', 102, 1, 2000, 'paid', 'unsafe-retry'),
  ('2026-10-25', 'e3', 103, 1, 3500, 'paid', 'bad-transform'),
  ('2026-10-25', 'e4', 104, 1, 4000, 'paid', 'attempt-2'),
  ('2026-10-25', 'unexpected', 9999, 1, 6000, 'paid', 'wrong-input');

ASSERT FALSE AS 'Simulated orchestration failure after committed inserts';
