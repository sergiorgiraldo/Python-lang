"""
Reading Spark Explain Plans.

This file teaches how to read Spark's physical execution plan, which
is one of the most important debugging skills for production Spark jobs.

Key nodes to recognize:
  - Scan: reading data (InMemoryTableScan for cached, FileScan for Parquet)
  - Filter: WHERE clause / .filter()
  - Project: SELECT clause / .select()
  - Exchange: SHUFFLE (data moves between partitions, this is expensive)
  - Sort: sorting data within partitions
  - HashAggregate: GROUP BY aggregation
  - BroadcastHashJoin: join with broadcast (small table sent to all workers)
  - SortMergeJoin: join with shuffle + sort (both sides shuffled)
  - BroadcastExchange: sending data to all workers
  - TakeOrderedAndProject: optimized top-k (limit after orderBy)

Reading order: bottom to top, left to right (leaf nodes are data sources).
"""

import pytest

pyspark = pytest.importorskip("pyspark")

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


# ---------------------------------------------------------------------------
# Plan extraction helper
# ---------------------------------------------------------------------------


def get_plan(spark: SparkSession, df) -> str:
    """Extract the physical plan as a string.

    Args:
        spark: Active SparkSession.
        df: A DataFrame to explain.

    Returns:
        The physical plan as a string.
    """
    return df._jdf.queryExecution().simpleString()


def extract_plan_operations(plan: str) -> list[str]:
    """Extract key operation names from an explain plan string.

    Looks for known Spark plan node names and returns them in order.
    Useful for programmatically checking what operations a query uses.

    Args:
        plan: Physical plan string from explain().

    Returns:
        List of recognized operation names found in the plan.

    Example:
        >>> extract_plan_operations("HashAggregate ... Exchange ... Scan")
        ['HashAggregate', 'Exchange', 'Scan']
    """
    known_ops = [
        "TakeOrderedAndProject",
        "BroadcastHashJoin",
        "SortMergeJoin",
        "ShuffledHashJoin",
        "BroadcastExchange",
        "HashAggregate",
        "Exchange",
        "Sort",
        "Filter",
        "Project",
        "Scan",
    ]
    found: list[str] = []
    for op in known_ops:
        if op in plan:
            found.append(op)
    return found


# ---------------------------------------------------------------------------
# Demo queries for plan inspection
# ---------------------------------------------------------------------------


def plan_simple_filter(spark: SparkSession) -> tuple[str, list[str]]:
    """Show the plan for a simple filter + select query.

    A filter followed by select should show Filter and Project nodes
    but no Exchange (no shuffle needed).

    Returns:
        Tuple of (plan_string, operations_found).
    """
    data = [(i, f"name_{i}", i * 10) for i in range(100)]
    df = spark.createDataFrame(data, ["id", "name", "score"])

    result = df.filter(F.col("score") > 500).select("id", "name")
    plan = get_plan(spark, result)
    return plan, extract_plan_operations(plan)


def plan_aggregation(spark: SparkSession) -> tuple[str, list[str]]:
    """Show the plan for a groupBy aggregation.

    A groupBy triggers a shuffle (Exchange) and uses HashAggregate
    for both partial (map-side) and final aggregation.

    Returns:
        Tuple of (plan_string, operations_found).
    """
    data = [(f"cat_{i % 5}", i * 10) for i in range(100)]
    df = spark.createDataFrame(data, ["category", "amount"])

    result = df.groupBy("category").agg(F.sum("amount").alias("total"))
    plan = get_plan(spark, result)
    return plan, extract_plan_operations(plan)


def plan_join(spark: SparkSession) -> tuple[str, list[str]]:
    """Show the plan for a join between two DataFrames.

    Without broadcast, Spark uses SortMergeJoin with Exchange nodes
    on both sides. With broadcast, one side uses BroadcastExchange.

    Returns:
        Tuple of (plan_string, operations_found).
    """
    left = [(i, f"val_{i}") for i in range(100)]
    right = [(i, f"label_{i}") for i in range(50)]

    left_df = spark.createDataFrame(left, ["key", "value"])
    right_df = spark.createDataFrame(right, ["key", "label"])

    # Force shuffle join to show Exchange nodes
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
    try:
        result = left_df.join(right_df, on="key")
        plan = get_plan(spark, result)
        ops = extract_plan_operations(plan)
    finally:
        spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "10485760")

    return plan, ops


def plan_topk(spark: SparkSession) -> tuple[str, list[str]]:
    """Show the plan for orderBy().limit(k).

    Spark optimizes this into TakeOrderedAndProject instead of a full sort.

    Returns:
        Tuple of (plan_string, operations_found).
    """
    data = [(f"item_{i}", i * 7 % 100) for i in range(100)]
    df = spark.createDataFrame(data, ["name", "score"])

    result = df.orderBy(F.desc("score")).limit(5)
    plan = get_plan(spark, result)
    return plan, extract_plan_operations(plan)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestExplainPlans:
    """Verify that explain plans contain expected operations."""

    def test_filter_no_exchange(self, spark: SparkSession) -> None:
        _, ops = plan_simple_filter(spark)
        assert "Exchange" not in ops, (
            f"Simple filter should not have Exchange (shuffle), found: {ops}"
        )
        assert "Filter" in ops

    def test_aggregation_has_hash_aggregate(self, spark: SparkSession) -> None:
        _, ops = plan_aggregation(spark)
        assert "HashAggregate" in ops, (
            f"GroupBy should use HashAggregate, found: {ops}"
        )

    def test_join_has_exchange(self, spark: SparkSession) -> None:
        _, ops = plan_join(spark)
        assert "Exchange" in ops, (
            f"Shuffle join should have Exchange nodes, found: {ops}"
        )
        # Should be SortMergeJoin or ShuffledHashJoin (not Broadcast)
        assert "SortMergeJoin" in ops or "ShuffledHashJoin" in ops, (
            f"Expected SortMergeJoin or ShuffledHashJoin, found: {ops}"
        )

    def test_topk_optimization(self, spark: SparkSession) -> None:
        _, ops = plan_topk(spark)
        assert "TakeOrderedAndProject" in ops, (
            f"orderBy().limit() should use TakeOrderedAndProject, found: {ops}"
        )
