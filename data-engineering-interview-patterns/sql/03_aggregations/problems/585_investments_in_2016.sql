/*
LeetCode 585: Investments in 2016

Find the total tiv_2016 for policyholders who:
1. Have the same tiv_2015 as at least one other policyholder
2. Are NOT in the same city as any other policyholder (unique lat/lon)

Pattern: Subquery with GROUP BY + HAVING for set membership
*/

SELECT ROUND(SUM(tiv_2016), 2) AS tiv_2016
FROM Insurance
WHERE tiv_2015 IN (
    SELECT tiv_2015
    FROM Insurance
    GROUP BY tiv_2015
    HAVING COUNT(*) > 1
)
AND (lat, lon) IN (
    SELECT lat, lon
    FROM Insurance
    GROUP BY lat, lon
    HAVING COUNT(*) = 1
);
