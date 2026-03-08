/*
LeetCode 178: Rank Scores

Return scores with their dense rank, ordered by score descending.
Column names: score, rank

Pattern: DENSE_RANK window function
*/

SELECT score,
       DENSE_RANK() OVER (ORDER BY score DESC) AS "rank"
FROM Scores
ORDER BY score DESC;
