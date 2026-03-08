# DE Scenario: Expression Evaluation for Config-Driven Pipelines

## Real-World Context

Config-driven pipelines define computed columns as expressions: `"profit": "revenue - cost"`. Evaluating these at runtime requires expression parsing. The shunting-yard algorithm converts infix expressions to postfix using a stack, then evaluates the postfix using a second stack. Same mechanics as Eval RPN (problem 150) with a preprocessing step.

## Worked Example

Two stacks in sequence. First, the shunting-yard algorithm converts infix (human-readable) to postfix (machine-evaluable) using an operator stack. Then the evaluation stack computes the result, exactly like problem 150.

```
Expression: "(revenue - cost) * tax_rate"
Variables: revenue=1000000, cost=750000, tax_rate=0.21

Step 1: Tokenize with variable substitution
  (1000000 - 750000) * 0.21

Step 2: Shunting-yard (infix → postfix)
  '('      → push to op_stack. Op: ['(']
  1000000  → output. Out: [1000000]
  '-'      → push. Op: ['(', '-']
  750000   → output. Out: [1000000, 750000]
  ')'      → pop until '('. Pop '-'. Out: [1000000, 750000, '-']. Op: []
  '*'      → push. Op: ['*']
  0.21     → output. Out: [1000000, 750000, '-', 0.21]
  End      → flush op_stack. Out: [1000000, 750000, '-', 0.21, '*']

Step 3: Evaluate postfix (same as Eval RPN)
  1000000  → push. Stack: [1000000]
  750000   → push. Stack: [1000000, 750000]
  '-'      → pop 750000, 1000000. Compute 1000000-750000=250000. Push.
             Stack: [250000]
  0.21     → push. Stack: [250000, 0.21]
  '*'      → pop 0.21, 250000. Compute 250000*0.21=52500. Push.
             Stack: [52500]

  Result: 52500
```
