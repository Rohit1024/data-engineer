-- Run once after stopping writers. Preserve evidence; do not overwrite it.
CREATE SNAPSHOT TABLE `YOUR_PROJECT_ID.recovery_lab.before_repair`
CLONE `YOUR_PROJECT_ID.recovery_lab.actual_events`;

-- In production, read a retained, verified source export at a recorded boundary.
CREATE TABLE `YOUR_PROJECT_ID.recovery_lab.backfill_20261025` AS
SELECT * FROM `YOUR_PROJECT_ID.recovery_lab.expected_events`
WHERE event_day = DATE '2026-10-25';
