# Change Detection

## Overview

Change detection uses LAG to compare each row with the previous and identify when a value changed. This is the core technique for implementing Slowly Changing Dimensions (SCD Type 2), building audit trails and detecting state transitions in entity histories.

## The Pattern

```sql
WITH with_prev AS (
    SELECT *,
           LAG(status) OVER (PARTITION BY entity_id ORDER BY timestamp) AS prev_status
    FROM status_log
)
SELECT *,
       CASE
           WHEN prev_status IS NULL THEN 'initial'
           WHEN prev_status != status THEN 'changed'
           ELSE 'unchanged'
       END AS change_type
FROM with_prev
```

The three-way CASE handles:
- **NULL prev_status:** first record for this entity (initial state)
- **Different prev_status:** a transition occurred
- **Same prev_status:** no change (can be filtered out)

## SCD Type 2 with Window Functions

SCD Type 2 tracks the history of an entity by creating a new row for each change. Each row has a valid_from and valid_to timestamp defining when that version was active.

```sql
-- Filter to only changed rows, then use LEAD for validity ranges
WITH changes AS (
    SELECT entity_id, status, recorded_at
    FROM (
        SELECT *, LAG(status) OVER (PARTITION BY entity_id ORDER BY recorded_at) AS prev
        FROM status_log
    ) t
    WHERE prev IS NULL OR prev != status
)
SELECT
    entity_id,
    status,
    recorded_at AS valid_from,
    LEAD(recorded_at) OVER (PARTITION BY entity_id ORDER BY recorded_at) AS valid_to
FROM changes
```

A NULL valid_to means the row is the current version.

## Detecting Specific Transitions

Sometimes you need to find specific state changes, not all changes:

```sql
-- Find users who went from 'active' to 'churned'
WHERE prev_status = 'active' AND status = 'churned'
```

This powers churn analysis, downgrade detection and lifecycle stage tracking.

## At Scale

Change detection is a single sorted pass per partition: O(n log n) for the sort, O(n) for the LAG comparison. For entities with long histories (1000+ status records per entity), the comparison is still O(1) per row because LAG only looks back one row.

In production, change detection often runs incrementally: process only new records since the last run, compare the latest new record against the last known state. This reduces the scope from "entire history" to "delta since last checkpoint."

## Production Context

**SCD Type 2 pipelines:** The most common use of change detection in data warehousing. Source systems provide current state; the pipeline detects changes and maintains version history. Tools like dbt handle this with snapshot strategies, which use the same LAG-based comparison under the hood.

**Audit trails:** Regulatory compliance (SOX, GDPR) requires tracking when and how data changed. Change detection builds the audit log from transactional data.

**Alerting on state changes:** "Notify when a customer's subscription status changes" or "alert when a server's health status transitions from healthy to degraded." The LAG comparison triggers the notification.

**Data quality monitoring:** Detect when a column that should be stable (account type, country) changes unexpectedly. Unexpected changes may indicate data corruption or ETL bugs.

## Common Interview Variants

- "Implement SCD Type 2 in SQL" (this exact pattern)
- "Find when each user first became inactive"
- "Count the number of status changes per entity"
- "Build a timeline of state transitions"
