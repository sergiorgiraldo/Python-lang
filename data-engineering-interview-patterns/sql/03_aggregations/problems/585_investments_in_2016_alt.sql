/*
LeetCode 585: Investments in 2016 - Window Function Approach

Window function approach avoids subqueries by computing both counts
in a single pass over the data.
*/

SELECT ROUND(SUM(tiv_2016), 2) AS tiv_2016
FROM (
    SELECT tiv_2016,
           COUNT(*) OVER (PARTITION BY tiv_2015) AS tiv_cnt,
           COUNT(*) OVER (PARTITION BY lat, lon) AS loc_cnt
    FROM Insurance
) t
WHERE tiv_cnt > 1 AND loc_cnt = 1;
