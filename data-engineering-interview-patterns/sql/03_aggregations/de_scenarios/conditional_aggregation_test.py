"""Tests for conditional aggregation scenario."""

from pathlib import Path

import duckdb

SQL_DIR = Path(__file__).parent


class TestConditionalAggregation:
    """Test SUM(CASE WHEN ...) conditional aggregation patterns."""

    def _setup(self, db: duckdb.DuckDBPyConnection) -> None:
        """Create and populate the orders table."""
        sql = (SQL_DIR / "conditional_aggregation.sql").read_text()
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if not stmt:
                continue
            upper = stmt.upper().lstrip()
            if upper.startswith("SELECT") or upper.startswith("--"):
                continue
            stripped = "\n".join(
                line for line in stmt.split("\n")
                if not line.strip().startswith("--") and not line.strip().startswith("/*")
            ).strip()
            if not stripped:
                continue
            db.execute(stmt)

    def test_january_electronics_revenue(
        self, db: duckdb.DuckDBPyConnection
    ) -> None:
        """January electronics revenue is 299.99 + 199.99 = 499.98."""
        self._setup(db)
        result = db.execute("""
            SELECT SUM(CASE WHEN category = 'electronics' THEN amount ELSE 0 END)
            FROM orders
            WHERE status = 'completed'
              AND DATE_TRUNC('month', order_date) = DATE '2024-01-01'
        """).fetchone()
        assert float(result[0]) == 499.98

    def test_cancelled_orders_excluded(self, db: duckdb.DuckDBPyConnection) -> None:
        """Cancelled orders are excluded from completed-only aggregation."""
        self._setup(db)
        result = db.execute("""
            SELECT SUM(CASE WHEN category = 'food' THEN amount ELSE 0 END)
            FROM orders
            WHERE status = 'completed'
              AND DATE_TRUNC('month', order_date) = DATE '2024-01-01'
        """).fetchone()
        # Food order in Jan is cancelled (id=4), so food revenue = 0
        assert float(result[0]) == 0

    def test_total_matches_sum_of_categories(
        self, db: duckdb.DuckDBPyConnection
    ) -> None:
        """Total revenue equals sum of all category revenues per month."""
        self._setup(db)
        result = db.execute("""
            SELECT
                SUM(CASE WHEN category = 'electronics' THEN amount ELSE 0 END)
                + SUM(CASE WHEN category = 'clothing' THEN amount ELSE 0 END)
                + SUM(CASE WHEN category = 'food' THEN amount ELSE 0 END) AS cat_sum,
                SUM(amount) AS total
            FROM orders
            WHERE status = 'completed'
        """).fetchone()
        assert result[0] == result[1]

    def test_two_months_in_output(self, db: duckdb.DuckDBPyConnection) -> None:
        """Output has two monthly groups (January and February)."""
        self._setup(db)
        result = db.execute("""
            SELECT DISTINCT DATE_TRUNC('month', order_date)
            FROM orders
            WHERE status = 'completed'
            ORDER BY 1
        """).fetchall()
        assert len(result) == 2
