"""
Top-K Without Full Sort.

Pattern connection: patterns/05_heap_priority_queue/
  Python: heapq.nlargest(k, data) is O(n log k), better than full sort O(n log n).
  Spark: orderBy().limit(k) with Spark's TakeOrderedAndProject optimization.

Under the hood:
  - Spark doesn't sort the entire DataFrame when you use orderBy().limit(k)
  - It uses a top-k algorithm per partition (like a distributed heap)
  - Each partition finds its local top-k, then a final merge finds the global top-k
  - Physical plan shows "TakeOrderedAndProject" instead of full "Sort"
  - Much faster than sorting 1TB when you only need top 100

When to use:
  - "Find the top N customers by revenue"
  - "What are the 10 most frequent events?"
  - Any time k << n
"""

import pytest

pyspark = pytest.importorskip("pyspark")

import heapq

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


# ---------------------------------------------------------------------------
# Pure Python: heap-based top-k
# ---------------------------------------------------------------------------


def topk_python(data: list[tuple[str, int]], k: int) -> list[tuple[str, int]]:
    """Find the top-k elements by value using a heap.

    Uses heapq.nlargest which maintains a min-heap of size k,
    giving O(n log k) time instead of O(n log n) for a full sort.

    Args:
        data: List of (name, value) tuples.
        k: Number of top elements to return.

    Returns:
        Top-k elements sorted by value descending.

    Example:
        >>> topk_python([("a", 3), ("b", 1), ("c", 5)], 2)
        [('c', 5), ('a', 3)]
    """
    return heapq.nlargest(k, data, key=lambda x: x[1])


# ---------------------------------------------------------------------------
# PySpark: orderBy().limit(k) with TakeOrderedAndProject
# ---------------------------------------------------------------------------


def topk_spark(
    spark: SparkSession,
    data: list[tuple[str, int]],
    k: int,
) -> list[tuple[str, int]]:
    """Find the top-k elements using Spark's optimized limit.

    Spark detects the orderBy().limit(k) pattern and uses
    TakeOrderedAndProject instead of a full sort. Each partition
    keeps its local top-k, then a final merge picks the global top-k.

    Args:
        spark: Active SparkSession.
        data: List of (name, value) tuples.
        k: Number of top elements to return.

    Returns:
        Top-k elements as a list of (name, value) tuples, sorted descending.
    """
    df = spark.createDataFrame(data, ["name", "value"])
    result = df.orderBy(F.desc("value")).limit(k)
    return [(r["name"], r["value"]) for r in result.collect()]


def get_topk_plan(
    spark: SparkSession,
    data: list[tuple[str, int]],
    k: int,
) -> str:
    """Return the physical plan for a top-k query.

    Should show TakeOrderedAndProject instead of a full Sort node,
    demonstrating that Spark optimizes the orderBy().limit(k) pattern.

    Args:
        spark: Active SparkSession.
        data: List of (name, value) tuples.
        k: Number of top elements.

    Returns:
        The explain plan as a string.
    """
    df = spark.createDataFrame(data, ["name", "value"])
    result = df.orderBy(F.desc("value")).limit(k)
    return result._jdf.queryExecution().simpleString()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


TEST_DATA: list[tuple[str, int]] = [
    ("alice", 500),
    ("bob", 300),
    ("carol", 800),
    ("dave", 150),
    ("eve", 950),
    ("frank", 720),
    ("grace", 410),
    ("heidi", 660),
]


class TestTopK:
    """Top-k with Spark should match the Python heap result."""

    def test_topk_matches_python(self, spark: SparkSession) -> None:
        k = 3
        python_result = topk_python(TEST_DATA, k)
        spark_result = topk_spark(spark, TEST_DATA, k)
        assert spark_result == python_result

    def test_topk_correct_values(self, spark: SparkSession) -> None:
        k = 3
        result = topk_spark(spark, TEST_DATA, k)
        names = [name for name, _ in result]
        # Top 3 by value: eve(950), carol(800), frank(720)
        assert names == ["eve", "carol", "frank"]

    def test_topk_plan_optimization(self, spark: SparkSession) -> None:
        plan = get_topk_plan(spark, TEST_DATA, 3)
        assert "TakeOrderedAndProject" in plan, (
            f"Expected TakeOrderedAndProject in plan:\n{plan}"
        )
