"""
Tests for mart layer models.

Verifies:
- fct_orders: fact table joins and date dimension extraction
- rpt_daily_revenue: aggregation, cumulative totals, state breakdowns
- rpt_customer_cohorts: cohort sizing and conversion rates
"""

import duckdb
import pytest
from datetime import date


@pytest.fixture
def db():
    conn = duckdb.connect(":memory:")
    yield conn
    conn.close()


# ---- Table schema helpers ----

def _create_stg_tables(db):
    """Create stg_orders and stg_customers schemas."""
    db.execute("""
        CREATE TABLE stg_orders (
            order_id INTEGER, customer_id INTEGER, product_id INTEGER,
            quantity INTEGER, unit_price DECIMAL(10,2),
            order_date DATE, status VARCHAR(20), line_total DECIMAL(10,2)
        )
    """)
    db.execute("""
        CREATE TABLE stg_customers (
            customer_id INTEGER, customer_name VARCHAR(100),
            email VARCHAR(100), city VARCHAR(50),
            state VARCHAR(2), signup_date DATE
        )
    """)


def _create_int_customer_orders_table(db):
    """Create int_customer_orders schema."""
    db.execute("""
        CREATE TABLE int_customer_orders (
            customer_id INTEGER, customer_name VARCHAR(100),
            email VARCHAR(100), city VARCHAR(50), state VARCHAR(2),
            signup_date DATE, total_orders INTEGER,
            completed_orders INTEGER, total_revenue DECIMAL(10,2),
            first_order_date DATE, last_order_date DATE,
            customer_status VARCHAR(20)
        )
    """)


# ---- Model SQL ----

FCT_ORDERS_SQL = """
CREATE TABLE fct_orders AS
SELECT
    o.order_id,
    o.customer_id,
    c.customer_name,
    c.city AS customer_city,
    c.state AS customer_state,
    o.product_id,
    o.quantity,
    o.unit_price,
    o.line_total,
    o.order_date,
    o.status,
    EXTRACT(YEAR FROM o.order_date) AS order_year,
    EXTRACT(MONTH FROM o.order_date) AS order_month,
    EXTRACT(DOW FROM o.order_date) AS order_day_of_week
FROM stg_orders o
LEFT JOIN stg_customers c ON o.customer_id = c.customer_id
"""

RPT_DAILY_REVENUE_SQL = """
CREATE TABLE rpt_daily_revenue AS
WITH orders AS (
    SELECT * FROM fct_orders WHERE status = 'completed'
),
daily_revenue AS (
    SELECT
        order_date,
        COUNT(*) AS order_count,
        COUNT(DISTINCT customer_id) AS unique_customers,
        SUM(line_total) AS total_revenue,
        AVG(line_total) AS avg_order_value,
        SUM(CASE WHEN customer_state = 'OR' THEN line_total ELSE 0 END) AS revenue_oregon,
        SUM(CASE WHEN customer_state = 'WA' THEN line_total ELSE 0 END) AS revenue_washington,
        SUM(CASE WHEN customer_state = 'CA' THEN line_total ELSE 0 END) AS revenue_california
    FROM orders
    GROUP BY order_date
)
SELECT *,
    SUM(total_revenue) OVER (ORDER BY order_date ROWS UNBOUNDED PRECEDING) AS cumulative_revenue
FROM daily_revenue
"""

RPT_CUSTOMER_COHORTS_SQL = """
CREATE TABLE rpt_customer_cohorts AS
WITH cohorts AS (
    SELECT
        DATE_TRUNC('month', signup_date) AS cohort_month,
        COUNT(*) AS cohort_size,
        COUNT(CASE WHEN total_orders > 0 THEN 1 END) AS customers_with_orders,
        SUM(total_revenue) AS cohort_revenue,
        AVG(total_orders) AS avg_orders_per_customer,
        AVG(total_revenue) AS avg_revenue_per_customer
    FROM int_customer_orders
    GROUP BY DATE_TRUNC('month', signup_date)
)
SELECT *,
    ROUND(100.0 * customers_with_orders / cohort_size, 1) AS conversion_rate_pct
FROM cohorts
"""


# ============================================================
# fct_orders tests
# ============================================================

class TestFctOrders:
    def test_orders_joined_with_customers(self, db):
        """All orders present with customer attributes joined."""
        _create_stg_tables(db)
        db.execute("""
            INSERT INTO stg_customers VALUES
            (100, 'Alice Smith', 'alice@x.com', 'Portland', 'OR', '2023-06-01'),
            (101, 'Bob Johnson', 'bob@x.com', 'Seattle', 'WA', '2023-07-15')
        """)
        db.execute("""
            INSERT INTO stg_orders VALUES
            (1, 100, 10, 2, 25.00, '2024-01-15', 'completed', 50.00),
            (2, 101, 11, 1, 50.00, '2024-01-15', 'completed', 50.00),
            (3, 100, 12, 1, 15.00, '2024-01-16', 'pending', 15.00)
        """)
        db.execute(FCT_ORDERS_SQL)
        count = db.execute("SELECT COUNT(*) FROM fct_orders").fetchone()[0]
        assert count == 3
        # Verify customer attributes are joined
        result = db.execute("""
            SELECT customer_name, customer_city, customer_state
            FROM fct_orders WHERE order_id = 1
        """).fetchone()
        assert result == ('Alice Smith', 'Portland', 'OR')

    def test_no_orders_customer_excluded(self, db):
        """Customer without orders does not appear in the fact table."""
        _create_stg_tables(db)
        db.execute("""
            INSERT INTO stg_customers VALUES
            (100, 'Alice', 'alice@x.com', 'Portland', 'OR', '2023-06-01'),
            (105, 'Frank', 'frank@x.com', 'Denver', 'CO', '2024-01-15')
        """)
        db.execute("""
            INSERT INTO stg_orders VALUES
            (1, 100, 10, 1, 25.00, '2024-01-15', 'completed', 25.00)
        """)
        db.execute(FCT_ORDERS_SQL)
        # Customer 105 exists in staging but has no orders
        in_staging = db.execute(
            "SELECT COUNT(*) FROM stg_customers WHERE customer_id = 105"
        ).fetchone()[0]
        assert in_staging == 1
        in_fact = db.execute(
            "SELECT COUNT(*) FROM fct_orders WHERE customer_id = 105"
        ).fetchone()[0]
        assert in_fact == 0

    def test_date_dimensions(self, db):
        """Date dimension fields extracted correctly from order_date."""
        _create_stg_tables(db)
        db.execute("""
            INSERT INTO stg_customers VALUES
            (100, 'Alice', 'alice@x.com', 'Portland', 'OR', '2023-06-01')
        """)
        db.execute("""
            INSERT INTO stg_orders VALUES
            (1, 100, 10, 1, 25.00, '2024-01-15', 'completed', 25.00)
        """)
        db.execute(FCT_ORDERS_SQL)
        result = db.execute("""
            SELECT order_year, order_month, order_day_of_week
            FROM fct_orders WHERE order_id = 1
        """).fetchone()
        assert result[0] == 2024
        assert result[1] == 1    # January
        assert result[2] == 1    # Monday (DOW: Sun=0, Mon=1, ..., Sat=6)


# ============================================================
# rpt_daily_revenue tests
# ============================================================

class TestRptDailyRevenue:
    def _setup_revenue_data(self, db):
        """Standard dataset for daily revenue tests."""
        _create_stg_tables(db)
        db.execute("""
            INSERT INTO stg_customers VALUES
            (100, 'Alice', 'alice@x.com', 'Portland', 'OR', '2023-06-01'),
            (101, 'Bob', 'bob@x.com', 'Seattle', 'WA', '2023-07-15'),
            (103, 'Dave', 'dave@x.com', 'San Francisco', 'CA', '2023-09-10')
        """)
        db.execute("""
            INSERT INTO stg_orders VALUES
            (1, 100, 10, 2, 25.00, '2024-01-15', 'completed', 50.00),
            (2, 101, 11, 1, 50.00, '2024-01-15', 'completed', 50.00),
            (3, 100, 12, 3, 15.00, '2024-01-16', 'completed', 45.00),
            (4, 100, 10, 1, 25.00, '2024-01-16', 'pending', 25.00),
            (5, 103, 10, 5, 25.00, '2024-01-17', 'completed', 125.00),
            (6, 100, 11, 1, 50.00, '2024-01-17', 'cancelled', 50.00)
        """)
        db.execute(FCT_ORDERS_SQL)
        db.execute(RPT_DAILY_REVENUE_SQL)

    def test_only_completed_counted(self, db):
        """Pending and cancelled orders are excluded from revenue."""
        self._setup_revenue_data(db)
        # 6 total orders, but only 4 completed across 3 days
        total_counted = db.execute(
            "SELECT SUM(order_count) FROM rpt_daily_revenue"
        ).fetchone()[0]
        assert total_counted == 4

    def test_daily_totals(self, db):
        """Daily revenue totals are correct."""
        self._setup_revenue_data(db)
        result = db.execute("""
            SELECT order_date, order_count, total_revenue
            FROM rpt_daily_revenue ORDER BY order_date
        """).fetchall()
        # Day 1: Alice (50) + Bob (50) = 100
        assert result[0][1] == 2
        assert result[0][2] == 100.00
        # Day 2: Alice (45) only (pending excluded)
        assert result[1][1] == 1
        assert result[1][2] == 45.00
        # Day 3: Dave (125) only (cancelled excluded)
        assert result[2][1] == 1
        assert result[2][2] == 125.00

    def test_cumulative_revenue_monotonic(self, db):
        """Cumulative revenue never decreases across days."""
        self._setup_revenue_data(db)
        result = db.execute("""
            SELECT cumulative_revenue FROM rpt_daily_revenue
            ORDER BY order_date
        """).fetchall()
        values = [r[0] for r in result]
        assert len(values) == 3
        for i in range(1, len(values)):
            assert values[i] >= values[i - 1]
        # Verify final cumulative = sum of all daily totals
        assert values[-1] == 270.00

    def test_state_revenue_breakdown(self, db):
        """State columns correctly break down revenue by customer state."""
        self._setup_revenue_data(db)
        result = db.execute("""
            SELECT total_revenue, revenue_oregon, revenue_washington, revenue_california
            FROM rpt_daily_revenue WHERE order_date = '2024-01-15'
        """).fetchone()
        assert result[0] == 100.00   # total
        assert result[1] == 50.00    # Oregon (Alice)
        assert result[2] == 50.00    # Washington (Bob)
        assert result[3] == 0        # California


# ============================================================
# rpt_customer_cohorts tests
# ============================================================

class TestRptCustomerCohorts:
    def test_cohort_size(self, db):
        """Cohort size matches number of customers in that signup month."""
        _create_int_customer_orders_table(db)
        db.execute("""
            INSERT INTO int_customer_orders VALUES
            (100, 'Alice', 'a@x.com', 'Portland', 'OR', '2023-06-01',
             3, 2, 120.00, '2024-01-15', '2024-01-22', 'churned'),
            (101, 'Bob', 'b@x.com', 'Seattle', 'WA', '2023-06-20',
             2, 2, 110.00, '2024-01-15', '2024-01-18', 'churned'),
            (102, 'Carol', 'c@x.com', 'Portland', 'OR', '2023-08-10',
             1, 1, 30.00, '2024-01-20', '2024-01-20', 'churned')
        """)
        db.execute(RPT_CUSTOMER_COHORTS_SQL)
        result = db.execute("""
            SELECT cohort_size FROM rpt_customer_cohorts
            WHERE cohort_month = '2023-06-01'
        """).fetchone()
        assert result[0] == 2
        result_aug = db.execute("""
            SELECT cohort_size FROM rpt_customer_cohorts
            WHERE cohort_month = '2023-08-01'
        """).fetchone()
        assert result_aug[0] == 1

    def test_conversion_rate(self, db):
        """Conversion rate = customers_with_orders / cohort_size * 100."""
        _create_int_customer_orders_table(db)
        db.execute("""
            INSERT INTO int_customer_orders VALUES
            (100, 'Alice', 'a@x.com', 'Portland', 'OR', '2024-01-05',
             2, 2, 80.00, '2024-01-15', '2024-01-18', 'churned'),
            (101, 'Bob', 'b@x.com', 'Seattle', 'WA', '2024-01-10',
             0, 0, 0, NULL, NULL, 'never_ordered')
        """)
        db.execute(RPT_CUSTOMER_COHORTS_SQL)
        result = db.execute("""
            SELECT cohort_size, customers_with_orders, conversion_rate_pct
            FROM rpt_customer_cohorts WHERE cohort_month = '2024-01-01'
        """).fetchone()
        assert result[0] == 2     # cohort_size
        assert result[1] == 1     # customers_with_orders
        assert result[2] == 50.0  # 1/2 * 100

    def test_zero_order_customers_in_cohort(self, db):
        """Customers with no orders are counted in cohort_size."""
        _create_int_customer_orders_table(db)
        db.execute("""
            INSERT INTO int_customer_orders VALUES
            (200, 'X', 'x@x.com', 'A', 'XX', '2024-02-01',
             0, 0, 0, NULL, NULL, 'never_ordered'),
            (201, 'Y', 'y@x.com', 'B', 'XX', '2024-02-15',
             0, 0, 0, NULL, NULL, 'never_ordered')
        """)
        db.execute(RPT_CUSTOMER_COHORTS_SQL)
        result = db.execute("""
            SELECT cohort_size, customers_with_orders, conversion_rate_pct
            FROM rpt_customer_cohorts WHERE cohort_month = '2024-02-01'
        """).fetchone()
        assert result[0] == 2     # both counted
        assert result[1] == 0     # neither has orders
        assert result[2] == 0.0   # 0% conversion
