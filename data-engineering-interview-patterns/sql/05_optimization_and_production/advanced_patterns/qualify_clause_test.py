"""Tests for QUALIFY clause pattern."""

import duckdb
import pytest
from datetime import datetime


@pytest.fixture
def db_events(db: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyConnection:
    """DuckDB with events table loaded."""
    db.execute("""
        CREATE TABLE events (
            user_id INTEGER,
            event_type VARCHAR(20),
            event_time TIMESTAMP
        )
    """)
    db.execute("""
        INSERT INTO events VALUES
            (1, 'login', '2024-01-01 10:00:00'),
            (1, 'login', '2024-01-02 10:00:00'),
            (1, 'purchase', '2024-01-01 11:00:00'),
            (2, 'login', '2024-01-01 09:00:00'),
            (2, 'login', '2024-01-03 09:00:00')
    """)
    return db


class TestQualifyDedup:
    """Test QUALIFY-based deduplication."""

    def test_dedup_keeps_latest(self, db_events: duckdb.DuckDBPyConnection) -> None:
        """Keep only the latest event per (user_id, event_type)."""
        result = db_events.execute("""
            SELECT user_id, event_type, event_time
            FROM events
            QUALIFY ROW_NUMBER() OVER (
                PARTITION BY user_id, event_type
                ORDER BY event_time DESC
            ) = 1
            ORDER BY user_id, event_type
        """).fetchall()
        assert len(result) == 3
        # User 1 login: latest is 2024-01-02
        assert result[0] == (1, "login", datetime(2024, 1, 2, 10, 0, 0))
        # User 1 purchase: only one
        assert result[1] == (1, "purchase", datetime(2024, 1, 1, 11, 0, 0))
        # User 2 login: latest is 2024-01-03
        assert result[2] == (2, "login", datetime(2024, 1, 3, 9, 0, 0))

    def test_qualify_matches_subquery(
        self, db_events: duckdb.DuckDBPyConnection
    ) -> None:
        """QUALIFY produces same results as the subquery workaround."""
        qualify_result = db_events.execute("""
            SELECT user_id, event_type, event_time
            FROM events
            QUALIFY ROW_NUMBER() OVER (
                PARTITION BY user_id, event_type
                ORDER BY event_time DESC
            ) = 1
            ORDER BY user_id, event_type
        """).fetchall()
        subquery_result = db_events.execute("""
            SELECT user_id, event_type, event_time FROM (
                SELECT *, ROW_NUMBER() OVER (
                    PARTITION BY user_id, event_type
                    ORDER BY event_time DESC
                ) AS rn
                FROM events
            ) t WHERE rn = 1
            ORDER BY user_id, event_type
        """).fetchall()
        assert qualify_result == subquery_result


class TestQualifyTopN:
    """Test QUALIFY for top-N per group."""

    def test_top_n_per_group(self, db: duckdb.DuckDBPyConnection) -> None:
        """QUALIFY with RANK to get top earners per department."""
        db.execute("""
            CREATE TABLE employees (
                id INTEGER, name VARCHAR, department_id INTEGER, salary INTEGER
            )
        """)
        db.execute("""
            INSERT INTO employees VALUES
                (1, 'Alice', 1, 120000), (2, 'Bob', 1, 110000),
                (3, 'Carol', 1, 105000), (4, 'Dave', 2, 95000),
                (5, 'Eve', 2, 90000)
        """)
        result = db.execute("""
            SELECT name, department_id, salary
            FROM employees
            QUALIFY RANK() OVER (
                PARTITION BY department_id ORDER BY salary DESC
            ) <= 2
            ORDER BY department_id, salary DESC
        """).fetchall()
        assert len(result) == 4
        assert result[0] == ("Alice", 1, 120000)
        assert result[1] == ("Bob", 1, 110000)
        assert result[2] == ("Dave", 2, 95000)
        assert result[3] == ("Eve", 2, 90000)
