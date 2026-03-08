-- Friend request tables
-- Used by: 602

CREATE TABLE IF NOT EXISTS RequestAccepted (
    requester_id INTEGER,
    accepter_id INTEGER,
    accept_date DATE
);
