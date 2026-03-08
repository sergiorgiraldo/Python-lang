"""
Structured Streaming Basics.

Pattern connection:
  patterns/04_sliding_window/ - processing elements as they arrive
  system_design/walkthroughs/design_event_pipeline/ - real-time event processing

Structured Streaming treats a stream as an unbounded table. New data
arrives as new rows appended to the table. Queries run incrementally,
processing only the new rows.

Key concepts:
  - Source: where data comes from (Kafka, files, rate for testing)
  - Sink: where results go (Kafka, files, console, memory for testing)
  - Trigger: how often to process (processingTime, once, availableNow)
  - Output mode: append (new rows only), complete (full result), update (changed rows)
  - Watermark: how late data is tolerated before being dropped

Testing approach:
  - "rate" source generates rows with (timestamp, value) at a fixed rate
  - "memory" sink stores results in an in-memory table queryable with SQL
  - awaitTermination(timeout) prevents tests from hanging
"""

import pytest

pyspark = pytest.importorskip("pyspark")

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.streaming import StreamingQuery


# ---------------------------------------------------------------------------
# Basic streaming query with rate source
# ---------------------------------------------------------------------------


def start_rate_stream(
    spark: SparkSession,
    rows_per_second: int = 10,
    query_name: str = "rate_test",
) -> StreamingQuery:
    """Start a basic streaming query using the rate source.

    The rate source generates rows with (timestamp, value) at the given rate.
    Results are written to a memory sink for inspection.

    Args:
        spark: Active SparkSession.
        rows_per_second: How many rows to generate per second.
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

    query = (
        stream.writeStream
        .format("memory")
        .queryName(query_name)
        .outputMode("append")
        .start()
    )
    return query


# ---------------------------------------------------------------------------
# Streaming aggregation with watermark
# ---------------------------------------------------------------------------


def start_windowed_count(
    spark: SparkSession,
    rows_per_second: int = 10,
    window_duration: str = "10 seconds",
    watermark_delay: str = "10 seconds",
    query_name: str = "windowed_counts",
) -> StreamingQuery:
    """Start a streaming query that counts events per time window.

    Uses a watermark to bound state: windows older than the watermark
    delay are finalized and their state is dropped.

    Args:
        spark: Active SparkSession.
        rows_per_second: Rate source generation speed.
        window_duration: Size of the tumbling window.
        watermark_delay: How late events are tolerated.
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
        .withWatermark("timestamp", watermark_delay)
        .groupBy(F.window("timestamp", window_duration))
        .count()
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


class TestStructuredStreamingBasics:
    """Streaming queries should start, produce output and stop cleanly."""

    def test_rate_stream_produces_output(self, spark: SparkSession) -> None:
        query_name = "test_rate_basic"
        query = start_rate_stream(spark, rows_per_second=100, query_name=query_name)
        try:
            query.awaitTermination(timeout=5)
            result = spark.sql(f"SELECT * FROM {query_name}")
            count = result.count()
            # Rate source at 100 rows/sec for up to 5 seconds
            assert count > 0, "Expected at least some rows from rate source"
        finally:
            query.stop()

    def test_query_is_active(self, spark: SparkSession) -> None:
        query = start_rate_stream(spark, query_name="test_active_check")
        try:
            assert query.isActive, "Query should be active after start"
        finally:
            query.stop()

    def test_query_stops_cleanly(self, spark: SparkSession) -> None:
        query = start_rate_stream(spark, query_name="test_stop_clean")
        query.stop()
        assert not query.isActive, "Query should not be active after stop"

    def test_windowed_count_produces_output(
        self, spark: SparkSession
    ) -> None:
        query_name = "test_windowed_basic"
        query = start_windowed_count(
            spark,
            rows_per_second=100,
            window_duration="5 seconds",
            watermark_delay="5 seconds",
            query_name=query_name,
        )
        try:
            query.awaitTermination(timeout=5)
            result = spark.sql(f"SELECT * FROM {query_name}")
            count = result.count()
            assert count > 0, "Expected at least one window result"
        finally:
            query.stop()
