"""Tests for running totals with window functions scenario."""

from pathlib import Path

import duckdb

SQL_DIR = Path(__file__).parent


class TestRunningTotals:
    """Test cumulative sum and running average computations."""

    def _setup(self, db: duckdb.DuckDBPyConnection) -> None:
        """Create and populate the daily_revenue table."""
        sql = (SQL_DIR / "running_totals.sql").read_text()
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if not stmt or stmt.upper().lstrip().startswith("SELECT"):
                continue
            stripped = "\n".join(
                line for line in stmt.split("\n")
                if not line.strip().startswith("--") and not line.strip().startswith("/*")
            ).strip()
            if not stripped:
                continue
            db.execute(stmt)

    def test_final_cumulative_equals_total(self, db: duckdb.DuckDBPyConnection) -> None:
        """Running total on the last row equals the sum of all daily revenues."""
        self._setup(db)
        result = db.execute("""
            SELECT cumulative_revenue FROM (
                SELECT
                    revenue_date,
                    SUM(revenue) OVER (
                        ORDER BY revenue_date
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ) AS cumulative_revenue
                FROM daily_revenue
                ORDER BY revenue_date
            )
            ORDER BY revenue_date DESC
            LIMIT 1
        """).fetchone()
        total = db.execute("SELECT SUM(revenue) FROM daily_revenue").fetchone()
        assert result[0] == total[0]

    def test_running_total_is_monotonically_increasing(
        self, db: duckdb.DuckDBPyConnection
    ) -> None:
        """Running total never decreases (all revenues are positive)."""
        self._setup(db)
        result = db.execute("""
            SELECT
                SUM(revenue) OVER (
                    ORDER BY revenue_date
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS cumulative_revenue
            FROM daily_revenue
            ORDER BY revenue_date
        """).fetchall()
        values = [r[0] for r in result]
        for i in range(1, len(values)):
            assert values[i] >= values[i - 1]

    def test_first_row_cumulative_equals_first_day(
        self, db: duckdb.DuckDBPyConnection
    ) -> None:
        """Running total on the first row equals that day's revenue."""
        self._setup(db)
        result = db.execute("""
            SELECT
                revenue,
                SUM(revenue) OVER (
                    ORDER BY revenue_date
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS cumulative_revenue
            FROM daily_revenue
            ORDER BY revenue_date
            LIMIT 1
        """).fetchone()
        assert result[0] == result[1]

    def test_running_avg_bounded_by_min_max(
        self, db: duckdb.DuckDBPyConnection
    ) -> None:
        """Running average stays between min and max daily revenue."""
        self._setup(db)
        bounds = db.execute(
            "SELECT MIN(revenue), MAX(revenue) FROM daily_revenue"
        ).fetchone()
        result = db.execute("""
            SELECT ROUND(AVG(revenue) OVER (
                ORDER BY revenue_date
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ), 2) AS running_avg
            FROM daily_revenue
        """).fetchall()
        for row in result:
            assert bounds[0] <= row[0] <= bounds[1]
