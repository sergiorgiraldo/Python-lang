"""Tests for GROUPING SETS, ROLLUP and CUBE patterns."""

import duckdb
import pytest


@pytest.fixture
def db_sales(db: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyConnection:
    """DuckDB with sales table loaded."""
    db.execute("""
        CREATE TABLE sales (
            region VARCHAR(20),
            product VARCHAR(20),
            quarter VARCHAR(10),
            revenue INTEGER
        )
    """)
    db.execute("""
        INSERT INTO sales VALUES
            ('East', 'Widget', 'Q1', 100), ('East', 'Widget', 'Q2', 150),
            ('East', 'Gadget', 'Q1', 200), ('East', 'Gadget', 'Q2', 250),
            ('West', 'Widget', 'Q1', 120), ('West', 'Widget', 'Q2', 180),
            ('West', 'Gadget', 'Q1', 220), ('West', 'Gadget', 'Q2', 280)
    """)
    return db


class TestGroupingSets:
    """Test GROUPING SETS produces correct multi-level aggregation."""

    def test_row_count(self, db_sales: duckdb.DuckDBPyConnection) -> None:
        """GROUPING SETS with 3 levels: 4 detail + 2 subtotal + 1 grand = 7."""
        result = db_sales.execute("""
            SELECT region, product, SUM(revenue) AS total
            FROM sales
            GROUP BY GROUPING SETS (
                (region, product),
                (region),
                ()
            )
        """).fetchall()
        assert len(result) == 7

    def test_grand_total(self, db_sales: duckdb.DuckDBPyConnection) -> None:
        """Grand total row has NULL region and NULL product."""
        result = db_sales.execute("""
            SELECT region, product, SUM(revenue) AS total
            FROM sales
            GROUP BY GROUPING SETS (
                (region, product),
                (region),
                ()
            )
            HAVING region IS NULL AND product IS NULL
        """).fetchall()
        assert len(result) == 1
        assert result[0][2] == 1500  # sum of all revenue

    def test_region_subtotals(self, db_sales: duckdb.DuckDBPyConnection) -> None:
        """Region subtotals: East=700, West=800."""
        result = db_sales.execute("""
            SELECT region, SUM(revenue) AS total
            FROM sales
            GROUP BY GROUPING SETS ((region), ())
            HAVING region IS NOT NULL
            ORDER BY region
        """).fetchall()
        assert result[0] == ("East", 700)
        assert result[1] == ("West", 800)

    def test_grouping_function(self, db_sales: duckdb.DuckDBPyConnection) -> None:
        """GROUPING() returns 1 for rolled-up columns, 0 for real groups."""
        result = db_sales.execute("""
            SELECT
                region,
                product,
                SUM(revenue) AS total,
                GROUPING(region) AS g_region,
                GROUPING(product) AS g_product
            FROM sales
            GROUP BY GROUPING SETS ((region, product), (region), ())
            ORDER BY region NULLS LAST, product NULLS LAST
        """).fetchall()
        # Detail rows: both grouping flags = 0
        detail_rows = [r for r in result if r[3] == 0 and r[4] == 0]
        assert len(detail_rows) == 4
        # Subtotal rows: product rolled up (g_product=1), region real (g_region=0)
        subtotal_rows = [r for r in result if r[3] == 0 and r[4] == 1]
        assert len(subtotal_rows) == 2
        # Grand total: both rolled up
        grand_rows = [r for r in result if r[3] == 1 and r[4] == 1]
        assert len(grand_rows) == 1


class TestRollup:
    """Test ROLLUP produces hierarchical subtotals."""

    def test_rollup_matches_grouping_sets(
        self, db_sales: duckdb.DuckDBPyConnection
    ) -> None:
        """ROLLUP(region, product) = GROUPING SETS ((region,product),(region),())."""
        rollup = db_sales.execute("""
            SELECT region, product, SUM(revenue) AS total
            FROM sales
            GROUP BY ROLLUP (region, product)
            ORDER BY region NULLS LAST, product NULLS LAST
        """).fetchall()
        gs = db_sales.execute("""
            SELECT region, product, SUM(revenue) AS total
            FROM sales
            GROUP BY GROUPING SETS ((region, product), (region), ())
            ORDER BY region NULLS LAST, product NULLS LAST
        """).fetchall()
        assert rollup == gs

    def test_rollup_row_count(self, db_sales: duckdb.DuckDBPyConnection) -> None:
        """ROLLUP with 2 regions * 2 products: 4 + 2 + 1 = 7 rows."""
        result = db_sales.execute("""
            SELECT region, product, SUM(revenue) AS total
            FROM sales
            GROUP BY ROLLUP (region, product)
        """).fetchall()
        assert len(result) == 7


class TestCube:
    """Test CUBE produces all dimension combinations."""

    def test_cube_row_count(self, db_sales: duckdb.DuckDBPyConnection) -> None:
        """CUBE with 2 regions * 2 products: 4 + 2 + 2 + 1 = 9 rows."""
        result = db_sales.execute("""
            SELECT region, product, SUM(revenue) AS total
            FROM sales
            GROUP BY CUBE (region, product)
        """).fetchall()
        assert len(result) == 9

    def test_cube_has_product_subtotals(
        self, db_sales: duckdb.DuckDBPyConnection
    ) -> None:
        """CUBE includes per-product subtotals (which ROLLUP does not)."""
        result = db_sales.execute("""
            SELECT region, product, SUM(revenue) AS total
            FROM sales
            GROUP BY CUBE (region, product)
            HAVING region IS NULL AND product IS NOT NULL
            ORDER BY product
        """).fetchall()
        # Widget total: 100+150+120+180=550, Gadget total: 200+250+220+280=950
        assert len(result) == 2
        assert result[0] == (None, "Gadget", 950)
        assert result[1] == (None, "Widget", 550)
