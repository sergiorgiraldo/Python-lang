/*
LeetCode 196: Delete Duplicate Emails

Keep only the row with the smallest id for each email.
Delete all other duplicates.

Pattern: DELETE with subquery
Note: DuckDB supports DELETE with subquery.
*/

DELETE FROM Person_Email
WHERE id NOT IN (
    SELECT MIN(id)
    FROM Person_Email
    GROUP BY email
);
