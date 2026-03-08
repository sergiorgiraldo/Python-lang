# Execute Pattern 12 (Combined Patterns) Creation Prompts

Read and execute the following prompt files in order, one at a time. After completing each file, run its verification section and confirm it passes before moving to the next.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

**Notes for this pattern:**
- This is the capstone pattern. It combines techniques from earlier patterns.
- 4 LeetCode problems + 2 DE scenarios (smaller than other patterns).
- No new dependencies needed.
- The README emphasizes pattern recognition and composition skills.

## Execution Order

1. `prompts/create_12_part1_readme.md` - Directory setup, conftest, README
2. `prompts/create_12_part2_prob1_2.md` - 3Sum (15), Minimum Window Substring (76)
3. `prompts/create_12_part3_prob3_4.md` - Top K Frequent (347), Network Delay Time (743)
4. `prompts/create_12_part4_de_scenarios.md` - Pipeline Analysis, Pattern Recognition Practice

## After All 4 Files Are Complete

Run the comprehensive audit:

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== PATTERN 12 CREATION SUMMARY ==="

echo ""
echo "=== Full test suite ==="
uv run pytest patterns/12_combined_patterns/ -v --tb=short 2>&1 | tail -20

echo ""
echo "=== File inventory ==="
echo "Python files:"
find patterns/12_combined_patterns/ -name "*.py" | sort
echo ""
echo "Markdown files:"
find patterns/12_combined_patterns/ -name "*.md" | sort

echo ""
echo "=== README quality ==="
grep "^### " patterns/12_combined_patterns/README.md

echo ""
echo "=== Worked Example check ==="
for f in patterns/12_combined_patterns/problems/*.md patterns/12_combined_patterns/de_scenarios/*.md; do
    [ -f "$f" ] || continue
    name=$(basename "$f")
    has_we=$(grep -q "## Worked Example" "$f" && echo "Y" || echo "N")
    first=$(awk '/^## Worked Example/{found=1; next} found && /\S/{print; exit}' "$f")
    starts_prose=$(echo "$first" | grep -q '```' && echo "CODE" || echo "PROSE")
    echo "  $name: present=$has_we, starts=$starts_prose"
done

echo ""
echo "=== Approach explanation quality ==="
for f in patterns/12_combined_patterns/problems/*.md; do
    name=$(basename "$f")
    awk '/📝 Explanation/{found=1; lines=0; next} found && /<\/details>/{if(lines<4) printf "  ❌ %s: only %d lines\n", "'"$name"'", lines; else printf "  ✅ %s: %d lines\n", "'"$name"'", lines; found=0} found && /\S/{lines++}' "$f"
done

echo ""
echo "=== DE scenarios run ==="
uv run python -m patterns.12_combined_patterns.de_scenarios.pipeline_analysis 2>&1 | tail -3
uv run python -m patterns.12_combined_patterns.de_scenarios.pattern_recognition 2>&1 | tail -3

echo ""
echo "=== Style violations ==="
grep -r "—" patterns/12_combined_patterns/ && echo "❌ Em dashes" || echo "✅ No em dashes"

echo ""
echo "=== FULL REPOSITORY TEST SUITE ==="
echo "(This is the final Phase 1 check - all patterns 01-12)"
uv run pytest --tb=short 2>&1 | tail -5

echo ""
echo "=== PHASE 1 INVENTORY ==="
for i in $(seq -w 1 12); do
    dir="patterns/${i}_*"
    dir_actual=$(ls -d $dir 2>/dev/null | head -1)
    if [ -n "$dir_actual" ]; then
        probs=$(ls "$dir_actual/problems/"*.md 2>/dev/null | wc -l)
        des=$(ls "$dir_actual/de_scenarios/"*.md 2>/dev/null | wc -l)
        echo "  Pattern $i: $probs problems/implementations, $des DE scenarios"
    fi
done

echo ""
echo "=== TOTAL ==="
echo "  Problems/implementations: $(find patterns/ -path '*/problems/*.md' | wc -l)"
echo "  DE scenarios: $(find patterns/ -path '*/de_scenarios/*.md' | wc -l)"
echo "  Python files: $(find patterns/ -name '*.py' | wc -l)"
echo "  Tests passing: run count above"
```

Provide a comprehensive summary including the full Phase 1 inventory across all 12 patterns.
