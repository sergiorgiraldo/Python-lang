/*
LeetCode 180: Consecutive Numbers

Find all numbers that appear at least three times consecutively.
The Logs table has id (auto-increment) and num columns.

Pattern: LAG/LEAD window functions to compare adjacent rows
*/

SELECT DISTINCT num AS ConsecutiveNums
FROM (
    SELECT num,
           LAG(num, 1) OVER (ORDER BY id) AS prev1,
           LAG(num, 2) OVER (ORDER BY id) AS prev2
    FROM Logs
) t
WHERE num = prev1 AND num = prev2;
