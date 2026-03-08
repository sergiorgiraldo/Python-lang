# DE Scenario: Nested Structure Validation

## Real-World Context

Every data pipeline that ingests JSON, XML or config files needs to validate structure. A missing closing brace in a 500MB JSON file will either crash `json.loads()` with an unhelpful error or silently corrupt downstream data. Stack-based validation catches these errors in a single pass and reports the exact position.

## Worked Example

Bracket validation is Valid Parentheses (problem 20) applied to real data. The addition: track positions so error messages are actionable ("unclosed '{' at position 42" instead of just "invalid").

```
Input: '{"users": [{"name": "alice"}, {"name": "bob"}]'

  i=0  '{' → push ('{', 0).      Stack: [('{',0)]
  i=10 '[' → push ('[', 10).     Stack: [('{',0), ('[',10)]
  i=11 '{' → push ('{', 11).     Stack: [('{',0), ('[',10), ('{',11)]
  i=27 '}' → matches '{' at 11. Pop.  Stack: [('{',0), ('[',10)]
  i=30 '{' → push ('{', 30).     Stack: [('{',0), ('[',10), ('{',30)]
  i=44 '}' → matches '{' at 30. Pop.  Stack: [('{',0), ('[',10)]
  i=45 ']' → matches '[' at 10. Pop.  Stack: [('{',0)]
  End of string. Stack not empty.

  Error: "Unclosed '{' from position 0"
  Fix: add closing '}' at the end.
```
