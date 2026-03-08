"""
Sessionization with PySpark.

Pattern connection:
  patterns/04_sliding_window/de_scenarios/sessionization
  sql/01_window_functions/de_scenarios/sessionization

Sessionization assigns events to sessions based on inactivity gaps.
A new session starts when the gap between consecutive events exceeds
a threshold (typically 30 minutes).

Under the hood:
  - LAG() to get previous event timestamp
  - Compute gap between current and previous event
  - CASE WHEN gap > threshold to flag session boundaries
  - Running SUM() of boundary flags to assign session numbers
  - This requires data sorted by user + timestamp within each partition
  - Three sequential window operations = three passes over the sorted data
"""

import pytest

pyspark = pytest.importorskip("pyspark")

from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql import functions as F


# ---------------------------------------------------------------------------
# Pure Python: sessionization
# ---------------------------------------------------------------------------


def sessionize_python(
    events: list[tuple[str, int]],
    timeout: int,
) -> list[tuple[str, int, int]]:
    """Assign session IDs based on inactivity gaps.

    A new session starts when the gap between consecutive events
    for the same user exceeds the timeout threshold.

    Time:  O(n log n) for sort + O(n) for scan
    Space: O(n) for the result

    Args:
        events: List of (user_id, timestamp) tuples.
        timeout: Maximum gap (in seconds) before a new session starts.

    Returns:
        List of (user_id, timestamp, session_id) tuples.

    Example:
        >>> sessionize_python([("u1", 100), ("u1", 110), ("u1", 500)], 60)
        [('u1', 100, 0), ('u1', 110, 0), ('u1', 500, 1)]
    """
    # Sort by user then timestamp
    sorted_events = sorted(events, key=lambda x: (x[0], x[1]))

    result: list[tuple[str, int, int]] = []
    prev_user: str | None = None
    prev_ts: int = 0
    session_id: int = 0

    for user_id, ts in sorted_events:
        if user_id != prev_user:
            # New user, reset session counter
            session_id = 0
        elif ts - prev_ts > timeout:
            # Same user, gap exceeds timeout
            session_id += 1

        result.append((user_id, ts, session_id))
        prev_user = user_id
        prev_ts = ts

    return result


# ---------------------------------------------------------------------------
# PySpark: sessionization with LAG + cumulative SUM
# ---------------------------------------------------------------------------


def sessionize_spark(
    spark: SparkSession,
    events: list[tuple[str, int]],
    timeout: int,
) -> DataFrame:
    """Assign session IDs using window functions.

    Three-step pattern:
      1. LAG to get previous timestamp per user
      2. Flag rows where gap > timeout as session boundaries
      3. Cumulative SUM of flags to assign session IDs

    Args:
        spark: Active SparkSession.
        events: List of (user_id, timestamp) tuples.
        timeout: Maximum gap (in seconds) before a new session starts.

    Returns:
        DataFrame with columns: user_id, timestamp, session_id.
    """
    df = spark.createDataFrame(events, ["user_id", "timestamp"])

    # Step 1: get previous timestamp per user
    user_window = Window.partitionBy("user_id").orderBy("timestamp")

    df_with_prev = df.withColumn(
        "prev_ts",
        F.lag("timestamp").over(user_window),
    )

    # Step 2: flag session boundaries (gap > timeout or first event)
    df_with_flag = df_with_prev.withColumn(
        "new_session",
        F.when(
            F.col("prev_ts").isNull() | (F.col("timestamp") - F.col("prev_ts") > timeout),
            F.lit(1),
        ).otherwise(F.lit(0)),
    )

    # Step 3: cumulative sum of flags = session ID
    session_window = (
        Window.partitionBy("user_id")
        .orderBy("timestamp")
        .rowsBetween(Window.unboundedPreceding, Window.currentRow)
    )

    result = df_with_flag.withColumn(
        "session_id",
        F.sum("new_session").over(session_window) - 1,
    )

    return result.select("user_id", "timestamp", "session_id")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


EVENTS: list[tuple[str, int]] = [
    # User 1: two sessions (gap at 500)
    ("u1", 100),
    ("u1", 110),
    ("u1", 120),
    ("u1", 500),
    ("u1", 510),
    # User 2: one session (all within timeout)
    ("u2", 200),
    ("u2", 220),
    ("u2", 240),
    # User 3: three sessions
    ("u3", 100),
    ("u3", 400),
    ("u3", 700),
]

TIMEOUT = 60


class TestSessionization:
    """Sessionization should assign correct session IDs based on gaps."""

    def test_events_within_timeout_same_session(
        self, spark: SparkSession
    ) -> None:
        result = sessionize_spark(spark, EVENTS, TIMEOUT)
        u2_rows = [r for r in result.collect() if r["user_id"] == "u2"]
        session_ids = {r["session_id"] for r in u2_rows}
        # All u2 events are within 60s of each other
        assert session_ids == {0}

    def test_gap_exceeds_timeout_new_session(
        self, spark: SparkSession
    ) -> None:
        result = sessionize_spark(spark, EVENTS, TIMEOUT)
        u1_rows = sorted(
            [(r["timestamp"], r["session_id"]) for r in result.collect() if r["user_id"] == "u1"]
        )
        # Events 100, 110, 120 in session 0; events 500, 510 in session 1
        assert u1_rows == [(100, 0), (110, 0), (120, 0), (500, 1), (510, 1)]

    def test_each_gap_starts_new_session(self, spark: SparkSession) -> None:
        result = sessionize_spark(spark, EVENTS, TIMEOUT)
        u3_rows = sorted(
            [(r["timestamp"], r["session_id"]) for r in result.collect() if r["user_id"] == "u3"]
        )
        # Each event is >60s apart, so each is its own session
        assert u3_rows == [(100, 0), (400, 1), (700, 2)]

    def test_users_have_independent_sessions(
        self, spark: SparkSession
    ) -> None:
        result = sessionize_spark(spark, EVENTS, TIMEOUT)
        rows = result.collect()

        # Each user starts at session_id 0
        for user in ["u1", "u2", "u3"]:
            user_rows = [r for r in rows if r["user_id"] == user]
            min_session = min(r["session_id"] for r in user_rows)
            assert min_session == 0, f"{user} should start at session 0"

    def test_matches_python_sessionization(
        self, spark: SparkSession
    ) -> None:
        python_result = sessionize_python(EVENTS, TIMEOUT)
        spark_result = sessionize_spark(spark, EVENTS, TIMEOUT)

        spark_rows = sorted(
            [
                (r["user_id"], r["timestamp"], r["session_id"])
                for r in spark_result.collect()
            ]
        )
        assert spark_rows == sorted(python_result)
