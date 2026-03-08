/*
Delete duplicates using ROW_NUMBER (more flexible).
*/

DELETE FROM Person_Email
WHERE id IN (
    SELECT id FROM (
        SELECT id,
               ROW_NUMBER() OVER (PARTITION BY email ORDER BY id) AS rn
        FROM Person_Email
    ) t
    WHERE rn > 1
);
