"""
Broadcast Join: Small table + large table.

Pattern connection: patterns/01_hash_map/
  Python: build a dict from the small dataset, look up each element from the large dataset.
  Spark: broadcast the small DataFrame to every worker, join locally (no shuffle).

Under the hood:
  - Spark serializes the small DataFrame and sends it to every executor
  - Each executor builds a local hash table from the broadcast data
  - The large DataFrame stays in place (no network I/O for the large side)
  - Default threshold: 10MB (spark.sql.autoBroadcastJoinThreshold)
  - For larger "small" tables, use broadcast() hint to force it

When to use:
  - One side fits in executor memory (typically < 1GB)
  - You want to avoid a shuffle on the large side
  - Common in DE: joining a large fact table with a small dimension table
"""

import pytest

pyspark = pytest.importorskip("pyspark")

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


# ---------------------------------------------------------------------------
# Pure Python: dict lookup (the pattern behind broadcast join)
# ---------------------------------------------------------------------------


def join_with_dict(
    large: list[tuple[str, int]], small: list[tuple[str, str]]
) -> list[tuple[str, int, str]]:
    """Join two datasets using a dict built from the small side.

    Time:  O(n + m) where n = len(large), m = len(small)
    Space: O(m) for the lookup dict

    Args:
        large: List of (key, value) tuples representing the large dataset.
        small: List of (key, label) tuples representing the small dataset.

    Returns:
        List of (key, value, label) tuples for matching keys.

    Example:
        >>> join_with_dict([("a", 1), ("b", 2)], [("a", "x")])
        [('a', 1, 'x')]
    """
    lookup = {k: v for k, v in small}
    return [(k, v, lookup[k]) for k, v in large if k in lookup]


# ---------------------------------------------------------------------------
# PySpark: broadcast join
# ---------------------------------------------------------------------------


def broadcast_join(
    spark: SparkSession,
    large_data: list[tuple[str, int]],
    small_data: list[tuple[str, str]],
) -> DataFrame:
    """Broadcast the small DataFrame to avoid shuffling the large one.

    The broadcast() hint tells Spark to send the small DataFrame to every
    executor. Each executor builds a local hash table and joins against
    its partition of the large DataFrame with zero shuffle on the large side.

    Args:
        spark: Active SparkSession.
        large_data: Rows for the large DataFrame (key, value).
        small_data: Rows for the small DataFrame (key, label).

    Returns:
        Joined DataFrame with columns: key, value, label.
    """
    large_df = spark.createDataFrame(large_data, ["key", "value"])
    small_df = spark.createDataFrame(small_data, ["key", "label"])

    # Explicit broadcast hint: small_df is sent to every executor
    result = large_df.join(F.broadcast(small_df), on="key", how="inner")
    return result


def get_broadcast_plan(
    spark: SparkSession,
    large_data: list[tuple[str, int]],
    small_data: list[tuple[str, str]],
) -> str:
    """Return the physical plan string showing BroadcastHashJoin.

    Useful for verifying that Spark chose the broadcast strategy.

    Args:
        spark: Active SparkSession.
        large_data: Rows for the large DataFrame (key, value).
        small_data: Rows for the small DataFrame (key, label).

    Returns:
        The explain plan as a string.
    """
    large_df = spark.createDataFrame(large_data, ["key", "value"])
    small_df = spark.createDataFrame(small_data, ["key", "label"])
    result = large_df.join(F.broadcast(small_df), on="key")

    # explain(True) prints to stdout; _jdf.queryExecution() gives the plan string
    # == Physical Plan ==
    # *(2) BroadcastHashJoin [key#0], [key#2], Inner, ...
    #    :- *(2) ... (large side, no Exchange/shuffle)
    #    +- BroadcastExchange HashedRelationBroadcastMode(...)
    #       +- *(1) ... (small side, broadcast)
    return result._jdf.queryExecution().simpleString()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


LARGE_DATA: list[tuple[str, int]] = [
    ("a", 1),
    ("b", 2),
    ("c", 3),
    ("d", 4),
    ("e", 5),
]

SMALL_DATA: list[tuple[str, str]] = [
    ("a", "alpha"),
    ("c", "charlie"),
    ("e", "echo"),
]


class TestBroadcastJoin:
    """Broadcast join should match the Python dict-lookup approach."""

    def test_matches_python_dict_join(self, spark: SparkSession) -> None:
        python_result = join_with_dict(LARGE_DATA, SMALL_DATA)
        spark_result = broadcast_join(spark, LARGE_DATA, SMALL_DATA)

        spark_rows = sorted(
            [(r["key"], r["value"], r["label"]) for r in spark_result.collect()]
        )
        assert spark_rows == sorted(python_result)

    def test_all_matching_keys_present(self, spark: SparkSession) -> None:
        result = broadcast_join(spark, LARGE_DATA, SMALL_DATA)
        keys = {r["key"] for r in result.collect()}
        assert keys == {"a", "c", "e"}

    def test_non_matching_keys_excluded(self, spark: SparkSession) -> None:
        result = broadcast_join(spark, LARGE_DATA, SMALL_DATA)
        keys = {r["key"] for r in result.collect()}
        assert "b" not in keys
        assert "d" not in keys

    def test_explain_plan_shows_broadcast(self, spark: SparkSession) -> None:
        plan = get_broadcast_plan(spark, LARGE_DATA, SMALL_DATA)
        assert "Broadcast" in plan, f"Expected Broadcast in plan:\n{plan}"

    def test_duplicate_keys_in_large_table(self, spark: SparkSession) -> None:
        large_with_dupes: list[tuple[str, int]] = [
            ("a", 1),
            ("a", 10),
            ("a", 100),
            ("b", 2),
        ]
        small: list[tuple[str, str]] = [("a", "alpha")]

        python_result = join_with_dict(large_with_dupes, small)
        spark_result = broadcast_join(spark, large_with_dupes, small)
        spark_rows = sorted(
            [(r["key"], r["value"], r["label"]) for r in spark_result.collect()]
        )

        # dict join only keeps the last value for duplicate keys in small,
        # but large side duplicates all get matched
        assert len(spark_rows) == 3
        assert spark_rows == sorted(python_result)
