"""
Approximate Counting in PySpark.

Pattern connection:
  patterns/11_probabilistic_structures/ - HyperLogLog, Bloom Filter, Count-Min Sketch
  sql/03_aggregations/de_scenarios/approximate_counting

Exact COUNT(DISTINCT) requires a full shuffle to collect all unique values.
For very high cardinality (billions of unique values), this is expensive.
Approximate counting trades accuracy for speed and memory.

PySpark provides:
  - approx_count_distinct(): HyperLogLog-based, configurable error rate
  - Default relative standard deviation (rsd) is 0.05 (5% error)
  - Lower rsd = more accuracy = more memory

When to use exact vs approximate:
  - Exact: billing, compliance, audit trails (correctness required)
  - Approximate: dashboards, exploration, trend monitoring (speed preferred)

Under the hood:
  - HyperLogLog hashes each value and tracks the maximum number of leading zeros
  - Partial aggregation works: HLL sketches are mergeable across partitions
  - This means Spark can do map-side combine then merge sketches at reduce
  - Memory: ~16KB per sketch regardless of cardinality
"""

import pytest

pyspark = pytest.importorskip("pyspark")

import random

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


# ---------------------------------------------------------------------------
# Pure Python: exact vs approximate distinct counting
# ---------------------------------------------------------------------------


def exact_count_distinct(values: list[str]) -> int:
    """Exact distinct count using a set.

    Time:  O(n)
    Space: O(k) where k = number of unique values

    Args:
        values: List of values to count distinct elements of.

    Returns:
        Exact number of distinct values.
    """
    return len(set(values))


# ---------------------------------------------------------------------------
# PySpark: exact vs approximate count distinct
# ---------------------------------------------------------------------------


def exact_count_spark(
    spark: SparkSession,
    data: list[tuple[str, str]],
) -> int:
    """Exact COUNT(DISTINCT) in Spark.

    Requires a full shuffle to collect all unique values on one partition.
    Expensive for high-cardinality columns at scale.

    Args:
        spark: Active SparkSession.
        data: List of (category, user_id) tuples.

    Returns:
        Exact distinct count of user_id.
    """
    df = spark.createDataFrame(data, ["category", "user_id"])
    row = df.select(F.countDistinct("user_id").alias("exact")).collect()[0]
    return row["exact"]


def approx_count_spark(
    spark: SparkSession,
    data: list[tuple[str, str]],
    rsd: float = 0.05,
) -> int:
    """Approximate COUNT(DISTINCT) using HyperLogLog.

    Uses probabilistic counting with configurable error rate. Lower rsd
    means higher accuracy but more memory per sketch.

    Args:
        spark: Active SparkSession.
        data: List of (category, user_id) tuples.
        rsd: Relative standard deviation (error rate). Default 0.05 = 5%.

    Returns:
        Approximate distinct count of user_id.
    """
    df = spark.createDataFrame(data, ["category", "user_id"])
    row = df.select(
        F.approx_count_distinct("user_id", rsd=rsd).alias("approx")
    ).collect()[0]
    return row["approx"]


def approx_count_per_group(
    spark: SparkSession,
    data: list[tuple[str, str]],
    rsd: float = 0.05,
) -> dict[str, int]:
    """Approximate distinct count per group.

    HLL sketches are computed per partition then merged per group.
    This avoids a full shuffle of all unique values.

    Args:
        spark: Active SparkSession.
        data: List of (category, user_id) tuples.
        rsd: Relative standard deviation (error rate).

    Returns:
        Dict of category -> approximate distinct user count.
    """
    df = spark.createDataFrame(data, ["category", "user_id"])
    result = df.groupBy("category").agg(
        F.approx_count_distinct("user_id", rsd=rsd).alias("approx_users")
    )
    return {r["category"]: r["approx_users"] for r in result.collect()}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def _generate_test_data(
    num_categories: int = 3,
    users_per_category: int = 100,
    events_per_user: int = 5,
    seed: int = 42,
) -> list[tuple[str, str]]:
    """Generate test data with known distinct counts."""
    rng = random.Random(seed)
    data: list[tuple[str, str]] = []
    for cat_id in range(num_categories):
        category = f"cat_{cat_id}"
        for user_id in range(users_per_category):
            user = f"user_{cat_id}_{user_id}"
            for _ in range(events_per_user):
                data.append((category, user))
    rng.shuffle(data)
    return data


class TestApproximateCounting:
    """Approximate counting should be close to exact counting."""

    def test_approx_within_tolerance(self, spark: SparkSession) -> None:
        data = _generate_test_data(num_categories=1, users_per_category=200)
        exact = exact_count_spark(spark, data)
        approx = approx_count_spark(spark, data, rsd=0.05)

        # With 200 distinct values and 5% rsd, should be within 10%
        tolerance = exact * 0.10
        assert abs(approx - exact) <= tolerance, (
            f"Approximate {approx} too far from exact {exact}"
        )

    def test_exact_count_is_correct(self, spark: SparkSession) -> None:
        data = _generate_test_data(
            num_categories=1, users_per_category=50, events_per_user=3
        )
        exact = exact_count_spark(spark, data)
        # 50 unique users, each appearing 3 times
        assert exact == 50

    def test_approx_per_group(self, spark: SparkSession) -> None:
        data = _generate_test_data(
            num_categories=3, users_per_category=100, events_per_user=5
        )
        result = approx_count_per_group(spark, data, rsd=0.05)

        assert len(result) == 3
        for category, count in result.items():
            # Each category has 100 unique users, allow 15% tolerance
            assert 85 <= count <= 115, (
                f"{category}: expected ~100, got {count}"
            )
