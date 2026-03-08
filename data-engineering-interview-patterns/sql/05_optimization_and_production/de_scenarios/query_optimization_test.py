"""Tests for the query optimization walkthrough."""

import duckdb
import pytest


@pytest.fixture
def db_orders(db: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyConnection:
    """DuckDB with orders and order_items tables for optimization tests."""
    db.execute("""
        CREATE TABLE orders_opt (
            order_id INTEGER,
            customer_id INTEGER,
            order_date DATE,
            status VARCHAR(20),
            region VARCHAR(20),
            total_amount DECIMAL(10,2)
        )
    """)
    db.execute("""
        CREATE TABLE order_items_opt (
            item_id INTEGER,
            order_id INTEGER,
            product_name VARCHAR(50),
            quantity INTEGER,
            unit_price DECIMAL(10,2)
        )
    """)
    # Generate 10K orders for tests (smaller than the full demo)
    db.execute("""
        INSERT INTO orders_opt
        SELECT
            i AS order_id,
            (i % 1000) + 1 AS customer_id,
            DATE '2023-01-01' + CAST(i % 365 AS INTEGER) AS order_date,
            CASE i % 4
                WHEN 0 THEN 'completed'
                WHEN 1 THEN 'pending'
                WHEN 2 THEN 'shipped'
                ELSE 'cancelled'
            END AS status,
            CASE i % 4
                WHEN 0 THEN 'East'
                WHEN 1 THEN 'West'
                WHEN 2 THEN 'North'
                ELSE 'South'
            END AS region,
            ROUND((i % 500) + 10.0, 2) AS total_amount
        FROM generate_series(1, 10000) AS t(i)
    """)
    db.execute("""
        INSERT INTO order_items_opt
        SELECT
            ROW_NUMBER() OVER () AS item_id,
            o.order_id,
            'Product_' || ((o.order_id + s.n) % 5) AS product_name,
            ((o.order_id + s.n) % 10) + 1 AS quantity,
            ROUND(((o.order_id + s.n) % 50) + 5.0, 2) AS unit_price
        FROM orders_opt o
        CROSS JOIN (SELECT unnest(generate_series(1, 3)) AS n) s
    """)
    return db


class TestBadQueryCorrectness:
    """Verify the bad and optimized queries return equivalent results."""

    def test_both_queries_match(
        self, db_orders: duckdb.DuckDBPyConnection
    ) -> None:
        """Bad and optimized queries return the same order IDs."""
        bad_result = db_orders.execute("""
            SELECT DISTINCT o.order_id
            FROM (
                SELECT * FROM orders_opt ORDER BY order_date DESC
            ) o
            JOIN order_items_opt i ON o.order_id = i.order_id
            WHERE YEAR(o.order_date) = 2023
              AND o.status = 'completed'
              AND o.region = 'East'
            ORDER BY o.order_id
        """).fetchall()
        optimized_result = db_orders.execute("""
            SELECT o.order_id
            FROM orders_opt o
            WHERE o.order_date >= '2023-01-01'
              AND o.order_date < '2024-01-01'
              AND o.status = 'completed'
              AND o.region = 'East'
              AND EXISTS (
                  SELECT 1 FROM order_items_opt i
                  WHERE i.order_id = o.order_id
              )
            ORDER BY o.order_id
        """).fetchall()
        assert bad_result == optimized_result

    def test_optimized_returns_expected_columns(
        self, db_orders: duckdb.DuckDBPyConnection
    ) -> None:
        """Optimized query returns only the needed columns."""
        result = db_orders.execute("""
            SELECT o.order_id, o.customer_id, o.order_date, o.total_amount
            FROM orders_opt o
            WHERE o.order_date >= '2023-01-01'
              AND o.order_date < '2024-01-01'
              AND o.status = 'completed'
              AND o.region = 'East'
              AND EXISTS (
                  SELECT 1 FROM order_items_opt i
                  WHERE i.order_id = o.order_id
              )
            LIMIT 1
        """)
        columns = [desc[0] for desc in result.description]
        assert columns == ["order_id", "customer_id", "order_date", "total_amount"]


class TestExistsVsJoin:
    """Verify EXISTS produces same results as JOIN + DISTINCT."""

    def test_exists_matches_distinct_join(
        self, db_orders: duckdb.DuckDBPyConnection
    ) -> None:
        """EXISTS returns same order IDs as JOIN + DISTINCT."""
        join_ids = db_orders.execute("""
            SELECT DISTINCT o.order_id
            FROM orders_opt o
            JOIN order_items_opt i ON o.order_id = i.order_id
            WHERE o.status = 'completed'
            ORDER BY o.order_id
        """).fetchall()
        exists_ids = db_orders.execute("""
            SELECT o.order_id
            FROM orders_opt o
            WHERE o.status = 'completed'
              AND EXISTS (
                  SELECT 1 FROM order_items_opt i WHERE i.order_id = o.order_id
              )
            ORDER BY o.order_id
        """).fetchall()
        assert join_ids == exists_ids


class TestSargability:
    """Verify sargable vs non-sargable predicates produce same results."""

    def test_year_function_vs_range(
        self, db_orders: duckdb.DuckDBPyConnection
    ) -> None:
        """YEAR() function and range predicate return same rows."""
        function_result = db_orders.execute("""
            SELECT COUNT(*) FROM orders_opt
            WHERE YEAR(order_date) = 2023
        """).fetchone()
        range_result = db_orders.execute("""
            SELECT COUNT(*) FROM orders_opt
            WHERE order_date >= '2023-01-01' AND order_date < '2024-01-01'
        """).fetchone()
        assert function_result == range_result
