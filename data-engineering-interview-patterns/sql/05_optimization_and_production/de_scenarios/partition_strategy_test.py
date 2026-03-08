"""Tests for partition strategy scenarios."""

import duckdb
import pytest


@pytest.fixture
def db_web_events(db: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyConnection:
    """DuckDB with web_events table for partition tests."""
    db.execute("""
        CREATE TABLE web_events (
            event_id INTEGER,
            user_id INTEGER,
            event_date DATE,
            event_type VARCHAR(20),
            page_url VARCHAR(200),
            session_id VARCHAR(50)
        )
    """)
    db.execute("""
        INSERT INTO web_events
        SELECT
            i AS event_id,
            (i % 500) + 1 AS user_id,
            DATE '2023-01-01' + CAST(i % 365 AS INTEGER) AS event_date,
            CASE i % 4
                WHEN 0 THEN 'pageview'
                WHEN 1 THEN 'click'
                WHEN 2 THEN 'scroll'
                ELSE 'submit'
            END AS event_type,
            '/page/' || (i % 50) AS page_url,
            'session_' || (i % 1000) AS session_id
        FROM generate_series(1, 10950) AS t(i)
    """)
    return db


class TestPartitionFiltering:
    """Test that partition-filtered queries return correct results."""

    def test_single_date_filter(
        self, db_web_events: duckdb.DuckDBPyConnection
    ) -> None:
        """Filtering to a single date returns only that date's events."""
        result = db_web_events.execute("""
            SELECT DISTINCT event_date
            FROM web_events
            WHERE event_date = DATE '2023-06-15'
        """).fetchall()
        assert len(result) == 1
        assert str(result[0][0]) == "2023-06-15"

    def test_date_range_filter(
        self, db_web_events: duckdb.DuckDBPyConnection
    ) -> None:
        """Date range filter returns only dates within range."""
        result = db_web_events.execute("""
            SELECT DISTINCT event_date
            FROM web_events
            WHERE event_date >= DATE '2023-06-01'
              AND event_date < DATE '2023-07-01'
            ORDER BY event_date
        """).fetchall()
        dates = [str(r[0]) for r in result]
        assert all(d.startswith("2023-06") for d in dates)
        assert len(dates) == 30  # June has 30 days

    def test_no_filter_returns_all_dates(
        self, db_web_events: duckdb.DuckDBPyConnection
    ) -> None:
        """Without date filter, all dates are returned."""
        result = db_web_events.execute("""
            SELECT COUNT(DISTINCT event_date) FROM web_events
        """).fetchone()
        assert result[0] == 365

    def test_partition_filter_reduces_rows(
        self, db_web_events: duckdb.DuckDBPyConnection
    ) -> None:
        """Single-date filter returns far fewer rows than full scan."""
        total_count = db_web_events.execute(
            "SELECT COUNT(*) FROM web_events"
        ).fetchone()[0]
        filtered_count = db_web_events.execute("""
            SELECT COUNT(*) FROM web_events
            WHERE event_date = DATE '2023-06-15'
        """).fetchone()[0]
        # Single day should be ~1/365 of total
        assert filtered_count < total_count / 100


class TestPartitionAggregation:
    """Test aggregation queries with and without partition filters."""

    def test_aggregation_with_date_filter(
        self, db_web_events: duckdb.DuckDBPyConnection
    ) -> None:
        """Aggregation with date filter returns correct groups."""
        result = db_web_events.execute("""
            SELECT event_type, COUNT(*) AS cnt
            FROM web_events
            WHERE event_date = DATE '2023-06-15'
            GROUP BY event_type
            ORDER BY event_type
        """).fetchall()
        event_types = [r[0] for r in result]
        # All 4 event types should appear
        assert set(event_types) == {"click", "pageview", "scroll", "submit"}
        # Each count should be > 0
        assert all(r[1] > 0 for r in result)

    def test_monthly_aggregation(
        self, db_web_events: duckdb.DuckDBPyConnection
    ) -> None:
        """Monthly aggregation with date range produces daily breakdown."""
        result = db_web_events.execute("""
            SELECT event_date, event_type, COUNT(*) AS cnt
            FROM web_events
            WHERE event_date >= DATE '2023-06-01'
              AND event_date < DATE '2023-07-01'
            GROUP BY event_date, event_type
            ORDER BY event_date, event_type
        """).fetchall()
        # 30 days * 4 event types = 120 rows
        assert len(result) == 120
