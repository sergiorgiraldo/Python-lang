"""
Tests for intermediate layer models.

Verifies:
- Sessionization via LAG + gap detection
- Customer order aggregation with LEFT JOIN
- SCD Type 2 dimension building
"""

import duckdb
import pytest
from datetime import date


@pytest.fixture
def db():
    conn = duckdb.connect(":memory:")
    yield conn
    conn.close()


# ---- Sessionization helpers ----

SESSIONIZATION_SQL = """
CREATE TABLE int_deduped_events AS
WITH with_prev_timestamp AS (
    SELECT *,
        LAG(event_timestamp) OVER (
            PARTITION BY user_id ORDER BY event_timestamp
        ) AS prev_event_timestamp
    FROM stg_events
),
with_session_boundary AS (
    SELECT *,
        CASE
            WHEN prev_event_timestamp IS NULL THEN 1
            WHEN EXTRACT(EPOCH FROM event_timestamp - prev_event_timestamp) > 1800 THEN 1
            ELSE 0
        END AS is_new_session
    FROM with_prev_timestamp
),
with_session_id AS (
    SELECT event_id, user_id, event_type, event_timestamp, page_url,
        SUM(is_new_session) OVER (
            PARTITION BY user_id ORDER BY event_timestamp
            ROWS UNBOUNDED PRECEDING
        ) AS session_number
    FROM with_session_boundary
)
SELECT *, user_id || '-' || session_number AS session_id
FROM with_session_id
"""


def _create_events_table(db):
    db.execute("""
        CREATE TABLE stg_events (
            event_id INTEGER,
            user_id INTEGER,
            event_type VARCHAR(20),
            event_timestamp TIMESTAMP,
            page_url VARCHAR(200)
        )
    """)


# ---- Customer orders helpers ----

CUSTOMER_ORDERS_SQL = """
CREATE TABLE int_customer_orders AS
WITH order_summary AS (
    SELECT
        customer_id,
        COUNT(*) AS total_orders,
        COUNT(CASE WHEN status = 'completed' THEN 1 END) AS completed_orders,
        SUM(CASE WHEN status = 'completed' THEN line_total ELSE 0 END) AS total_revenue,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date
    FROM stg_orders
    GROUP BY customer_id
)
SELECT
    c.customer_id,
    c.customer_name,
    c.email,
    c.city,
    c.state,
    c.signup_date,
    COALESCE(o.total_orders, 0) AS total_orders,
    COALESCE(o.completed_orders, 0) AS completed_orders,
    COALESCE(o.total_revenue, 0) AS total_revenue,
    o.first_order_date,
    o.last_order_date,
    CASE
        WHEN o.total_orders IS NULL THEN 'never_ordered'
        WHEN o.last_order_date >= current_date - INTERVAL '30' DAY THEN 'active'
        WHEN o.last_order_date >= current_date - INTERVAL '90' DAY THEN 'lapsing'
        ELSE 'churned'
    END AS customer_status
FROM stg_customers c
LEFT JOIN order_summary o ON c.customer_id = o.customer_id
"""


def _create_customer_orders_tables(db):
    db.execute("""
        CREATE TABLE stg_customers (
            customer_id INTEGER,
            customer_name VARCHAR(100),
            email VARCHAR(100),
            city VARCHAR(50),
            state VARCHAR(2),
            signup_date DATE
        )
    """)
    db.execute("""
        CREATE TABLE stg_orders (
            order_id INTEGER,
            customer_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            unit_price DECIMAL(10,2),
            order_date DATE,
            status VARCHAR(20),
            line_total DECIMAL(10,2)
        )
    """)


# ---- SCD Type 2 helpers ----

SCD2_SQL = """
CREATE TABLE int_customers_scd2 AS
WITH with_row_number AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id ORDER BY effective_date
        ) AS version_number,
        LEAD(effective_date) OVER (
            PARTITION BY customer_id ORDER BY effective_date
        ) AS next_effective_date
    FROM raw_customer_history
)
SELECT
    customer_id,
    name AS customer_name,
    email,
    city,
    state,
    effective_date,
    COALESCE(
        next_effective_date - INTERVAL '1' DAY,
        CAST('9999-12-31' AS DATE)
    ) AS expiry_date,
    CASE
        WHEN next_effective_date IS NULL THEN true
        ELSE false
    END AS is_current,
    version_number
FROM with_row_number
"""


def _create_customer_history_table(db):
    db.execute("""
        CREATE TABLE raw_customer_history (
            customer_id INTEGER,
            name VARCHAR(100),
            email VARCHAR(100),
            city VARCHAR(50),
            state VARCHAR(2),
            effective_date DATE
        )
    """)


# ============================================================
# Sessionization tests
# ============================================================

class TestSessionization:
    def test_same_session_within_30_min(self, db):
        """Events within 30 minutes get the same session_id."""
        _create_events_table(db)
        db.execute("""
            INSERT INTO stg_events VALUES
            (1, 100, 'page_view', '2024-01-15 10:00:00', '/home'),
            (2, 100, 'page_view', '2024-01-15 10:02:00', '/products'),
            (3, 100, 'add_to_cart', '2024-01-15 10:05:00', '/products/10')
        """)
        db.execute(SESSIONIZATION_SQL)
        result = db.execute("""
            SELECT DISTINCT session_id FROM int_deduped_events
            WHERE user_id = 100
        """).fetchall()
        assert len(result) == 1
        assert result[0][0] == '100-1'

    def test_new_session_after_30_min_gap(self, db):
        """Events more than 30 minutes apart get different session_ids."""
        _create_events_table(db)
        db.execute("""
            INSERT INTO stg_events VALUES
            (1, 100, 'page_view', '2024-01-15 10:00:00', '/home'),
            (2, 100, 'page_view', '2024-01-15 10:05:00', '/products'),
            (3, 100, 'page_view', '2024-01-15 14:00:00', '/home')
        """)
        db.execute(SESSIONIZATION_SQL)
        result = db.execute("""
            SELECT event_id, session_id FROM int_deduped_events
            ORDER BY event_timestamp
        """).fetchall()
        assert result[0][1] == '100-1'
        assert result[1][1] == '100-1'
        assert result[2][1] == '100-2'

    def test_independent_user_sessions(self, db):
        """Different users have independent session numbering."""
        _create_events_table(db)
        db.execute("""
            INSERT INTO stg_events VALUES
            (1, 100, 'page_view', '2024-01-15 10:00:00', '/home'),
            (2, 101, 'page_view', '2024-01-15 10:00:00', '/home'),
            (3, 100, 'page_view', '2024-01-15 14:00:00', '/products'),
            (4, 101, 'page_view', '2024-01-15 14:00:00', '/products')
        """)
        db.execute(SESSIONIZATION_SQL)
        sessions_100 = db.execute("""
            SELECT DISTINCT session_number FROM int_deduped_events
            WHERE user_id = 100 ORDER BY session_number
        """).fetchall()
        sessions_101 = db.execute("""
            SELECT DISTINCT session_number FROM int_deduped_events
            WHERE user_id = 101 ORDER BY session_number
        """).fetchall()
        # Both users should independently have sessions 1 and 2
        assert [r[0] for r in sessions_100] == [1, 2]
        assert [r[0] for r in sessions_101] == [1, 2]

    def test_first_event_starts_session(self, db):
        """First event per user always starts a new session (session 1)."""
        _create_events_table(db)
        db.execute("""
            INSERT INTO stg_events VALUES
            (1, 100, 'page_view', '2024-01-15 10:00:00', '/home'),
            (2, 101, 'page_view', '2024-01-15 11:00:00', '/home')
        """)
        db.execute(SESSIONIZATION_SQL)
        result = db.execute("""
            SELECT user_id, session_number FROM int_deduped_events
            ORDER BY user_id
        """).fetchall()
        assert result[0] == (100, 1)
        assert result[1] == (101, 1)

    def test_session_id_format(self, db):
        """Session IDs are formatted as 'user_id-session_number'."""
        _create_events_table(db)
        db.execute("""
            INSERT INTO stg_events VALUES
            (1, 200, 'page_view', '2024-01-15 10:00:00', '/home'),
            (2, 200, 'page_view', '2024-01-15 14:00:00', '/products')
        """)
        db.execute(SESSIONIZATION_SQL)
        result = db.execute("""
            SELECT session_id FROM int_deduped_events
            ORDER BY event_timestamp
        """).fetchall()
        assert result[0][0] == '200-1'
        assert result[1][0] == '200-2'


# ============================================================
# Customer orders tests
# ============================================================

class TestCustomerOrders:
    def test_order_totals_correct(self, db):
        """Customer with orders has correct counts and revenue."""
        _create_customer_orders_tables(db)
        db.execute("""
            INSERT INTO stg_customers VALUES
            (100, 'Alice Smith', 'alice@example.com', 'Portland', 'OR', '2023-06-01')
        """)
        db.execute("""
            INSERT INTO stg_orders VALUES
            (1, 100, 10, 2, 25.00, current_date, 'completed', 50.00),
            (2, 100, 11, 1, 50.00, current_date, 'completed', 50.00),
            (3, 100, 12, 1, 30.00, current_date, 'cancelled', 30.00)
        """)
        db.execute(CUSTOMER_ORDERS_SQL)
        result = db.execute("""
            SELECT total_orders, completed_orders, total_revenue
            FROM int_customer_orders WHERE customer_id = 100
        """).fetchone()
        assert result == (3, 2, 100.00)

    def test_customer_without_orders(self, db):
        """Customer with no orders is preserved via LEFT JOIN with zeros."""
        _create_customer_orders_tables(db)
        db.execute("""
            INSERT INTO stg_customers VALUES
            (100, 'Alice', 'alice@example.com', 'Portland', 'OR', '2023-06-01'),
            (200, 'No Orders', 'noorders@example.com', 'Denver', 'CO', '2024-01-01')
        """)
        db.execute("""
            INSERT INTO stg_orders VALUES
            (1, 100, 10, 1, 25.00, current_date, 'completed', 25.00)
        """)
        db.execute(CUSTOMER_ORDERS_SQL)
        result = db.execute("""
            SELECT total_orders, completed_orders, total_revenue
            FROM int_customer_orders WHERE customer_id = 200
        """).fetchone()
        assert result == (0, 0, 0)

    def test_only_completed_count_as_revenue(self, db):
        """Only completed orders count toward revenue."""
        _create_customer_orders_tables(db)
        db.execute("""
            INSERT INTO stg_customers VALUES
            (100, 'Alice', 'alice@example.com', 'Portland', 'OR', '2023-06-01')
        """)
        db.execute("""
            INSERT INTO stg_orders VALUES
            (1, 100, 10, 1, 25.00, current_date, 'completed', 25.00),
            (2, 100, 11, 1, 50.00, current_date, 'pending', 50.00),
            (3, 100, 12, 1, 30.00, current_date, 'cancelled', 30.00)
        """)
        db.execute(CUSTOMER_ORDERS_SQL)
        result = db.execute("""
            SELECT total_revenue, completed_orders
            FROM int_customer_orders WHERE customer_id = 100
        """).fetchone()
        assert result[0] == 25.00
        assert result[1] == 1

    def test_customer_status_classification(self, db):
        """Customer status is based on recency of last order."""
        _create_customer_orders_tables(db)
        db.execute("""
            INSERT INTO stg_customers VALUES
            (200, 'Never', 'never@x.com', 'X', 'XX', '2023-01-01'),
            (201, 'Active', 'active@x.com', 'X', 'XX', '2023-01-01'),
            (202, 'Lapsing', 'lapsing@x.com', 'X', 'XX', '2023-01-01'),
            (203, 'Churned', 'churned@x.com', 'X', 'XX', '2023-01-01')
        """)
        db.execute("""
            INSERT INTO stg_orders
            SELECT 1, 201, 10, 1, 25.00, current_date, 'completed', 25.00
            UNION ALL
            SELECT 2, 202, 10, 1, 25.00,
                   CAST(current_date - INTERVAL '60 days' AS DATE), 'completed', 25.00
            UNION ALL
            SELECT 3, 203, 10, 1, 25.00,
                   CAST(current_date - INTERVAL '120 days' AS DATE), 'completed', 25.00
        """)
        db.execute(CUSTOMER_ORDERS_SQL)
        result = db.execute("""
            SELECT customer_id, customer_status
            FROM int_customer_orders ORDER BY customer_id
        """).fetchall()
        status_map = {r[0]: r[1] for r in result}
        assert status_map[200] == 'never_ordered'
        assert status_map[201] == 'active'
        assert status_map[202] == 'lapsing'
        assert status_map[203] == 'churned'


# ============================================================
# SCD Type 2 tests
# ============================================================

class TestSCD2:
    def test_multiple_versions_per_customer(self, db):
        """Customer with 2 address changes has 2 rows."""
        _create_customer_history_table(db)
        db.execute("""
            INSERT INTO raw_customer_history VALUES
            (100, 'Alice', 'alice@example.com', 'Eugene', 'OR', '2023-06-01'),
            (100, 'Alice', 'alice@example.com', 'Portland', 'OR', '2023-09-15'),
            (101, 'Bob', 'bob@example.com', 'Seattle', 'WA', '2023-07-15')
        """)
        db.execute(SCD2_SQL)
        count_100 = db.execute(
            "SELECT COUNT(*) FROM int_customers_scd2 WHERE customer_id = 100"
        ).fetchone()[0]
        count_101 = db.execute(
            "SELECT COUNT(*) FROM int_customers_scd2 WHERE customer_id = 101"
        ).fetchone()[0]
        assert count_100 == 2
        assert count_101 == 1

    def test_only_latest_is_current(self, db):
        """Only the latest version per customer has is_current = true."""
        _create_customer_history_table(db)
        db.execute("""
            INSERT INTO raw_customer_history VALUES
            (100, 'Alice', 'alice@example.com', 'Eugene', 'OR', '2023-06-01'),
            (100, 'Alice', 'alice@example.com', 'Portland', 'OR', '2023-09-15')
        """)
        db.execute(SCD2_SQL)
        result = db.execute("""
            SELECT city, is_current FROM int_customers_scd2
            WHERE customer_id = 100 ORDER BY effective_date
        """).fetchall()
        assert result[0] == ('Eugene', False)
        assert result[1] == ('Portland', True)

    def test_expiry_dates_chain(self, db):
        """Version N expiry = version N+1 effective_date - 1 day."""
        _create_customer_history_table(db)
        db.execute("""
            INSERT INTO raw_customer_history VALUES
            (100, 'Alice', 'alice@example.com', 'Eugene', 'OR', '2023-06-01'),
            (100, 'Alice', 'alice@example.com', 'Portland', 'OR', '2023-09-15')
        """)
        db.execute(SCD2_SQL)
        result = db.execute("""
            SELECT CAST(expiry_date AS DATE) FROM int_customers_scd2
            WHERE customer_id = 100 AND version_number = 1
        """).fetchone()
        assert result[0] == date(2023, 9, 14)

    def test_latest_expiry_is_9999(self, db):
        """Latest version has expiry_date = 9999-12-31."""
        _create_customer_history_table(db)
        db.execute("""
            INSERT INTO raw_customer_history VALUES
            (100, 'Alice', 'alice@example.com', 'Eugene', 'OR', '2023-06-01'),
            (100, 'Alice', 'alice@example.com', 'Portland', 'OR', '2023-09-15')
        """)
        db.execute(SCD2_SQL)
        result = db.execute("""
            SELECT CAST(expiry_date AS DATE) FROM int_customers_scd2
            WHERE customer_id = 100 AND is_current = true
        """).fetchone()
        assert result[0] == date(9999, 12, 31)
