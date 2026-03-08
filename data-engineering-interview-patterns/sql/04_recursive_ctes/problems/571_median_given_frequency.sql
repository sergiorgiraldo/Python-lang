/*
LeetCode 571: Find Median Given Frequency of Numbers

Numbers table has (num, frequency). Find the median of all numbers
when each num is repeated frequency times.

Pattern: Cumulative frequency with window function to find median position
*/

WITH cumulative AS (
    SELECT num,
           frequency,
           SUM(frequency) OVER (ORDER BY num) AS cum_freq,
           SUM(frequency) OVER () AS total
    FROM Numbers
)
SELECT ROUND(AVG(num), 1) AS median
FROM cumulative
WHERE cum_freq >= FLOOR((total + 1) / 2.0)
  AND cum_freq - frequency < CEIL((total + 1) / 2.0);
