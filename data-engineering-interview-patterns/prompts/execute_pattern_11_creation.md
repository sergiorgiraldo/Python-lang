# Execute Pattern 11 (Probabilistic Structures) Creation Prompts

Read and execute the following prompt files in order, one at a time. After completing each file, run its verification section and confirm it passes before moving to the next.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

**Critical notes for this pattern:**

1. **New dependency:** This pattern requires the `mmh3` (MurmurHash3) package. Add it to the project before running any code:
   ```bash
   cd ~/dev/projects/data-engineering-interview-patterns
   uv add mmh3
   ```
   If `uv add` doesn't work, try adding `mmh3` to `pyproject.toml` dependencies manually and running `uv sync`.

2. **No LeetCode problems.** This pattern has implementations (Bloom filter, HyperLogLog, Count-Min Sketch) instead of LeetCode solutions. Same quality standards apply.

3. **Statistical tests.** Some tests verify probabilistic bounds (e.g., "false positive rate should be below 3%"). These may occasionally fail due to randomness. If a statistical test fails, re-run once before investigating. If it fails consistently, adjust the bounds.

4. **Import paths in DE scenarios.** The DE scenario files import from the problems directory. They use `sys.path.insert(0, "patterns/11_probabilistic_structures/problems")` to make imports work. Adjust if needed so that `uv run python -m patterns.11_probabilistic_structures.de_scenarios.X` works from the repo root.

## Execution Order

1. `prompts/create_11_part1_readme.md` - Directory setup, conftest, README
2. `prompts/create_11_part2_bloom.md` - Bloom Filter (impl + tests + docs)
3. `prompts/create_11_part3_hll.md` - HyperLogLog (impl + tests + docs)
4. `prompts/create_11_part4_cms.md` - Count-Min Sketch (impl + tests + docs)
5. `prompts/create_11_part5_de_scenarios.md` - All 4 DE scenarios

## After All 5 Files Are Complete

Run the comprehensive audit:

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== PATTERN 11 CREATION SUMMARY ==="

echo ""
echo "=== mmh3 dependency ==="
uv run python -c "import mmh3; print(f'mmh3 version: {mmh3.__version__}')" 2>&1

echo ""
echo "=== Full test suite ==="
uv run pytest patterns/11_probabilistic_structures/ -v --tb=short 2>&1 | tail -30

echo ""
echo "=== File inventory ==="
echo "Python files:"
find patterns/11_probabilistic_structures/ -name "*.py" | sort
echo ""
echo "Markdown files:"
find patterns/11_probabilistic_structures/ -name "*.md" | sort

echo ""
echo "=== README quality ==="
grep "^### " patterns/11_probabilistic_structures/README.md

echo ""
echo "=== Worked Example check ==="
for f in patterns/11_probabilistic_structures/problems/*.md patterns/11_probabilistic_structures/de_scenarios/*.md; do
    [ -f "$f" ] || continue
    name=$(basename "$f")
    has_we=$(grep -q "## Worked Example" "$f" && echo "Y" || echo "N")
    first=$(awk '/^## Worked Example/{found=1; next} found && /\S/{print; exit}' "$f")
    starts_prose=$(echo "$first" | grep -q '```' && echo "CODE" || echo "PROSE")
    echo "  $name: present=$has_we, starts=$starts_prose"
done

echo ""
echo "=== Approach explanation quality ==="
for f in patterns/11_probabilistic_structures/problems/*.md; do
    name=$(basename "$f")
    awk '/📝 Explanation/{found=1; lines=0; next} found && /<\/details>/{if(lines<4) printf "  ❌ %s: only %d lines\n", "'"$name"'", lines; else printf "  ✅ %s: %d lines\n", "'"$name"'", lines; found=0} found && /\S/{lines++}' "$f"
done

echo ""
echo "=== DE scenarios run ==="
uv run python -m patterns.11_probabilistic_structures.de_scenarios.stream_dedup 2>&1 | tail -3
uv run python -m patterns.11_probabilistic_structures.de_scenarios.approx_distinct 2>&1 | tail -3
uv run python -m patterns.11_probabilistic_structures.de_scenarios.heavy_hitters 2>&1 | tail -3
uv run python -m patterns.11_probabilistic_structures.de_scenarios.memory_budget 2>&1 | tail -3

echo ""
echo "=== Style violations ==="
grep -r "—" patterns/11_probabilistic_structures/ && echo "❌ Em dashes" || echo "✅ No em dashes"

echo ""
echo "=== Cross-pattern test suite ==="
uv run pytest --tb=short 2>&1 | tail -3
```

Provide a comprehensive summary of what was created, test results, and any issues encountered. Pay special attention to:
- The mmh3 dependency installation
- Statistical test stability (re-run once if a probabilistic test fails)
- Import paths for DE scenarios
