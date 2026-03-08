"""
Ranking and Dedup with PySpark Window Functions.

Pattern connection:
  patterns/04_sliding_window/ - maintaining state across ordered elements
  sql/01_window_functions/ - ROW_NUMBER, RANK, DENSE_RANK
  sql/06_dbt_patterns/ - dedup_by_key macro

This is the single most common PySpark interview pattern. "Deduplicate
this DataFrame keeping the most recent record per key" appears in
nearly every DE coding interview that includes Spark.

Under the hood:
  - Window functions trigger a sort within each partition
  - PARTITION BY determines the grouping (like GROUP BY but keeps all rows)
  - ORDER BY determines the sort within each partition
  - row_number() assigns sequential integers within each partition
  - Dedup = row_number() == 1 after ordering by your preferred tiebreaker
"""

import pytest

pyspark = pytest.importorskip("pyspark")

from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql import functions as F


# ---------------------------------------------------------------------------
# Pure Python: dedup keeping latest per key
# ---------------------------------------------------------------------------


def dedup_latest_python(
    events: list[tuple[str, str, str]],
) -> list[tuple[str, str, str]]:
    """Keep the most recent event per user using a dict.

    Time:  O(n)
    Space: O(k) where k = number of unique users

    Args:
        events: List of (user_id, event_timestamp, event_type) tuples.

    Returns:
        Deduplicated list with one row per user (the latest event).

    Example:
        >>> dedup_latest_python([
        ...     ("u1", "2024-01-02", "click"),
        ...     ("u1", "2024-01-01", "view"),
        ... ])
        [('u1', '2024-01-02', 'click')]
    """
    latest: dict[str, tuple[str, str, str]] = {}
    for user_id, ts, event_type in events:
        if user_id not in latest or ts > latest[user_id][1]:
            latest[user_id] = (user_id, ts, event_type)
    return sorted(latest.values())


# ---------------------------------------------------------------------------
# PySpark: dedup with Window + row_number
# ---------------------------------------------------------------------------


def dedup_with_window(
    spark: SparkSession,
    events: list[tuple[str, str, str]],
) -> DataFrame:
    """Deduplicate keeping the latest event per user using row_number().

    This is the standard Spark dedup pattern:
      1. Define a window partitioned by the dedup key, ordered by tiebreaker
      2. Assign row_number() within each partition
      3. Filter to row_number == 1

    Args:
        spark: Active SparkSession.
        events: List of (user_id, event_timestamp, event_type) tuples.

    Returns:
        DataFrame with one row per user_id (most recent event).
    """
    df = spark.createDataFrame(events, ["user_id", "event_timestamp", "event_type"])

    window = Window.partitionBy("user_id").orderBy(F.desc("event_timestamp"))
    deduped = (
        df.withColumn("rn", F.row_number().over(window))
        .filter(F.col("rn") == 1)
        .drop("rn")
    )
    return deduped


def dedup_with_sql(
    spark: SparkSession,
    events: list[tuple[str, str, str]],
) -> DataFrame:
    """Deduplicate using Spark SQL (equivalent to the DataFrame API approach).

    Args:
        spark: Active SparkSession.
        events: List of (user_id, event_timestamp, event_type) tuples.

    Returns:
        DataFrame with one row per user_id (most recent event).
    """
    df = spark.createDataFrame(events, ["user_id", "event_timestamp", "event_type"])
    df.createOrReplaceTempView("events")

    return spark.sql("""
        SELECT user_id, event_timestamp, event_type
        FROM (
            SELECT *,
                ROW_NUMBER() OVER (
                    PARTITION BY user_id ORDER BY event_timestamp DESC
                ) AS rn
            FROM events
        )
        WHERE rn = 1
    """)


# ---------------------------------------------------------------------------
# Ranking function comparison
# ---------------------------------------------------------------------------


def compare_ranking_functions(
    spark: SparkSession,
    data: list[tuple[str, int]],
) -> list[dict]:
    """Show the difference between row_number, rank and dense_rank.

    Given data with ties, the three functions behave differently:
      - row_number: sequential, no ties (1, 2, 3, 4)
      - rank: ties get same rank, gaps after (1, 2, 2, 4)
      - dense_rank: ties get same rank, no gaps (1, 2, 2, 3)

    Args:
        spark: Active SparkSession.
        data: List of (name, score) tuples (may contain tied scores).

    Returns:
        List of dicts with name, score, row_num, rank, dense_rank.
    """
    df = spark.createDataFrame(data, ["name", "score"])
    window = Window.orderBy(F.desc("score"))

    result = df.select(
        "name",
        "score",
        F.row_number().over(window).alias("row_num"),
        F.rank().over(window).alias("rank"),
        F.dense_rank().over(window).alias("dense_rank"),
    ).orderBy(F.desc("score"), "name")

    return [row.asDict() for row in result.collect()]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


EVENTS: list[tuple[str, str, str]] = [
    ("u1", "2024-01-01", "view"),
    ("u1", "2024-01-03", "click"),
    ("u1", "2024-01-02", "scroll"),
    ("u2", "2024-01-01", "view"),
    ("u2", "2024-01-04", "purchase"),
    ("u3", "2024-01-02", "click"),
]


class TestDedupWithWindow:
    """Dedup should keep one row per user with the latest event."""

    def test_one_row_per_user(self, spark: SparkSession) -> None:
        result = dedup_with_window(spark, EVENTS)
        user_ids = [r["user_id"] for r in result.collect()]
        assert sorted(user_ids) == ["u1", "u2", "u3"]

    def test_keeps_latest_event(self, spark: SparkSession) -> None:
        result = dedup_with_window(spark, EVENTS)
        rows = {r["user_id"]: r for r in result.collect()}
        assert rows["u1"]["event_timestamp"] == "2024-01-03"
        assert rows["u1"]["event_type"] == "click"
        assert rows["u2"]["event_timestamp"] == "2024-01-04"
        assert rows["u2"]["event_type"] == "purchase"

    def test_sql_matches_dataframe_api(self, spark: SparkSession) -> None:
        df_result = dedup_with_window(spark, EVENTS)
        sql_result = dedup_with_sql(spark, EVENTS)

        df_rows = sorted(
            [(r["user_id"], r["event_timestamp"]) for r in df_result.collect()]
        )
        sql_rows = sorted(
            [(r["user_id"], r["event_timestamp"]) for r in sql_result.collect()]
        )
        assert df_rows == sql_rows

    def test_matches_python_dedup(self, spark: SparkSession) -> None:
        python_result = dedup_latest_python(EVENTS)
        spark_result = dedup_with_window(spark, EVENTS)

        spark_rows = sorted(
            [
                (r["user_id"], r["event_timestamp"], r["event_type"])
                for r in spark_result.collect()
            ]
        )
        assert spark_rows == python_result


class TestRankingFunctions:
    """Compare row_number, rank and dense_rank behavior."""

    def test_ranking_with_ties(self, spark: SparkSession) -> None:
        # alice and carol tie at 90
        data: list[tuple[str, int]] = [
            ("alice", 90),
            ("bob", 80),
            ("carol", 90),
            ("dave", 70),
        ]
        rows = compare_ranking_functions(spark, data)

        # row_number: all unique (1, 2, 3, 4)
        row_nums = [r["row_num"] for r in rows]
        assert row_nums == [1, 2, 3, 4]

        # rank: ties get same rank, gap after (1, 1, 3, 4)
        ranks = [r["rank"] for r in rows]
        assert ranks == [1, 1, 3, 4]

        # dense_rank: ties get same rank, no gap (1, 1, 2, 3)
        dense_ranks = [r["dense_rank"] for r in rows]
        assert dense_ranks == [1, 1, 2, 3]

    def test_no_ties_all_agree(self, spark: SparkSession) -> None:
        data: list[tuple[str, int]] = [
            ("alice", 100),
            ("bob", 90),
            ("carol", 80),
        ]
        rows = compare_ranking_functions(spark, data)
        for r in rows:
            assert r["row_num"] == r["rank"] == r["dense_rank"]
