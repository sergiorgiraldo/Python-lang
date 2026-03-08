"""Tests for approximate counting scenario."""

from pathlib import Path

import duckdb

SQL_DIR = Path(__file__).parent


class TestApproximateCounting:
    """Test exact vs approximate distinct counting."""

    def _setup(self, db: duckdb.DuckDBPyConnection) -> None:
        """Create the page_views table with generated data."""
        sql = (SQL_DIR / "approximate_counting.sql").read_text()
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

    def test_exact_count_reasonable_range(
        self, db: duckdb.DuckDBPyConnection
    ) -> None:
        """Exact distinct user count is in a reasonable range for random data."""
        self._setup(db)
        result = db.execute(
            "SELECT COUNT(DISTINCT user_id) FROM page_views"
        ).fetchone()
        exact = result[0]
        # With 1M rows and random() * 100000, expect ~63K-100K distinct
        assert 50000 <= exact <= 100001

    def test_approx_count_within_bounds(
        self, db: duckdb.DuckDBPyConnection
    ) -> None:
        """Approximate count is within 5% of exact count."""
        self._setup(db)
        exact = db.execute(
            "SELECT COUNT(DISTINCT user_id) FROM page_views"
        ).fetchone()[0]
        approx = db.execute(
            "SELECT APPROX_COUNT_DISTINCT(user_id) FROM page_views"
        ).fetchone()[0]
        error_pct = abs(exact - approx) / exact * 100
        assert error_pct < 5.0

    def test_table_has_expected_row_count(
        self, db: duckdb.DuckDBPyConnection
    ) -> None:
        """Generated table has 1M rows."""
        self._setup(db)
        result = db.execute("SELECT COUNT(*) FROM page_views").fetchone()
        assert result[0] == 1000000

    def test_five_page_types_exist(self, db: duckdb.DuckDBPyConnection) -> None:
        """Table has exactly 5 page types: home, product, cart, checkout, search."""
        self._setup(db)
        result = db.execute(
            "SELECT DISTINCT page FROM page_views ORDER BY page"
        ).fetchall()
        pages = [r[0] for r in result]
        assert pages == ["cart", "checkout", "home", "product", "search"]
