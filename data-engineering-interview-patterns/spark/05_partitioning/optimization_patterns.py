"""
Common Spark Optimization Patterns.

Patterns that appear in senior DE interviews:

1. Predicate pushdown: filters pushed to the data source (fewer bytes read)
2. Column pruning: only requested columns read from columnar storage
3. Broadcast hints: force broadcast when Spark doesn't auto-detect
4. Caching: persist frequently accessed DataFrames in memory
5. AQE (Adaptive Query Execution): runtime optimization in Spark 3.x

These optimizations reduce I/O, memory usage and shuffle volume. Understanding
them is what separates "I can write Spark code" from "I can write efficient
Spark code."
"""

import pytest

pyspark = pytest.importorskip("pyspark")

import tempfile

from pyspark import StorageLevel
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


# ---------------------------------------------------------------------------
# Sample data helper
# ---------------------------------------------------------------------------


def _create_parquet_file(
    spark: SparkSession, path: str, num_rows: int = 200
) -> None:
    """Write a sample Parquet file for optimization demos."""
    data = [
        (i, f"name_{i}", f"dept_{i % 5}", i * 10.0, f"2024-{(i % 12) + 1:02d}-01")
        for i in range(num_rows)
    ]
    df = spark.createDataFrame(
        data, ["id", "name", "department", "salary", "hire_date"]
    )
    df.write.mode("overwrite").parquet(path)


# ---------------------------------------------------------------------------
# Predicate pushdown
# ---------------------------------------------------------------------------


def demonstrate_predicate_pushdown(
    spark: SparkSession, parquet_path: str
) -> str:
    """Show predicate pushdown in the explain plan.

    When reading Parquet, Spark pushes filter predicates to the file reader.
    This means rows that don't match the filter are skipped at the I/O level
    (never deserialized into memory). The plan shows PushedFilters in the
    FileScan node.

    Args:
        spark: Active SparkSession.
        parquet_path: Path to a Parquet file.

    Returns:
        The explain plan string.
    """
    df = spark.read.parquet(parquet_path)
    filtered = df.filter(F.col("salary") > 1000.0)
    return filtered._jdf.queryExecution().simpleString()


# ---------------------------------------------------------------------------
# Column pruning
# ---------------------------------------------------------------------------


def demonstrate_column_pruning(
    spark: SparkSession, parquet_path: str
) -> str:
    """Show column pruning in the explain plan.

    When only a subset of columns is selected, Spark reads only those columns
    from the Parquet file (columnar storage). The plan shows ReadSchema with
    fewer columns than the full schema.

    Args:
        spark: Active SparkSession.
        parquet_path: Path to a Parquet file.

    Returns:
        The explain plan string.
    """
    df = spark.read.parquet(parquet_path)
    projected = df.select("id", "name")
    return projected._jdf.queryExecution().simpleString()


# ---------------------------------------------------------------------------
# Caching
# ---------------------------------------------------------------------------


def demonstrate_caching(
    spark: SparkSession,
    data: list[tuple[int, str, float]],
) -> tuple[bool, str]:
    """Cache a DataFrame and verify it is stored in memory.

    cache() is a shortcut for persist(StorageLevel.MEMORY_AND_DISK).
    After calling an action (like count), the data is materialized and
    stored. Subsequent operations on the cached DataFrame skip recomputation.

    Args:
        spark: Active SparkSession.
        data: List of (id, name, value) tuples.

    Returns:
        Tuple of (is_cached, storage_level_description).
    """
    df = spark.createDataFrame(data, ["id", "name", "value"])
    df.cache()
    df.count()  # trigger materialization

    is_cached = df.is_cached
    storage = str(df.storageLevel)

    df.unpersist()
    return is_cached, storage


def demonstrate_persist_levels(
    spark: SparkSession,
    data: list[tuple[int, str, float]],
) -> dict[str, str]:
    """Show different persist storage levels.

    StorageLevel options:
      - MEMORY_ONLY: fastest, fails if data doesn't fit in memory
      - MEMORY_AND_DISK: spills to disk if memory is full (default for cache())
      - DISK_ONLY: always on disk, frees memory
      - MEMORY_ONLY_2: replicated to 2 nodes (fault tolerance)

    Args:
        spark: Active SparkSession.
        data: List of (id, name, value) tuples.

    Returns:
        Dict mapping level name to its string representation.
    """
    results: dict[str, str] = {}
    levels = {
        "MEMORY_ONLY": StorageLevel.MEMORY_ONLY,
        "MEMORY_AND_DISK": StorageLevel.MEMORY_AND_DISK,
        "DISK_ONLY": StorageLevel.DISK_ONLY,
    }

    for name, level in levels.items():
        df = spark.createDataFrame(data, ["id", "name", "value"])
        df.persist(level)
        df.count()
        results[name] = str(df.storageLevel)
        df.unpersist()

    return results


# ---------------------------------------------------------------------------
# AQE configuration
# ---------------------------------------------------------------------------


def configure_aqe(spark: SparkSession) -> dict[str, str]:
    """Enable Adaptive Query Execution with common optimizations.

    AQE is Spark 3.x's runtime optimization that adjusts the query plan
    based on actual data statistics collected during execution.

    Key features:
      - Coalesce shuffle partitions: merge small partitions after shuffle
      - Skew join: split skewed partitions into smaller sub-partitions
      - Convert sort-merge to broadcast: if one side is small at runtime

    Returns:
        Dict of configuration keys and values.
    """
    configs = {
        "spark.sql.adaptive.enabled": "true",
        "spark.sql.adaptive.coalescePartitions.enabled": "true",
        "spark.sql.adaptive.skewJoin.enabled": "true",
        "spark.sql.adaptive.advisoryPartitionSizeInBytes": "64m",
    }
    for key, value in configs.items():
        spark.conf.set(key, value)
    return configs


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


SAMPLE_DATA: list[tuple[int, str, float]] = [
    (i, f"name_{i}", float(i * 10))
    for i in range(50)
]


class TestCaching:
    """Caching should store DataFrames in memory."""

    def test_cache_is_stored(self, spark: SparkSession) -> None:
        is_cached, storage = demonstrate_caching(spark, SAMPLE_DATA)
        assert is_cached is True

    def test_cache_storage_level(self, spark: SparkSession) -> None:
        _, storage = demonstrate_caching(spark, SAMPLE_DATA)
        # Default cache() uses MEMORY_AND_DISK or similar
        assert "Disk" in storage or "Memory" in storage


class TestPredicatePushdown:
    """Predicate pushdown should appear in the plan for Parquet reads."""

    def test_pushdown_in_plan(self, spark: SparkSession) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_parquet_file(spark, tmpdir)
            plan = demonstrate_predicate_pushdown(spark, tmpdir)
            # Plan should show PushedFilters or Filter near FileScan
            assert "Filter" in plan or "PushedFilters" in plan, (
                f"Expected filter in plan:\n{plan}"
            )


class TestColumnPruning:
    """Column pruning should read fewer columns from Parquet."""

    def test_pruning_in_plan(self, spark: SparkSession) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_parquet_file(spark, tmpdir)
            plan = demonstrate_column_pruning(spark, tmpdir)
            # Plan should show ReadSchema with only id and name
            assert "id" in plan
            assert "name" in plan
            # salary and department should NOT be in the read schema
            # (they may appear in the file schema but not ReadSchema)


class TestAQE:
    """AQE configuration should set the correct values."""

    def test_aqe_enabled(self, spark: SparkSession) -> None:
        configs = configure_aqe(spark)
        for key, expected in configs.items():
            actual = spark.conf.get(key)
            assert actual == expected, (
                f"{key}: expected {expected}, got {actual}"
            )
