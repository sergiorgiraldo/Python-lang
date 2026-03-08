"""
Sort-Merge Operations in Spark.

Pattern connection: patterns/02_two_pointers/
  Python: merge two sorted arrays with two pointers in O(n+m) time, O(1) space.
  Spark: sort-merge join sorts both sides by key then merges with a pointer scan.

Under the hood:
  - Spark sorts both DataFrames by join key (Exchange + Sort nodes in the plan)
  - Then merges with a streaming scan (like the merge step of merge sort)
  - This is Spark's default for equi-joins when both sides are large
  - More disk-friendly than hash join (sorted data can spill efficiently)

orderBy() vs sortWithinPartitions():
  - orderBy(): global sort (shuffle to range partitions then sort each)
  - sortWithinPartitions(): sort within each partition (no shuffle)
  - Use sortWithinPartitions when downstream only needs local order
    (e.g., writing partitioned Parquet files)
"""

import pytest

pyspark = pytest.importorskip("pyspark")

from pyspark.sql import DataFrame, SparkSession


# ---------------------------------------------------------------------------
# Pure Python: two-pointer merge of sorted lists
# ---------------------------------------------------------------------------


def merge_sorted(
    left: list[tuple[int, str]],
    right: list[tuple[int, str]],
) -> list[tuple[int, str, str]]:
    """Merge two sorted lists by key using the two-pointer technique.

    Both inputs must be sorted by the first element (the key).

    Time:  O(n + m)
    Space: O(n + m) for the result

    Args:
        left: Sorted list of (key, value) tuples.
        right: Sorted list of (key, label) tuples.

    Returns:
        List of (key, value, label) tuples for matching keys.

    Example:
        >>> merge_sorted([(1, "a"), (3, "c")], [(1, "x"), (2, "y")])
        [(1, 'a', 'x')]
    """
    result: list[tuple[int, str, str]] = []
    i, j = 0, 0

    while i < len(left) and j < len(right):
        lk, lv = left[i]
        rk, rv = right[j]

        if lk == rk:
            result.append((lk, lv, rv))
            i += 1
            j += 1
        elif lk < rk:
            i += 1
        else:
            j += 1

    return result


# ---------------------------------------------------------------------------
# PySpark: sort-merge join
# ---------------------------------------------------------------------------


def sort_merge_join(
    spark: SparkSession,
    left_data: list[tuple[int, str]],
    right_data: list[tuple[int, str]],
) -> DataFrame:
    """Join two DataFrames using Spark's sort-merge join strategy.

    Disables broadcast to force Spark into SortMergeJoin. Both sides are
    shuffled by key (Exchange), sorted (Sort), then merged with a scan.

    Args:
        spark: Active SparkSession.
        left_data: Rows for the left DataFrame (key, value).
        right_data: Rows for the right DataFrame (key, label).

    Returns:
        Joined DataFrame with columns: key, value, label.
    """
    # Disable broadcast to force sort-merge join on small test data
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
    try:
        left_df = spark.createDataFrame(left_data, ["key", "value"])
        right_df = spark.createDataFrame(right_data, ["key", "label"])
        result = left_df.join(right_df, on="key", how="inner")
        # Materialize before restoring config
        result = spark.createDataFrame(result.collect(), result.schema)
    finally:
        spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "10485760")
    return result


# ---------------------------------------------------------------------------
# orderBy vs sortWithinPartitions
# ---------------------------------------------------------------------------


def demonstrate_order_by(
    spark: SparkSession,
    data: list[tuple[int, str]],
) -> list[tuple[int, str]]:
    """Global sort using orderBy (triggers a shuffle).

    orderBy() range-partitions the data then sorts each partition.
    The result is globally ordered across all partitions.

    Args:
        spark: Active SparkSession.
        data: Rows of (key, value) tuples.

    Returns:
        Globally sorted list of (key, value) tuples.
    """
    df = spark.createDataFrame(data, ["key", "value"])
    sorted_df = df.orderBy("key")
    return [(r["key"], r["value"]) for r in sorted_df.collect()]


def demonstrate_sort_within_partitions(
    spark: SparkSession,
    data: list[tuple[int, str]],
    num_partitions: int = 2,
) -> list[list[tuple[int, str]]]:
    """Local sort using sortWithinPartitions (no shuffle).

    Each partition is sorted independently. The result is NOT globally
    ordered but each partition's data is sorted. Useful when writing
    Parquet files that need to be sorted within each partition.

    Args:
        spark: Active SparkSession.
        data: Rows of (key, value) tuples.
        num_partitions: Number of partitions to repartition into.

    Returns:
        List of partitions, each containing sorted (key, value) tuples.
    """
    df = spark.createDataFrame(data, ["key", "value"])
    df = df.repartition(num_partitions)
    sorted_df = df.sortWithinPartitions("key")

    # Collect each partition separately using mapPartitions
    def partition_to_list(iterator):
        rows = [(r["key"], r["value"]) for r in iterator]
        yield rows

    partitions = sorted_df.rdd.mapPartitions(partition_to_list).collect()
    return partitions


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


LEFT_DATA: list[tuple[int, str]] = [
    (1, "a"),
    (2, "b"),
    (3, "c"),
    (5, "e"),
    (7, "g"),
]

RIGHT_DATA: list[tuple[int, str]] = [
    (1, "alpha"),
    (3, "charlie"),
    (5, "echo"),
    (6, "foxtrot"),
]


class TestSortMergeJoin:
    """Sort-merge join should match the two-pointer merge."""

    def test_matches_python_merge(self, spark: SparkSession) -> None:
        python_result = merge_sorted(LEFT_DATA, RIGHT_DATA)
        spark_result = sort_merge_join(spark, LEFT_DATA, RIGHT_DATA)

        spark_rows = sorted(
            [(r["key"], r["value"], r["label"]) for r in spark_result.collect()]
        )
        assert spark_rows == sorted(python_result)

    def test_only_matching_keys(self, spark: SparkSession) -> None:
        result = sort_merge_join(spark, LEFT_DATA, RIGHT_DATA)
        keys = {r["key"] for r in result.collect()}
        assert keys == {1, 3, 5}


class TestSortOperations:
    """orderBy and sortWithinPartitions behavior."""

    def test_order_by_globally_sorted(self, spark: SparkSession) -> None:
        data: list[tuple[int, str]] = [
            (5, "e"),
            (1, "a"),
            (3, "c"),
            (2, "b"),
            (4, "d"),
        ]
        result = demonstrate_order_by(spark, data)
        keys = [k for k, v in result]
        assert keys == sorted(keys)

    def test_sort_within_partitions_locally_sorted(
        self, spark: SparkSession
    ) -> None:
        data: list[tuple[int, str]] = [
            (5, "e"),
            (1, "a"),
            (3, "c"),
            (2, "b"),
            (4, "d"),
            (8, "h"),
            (6, "f"),
            (7, "g"),
        ]
        partitions = demonstrate_sort_within_partitions(
            spark, data, num_partitions=2
        )

        # Each partition should be sorted by key
        for partition in partitions:
            keys = [k for k, v in partition]
            assert keys == sorted(keys), (
                f"Partition not sorted: {keys}"
            )

        # But concatenating all partitions may NOT be globally sorted
        # (this is the key difference from orderBy)
        all_keys = [k for partition in partitions for k, v in partition]
        # We just check that each partition is individually sorted
        # The global order depends on how repartition distributes data
        assert len(all_keys) == len(data)
