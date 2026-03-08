# Interview Strategy Guide

This guide covers the non-technical aspects of interviewing: pacing, communication and what to do when stuck. Technical knowledge is necessary but not sufficient. How you communicate is half the evaluation.

---

## Coding Round Strategy (45-60 minutes)

```
First 5 minutes: Understand the problem
  - Restate the problem in your own words
  - Ask about input constraints (size, range, sorted?)
  - Ask about edge cases (empty input, single element, duplicates?)
  - Confirm expected output format
  - State your approach before coding

Next 20-30 minutes: Implement
  - Start with brute force if unsure (shows you can solve it)
  - Narrate as you code: "I'm using a hash map here because..."
  - Write clean code: meaningful variable names, helper functions
  - Handle edge cases explicitly (don't ignore empty input)

Last 10-15 minutes: Test and optimize
  - Walk through your code with a concrete example
  - Test edge cases
  - Discuss time and space complexity
  - If time remains, discuss optimization or follow-ups
```

---

## SQL Round Strategy (30-45 minutes)

```
First 2 minutes: Understand the schema
  - Ask to see the table schemas (or draw them yourself)
  - Clarify column types and NULLability
  - Ask about data volume (affects approach choice)

Next 15-25 minutes: Write the query
  - Start with a simple version, then add complexity
  - Build incrementally: get the JOIN right, then add WHERE, then GROUP BY
  - Use CTEs for readability (name them meaningfully)
  - Test mentally with the sample data

Last 5-10 minutes: Discuss
  - Explain your query plan (what happens first, second, etc.)
  - Discuss performance: indexes, partitioning, approximate functions
  - Mention dialect differences if relevant to the company's stack
```

---

## System Design Round Strategy (45 minutes)

See `system_design/foundations/communication_framework.md` for the detailed 45-minute breakdown.

Brief summary of the five phases:

1. **Requirements** (5 min) - Clarify scope, ask about scale, establish functional and non-functional requirements
2. **Data model** (5 min) - Define key entities, relationships and access patterns
3. **High-level architecture** (10 min) - Draw the end-to-end data flow from ingestion to consumption
4. **Deep dives** (20 min) - Go deep on 2-3 components the interviewer cares about most
5. **Trade-offs and extensions** (5 min) - Discuss alternatives, failure modes and what you would do differently at 10x scale

---

## What to Do When Stuck

| Situation | Strategy |
|---|---|
| Can't find the right pattern | State the brute force approach and its complexity. Ask: "what makes this slow?" The answer often reveals the optimization. |
| Know the pattern but can't implement | Write pseudocode first. Focus on the algorithm structure, then translate to code. |
| Off-by-one error | Stop coding. Write out the loop invariant. Trace through with a 3-element example. |
| SQL query returning wrong results | Break the query into CTEs. Run each CTE mentally against sample data. Find where results diverge from expectations. |
| System design: don't know where to start | Start with data flow. "Data enters here, gets processed here, gets stored here, gets consumed here." Fill in the boxes after. |
| Interviewer gives a hint | Take it. Thank them. Don't view hints as failures. The interviewer is testing whether you can collaborate. |
| Running out of time | State what you would do with more time. "Given 10 more minutes, I'd add error handling for edge case X and optimize the sort step." |

---

## Common Mistakes

- Coding too fast without thinking (produces bugs, wastes time debugging)
- Going silent for long stretches (interviewer can't evaluate what they can't see)
- Ignoring edge cases until the end (they're testing attention to detail)
- Optimizing prematurely (get a working solution first)
- Not testing with examples (tracing through code catches most bugs)
- In SQL: using COUNT(*) with LEFT JOIN (gets wrong count for empty groups)
- In system design: jumping to technology choices without establishing requirements
- Saying "I don't know" without trying (say "I'm not sure, but my intuition is..." and reason through it)

---

## Pacing Yourself

| Round | Phase | Time |
|---|---|---|
| Coding | Read and clarify | ~2 min |
| Coding | Plan approach | ~3 min |
| Coding | Implement | ~20 min |
| Coding | Test and discuss | ~10 min |
| SQL | Read schema | ~2 min |
| SQL | Write query | ~15 min |
| SQL | Test and discuss | ~5 min |
| System design | Full breakdown | See `system_design/foundations/` |

If you finish early, discuss trade-offs, optimizations or alternative approaches. Don't just sit there.

---

## What to Say in an Interview

When you recognize a pattern, articulate it:

> "This looks like a [pattern name] problem because [signal]. My first thought is [brute force]. I can do better with [pattern] because [reason], which gives me [complexity]."

Interviewers want to see that you're identifying patterns, not just memorizing solutions. Explaining *why* a pattern fits matters more than jumping to code.
