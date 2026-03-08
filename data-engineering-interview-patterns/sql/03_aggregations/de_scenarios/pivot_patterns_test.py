"""Tests for pivot patterns scenario."""

from pathlib import Path

import duckdb

SQL_DIR = Path(__file__).parent


class TestPivotPatterns:
    """Test row-to-column pivot transformation."""

    @staticmethod
    def _first_keyword(stmt: str) -> str:
        """Return the first SQL keyword after stripping comments."""
        in_block = False
        for line in stmt.split("\n"):
            line = line.strip()
            if in_block:
                if "*/" in line:
                    in_block = False
                continue
            if not line or line.startswith("--"):
                continue
            if line.startswith("/*"):
                if "*/" not in line:
                    in_block = True
                continue
            return line.split()[0].upper() if line.split() else ""
        return ""

    def _setup(self, db: duckdb.DuckDBPyConnection) -> None:
        """Create and populate user_events and user_features tables."""
        sql = (SQL_DIR / "pivot_patterns.sql").read_text()
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if not stmt:
                continue
            keyword = self._first_keyword(stmt)
            if keyword in ("CREATE", "INSERT"):
                db.execute(stmt)

    def test_pivot_output_shape(self, db: duckdb.DuckDBPyConnection) -> None:
        """Pivoted output has 3 rows (one per user) and 4 columns."""
        self._setup(db)
        result = db.execute("""
            SELECT
                user_id,
                SUM(CASE WHEN event_type = 'page_view' THEN event_count ELSE 0 END) AS page_views,
                SUM(CASE WHEN event_type = 'click' THEN event_count ELSE 0 END) AS clicks,
                SUM(CASE WHEN event_type = 'purchase' THEN event_count ELSE 0 END) AS purchases
            FROM user_events
            GROUP BY user_id
            ORDER BY user_id
        """)
        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()
        assert len(rows) == 3
        assert len(columns) == 4

    def test_pivot_values_correct(self, db: duckdb.DuckDBPyConnection) -> None:
        """Pivoted values match the source data for user 1."""
        self._setup(db)
        result = db.execute("""
            SELECT
                SUM(CASE WHEN event_type = 'page_view' THEN event_count ELSE 0 END) AS page_views,
                SUM(CASE WHEN event_type = 'click' THEN event_count ELSE 0 END) AS clicks,
                SUM(CASE WHEN event_type = 'purchase' THEN event_count ELSE 0 END) AS purchases
            FROM user_events
            WHERE user_id = 1
        """).fetchone()
        assert result[0] == 120  # page_views
        assert result[1] == 45   # clicks
        assert result[2] == 3    # purchases

    def test_missing_event_type_is_zero(self, db: duckdb.DuckDBPyConnection) -> None:
        """User 2 has no purchases, pivot shows 0."""
        self._setup(db)
        result = db.execute("""
            SELECT
                SUM(CASE WHEN event_type = 'purchase' THEN event_count ELSE 0 END) AS purchases
            FROM user_events
            WHERE user_id = 2
        """).fetchone()
        assert result[0] == 0

    def test_unpivot_round_trips(self, db: duckdb.DuckDBPyConnection) -> None:
        """Unpivoting user_features back to rows produces expected row count."""
        self._setup(db)
        result = db.execute("""
            SELECT user_id, 'page_view' AS event_type, page_views AS event_count
            FROM user_features
            UNION ALL
            SELECT user_id, 'click', clicks
            FROM user_features
            UNION ALL
            SELECT user_id, 'purchase', purchases
            FROM user_features
        """).fetchall()
        # 3 users * 3 event types = 9 rows
        assert len(result) == 9
