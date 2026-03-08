"""
Handling Data Skew in Joins.

Pattern connection: patterns/01_hash_map/ "At Scale" sections (key skew)
  When one key appears much more frequently than others, the partition
  handling that key gets disproportionate work while others sit idle.

Techniques:
  1. Salted join: append random suffix to hot keys, join on salted key
  2. AQE skew join: Spark 3.x can detect and split skewed partitions at runtime
  3. Broadcast the skewed key separately
  4. Pre-aggregate the hot key before joining

This file demonstrates the salted join technique and AQE configuration.

Under the hood (salted join):
  - Identify the "hot" key that causes skew
  - Large side: append a random salt (0 to N-1) to the hot key
  - Small side: replicate each row N times, once per salt value
  - Join on (original_key, salt) instead of just original_key
  - The hot key's data is now spread across N partitions instead of one
  - After join, drop the salt column
"""

import pytest

pyspark = pytest.importorskip("pyspark")

import random

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T


# ---------------------------------------------------------------------------
# Pure Python: salted join
# ---------------------------------------------------------------------------


def salted_join_python(
    large: list[tuple[str, int]],
    small: list[tuple[str, str]],
    hot_keys: set[str],
    num_salts: int = 10,
) -> list[tuple[str, int, str]]:
    """Join with salt applied to hot keys to spread skewed data.

    Time:  O(n + m * num_salts) for hot keys
    Space: O(m * num_salts) for replicated small side

    Args:
        large: List of (key, value) tuples (may have skewed keys).
        small: List of (key, label) tuples.
        hot_keys: Set of keys that are disproportionately common.
        num_salts: Number of salt buckets to spread hot keys across.

    Returns:
        List of (key, value, label) tuples for matching keys.

    Example:
        >>> salted_join_python(
        ...     [("hot", 1), ("hot", 2), ("ok", 3)],
        ...     [("hot", "h"), ("ok", "o")],
        ...     {"hot"}, num_salts=2,
        ... )  # doctest: +SKIP
        [('hot', 1, 'h'), ('hot', 2, 'h'), ('ok', 3, 'o')]
    """
    # Replicate small side for hot keys
    small_lookup: dict[tuple[str, int], str] = {}
    for k, label in small:
        if k in hot_keys:
            for salt in range(num_salts):
                small_lookup[(k, salt)] = label
        else:
            small_lookup[(k, -1)] = label

    # Salt the large side and probe
    results: list[tuple[str, int, str]] = []
    for k, v in large:
        if k in hot_keys:
            salt = random.randint(0, num_salts - 1)
            lookup_key = (k, salt)
        else:
            lookup_key = (k, -1)

        if lookup_key in small_lookup:
            results.append((k, v, small_lookup[lookup_key]))

    return results


# ---------------------------------------------------------------------------
# PySpark: salted join
# ---------------------------------------------------------------------------


def salted_join_spark(
    spark: SparkSession,
    large_data: list[tuple[str, int]],
    small_data: list[tuple[str, str]],
    hot_keys: list[str],
    num_salts: int = 10,
) -> DataFrame:
    """Join with salt to handle skewed keys in the large DataFrame.

    Strategy:
      1. Large side: add random salt column (0 to num_salts-1) for hot keys, 0 otherwise
      2. Small side: explode hot key rows into num_salts copies with salt 0..N-1
      3. Join on (key, salt)
      4. Drop the salt column

    Args:
        spark: Active SparkSession.
        large_data: Rows for the large DataFrame (key, value).
        small_data: Rows for the small DataFrame (key, label).
        hot_keys: Keys that are disproportionately common.
        num_salts: Number of salt buckets.

    Returns:
        Joined DataFrame with columns: key, value, label.
    """
    large_df = spark.createDataFrame(large_data, ["key", "value"])
    small_df = spark.createDataFrame(small_data, ["key", "label"])

    hot_keys_set = set(hot_keys)

    # Large side: add random salt for hot keys
    large_salted = large_df.withColumn(
        "salt",
        F.when(
            F.col("key").isin(hot_keys),
            (F.rand() * num_salts).cast(T.IntegerType()),
        ).otherwise(F.lit(0)),
    )

    # Small side: explode hot key rows into num_salts copies
    salt_range = spark.createDataFrame(
        [(i,) for i in range(num_salts)], ["salt"]
    )

    # Split small into hot and non-hot
    small_hot = small_df.filter(F.col("key").isin(hot_keys))
    small_cold = small_df.filter(~F.col("key").isin(hot_keys))

    # Cross join hot rows with all salt values
    small_hot_salted = small_hot.crossJoin(salt_range)

    # Non-hot rows get salt = 0
    small_cold_salted = small_cold.withColumn("salt", F.lit(0))

    # Union the two sides
    small_salted = small_hot_salted.unionByName(small_cold_salted)

    # Join on (key, salt) then drop salt
    result = large_salted.join(small_salted, on=["key", "salt"], how="inner")
    return result.drop("salt")


# ---------------------------------------------------------------------------
# AQE configuration helper
# ---------------------------------------------------------------------------


def configure_aqe_skew_join(spark: SparkSession) -> dict[str, str]:
    """Enable Adaptive Query Execution with skew join optimization.

    AQE detects skewed partitions at runtime and splits them into smaller
    sub-partitions automatically. This is the preferred approach in Spark 3.x+
    because it requires no code changes.

    Returns:
        Dict of configuration keys and their values.
    """
    configs = {
        "spark.sql.adaptive.enabled": "true",
        "spark.sql.adaptive.skewJoin.enabled": "true",
        # A partition is skewed if it's 5x the median and > 256MB
        "spark.sql.adaptive.skewJoin.skewedPartitionFactor": "5",
        "spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes": "256m",
    }
    for key, value in configs.items():
        spark.conf.set(key, value)
    return configs


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def _make_skewed_data(
    hot_key: str = "hot",
    hot_count: int = 1000,
    cold_keys: int = 10,
) -> tuple[list[tuple[str, int]], list[tuple[str, str]]]:
    """Generate skewed test data where one key dominates."""
    large: list[tuple[str, int]] = []
    # Hot key: appears hot_count times
    for i in range(hot_count):
        large.append((hot_key, i))
    # Cold keys: appear once each
    for i in range(cold_keys):
        large.append((f"cold_{i}", i))

    small: list[tuple[str, str]] = [(hot_key, "hot_label")]
    for i in range(cold_keys):
        small.append((f"cold_{i}", f"label_{i}"))

    return large, small


class TestSaltedJoin:
    """Salted join should correctly handle skewed keys."""

    def test_salted_join_correct_count(self, spark: SparkSession) -> None:
        large, small = _make_skewed_data(hot_count=1000, cold_keys=10)
        result = salted_join_spark(
            spark, large, small, hot_keys=["hot"], num_salts=10
        )
        # Every row in large should match: 1000 hot + 10 cold = 1010
        assert result.count() == 1010

    def test_salted_matches_unsalted(self, spark: SparkSession) -> None:
        large, small = _make_skewed_data(hot_count=100, cold_keys=5)

        # Salted join
        salted_result = salted_join_spark(
            spark, large, small, hot_keys=["hot"], num_salts=5
        )
        salted_keys = sorted(
            [(r["key"], r["value"]) for r in salted_result.collect()]
        )

        # Regular join (no salt)
        large_df = spark.createDataFrame(large, ["key", "value"])
        small_df = spark.createDataFrame(small, ["key", "label"])
        regular_result = large_df.join(small_df, on="key", how="inner")
        regular_keys = sorted(
            [(r["key"], r["value"]) for r in regular_result.collect()]
        )

        assert salted_keys == regular_keys

    def test_cold_keys_unaffected(self, spark: SparkSession) -> None:
        large, small = _make_skewed_data(hot_count=50, cold_keys=5)
        result = salted_join_spark(
            spark, large, small, hot_keys=["hot"], num_salts=10
        )
        cold_rows = [r for r in result.collect() if r["key"] != "hot"]
        assert len(cold_rows) == 5

    def test_aqe_config_sets_values(self, spark: SparkSession) -> None:
        configs = configure_aqe_skew_join(spark)
        for key, expected in configs.items():
            actual = spark.conf.get(key)
            assert actual == expected, f"{key}: expected {expected}, got {actual}"
