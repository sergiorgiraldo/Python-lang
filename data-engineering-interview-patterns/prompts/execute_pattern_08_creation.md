# Execute Pattern 08 (Stack) Creation Prompts

Read and execute the following prompt files in order, one at a time. Each file creates new files in the repo. After completing each file, run its verification section and confirm it passes before moving to the next. If any verification fails, fix the issue before proceeding.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Execution Order

1. `prompts/create_08_part1_readme.md` - Directory setup, conftest, template, README
2. `prompts/create_08_part2_prob1_2.md` - Valid Parentheses (20), Min Stack (155)
3. `prompts/create_08_part3_prob3_4.md` - Eval RPN (150), Daily Temperatures (739)
4. `prompts/create_08_part4_prob5_6.md` - Car Fleet (853), Largest Rectangle (84)
5. `prompts/create_08_part5_de_scenarios.md` - DE scenarios + benchmark

## After All 5 Files Are Complete

Run the full test suite and comprehensive audit:

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== PATTERN 08 CREATION SUMMARY ==="

echo ""
echo "=== Full test suite ==="
uv run pytest patterns/08_stack/ -v --tb=short 2>&1 | tail -20

echo ""
echo "=== File inventory ==="
echo "Python files:"
find patterns/08_stack/ -name "*.py" | sort
echo ""
echo "Markdown files:"
find patterns/08_stack/ -name "*.md" | sort

echo ""
echo "=== README quality ==="
grep "^### " patterns/08_stack/README.md

echo ""
echo "=== Worked Example check ==="
for f in patterns/08_stack/problems/*.md patterns/08_stack/de_scenarios/*.md; do
    [ -f "$f" ] || continue
    name=$(basename "$f")
    has_we=$(grep -q "## Worked Example" "$f" && echo "Y" || echo "N")
    first=$(awk '/^## Worked Example/{found=1; next} found && /\S/{print; exit}' "$f")
    starts_prose=$(echo "$first" | grep -q '```' && echo "CODE" || echo "PROSE")
    echo "  $name: present=$has_we, starts=$starts_prose"
done

echo ""
echo "=== Approach explanation quality ==="
for f in patterns/08_stack/problems/*.md; do
    name=$(basename "$f")
    awk '/📝 Explanation/{found=1; lines=0; next} found && /<\/details>/{if(lines<4) printf "  ❌ %s: only %d lines\n", "'"$name"'", lines; else printf "  ✅ %s: %d lines\n", "'"$name"'", lines; found=0} found && /\S/{lines++}' "$f"
done

echo ""
echo "=== Style violations ==="
grep -rn "—" patterns/08_stack/ && echo "❌ Em dashes" || echo "✅ No em dashes"
grep -rn "## Visual Walkthrough" patterns/08_stack/ && echo "❌ Wrong section names" || echo "✅ Correct section names"

echo ""
echo "=== Run DE scenarios ==="
uv run python -m patterns.08_stack.de_scenarios.nested_validation 2>&1 | tail -5
uv run python -m patterns.08_stack.de_scenarios.expression_eval 2>&1 | tail -5
uv run python -m patterns.08_stack.de_scenarios.monotonic_time_series 2>&1 | tail -5

echo ""
echo "=== Cross-pattern test suite ==="
uv run pytest --tb=short 2>&1 | tail -3
```

Provide a comprehensive summary of what was created, test results, and any issues encountered.
