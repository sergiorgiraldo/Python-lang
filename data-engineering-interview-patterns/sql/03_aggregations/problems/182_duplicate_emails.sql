/*
LeetCode 182: Duplicate Emails

Find all emails that appear more than once in Person_Email.

Pattern: GROUP BY + HAVING COUNT > 1
*/

SELECT email
FROM Person_Email
GROUP BY email
HAVING COUNT(*) > 1;
