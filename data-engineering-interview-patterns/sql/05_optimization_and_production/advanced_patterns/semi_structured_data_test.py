"""Tests for semi-structured (JSON) data patterns."""

import duckdb
import pytest


@pytest.fixture
def db_json(db: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyConnection:
    """DuckDB with api_responses table containing JSON data."""
    db.execute("""
        CREATE TABLE api_responses (
            request_id INTEGER,
            response_json JSON
        )
    """)
    db.execute("""
        INSERT INTO api_responses VALUES
            (1, '{"status": "success", "data": {"user_id": 100, "items": [{"id": 1, "price": 25.0}, {"id": 2, "price": 50.0}]}}'),
            (2, '{"status": "error", "error_code": 404}'),
            (3, '{"status": "success", "data": {"user_id": 200, "items": [{"id": 3, "price": 75.0}]}}')
    """)
    return db


class TestJsonExtraction:
    """Test extracting scalar values from JSON."""

    def test_extract_top_level_string(
        self, db_json: duckdb.DuckDBPyConnection
    ) -> None:
        """Extract a top-level string field from JSON."""
        result = db_json.execute("""
            SELECT request_id, response_json->>'$.status' AS status
            FROM api_responses
            ORDER BY request_id
        """).fetchall()
        assert result[0] == (1, "success")
        assert result[1] == (2, "error")
        assert result[2] == (3, "success")

    def test_extract_nested_value(
        self, db_json: duckdb.DuckDBPyConnection
    ) -> None:
        """Navigate nested objects to extract a value."""
        result = db_json.execute("""
            SELECT
                request_id,
                response_json->>'$.data.user_id' AS user_id
            FROM api_responses
            WHERE response_json->>'$.status' = 'success'
            ORDER BY request_id
        """).fetchall()
        assert len(result) == 2
        assert result[0] == (1, "100")
        assert result[1] == (3, "200")

    def test_filter_on_json_field(
        self, db_json: duckdb.DuckDBPyConnection
    ) -> None:
        """Filter rows based on a JSON field value."""
        result = db_json.execute("""
            SELECT request_id
            FROM api_responses
            WHERE response_json->>'$.status' = 'error'
        """).fetchall()
        assert len(result) == 1
        assert result[0][0] == 2


class TestJsonArrayFlattening:
    """Test flattening JSON arrays into rows."""

    def test_unnest_json_array(
        self, db_json: duckdb.DuckDBPyConnection
    ) -> None:
        """Flatten a nested JSON array into individual rows."""
        result = db_json.execute("""
            SELECT
                request_id,
                CAST(item->>'$.id' AS INTEGER) AS item_id,
                CAST(item->>'$.price' AS DOUBLE) AS price
            FROM (
                SELECT
                    request_id,
                    unnest(json_extract(response_json, '$.data.items')::JSON[]) AS item
                FROM api_responses
                WHERE response_json->>'$.status' = 'success'
            ) flattened
            ORDER BY request_id, item_id
        """).fetchall()
        assert len(result) == 3
        assert result[0] == (1, 1, 25.0)
        assert result[1] == (1, 2, 50.0)
        assert result[2] == (3, 3, 75.0)

    def test_array_element_count(
        self, db_json: duckdb.DuckDBPyConnection
    ) -> None:
        """Count array elements per request."""
        result = db_json.execute("""
            SELECT
                request_id,
                json_array_length(json_extract(response_json, '$.data.items')) AS item_count
            FROM api_responses
            WHERE response_json->>'$.status' = 'success'
            ORDER BY request_id
        """).fetchall()
        assert result[0] == (1, 2)
        assert result[1] == (3, 1)

    def test_aggregate_over_flattened(
        self, db_json: duckdb.DuckDBPyConnection
    ) -> None:
        """Aggregate values from flattened JSON arrays."""
        result = db_json.execute("""
            SELECT
                response_json->>'$.data.user_id' AS user_id,
                SUM(CAST(item->>'$.price' AS DOUBLE)) AS total_price
            FROM (
                SELECT
                    response_json,
                    unnest(json_extract(response_json, '$.data.items')::JSON[]) AS item
                FROM api_responses
                WHERE response_json->>'$.status' = 'success'
            ) flattened
            GROUP BY response_json->>'$.data.user_id'
            ORDER BY user_id
        """).fetchall()
        assert len(result) == 2
        assert result[0] == ("100", 75.0)   # 25 + 50
        assert result[1] == ("200", 75.0)   # 75
