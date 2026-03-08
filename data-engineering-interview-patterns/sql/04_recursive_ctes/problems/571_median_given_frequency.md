# Find Median Given Frequency of Numbers (LeetCode #571)

🔗 [LeetCode 571: Find Median Given Frequency of Numbers](https://leetcode.com/problems/find-median-given-frequency-of-numbers/)

> **Difficulty:** Hard | **Interview Frequency:** Occasional

## Problem Statement

The Numbers table has columns `num` and `frequency`. Each row indicates that `num` appears `frequency` times. Find the median of all numbers when expanded by their frequencies.

## Thought Process

1. **Why not expand the data?** Expanding frequency=1M rows for a single number wastes memory. Instead, use cumulative frequency to find the median position without expansion.
2. **Where is the median position?** For total count T (sum of all frequencies), the median is at position (T+1)/2 for odd T, or the average of positions T/2 and T/2+1 for even T.
3. **Which number contains the median position?** The number whose cumulative frequency range spans that position. If cum_freq for numbers up to 5 is 100 and for numbers up to 6 is 150, then positions 101-150 are all the number 6.

## Worked Example

Consider Numbers = [(0,7), (1,1), (2,3), (3,1)]. The total count is 7+1+3+1 = 12. The median is the average of positions 6 and 7.

The key insight is that cumulative frequency tells you which number "owns" each position. Number 0 owns positions 1-7, number 1 owns position 8, number 2 owns positions 9-11, number 3 owns position 12. Positions 6 and 7 both fall within number 0's range, so the median is 0.

```
num | freq | cum_freq | total | range of positions
  0 |    7 |        7 |    12 | 1-7
  1 |    1 |        8 |    12 | 8-8
  2 |    3 |       11 |    12 | 9-11
  3 |    1 |       12 |    12 | 12-12

Median position: (12+1)/2 = 6.5
  -> positions 6 and 7 (for even total, we average the two middle values)
  -> both in num=0's range (cum_freq=7 >= FLOOR(6.5)=6, cum_freq-freq=0 < CEIL(6.5)=7)
  -> AVG(0) = 0.0
```

The WHERE clause uses `cum_freq >= FLOOR((total+1)/2)` and `cum_freq - frequency < CEIL((total+1)/2)` to identify numbers whose cumulative range includes the median position(s). FLOOR gives the lower median position and CEIL gives the upper median position. For odd totals these are the same value. For even totals, if the two middle positions span two different numbers, both pass the filter and AVG averages them.

## Approaches

### Approach 1: Cumulative Frequency Window

<details>
<summary>Explanation</summary>

Compute cumulative frequency with SUM() OVER (ORDER BY num). The cumulative frequency at each row tells you the last position owned by that number. The first position owned is `cum_freq - frequency + 1`.

The WHERE clause identifies numbers whose position range includes the median position. AVG handles the even-total case by averaging the two middle numbers (which may be the same or different).

Time complexity: O(d log d) where d is the number of distinct values (for the sort). This is independent of the total count, making it efficient for frequency tables representing billions of values.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| Single number, frequency 1 | That number | Only one value |
| Single number, high frequency | That number | All positions are the same value |
| Even total, same middle number | That number (not averaged) | AVG of identical values = that value |
| Even total, different middle numbers | Average of the two | AVG produces the correct median |
| Two numbers, frequency 1 each | Average of both | Classic even-case median |

## Interview Tips

> "I will compute cumulative frequency using SUM as a window function ordered by num. The median position is at (total+1)/2. The WHERE clause finds which number's cumulative range spans that position. AVG handles the even-count case automatically."

**What the interviewer evaluates:** This is a tricky problem. The cumulative frequency approach tests mathematical reasoning in SQL. Walking through a concrete example with the interviewer is essential. The WHERE clause condition is the hardest part to get right. Candidates who can derive the boundary conditions (`cum_freq - frequency < threshold AND cum_freq >= threshold`) from first principles demonstrate strong analytical skills.

## At Scale

This is compact data. A frequency table with 1000 distinct values representing 1B total values processes in milliseconds. The window function scan is O(d) where d is the count of distinct values, not the total expanded count.

Frequency tables are a common optimization in data warehouses. Pre-aggregating raw data into (value, count) pairs reduces storage and query time by orders of magnitude for statistical calculations.

For very large frequency tables (millions of distinct values), the sort on `num` is the bottleneck. An index on `num` avoids the sort entirely.

## DE Application

Frequency-based statistical calculations are common in data profiling and quality monitoring. Histogram analysis (what is the distribution of order values?), percentile computation on pre-aggregated data and outlier detection all use this cumulative frequency pattern.

When data is stored as frequency tables (common after GROUP BY aggregation), statistical queries like median, mode and percentiles use cumulative sums rather than expanding back to raw values. This is the standard approach in OLAP engines where data is pre-aggregated for performance.

## Dialect Notes

Syntax is identical across all major engines that support window functions. SUM() OVER, ROWS frame specifications and AVG are part of the SQL standard. Some engines (BigQuery, Snowflake) also offer PERCENTILE_CONT as a built-in median function, but the window function approach shown here works universally.

## Related Problems

- [569. Median Employee Salary](569_median_employee_salary.md) - Median on raw data
