/*
Working with JSON and nested data in SQL.
DuckDB has strong JSON support with arrow operators and type casting.

Key operations:
1. Extract a scalar value from JSON
2. Navigate nested objects
3. Flatten/unnest a JSON array
4. Filter on a JSON field
*/

CREATE TABLE api_responses (
    request_id INTEGER,
    response_json JSON
);

INSERT INTO api_responses VALUES
    (1, '{"status": "success", "data": {"user_id": 100, "items": [{"id": 1, "price": 25.0}, {"id": 2, "price": 50.0}]}}'),
    (2, '{"status": "error", "error_code": 404}'),
    (3, '{"status": "success", "data": {"user_id": 200, "items": [{"id": 3, "price": 75.0}]}}');

-- 1. Extract scalar values using ->> (returns VARCHAR)
SELECT
    request_id,
    response_json->>'$.status' AS status,
    response_json->>'$.data.user_id' AS user_id
FROM api_responses;

-- 2. Flatten nested arrays: cast to JSON[] then unnest
-- Extract items from successful responses with item details
SELECT
    request_id,
    response_json->>'$.data.user_id' AS user_id,
    CAST(item->>'$.id' AS INTEGER) AS item_id,
    CAST(item->>'$.price' AS DOUBLE) AS price
FROM (
    SELECT
        request_id,
        response_json,
        unnest(json_extract(response_json, '$.data.items')::JSON[]) AS item
    FROM api_responses
    WHERE response_json->>'$.status' = 'success'
) flattened
ORDER BY request_id, item_id;
