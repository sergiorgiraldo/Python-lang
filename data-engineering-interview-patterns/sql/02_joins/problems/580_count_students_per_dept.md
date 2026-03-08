# Count Student Number in Departments (LeetCode #580)

🔗 [LeetCode 580: Count Student Number in Departments](https://leetcode.com/problems/count-student-number-in-departments/)

> **Difficulty:** Easy | **Interview Frequency:** Occasional

## Problem Statement

Return each department's name and student count, ordered by student count descending then department name ascending. Include departments with zero students.

## Thought Process

1. **LEFT JOIN:** We need ALL departments in the output, even those with no students. LEFT JOIN preserves the left table (Department).
2. **COUNT(s.student_id) not COUNT(*):** This is the critical distinction. COUNT(*) counts rows, including NULLs from the LEFT JOIN. A department with no students still has one row after LEFT JOIN (with NULL student columns), so COUNT(*) would return 1. COUNT(s.student_id) counts non-NULL values, correctly returning 0.
3. **ORDER BY:** student_number DESC for highest first, dept_name ASC for alphabetical tiebreaking.

## Worked Example

The COUNT(*) vs COUNT(column) distinction is the core of this problem. After a LEFT JOIN, departments with no students produce one row where all Student columns are NULL. COUNT(*) counts that row (returning 1), while COUNT(s.student_id) skips the NULL (returning 0). Getting this wrong produces off-by-one errors for empty departments.

```
Department table:
  id | name
  1  | Engineering
  2  | Science
  3  | Law

Student table:
  student_id | student_name | department_id
  1          | Jack         | 1
  2          | Jane         | 1
  3          | Mark         | 2

LEFT JOIN Department -> Student on id = department_id:
  Engineering (1) -> Jack (1), Jane (2)   -- 2 matches
  Science (2)     -> Mark (3)             -- 1 match
  Law (3)         -> NULL                 -- no match

GROUP BY department:
  Engineering: COUNT(s.student_id) = 2, COUNT(*) = 2
  Science:     COUNT(s.student_id) = 1, COUNT(*) = 1
  Law:         COUNT(s.student_id) = 0, COUNT(*) = 1  <-- difference

ORDER BY student_number DESC, dept_name ASC:
  Engineering (2), Science (1), Law (0)
```

## Approaches

### Approach 1: LEFT JOIN + COUNT(column)

<details>
<summary>Explanation</summary>

```sql
SELECT d.name AS dept_name,
       COUNT(s.student_id) AS student_number
FROM Department d
LEFT JOIN Student s ON d.id = s.department_id
GROUP BY d.id, d.name
ORDER BY student_number DESC, dept_name ASC;
```

The LEFT JOIN ensures every department appears. COUNT(s.student_id) counts actual students, returning 0 for departments with no match.

**Why GROUP BY d.id, d.name:** Grouping by id alone is sufficient for correctness (id is the primary key), but including name avoids requiring the engine to pick which name to show. Some engines require all non-aggregated SELECT columns in GROUP BY.

</details>

### Approach 2: Subquery

<details>
<summary>Explanation</summary>

```sql
SELECT d.name AS dept_name,
       (SELECT COUNT(*) FROM Student s WHERE s.department_id = d.id) AS student_number
FROM Department d
ORDER BY student_number DESC, dept_name ASC;
```

A correlated subquery counts students per department. COUNT(*) is correct here because the subquery only returns matching rows (no LEFT JOIN NULLs). This avoids the COUNT(*) vs COUNT(column) trap but is less efficient for large tables.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| Department with no students | Count = 0 | LEFT JOIN + COUNT(column) handles this |
| All departments empty | All counts = 0 | LEFT JOIN preserves all departments |
| Tied counts | Alphabetical order | ORDER BY dept_name ASC as tiebreaker |
| Student with invalid department_id | Not counted | No matching department in LEFT JOIN |

## Interview Tips

> "I'll use LEFT JOIN to include all departments, even empty ones. The key subtlety is COUNT(s.student_id) instead of COUNT(*). COUNT(*) would return 1 for empty departments because the LEFT JOIN produces a row with NULLs, and COUNT(*) counts all rows including NULLs. COUNT(column) only counts non-NULL values."

**What the interviewer evaluates:** COUNT(*) vs COUNT(column) is the gotcha in this problem. Candidates who use COUNT(*) with LEFT JOIN get wrong results for empty groups, producing 1 instead of 0. Catching this distinction, or better yet explaining it proactively, is a strong signal of SQL experience. This is one of the most commonly tested subtle SQL behaviors in interviews.

## At Scale

LEFT JOIN + GROUP BY is a standard pattern for completeness reporting. The LEFT ensures that every dimension entity appears, even those with no activity.

For large Student tables with many departments, the query performs:
1. Hash join: build hash table from Student (department_id), probe with Department (id). O(n + m).
2. Group by: aggregate counts. O(n) where n is the number of matched rows.

Indexing department_id on the Student table improves the join performance when Department is much smaller than Student.

## DE Application

Completeness reporting with zero-count inclusion is critical for data quality:
- "How many records arrived per partition today?" (include partitions with 0 records)
- "Events per source system per hour" (include hours with no events to detect outages)
- "Tests per module" (include modules with no test coverage)

Using COUNT(*) instead of COUNT(column) in these reports masks missing data by showing 1 instead of 0. This is a real production bug that has caused missed SLA alerts.

## Dialect Notes

Syntax is identical across all major engines. LEFT JOIN, COUNT(column) vs COUNT(*) behavior and ORDER BY are part of the SQL standard with no dialect variation.

## Related Problems

- [175. Combine Two Tables](175_combine_two_tables.md) - Basic LEFT JOIN
- [183. Customers Who Never Order](183_customers_who_never_order.md) - LEFT JOIN + IS NULL
