-- Customers and Orders tables
-- Used by: 183

CREATE TABLE IF NOT EXISTS Customers (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS Orders (
    id INTEGER PRIMARY KEY,
    customerId INTEGER
);
