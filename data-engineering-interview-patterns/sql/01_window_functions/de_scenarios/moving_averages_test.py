"""Tests for moving averages with window functions scenario."""

from pathlib import Path

import duckdb

SQL_DIR = Path(__file__).parent


class TestMovingAverages:
    """Test ROWS-based and RANGE-based moving averages."""

    def _setup(self, db: duckdb.DuckDBPyConnection) -> None:
        """Create and populate the daily_metrics table."""
        sql = (SQL_DIR / "moving_averages.sql").read_text()
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

    def test_rows_moving_avg_first_row(self, db: duckdb.DuckDBPyConnection) -> None:
        """First row's ROWS-based moving avg equals its own value (only 1 row in window)."""
        self._setup(db)
        result = db.execute("""
            SELECT ROUND(AVG(value) OVER (
                ORDER BY metric_date
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ), 2) AS moving_avg_rows
            FROM daily_metrics
            ORDER BY metric_date
            LIMIT 1
        """).fetchone()
        first_value = db.execute(
            "SELECT value FROM daily_metrics ORDER BY metric_date LIMIT 1"
        ).fetchone()
        assert result[0] == first_value[0]

    def test_rows_moving_avg_full_window(self, db: duckdb.DuckDBPyConnection) -> None:
        """When 7+ rows exist, ROWS-based avg uses exactly 7 rows."""
        self._setup(db)
        result = db.execute("""
            SELECT metric_date, value,
                   ROUND(AVG(value) OVER (
                       ORDER BY metric_date
                       ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
                   ), 2) AS moving_avg_rows
            FROM daily_metrics
            ORDER BY metric_date
        """).fetchall()
        # Row index 6 (Jan 7) is the first with a full 7-row window
        # Values: 100, 120, 95, 140, 110, 130, 125 = 820 / 7 = 117.14
        assert result[6][2] == 117.14

    def test_range_vs_rows_differ_with_gaps(
        self, db: duckdb.DuckDBPyConnection
    ) -> None:
        """RANGE-based and ROWS-based averages differ when date gaps exist."""
        self._setup(db)
        rows_result = db.execute("""
            SELECT metric_date, ROUND(AVG(value) OVER (
                ORDER BY metric_date
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ), 2) AS avg
            FROM daily_metrics
            ORDER BY metric_date
        """).fetchall()
        range_result = db.execute("""
            SELECT metric_date, ROUND(AVG(value) OVER (
                ORDER BY metric_date
                RANGE BETWEEN INTERVAL '6 days' PRECEDING AND CURRENT ROW
            ), 2) AS avg
            FROM daily_metrics
            ORDER BY metric_date
        """).fetchall()
        # After the gap (Jan 13, 14), RANGE includes fewer rows than ROWS
        # Jan 13: ROWS looks back 6 physical rows, RANGE looks back 6 calendar days
        rows_jan13 = [r for r in rows_result if str(r[0]) == "2024-01-13"][0][1]
        range_jan13 = [r for r in range_result if str(r[0]) == "2024-01-13"][0][1]
        assert rows_jan13 != range_jan13

    def test_data_has_date_gaps(self, db: duckdb.DuckDBPyConnection) -> None:
        """Verify the test data has gaps (Jan 11-12 missing)."""
        self._setup(db)
        result = db.execute("""
            SELECT COUNT(*) FROM daily_metrics
            WHERE metric_date IN ('2024-01-11', '2024-01-12')
        """).fetchone()
        assert result[0] == 0
