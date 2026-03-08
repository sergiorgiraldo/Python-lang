"""Tests for materialized views and scheduled query patterns."""

import duckdb
import pytest
from datetime import date


@pytest.fixture
def db_page_events(db: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyConnection:
    """DuckDB with raw_page_events table for materialization tests."""
    db.execute("""
        CREATE TABLE raw_page_events (
            event_id INTEGER,
            user_id INTEGER,
            event_date DATE,
            event_type VARCHAR(20),
            page_url VARCHAR(200),
            duration_ms INTEGER
        )
    """)
    db.execute("""
        INSERT INTO raw_page_events
        SELECT
            i AS event_id,
            (i % 1000) + 1 AS user_id,
            DATE '2023-01-01' + CAST(i % 365 AS INTEGER) AS event_date,
            CASE i % 3
                WHEN 0 THEN 'pageview'
                WHEN 1 THEN 'click'
                ELSE 'scroll'
            END AS event_type,
            '/page/' || (i % 100) AS page_url,
            (i % 5000) + 100 AS duration_ms
        FROM generate_series(1, 20000) AS t(i)
    """)
    return db


class TestMaterializedView:
    """Test materialized view (table) creation and query equivalence."""

    def test_materialized_matches_on_the_fly(
        self, db_page_events: duckdb.DuckDBPyConnection
    ) -> None:
        """Materialized table returns same results as on-the-fly computation."""
        # Create the materialized summary
        db_page_events.execute("""
            CREATE TABLE daily_event_summary AS
            SELECT
                event_date,
                event_type,
                COUNT(*) AS event_count,
                COUNT(DISTINCT user_id) AS unique_users,
                ROUND(AVG(duration_ms), 2) AS avg_duration_ms
            FROM raw_page_events
            GROUP BY event_date, event_type
        """)
        # Query materialized
        mat_result = db_page_events.execute("""
            SELECT event_date, event_type, event_count, unique_users
            FROM daily_event_summary
            WHERE event_date >= DATE '2023-06-01'
              AND event_date < DATE '2023-07-01'
            ORDER BY event_date, event_type
        """).fetchall()
        # Query on the fly
        fly_result = db_page_events.execute("""
            SELECT
                event_date,
                event_type,
                COUNT(*) AS event_count,
                COUNT(DISTINCT user_id) AS unique_users
            FROM raw_page_events
            WHERE event_date >= DATE '2023-06-01'
              AND event_date < DATE '2023-07-01'
            GROUP BY event_date, event_type
            ORDER BY event_date, event_type
        """).fetchall()
        assert mat_result == fly_result

    def test_materialized_has_all_dates(
        self, db_page_events: duckdb.DuckDBPyConnection
    ) -> None:
        """Materialized summary covers all dates in the source."""
        db_page_events.execute("""
            CREATE TABLE daily_event_summary AS
            SELECT
                event_date,
                event_type,
                COUNT(*) AS event_count
            FROM raw_page_events
            GROUP BY event_date, event_type
        """)
        source_dates = db_page_events.execute("""
            SELECT COUNT(DISTINCT event_date) FROM raw_page_events
        """).fetchone()[0]
        summary_dates = db_page_events.execute("""
            SELECT COUNT(DISTINCT event_date) FROM daily_event_summary
        """).fetchone()[0]
        assert source_dates == summary_dates


class TestIncrementalRefresh:
    """Test incremental refresh pattern for materialized views."""

    def test_incremental_adds_new_date(
        self, db_page_events: duckdb.DuckDBPyConnection
    ) -> None:
        """Incremental refresh adds new date data without full rebuild."""
        # Create initial materialized summary
        db_page_events.execute("""
            CREATE TABLE daily_event_summary AS
            SELECT
                event_date,
                event_type,
                COUNT(*) AS event_count,
                COUNT(DISTINCT user_id) AS unique_users
            FROM raw_page_events
            GROUP BY event_date, event_type
        """)
        initial_dates = db_page_events.execute("""
            SELECT COUNT(DISTINCT event_date) FROM daily_event_summary
        """).fetchone()[0]

        # Insert new data for a new date
        new_date = date(2024, 1, 15)
        db_page_events.execute("""
            INSERT INTO raw_page_events
            SELECT
                20000 + i AS event_id,
                (i % 100) + 1 AS user_id,
                DATE '2024-01-15' AS event_date,
                CASE i % 3
                    WHEN 0 THEN 'pageview'
                    WHEN 1 THEN 'click'
                    ELSE 'scroll'
                END AS event_type,
                '/page/' || (i % 10) AS page_url,
                (i % 3000) + 200 AS duration_ms
            FROM generate_series(1, 500) AS t(i)
        """)

        # Incremental refresh: only process the new date
        db_page_events.execute("""
            DELETE FROM daily_event_summary
            WHERE event_date = DATE '2024-01-15'
        """)
        db_page_events.execute("""
            INSERT INTO daily_event_summary
            SELECT
                event_date,
                event_type,
                COUNT(*) AS event_count,
                COUNT(DISTINCT user_id) AS unique_users
            FROM raw_page_events
            WHERE event_date = DATE '2024-01-15'
            GROUP BY event_date, event_type
        """)

        # Verify new date was added
        final_dates = db_page_events.execute("""
            SELECT COUNT(DISTINCT event_date) FROM daily_event_summary
        """).fetchone()[0]
        assert final_dates == initial_dates + 1

        # Verify the new date's data is correct
        new_data = db_page_events.execute("""
            SELECT event_type, event_count
            FROM daily_event_summary
            WHERE event_date = DATE '2024-01-15'
            ORDER BY event_type
        """).fetchall()
        assert len(new_data) == 3  # 3 event types
        total_events = sum(r[1] for r in new_data)
        assert total_events == 500

    def test_incremental_is_idempotent(
        self, db_page_events: duckdb.DuckDBPyConnection
    ) -> None:
        """Running incremental refresh twice produces same result."""
        db_page_events.execute("""
            CREATE TABLE daily_event_summary AS
            SELECT
                event_date,
                event_type,
                COUNT(*) AS event_count
            FROM raw_page_events
            GROUP BY event_date, event_type
        """)

        target_date = "2023-06-15"
        for _ in range(2):
            db_page_events.execute(f"""
                DELETE FROM daily_event_summary
                WHERE event_date = DATE '{target_date}'
            """)
            db_page_events.execute(f"""
                INSERT INTO daily_event_summary
                SELECT event_date, event_type, COUNT(*) AS event_count
                FROM raw_page_events
                WHERE event_date = DATE '{target_date}'
                GROUP BY event_date, event_type
            """)

        result = db_page_events.execute(f"""
            SELECT COUNT(*) FROM daily_event_summary
            WHERE event_date = DATE '{target_date}'
        """).fetchone()[0]
        # Should have exactly 3 rows (one per event type), not 6
        assert result == 3
