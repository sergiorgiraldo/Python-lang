# Sessionization

## Overview

Sessionization groups a stream of events into logical sessions based on idle time gaps. When the time between consecutive events exceeds a threshold (typically 30 minutes for web analytics), a new session begins. This is one of the most commonly asked DE SQL questions and one of the most common production analytics patterns.

## The Pattern

Three steps, each building on the previous:

```sql
-- Step 1: Compute gap from previous event
LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time) AS prev_time

-- Step 2: Flag new sessions where gap exceeds threshold
CASE WHEN gap > 30 THEN 1 ELSE 0 END AS new_session_flag

-- Step 3: Running sum of flags = session counter
SUM(new_session_flag) OVER (PARTITION BY user_id ORDER BY event_time) AS session_id
```

The running sum of binary flags is an elegant trick: every time a new session starts (flag=1), the sum increments. Events within the same session (flag=0) share the same sum value.

## Why 30 Minutes?

The 30-minute idle timeout is an industry standard originating from Google Analytics. It represents a reasonable balance: short enough to separate distinct browsing intents, long enough to accommodate brief interruptions (phone call, coffee break). In practice, teams tune this threshold based on their product's usage patterns. Gaming apps might use 5 minutes. B2B SaaS might use 60 minutes.

## Session-Level Aggregation

After assigning session IDs, aggregate per session:

```sql
SELECT
    user_id,
    session_id,
    MIN(event_time) AS session_start,
    MAX(event_time) AS session_end,
    COUNT(*) AS events_in_session,
    EXTRACT(EPOCH FROM MAX(event_time) - MIN(event_time)) / 60.0 AS session_duration_minutes
FROM sessionized_events
GROUP BY user_id, session_id
```

This feeds session-level metrics: average session duration, events per session, bounce rate (sessions with 1 event).

## At Scale

The LAG + running SUM approach is two passes over the data (both sorted the same way, so effectively one sort): O(n log n). For 1B clickstream events across 10M users, the PARTITION BY user_id creates 10M partitions averaging 100 events each. Each partition sorts independently. In distributed engines (Spark), this is a shuffle by user_id followed by local sort and window computation.

Memory usage: the window buffer holds one partition at a time. If one user has 1M events (a bot or power user), that partition requires 1M rows in memory. Skewed users cause executor memory pressure.

## Production Context

**Web analytics:** Session detection is the foundation of web analytics. Page views become browsing sessions, which feed metrics like session duration, pages per session and conversion funnels.

**App analytics:** Mobile and desktop apps use the same pattern. Events include screen views, button clicks and API calls. Sessions represent distinct usage periods.

**Streaming pipelines:** In Kafka/Flink/Spark Streaming, sessionization runs in real time. The concept is the same (gap-based grouping) but implemented with session windows rather than SQL window functions.

**Security analytics:** Session detection in login events identifies suspicious patterns: sessions from unusual locations, concurrent sessions and session hijacking attempts.

## Common Interview Variants

- "Sessionize clickstream data" (this exact problem)
- "Find the average session duration per user"
- "Identify users with sessions longer than 1 hour"
- "Count sessions per day per user"

All start with the LAG + flag + running sum pattern.
