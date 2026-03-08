"""Tests for gap detection scenario."""

from pathlib import Path

import duckdb

SQL_DIR = Path(__file__).parent


class TestGapDetection:
    """Test generate_series + LEFT JOIN for finding missing dates."""

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
        """Create and populate the daily_partitions table."""
        sql = (SQL_DIR / "gap_detection.sql").read_text()
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if not stmt:
                continue
            keyword = self._first_keyword(stmt)
            if keyword in ("CREATE", "INSERT"):
                db.execute(stmt)

    def test_correct_missing_dates(self, db: duckdb.DuckDBPyConnection) -> None:
        """Jan 4 and Jan 6 are identified as missing."""
        self._setup(db)
        result = db.execute("""
            SELECT CAST(expected.d AS DATE) AS missing_date
            FROM generate_series(
                DATE '2024-01-01',
                DATE '2024-01-07',
                INTERVAL '1 day'
            ) AS expected(d)
            LEFT JOIN daily_partitions dp ON expected.d = dp.partition_date
            WHERE dp.partition_date IS NULL
            ORDER BY missing_date
        """).fetchall()
        missing = [str(r[0]) for r in result]
        assert missing == ["2024-01-04", "2024-01-06"]

    def test_missing_count(self, db: duckdb.DuckDBPyConnection) -> None:
        """Exactly 2 dates are missing from the 7-day range."""
        self._setup(db)
        result = db.execute("""
            SELECT COUNT(*)
            FROM generate_series(
                DATE '2024-01-01',
                DATE '2024-01-07',
                INTERVAL '1 day'
            ) AS expected(d)
            LEFT JOIN daily_partitions dp ON expected.d = dp.partition_date
            WHERE dp.partition_date IS NULL
        """).fetchone()
        assert result[0] == 2

    def test_present_dates_not_flagged(self, db: duckdb.DuckDBPyConnection) -> None:
        """Dates that exist in daily_partitions are not flagged as missing."""
        self._setup(db)
        present = db.execute(
            "SELECT partition_date FROM daily_partitions ORDER BY partition_date"
        ).fetchall()
        present_dates = {str(r[0]) for r in present}
        missing = db.execute("""
            SELECT expected.d
            FROM generate_series(
                DATE '2024-01-01',
                DATE '2024-01-07',
                INTERVAL '1 day'
            ) AS expected(d)
            LEFT JOIN daily_partitions dp ON expected.d = dp.partition_date
            WHERE dp.partition_date IS NULL
        """).fetchall()
        missing_dates = {str(r[0]) for r in missing}
        assert present_dates.isdisjoint(missing_dates)
