"""
Shuffle (Hash-Partitioned) Join: Both tables are large.

Pattern connection: patterns/01_hash_map/ at scale
  Python: when the dict doesn't fit in memory, partition both sides by key.
  Spark: hash both DataFrames by join key, send matching keys to same partition.

Under the hood:
  - Spark hashes the join key from BOTH sides
  - Data with the same hash goes to the same partition (shuffle/exchange)
  - Each partition does a local join (hash or sort-merge)
  - This is expensive: every row moves across the network
  - The "Exchange" node in the plan means shuffle

When to use:
  - Both sides are too large to broadcast
  - This is Spark's default join strategy for large-large joins

Cost:
  - Network I/O: all data moves (worst case)
  - Disk I/O: if partitions don't fit in memory, Spark spills to disk
  - For 1TB join 1TB: expect significant shuffle (minutes to hours depending on cluster)
"""

import pytest

pyspark = pytest.importorskip("pyspark")

from collections import defaultdict

from pyspark.sql import DataFrame, SparkSession


# ---------------------------------------------------------------------------
# Pure Python: hash-partition both sides, join per partition
# ---------------------------------------------------------------------------


def hash_partition_join(
    left: list[tuple[str, int]],
    right: list[tuple[str, str]],
    num_partitions: int = 4,
) -> list[tuple[str, int, str]]:
    """Simulate a shuffle join by hash-partitioning both sides.

    Each side is bucketed by hash(key) % num_partitions, then matching
    buckets are joined locally with a dict lookup.

    Time:  O(n + m) amortized
    Space: O(n + m) for the partitioned buckets

    Args:
        left: List of (key, value) tuples.
        right: List of (key, label) tuples.
        num_partitions: Number of hash buckets.

    Returns:
        List of (key, value, label) tuples for matching keys.

    Example:
        >>> hash_partition_join([("a", 1)], [("a", "x")], 2)
        [('a', 1, 'x')]
    """
    # Partition both sides by hash of key
    left_buckets: dict[int, list[tuple[str, int]]] = defaultdict(list)
    right_buckets: dict[int, list[tuple[str, str]]] = defaultdict(list)

    for k, v in left:
        left_buckets[hash(k) % num_partitions].append((k, v))
    for k, v in right:
        right_buckets[hash(k) % num_partitions].append((k, v))

    # Join within each partition
    results: list[tuple[str, int, str]] = []
    for partition_id in range(num_partitions):
        right_lookup = defaultdict(list)
        for k, v in right_buckets[partition_id]:
            right_lookup[k].append(v)

        for k, v in left_buckets[partition_id]:
            for label in right_lookup[k]:
                results.append((k, v, label))

    return results


# ---------------------------------------------------------------------------
# PySpark: shuffle join (no broadcast hint)
# ---------------------------------------------------------------------------


def shuffle_join(
    spark: SparkSession,
    left_data: list[tuple[str, int]],
    right_data: list[tuple[str, str]],
) -> DataFrame:
    """Join two large DataFrames using Spark's default shuffle strategy.

    Without a broadcast hint, Spark hash-partitions both sides by the join
    key and shuffles data across the network. Each partition then does a
    local join. The physical plan shows Exchange (shuffle) nodes on both sides.

    Args:
        spark: Active SparkSession.
        left_data: Rows for the left DataFrame (key, value).
        right_data: Rows for the right DataFrame (key, label).

    Returns:
        Joined DataFrame with columns: key, value, label.
    """
    # Disable broadcast to force shuffle join even on small data
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
    try:
        left_df = spark.createDataFrame(left_data, ["key", "value"])
        right_df = spark.createDataFrame(right_data, ["key", "label"])
        result = left_df.join(right_df, on="key", how="inner")
        # Materialize the result before restoring config
        result = spark.createDataFrame(result.collect(), result.schema)
    finally:
        # Restore default broadcast threshold (10MB)
        spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "10485760")
    return result


def get_shuffle_plan(
    spark: SparkSession,
    left_data: list[tuple[str, int]],
    right_data: list[tuple[str, str]],
) -> str:
    """Return the physical plan string for a shuffle join.

    The plan should show Exchange (shuffle) nodes and should NOT show
    BroadcastHashJoin. Expect SortMergeJoin or ShuffledHashJoin.

    Args:
        spark: Active SparkSession.
        left_data: Rows for the left DataFrame (key, value).
        right_data: Rows for the right DataFrame (key, label).

    Returns:
        The explain plan as a string.
    """
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
    try:
        left_df = spark.createDataFrame(left_data, ["key", "value"])
        right_df = spark.createDataFrame(right_data, ["key", "label"])
        result = left_df.join(right_df, on="key", how="inner")
        plan = result._jdf.queryExecution().simpleString()
    finally:
        spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "10485760")
    return plan


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


LEFT_DATA: list[tuple[str, int]] = [
    ("a", 1),
    ("b", 2),
    ("c", 3),
    ("d", 4),
    ("e", 5),
]

RIGHT_DATA: list[tuple[str, str]] = [
    ("a", "alpha"),
    ("c", "charlie"),
    ("e", "echo"),
    ("f", "foxtrot"),
]


class TestShuffleJoin:
    """Shuffle join should produce correct results without broadcast."""

    def test_correct_results(self, spark: SparkSession) -> None:
        python_result = hash_partition_join(LEFT_DATA, RIGHT_DATA)
        spark_result = shuffle_join(spark, LEFT_DATA, RIGHT_DATA)

        spark_rows = sorted(
            [(r["key"], r["value"], r["label"]) for r in spark_result.collect()]
        )
        assert spark_rows == sorted(python_result)

    def test_plan_is_not_broadcast(self, spark: SparkSession) -> None:
        plan = get_shuffle_plan(spark, LEFT_DATA, RIGHT_DATA)
        assert "BroadcastHashJoin" not in plan, (
            f"Expected no BroadcastHashJoin in plan:\n{plan}"
        )

    def test_null_keys_excluded_from_inner_join(
        self, spark: SparkSession
    ) -> None:
        left_with_null: list[tuple[str | None, int]] = [
            ("a", 1),
            (None, 99),
        ]
        right_with_null: list[tuple[str | None, str]] = [
            ("a", "alpha"),
            (None, "nothing"),
        ]
        result = shuffle_join(spark, left_with_null, right_with_null)
        rows = result.collect()
        keys = [r["key"] for r in rows]
        # Inner join on null keys: nulls do not match in equi-joins
        assert None not in keys
        assert len(rows) == 1
        assert rows[0]["key"] == "a"

    def test_many_to_many_join(self, spark: SparkSession) -> None:
        left: list[tuple[str, int]] = [("a", 1), ("a", 2)]
        right: list[tuple[str, str]] = [("a", "x"), ("a", "y")]

        result = shuffle_join(spark, left, right)
        rows = result.collect()
        # 2 left x 2 right = 4 result rows
        assert len(rows) == 4
