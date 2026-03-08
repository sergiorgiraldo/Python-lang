"""
Window Aggregations in Structured Streaming.

Pattern connection:
  patterns/04_sliding_window/ - fixed and variable size windows
  system_design/walkthroughs/design_real_time_dashboard/ - sliding window metrics

Streaming window types:
  1. Tumbling: non-overlapping, fixed-size
     window("timestamp", "1 minute")
  2. Sliding: overlapping, fixed-size with slide interval
     window("timestamp", "1 minute", "30 seconds")
  3. Session: gap-based, variable-size (Spark 3.2+)
     session_window("timestamp", "10 minutes")

Under the hood:
  - Tumbling: each event belongs to exactly one window
  - Sliding: each event belongs to (window_size / slide_interval) windows
  - Session: events are grouped by inactivity gap (like our sessionization pattern)
  - Watermark determines when a window is "closed" and results are finalized

Note on testing:
  Streaming tests with the rate source are timing-dependent. Tests here
  check that queries start, run without errors and produce non-empty output
  rather than asserting exact counts.
"""

import pytest

pyspark = pytest.importorskip("pyspark")

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.streaming import StreamingQuery


# ---------------------------------------------------------------------------
# Tumbling window
# ---------------------------------------------------------------------------


def start_tumbling_window(
    spark: SparkSession,
    rows_per_second: int = 100,
    window_duration: str = "5 seconds",
    query_name: str = "tumbling_counts",
) -> StreamingQuery:
    """Start a tumbling window aggregation.

    Tumbling windows are non-overlapping: each event belongs to exactly
    one window. A 5-second tumbling window groups events into
    [0s-5s), [5s-10s), [10s-15s), etc.

    Args:
        spark: Active SparkSession.
        rows_per_second: Rate source generation speed.
        window_duration: Size of the tumbling window.
        query_name: Name for the in-memory table.

    Returns:
        The active StreamingQuery handle.
    """
    stream = (
        spark.readStream
        .format("rate")
        .option("rowsPerSecond", rows_per_second)
        .load()
    )

    result = (
        stream
        .withWatermark("timestamp", "5 seconds")
        .groupBy(F.window("timestamp", window_duration))
        .agg(F.count("*").alias("event_count"))
    )

    query = (
        result.writeStream
        .format("memory")
        .queryName(query_name)
        .outputMode("complete")
        .start()
    )
    return query


# ---------------------------------------------------------------------------
# Sliding window
# ---------------------------------------------------------------------------


def start_sliding_window(
    spark: SparkSession,
    rows_per_second: int = 100,
    window_duration: str = "10 seconds",
    slide_duration: str = "5 seconds",
    query_name: str = "sliding_counts",
) -> StreamingQuery:
    """Start a sliding window aggregation.

    Sliding windows overlap: each event may belong to multiple windows.
    A 10-second window with a 5-second slide means each event is counted
    in two windows. This produces smoother aggregations than tumbling.

    Args:
        spark: Active SparkSession.
        rows_per_second: Rate source generation speed.
        window_duration: Total size of each window.
        slide_duration: How far the window slides each step.
        query_name: Name for the in-memory table.

    Returns:
        The active StreamingQuery handle.
    """
    stream = (
        spark.readStream
        .format("rate")
        .option("rowsPerSecond", rows_per_second)
        .load()
    )

    result = (
        stream
        .withWatermark("timestamp", "10 seconds")
        .groupBy(F.window("timestamp", window_duration, slide_duration))
        .agg(F.count("*").alias("event_count"))
    )

    query = (
        result.writeStream
        .format("memory")
        .queryName(query_name)
        .outputMode("complete")
        .start()
    )
    return query


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestTumblingWindow:
    """Tumbling window should produce non-overlapping window results."""

    def test_tumbling_produces_output(self, spark: SparkSession) -> None:
        query_name = "test_tumbling"
        query = start_tumbling_window(
            spark, rows_per_second=100, query_name=query_name
        )
        try:
            query.awaitTermination(timeout=5)
            result = spark.sql(f"SELECT * FROM {query_name}")
            assert result.count() > 0, (
                "Expected at least one tumbling window result"
            )
        finally:
            query.stop()

    def test_tumbling_stops_cleanly(self, spark: SparkSession) -> None:
        query = start_tumbling_window(spark, query_name="test_tumbling_stop")
        query.stop()
        assert not query.isActive


class TestSlidingWindow:
    """Sliding window should produce overlapping window results."""

    def test_sliding_produces_output(self, spark: SparkSession) -> None:
        query_name = "test_sliding"
        query = start_sliding_window(
            spark, rows_per_second=100, query_name=query_name
        )
        try:
            query.awaitTermination(timeout=5)
            result = spark.sql(f"SELECT * FROM {query_name}")
            assert result.count() > 0, (
                "Expected at least one sliding window result"
            )
        finally:
            query.stop()

    def test_sliding_stops_cleanly(self, spark: SparkSession) -> None:
        query = start_sliding_window(spark, query_name="test_sliding_stop")
        query.stop()
        assert not query.isActive
