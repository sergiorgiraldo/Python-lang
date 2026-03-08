"""
GroupBy Aggregation Patterns in PySpark.

Pattern connection:
  patterns/01_hash_map/ - Counter, defaultdict for frequency counting
  patterns/05_heap_priority_queue/ - heapq for top-k after counting
  sql/03_aggregations/ - GROUP BY, HAVING, conditional aggregation

Under the hood:
  - groupBy triggers a shuffle: rows with the same key go to the same partition
  - Each partition does a local aggregation
  - Partial aggregation (map-side combine) reduces shuffle data before the Exchange
  - The Exchange node in the explain plan shows the shuffle
  - For high-cardinality keys, the shuffle can be expensive
  - Pivot must know all distinct values (pass explicitly for best performance)
"""

import pytest

pyspark = pytest.importorskip("pyspark")

from collections import Counter, defaultdict

from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql import functions as F


# ---------------------------------------------------------------------------
# Pure Python: aggregation patterns
# ---------------------------------------------------------------------------


def aggregate_python(
    orders: list[tuple[str, str, str, float]],
) -> dict[str, dict[str, float]]:
    """Aggregate orders by category using dicts.

    Time:  O(n)
    Space: O(k) where k = number of unique categories

    Args:
        orders: List of (category, customer_id, status, amount) tuples.

    Returns:
        Dict of category -> {order_count, total_amount, unique_customers}.

    Example:
        >>> result = aggregate_python([("elec", "c1", "done", 100.0)])
        >>> result["elec"]["order_count"]
        1
    """
    counts: dict[str, int] = Counter()
    totals: dict[str, float] = defaultdict(float)
    customers: dict[str, set[str]] = defaultdict(set)

    for category, customer_id, status, amount in orders:
        counts[category] += 1
        totals[category] += amount
        customers[category].add(customer_id)

    result: dict[str, dict[str, float]] = {}
    for cat in counts:
        result[cat] = {
            "order_count": counts[cat],
            "total_amount": totals[cat],
            "unique_customers": len(customers[cat]),
        }
    return result


# ---------------------------------------------------------------------------
# PySpark: basic groupBy + agg
# ---------------------------------------------------------------------------


def basic_aggregation(
    spark: SparkSession,
    orders: list[tuple[str, str, str, float]],
) -> DataFrame:
    """Standard groupBy aggregation with multiple metrics.

    Args:
        spark: Active SparkSession.
        orders: List of (category, customer_id, status, amount) tuples.

    Returns:
        DataFrame grouped by category with aggregated metrics.
    """
    df = spark.createDataFrame(
        orders, ["category", "customer_id", "status", "amount"]
    )

    return df.groupBy("category").agg(
        F.count("*").alias("order_count"),
        F.sum("amount").alias("total_amount"),
        F.avg("amount").alias("avg_amount"),
        F.countDistinct("customer_id").alias("unique_customers"),
    )


# ---------------------------------------------------------------------------
# PySpark: conditional aggregation
# ---------------------------------------------------------------------------


def conditional_aggregation(
    spark: SparkSession,
    orders: list[tuple[str, str, str, float]],
) -> DataFrame:
    """Aggregate with conditions (CASE WHEN equivalent).

    Computes separate sums for completed vs pending orders in a single pass.

    Args:
        spark: Active SparkSession.
        orders: List of (category, customer_id, status, amount) tuples.

    Returns:
        DataFrame with completed_revenue and pending_revenue per category.
    """
    df = spark.createDataFrame(
        orders, ["category", "customer_id", "status", "amount"]
    )

    return df.groupBy("category").agg(
        F.sum(
            F.when(F.col("status") == "completed", F.col("amount")).otherwise(0)
        ).alias("completed_revenue"),
        F.sum(
            F.when(F.col("status") == "pending", F.col("amount")).otherwise(0)
        ).alias("pending_revenue"),
    )


# ---------------------------------------------------------------------------
# PySpark: pivot
# ---------------------------------------------------------------------------


def pivot_aggregation(
    spark: SparkSession,
    orders: list[tuple[str, str, str, float]],
    categories: list[str],
) -> DataFrame:
    """Pivot categories into columns with sum of amounts per customer.

    Passing explicit pivot values avoids an extra job to discover them.

    Args:
        spark: Active SparkSession.
        orders: List of (category, customer_id, status, amount) tuples.
        categories: Explicit list of category values for the pivot.

    Returns:
        DataFrame with customer_id and one column per category.
    """
    df = spark.createDataFrame(
        orders, ["category", "customer_id", "status", "amount"]
    )

    return (
        df.groupBy("customer_id")
        .pivot("category", categories)
        .agg(F.sum("amount"))
    )


# ---------------------------------------------------------------------------
# PySpark: top-N per group
# ---------------------------------------------------------------------------


def topn_per_group(
    spark: SparkSession,
    orders: list[tuple[str, str, str, float]],
    n: int,
) -> DataFrame:
    """Find the top-N orders by amount within each category.

    Uses window + row_number (same dedup pattern from 03_window_functions).

    Args:
        spark: Active SparkSession.
        orders: List of (category, customer_id, status, amount) tuples.
        n: Number of top orders per category.

    Returns:
        DataFrame with the top-N orders per category.
    """
    df = spark.createDataFrame(
        orders, ["category", "customer_id", "status", "amount"]
    )

    window = Window.partitionBy("category").orderBy(F.desc("amount"))
    return (
        df.withColumn("rank", F.row_number().over(window))
        .filter(F.col("rank") <= n)
        .drop("rank")
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


ORDERS: list[tuple[str, str, str, float]] = [
    ("electronics", "c1", "completed", 500.0),
    ("electronics", "c2", "completed", 300.0),
    ("electronics", "c1", "pending", 200.0),
    ("electronics", "c3", "completed", 150.0),
    ("clothing", "c1", "completed", 100.0),
    ("clothing", "c2", "pending", 75.0),
    ("clothing", "c2", "completed", 50.0),
]


class TestBasicAggregation:
    """groupBy + agg should produce correct aggregate metrics."""

    def test_order_count(self, spark: SparkSession) -> None:
        result = basic_aggregation(spark, ORDERS)
        rows = {r["category"]: r for r in result.collect()}
        assert rows["electronics"]["order_count"] == 4
        assert rows["clothing"]["order_count"] == 3

    def test_total_amount(self, spark: SparkSession) -> None:
        result = basic_aggregation(spark, ORDERS)
        rows = {r["category"]: r for r in result.collect()}
        assert rows["electronics"]["total_amount"] == 1150.0
        assert rows["clothing"]["total_amount"] == 225.0

    def test_unique_customers(self, spark: SparkSession) -> None:
        result = basic_aggregation(spark, ORDERS)
        rows = {r["category"]: r for r in result.collect()}
        assert rows["electronics"]["unique_customers"] == 3
        assert rows["clothing"]["unique_customers"] == 2

    def test_matches_python(self, spark: SparkSession) -> None:
        python_result = aggregate_python(ORDERS)
        spark_result = basic_aggregation(spark, ORDERS)
        rows = {r["category"]: r for r in spark_result.collect()}

        for cat in python_result:
            assert rows[cat]["order_count"] == python_result[cat]["order_count"]
            assert rows[cat]["total_amount"] == python_result[cat]["total_amount"]
            assert rows[cat]["unique_customers"] == python_result[cat]["unique_customers"]


class TestConditionalAggregation:
    """Conditional aggregation should split metrics by status."""

    def test_revenue_split(self, spark: SparkSession) -> None:
        result = conditional_aggregation(spark, ORDERS)
        rows = {r["category"]: r for r in result.collect()}

        # electronics: completed=500+300+150=950, pending=200
        assert rows["electronics"]["completed_revenue"] == 950.0
        assert rows["electronics"]["pending_revenue"] == 200.0

        # clothing: completed=100+50=150, pending=75
        assert rows["clothing"]["completed_revenue"] == 150.0
        assert rows["clothing"]["pending_revenue"] == 75.0


class TestPivot:
    """Pivot should create one column per category."""

    def test_pivot_columns(self, spark: SparkSession) -> None:
        result = pivot_aggregation(
            spark, ORDERS, ["electronics", "clothing"]
        )
        columns = set(result.columns)
        assert "electronics" in columns
        assert "clothing" in columns
        assert "customer_id" in columns

    def test_pivot_values(self, spark: SparkSession) -> None:
        result = pivot_aggregation(
            spark, ORDERS, ["electronics", "clothing"]
        )
        rows = {r["customer_id"]: r for r in result.collect()}
        # c1: electronics=500+200=700, clothing=100
        assert rows["c1"]["electronics"] == 700.0
        assert rows["c1"]["clothing"] == 100.0


class TestTopNPerGroup:
    """Top-N per group should return correct rows."""

    def test_top2_per_category(self, spark: SparkSession) -> None:
        result = topn_per_group(spark, ORDERS, n=2)
        rows = result.collect()

        elec = sorted(
            [r["amount"] for r in rows if r["category"] == "electronics"],
            reverse=True,
        )
        # Top 2 electronics by amount: 500, 300
        assert elec == [500.0, 300.0]

        cloth = sorted(
            [r["amount"] for r in rows if r["category"] == "clothing"],
            reverse=True,
        )
        # Top 2 clothing by amount: 100, 75
        assert cloth == [100.0, 75.0]
