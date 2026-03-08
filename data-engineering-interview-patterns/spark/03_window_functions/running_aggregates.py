"""
Running Aggregates with PySpark Windows.

Pattern connection:
  patterns/04_sliding_window/ - maintaining running sum/avg incrementally
  sql/01_window_functions/de_scenarios/running_totals

Under the hood:
  - Running sum/avg over an ordered window triggers sort + sequential scan
  - Frame: rowsBetween(Window.unboundedPreceding, Window.currentRow) for running total
  - Frame: rowsBetween(-6, Window.currentRow) for 7-row moving average
  - Spark processes each partition independently (partitions are sorted locally)
  - No shuffle if data is already partitioned by the PARTITION BY key

rowsBetween vs rangeBetween:
  - rowsBetween(start, end): counts by row position (fixed number of rows)
  - rangeBetween(start, end): counts by value distance (e.g., within 7 units)
  - Use rowsBetween when rows are evenly spaced (daily data with no gaps)
  - Use rangeBetween when rows may have gaps (event data with irregular timing)
"""

import pytest

pyspark = pytest.importorskip("pyspark")

from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql import functions as F


# ---------------------------------------------------------------------------
# Pure Python: running sum and moving average
# ---------------------------------------------------------------------------


def running_sum_python(values: list[float]) -> list[float]:
    """Compute running (cumulative) sum.

    Time:  O(n)
    Space: O(n) for the result

    Args:
        values: List of numeric values.

    Returns:
        List where result[i] = sum(values[0..i]).

    Example:
        >>> running_sum_python([10.0, 20.0, 30.0])
        [10.0, 30.0, 60.0]
    """
    result: list[float] = []
    total = 0.0
    for v in values:
        total += v
        result.append(total)
    return result


def moving_average_python(values: list[float], window_size: int) -> list[float]:
    """Compute moving average with a fixed window size.

    For positions with fewer than window_size preceding rows, the
    average is computed over all available rows up to that point.

    Time:  O(n)
    Space: O(n) for the result

    Args:
        values: List of numeric values.
        window_size: Number of rows to include in the average.

    Returns:
        List of moving averages.

    Example:
        >>> moving_average_python([10.0, 20.0, 30.0, 40.0], 3)
        [10.0, 15.0, 20.0, 30.0]
    """
    result: list[float] = []
    for i in range(len(values)):
        start = max(0, i - window_size + 1)
        window = values[start : i + 1]
        result.append(sum(window) / len(window))
    return result


# ---------------------------------------------------------------------------
# PySpark: running sum
# ---------------------------------------------------------------------------


def running_sum_spark(
    spark: SparkSession,
    data: list[tuple[str, str, float]],
) -> DataFrame:
    """Compute running total partitioned by category, ordered by date.

    Uses rowsBetween(unboundedPreceding, currentRow) for a cumulative frame.

    Args:
        spark: Active SparkSession.
        data: List of (category, date, amount) tuples.

    Returns:
        DataFrame with added running_total column.
    """
    df = spark.createDataFrame(data, ["category", "date", "amount"])

    window = (
        Window.partitionBy("category")
        .orderBy("date")
        .rowsBetween(Window.unboundedPreceding, Window.currentRow)
    )
    return df.withColumn("running_total", F.sum("amount").over(window))


# ---------------------------------------------------------------------------
# PySpark: moving average with fixed window
# ---------------------------------------------------------------------------


def moving_average_spark(
    spark: SparkSession,
    data: list[tuple[str, str, float]],
    window_size: int = 3,
) -> DataFrame:
    """Compute moving average over a fixed number of preceding rows.

    Uses rowsBetween(-(window_size-1), currentRow) for a sliding frame.

    Args:
        spark: Active SparkSession.
        data: List of (category, date, amount) tuples.
        window_size: Number of rows to include in the average.

    Returns:
        DataFrame with added moving_avg column.
    """
    df = spark.createDataFrame(data, ["category", "date", "amount"])

    window = (
        Window.partitionBy("category")
        .orderBy("date")
        .rowsBetween(-(window_size - 1), Window.currentRow)
    )
    return df.withColumn("moving_avg", F.avg("amount").over(window))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


SALES_DATA: list[tuple[str, str, float]] = [
    ("electronics", "2024-01-01", 100.0),
    ("electronics", "2024-01-02", 200.0),
    ("electronics", "2024-01-03", 150.0),
    ("electronics", "2024-01-04", 300.0),
    ("electronics", "2024-01-05", 250.0),
    ("clothing", "2024-01-01", 50.0),
    ("clothing", "2024-01-02", 75.0),
    ("clothing", "2024-01-03", 60.0),
]


class TestRunningSum:
    """Running total should match Python cumulative sum."""

    def test_running_total_matches_python(self, spark: SparkSession) -> None:
        result = running_sum_spark(spark, SALES_DATA)

        # Check electronics category
        elec_rows = sorted(
            [
                (r["date"], r["amount"], r["running_total"])
                for r in result.collect()
                if r["category"] == "electronics"
            ]
        )
        elec_amounts = [r[1] for r in elec_rows]
        elec_totals = [r[2] for r in elec_rows]
        assert elec_totals == running_sum_python(elec_amounts)

    def test_last_row_equals_full_sum(self, spark: SparkSession) -> None:
        result = running_sum_spark(spark, SALES_DATA)

        for category in ["electronics", "clothing"]:
            rows = [r for r in result.collect() if r["category"] == category]
            amounts = [r["amount"] for r in rows]
            last_total = max(r["running_total"] for r in rows)
            assert abs(last_total - sum(amounts)) < 0.01

    def test_partitions_are_independent(self, spark: SparkSession) -> None:
        result = running_sum_spark(spark, SALES_DATA)

        # Clothing running total should not include electronics amounts
        clothing_rows = sorted(
            [
                (r["date"], r["running_total"])
                for r in result.collect()
                if r["category"] == "clothing"
            ]
        )
        # clothing: 50, 50+75=125, 125+60=185
        expected = [50.0, 125.0, 185.0]
        actual = [r[1] for r in clothing_rows]
        assert actual == expected


class TestMovingAverage:
    """Moving average should match Python sliding window calculation."""

    def test_moving_avg_matches_python(self, spark: SparkSession) -> None:
        result = moving_average_spark(spark, SALES_DATA, window_size=3)

        elec_rows = sorted(
            [
                (r["date"], r["amount"], r["moving_avg"])
                for r in result.collect()
                if r["category"] == "electronics"
            ]
        )
        elec_amounts = [r[1] for r in elec_rows]
        expected = moving_average_python(elec_amounts, 3)
        actual = [r[2] for r in elec_rows]

        for a, e in zip(actual, expected):
            assert abs(a - e) < 0.01, f"Expected {e}, got {a}"
