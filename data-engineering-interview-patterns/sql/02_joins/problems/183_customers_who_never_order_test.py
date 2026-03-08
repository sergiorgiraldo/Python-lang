"""Tests for LeetCode 183: Customers Who Never Order."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


class TestCustomersWhoNeverOrder:

    def test_basic(self, db_customer_orders) -> None:
        db_customer_orders.execute("""
            INSERT INTO Customers (id, name) VALUES
                (1, 'Joe'), (2, 'Henry'), (3, 'Sam'), (4, 'Max');
            INSERT INTO Orders (id, customerId) VALUES
                (1, 3), (2, 1);
        """)
        result = run_sql_file_df(
            db_customer_orders, PROBLEM_DIR / "183_customers_who_never_order.sql"
        )
        names = {r["Customers"] for r in result}
        assert names == {"Henry", "Max"}

    def test_all_have_orders(self, db_customer_orders) -> None:
        db_customer_orders.execute("""
            INSERT INTO Customers (id, name) VALUES (1, 'Joe'), (2, 'Henry');
            INSERT INTO Orders (id, customerId) VALUES (1, 1), (2, 2);
        """)
        result = run_sql_file_df(
            db_customer_orders, PROBLEM_DIR / "183_customers_who_never_order.sql"
        )
        assert len(result) == 0

    def test_none_have_orders(self, db_customer_orders) -> None:
        db_customer_orders.execute("""
            INSERT INTO Customers (id, name) VALUES (1, 'Joe'), (2, 'Henry');
        """)
        result = run_sql_file_df(
            db_customer_orders, PROBLEM_DIR / "183_customers_who_never_order.sql"
        )
        names = {r["Customers"] for r in result}
        assert names == {"Joe", "Henry"}

    def test_multiple_orders_still_excluded(self, db_customer_orders) -> None:
        """Customer with multiple orders should not appear."""
        db_customer_orders.execute("""
            INSERT INTO Customers (id, name) VALUES (1, 'Joe'), (2, 'Henry');
            INSERT INTO Orders (id, customerId) VALUES (1, 1), (2, 1), (3, 1);
        """)
        result = run_sql_file_df(
            db_customer_orders, PROBLEM_DIR / "183_customers_who_never_order.sql"
        )
        names = {r["Customers"] for r in result}
        assert names == {"Henry"}


class TestCustomersWhoNeverOrderAlt:

    def test_basic(self, db_customer_orders) -> None:
        db_customer_orders.execute("""
            INSERT INTO Customers (id, name) VALUES
                (1, 'Joe'), (2, 'Henry'), (3, 'Sam'), (4, 'Max');
            INSERT INTO Orders (id, customerId) VALUES
                (1, 3), (2, 1);
        """)
        result = run_sql_file_df(
            db_customer_orders, PROBLEM_DIR / "183_customers_who_never_order_alt.sql"
        )
        names = {r["Customers"] for r in result}
        assert names == {"Henry", "Max"}

    def test_none_have_orders(self, db_customer_orders) -> None:
        db_customer_orders.execute("""
            INSERT INTO Customers (id, name) VALUES (1, 'Joe'), (2, 'Henry');
        """)
        result = run_sql_file_df(
            db_customer_orders, PROBLEM_DIR / "183_customers_who_never_order_alt.sql"
        )
        names = {r["Customers"] for r in result}
        assert names == {"Joe", "Henry"}
