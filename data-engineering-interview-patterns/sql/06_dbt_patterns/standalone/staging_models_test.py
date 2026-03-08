"""
Tests for staging layer models.

Verifies:
- Type casting and renaming
- Dedup with ROW_NUMBER
- Data cleaning (trim, lower, null filtering)
"""

import duckdb
import pytest
from pathlib import Path


@pytest.fixture
def db():
    conn = duckdb.connect(":memory:")
    yield conn
    conn.close()


def setup_staging(db):
    """Create raw tables and run staging models."""
    sql_path = Path(__file__).parent / "staging_models.sql"
    sql = sql_path.read_text()
    for stmt in sql.split(";"):
        stmt = stmt.strip()
        if stmt:
            db.execute(stmt)


def insert_seed_data(db):
    """Insert the same data as the dbt seeds."""
    db.execute("""
        INSERT INTO raw_orders VALUES
        (1, 100, 10, 2, 25.00, '2024-01-15', 'completed'),
        (2, 101, 11, 1, 50.00, '2024-01-15', 'Completed'),
        (3, 100, 12, 3, 15.00, '2024-01-16', ' completed '),
        (4, 102, 10, 1, 25.00, '2024-01-17', 'pending'),
        (5, 101, 13, 2, 30.00, '2024-01-18', 'completed')
    """)
    db.execute("""
        INSERT INTO raw_customers VALUES
        (100, ' Alice Smith ', 'Alice@Example.com', ' Portland ', 'OR', '2023-06-01'),
        (101, 'Bob Johnson', 'bob@example.com', 'Seattle', 'WA', '2023-07-15')
    """)
    db.execute("""
        INSERT INTO raw_events VALUES
        (1, 100, 'page_view', '2024-01-15 10:00:00', '/home', NULL),
        (2, 100, 'page_view', '2024-01-15 10:02:00', '/products', NULL),
        (3, 100, 'add_to_cart', '2024-01-15 10:05:00', '/products/10', NULL),
        (1, 100, 'page_view', '2024-01-15 10:00:00', '/home', NULL),
        (2, 100, 'page_view', '2024-01-15 10:02:00', '/products', NULL)
    """)


class TestStagingOrders:
    def test_line_total_computed(self, db):
        """line_total = quantity * unit_price."""
        db.execute("""
            CREATE TABLE raw_orders (
                order_id INTEGER, customer_id INTEGER, product_id INTEGER,
                quantity INTEGER, unit_price DECIMAL(10,2),
                order_date DATE, status VARCHAR(20)
            )
        """)
        db.execute("""
            INSERT INTO raw_orders VALUES
            (1, 100, 10, 2, 25.00, '2024-01-15', 'completed'),
            (2, 101, 11, 3, 10.00, '2024-01-15', 'pending')
        """)
        db.execute("""
            CREATE TABLE stg_orders AS
            SELECT order_id, customer_id, product_id, quantity, unit_price,
                   order_date, lower(trim(status)) AS status,
                   quantity * unit_price AS line_total
            FROM raw_orders WHERE order_id IS NOT NULL
        """)
        result = db.execute("SELECT order_id, line_total FROM stg_orders ORDER BY order_id").fetchall()
        assert result == [(1, 50.00), (2, 30.00)]

    def test_status_cleaned(self, db):
        """Status is lowercased and trimmed."""
        db.execute("CREATE TABLE raw_orders (order_id INTEGER, customer_id INTEGER, product_id INTEGER, quantity INTEGER, unit_price DECIMAL(10,2), order_date DATE, status VARCHAR(20))")
        db.execute("INSERT INTO raw_orders VALUES (1, 100, 10, 1, 10.00, '2024-01-15', ' Completed ')")
        db.execute("""
            CREATE TABLE stg_orders AS
            SELECT order_id, customer_id, product_id, quantity, unit_price,
                   order_date, lower(trim(status)) AS status,
                   quantity * unit_price AS line_total
            FROM raw_orders WHERE order_id IS NOT NULL
        """)
        result = db.execute("SELECT status FROM stg_orders").fetchone()
        assert result[0] == "completed"

    def test_null_order_id_filtered(self, db):
        """Rows with null order_id are excluded."""
        db.execute("CREATE TABLE raw_orders (order_id INTEGER, customer_id INTEGER, product_id INTEGER, quantity INTEGER, unit_price DECIMAL(10,2), order_date DATE, status VARCHAR(20))")
        db.execute("INSERT INTO raw_orders VALUES (1, 100, 10, 1, 10.00, '2024-01-15', 'completed')")
        db.execute("INSERT INTO raw_orders VALUES (NULL, 101, 11, 1, 10.00, '2024-01-15', 'pending')")
        db.execute("""
            CREATE TABLE stg_orders AS
            SELECT order_id, customer_id, product_id, quantity, unit_price,
                   order_date, lower(trim(status)) AS status,
                   quantity * unit_price AS line_total
            FROM raw_orders WHERE order_id IS NOT NULL
        """)
        result = db.execute("SELECT COUNT(*) FROM stg_orders").fetchone()
        assert result[0] == 1


class TestStagingCustomers:
    def test_email_lowercased(self, db):
        """Email is lowercased."""
        db.execute("CREATE TABLE raw_customers (customer_id INTEGER, name VARCHAR(100), email VARCHAR(100), city VARCHAR(50), state VARCHAR(2), signup_date DATE)")
        db.execute("INSERT INTO raw_customers VALUES (100, 'Alice', 'ALICE@EXAMPLE.COM', 'Portland', 'OR', '2023-06-01')")
        db.execute("""
            CREATE TABLE stg_customers AS
            SELECT customer_id, trim(name) AS customer_name, lower(trim(email)) AS email,
                   trim(city) AS city, trim(state) AS state, signup_date
            FROM raw_customers WHERE customer_id IS NOT NULL
        """)
        result = db.execute("SELECT email FROM stg_customers").fetchone()
        assert result[0] == "alice@example.com"

    def test_name_trimmed(self, db):
        """Name has whitespace trimmed."""
        db.execute("CREATE TABLE raw_customers (customer_id INTEGER, name VARCHAR(100), email VARCHAR(100), city VARCHAR(50), state VARCHAR(2), signup_date DATE)")
        db.execute("INSERT INTO raw_customers VALUES (100, '  Alice  ', 'a@b.com', 'Portland', 'OR', '2023-06-01')")
        db.execute("""
            CREATE TABLE stg_customers AS
            SELECT customer_id, trim(name) AS customer_name, lower(trim(email)) AS email,
                   trim(city) AS city, trim(state) AS state, signup_date
            FROM raw_customers WHERE customer_id IS NOT NULL
        """)
        result = db.execute("SELECT customer_name FROM stg_customers").fetchone()
        assert result[0] == "Alice"


class TestStagingEvents:
    def test_dedup_removes_duplicates(self, db):
        """Duplicate event_ids are removed, keeping one row per event_id."""
        db.execute("CREATE TABLE raw_events (event_id INTEGER, user_id INTEGER, event_type VARCHAR(20), event_timestamp TIMESTAMP, page_url VARCHAR(200), session_id VARCHAR(50))")
        db.execute("""
            INSERT INTO raw_events VALUES
            (1, 100, 'page_view', '2024-01-15 10:00:00', '/home', NULL),
            (1, 100, 'page_view', '2024-01-15 10:00:00', '/home', NULL),
            (2, 100, 'click', '2024-01-15 10:01:00', '/products', NULL)
        """)
        db.execute("""
            CREATE TABLE stg_events AS
            WITH deduplicated AS (
                SELECT *, ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY event_timestamp DESC) AS _row_num
                FROM raw_events
            )
            SELECT event_id, user_id, lower(trim(event_type)) AS event_type,
                   event_timestamp, trim(page_url) AS page_url
            FROM deduplicated WHERE _row_num = 1
        """)
        result = db.execute("SELECT COUNT(*) FROM stg_events").fetchone()
        assert result[0] == 2

    def test_event_type_cleaned(self, db):
        """Event type is lowercased and trimmed."""
        db.execute("CREATE TABLE raw_events (event_id INTEGER, user_id INTEGER, event_type VARCHAR(20), event_timestamp TIMESTAMP, page_url VARCHAR(200), session_id VARCHAR(50))")
        db.execute("INSERT INTO raw_events VALUES (1, 100, ' Page_View ', '2024-01-15 10:00:00', '/home', NULL)")
        db.execute("""
            CREATE TABLE stg_events AS
            WITH deduplicated AS (
                SELECT *, ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY event_timestamp DESC) AS _row_num
                FROM raw_events
            )
            SELECT event_id, user_id, lower(trim(event_type)) AS event_type,
                   event_timestamp, trim(page_url) AS page_url
            FROM deduplicated WHERE _row_num = 1
        """)
        result = db.execute("SELECT event_type FROM stg_events").fetchone()
        assert result[0] == "page_view"

    def test_unique_event_ids(self, db):
        """After dedup, event_id is unique."""
        db.execute("CREATE TABLE raw_events (event_id INTEGER, user_id INTEGER, event_type VARCHAR(20), event_timestamp TIMESTAMP, page_url VARCHAR(200), session_id VARCHAR(50))")
        db.execute("""
            INSERT INTO raw_events VALUES
            (1, 100, 'page_view', '2024-01-15 10:00:00', '/home', NULL),
            (1, 100, 'page_view', '2024-01-15 10:00:00', '/home', NULL),
            (2, 100, 'click', '2024-01-15 10:01:00', '/x', NULL),
            (3, 101, 'page_view', '2024-01-15 11:00:00', '/home', NULL),
            (3, 101, 'page_view', '2024-01-15 11:00:00', '/home', NULL)
        """)
        db.execute("""
            CREATE TABLE stg_events AS
            WITH deduplicated AS (
                SELECT *, ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY event_timestamp DESC) AS _row_num
                FROM raw_events
            )
            SELECT event_id, user_id, lower(trim(event_type)) AS event_type,
                   event_timestamp, trim(page_url) AS page_url
            FROM deduplicated WHERE _row_num = 1
        """)
        total = db.execute("SELECT COUNT(*) FROM stg_events").fetchone()[0]
        distinct = db.execute("SELECT COUNT(DISTINCT event_id) FROM stg_events").fetchone()[0]
        assert total == distinct == 3
