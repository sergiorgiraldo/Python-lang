# Execute Pattern 06 (Graph) Rework Prompts

Read and execute the following 3 prompt files in order. Each file contains instructions to modify `.md` files in this repo. After completing each file, run its verification section and confirm it passes before moving to the next.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

Only modify `.md` files. Never touch `.py` or `_test.py` files.

## Execution Order

1. `prompts/rework_06_readme.md`
2. `prompts/rework_06_worked_ex.md`
3. `prompts/rework_06_approaches.md`

## After All 3 Files Are Complete

Run:

```bash
cd ~/dev/projects/data-engineering-interview-patterns
uv run pytest patterns/06_graph_topological_sort/ -v --tb=short 2>&1 | tail -10

echo "=== README subsections ==="
grep "^### " patterns/06_graph_topological_sort/README.md

echo ""
echo "=== Worked Example count ==="
grep -rl "## Worked Example" patterns/06_graph_topological_sort/ | wc -l
echo "(should be 11: 7 problems + 4 DE scenarios)"

echo ""
echo "=== Approach explanation quality ==="
for f in patterns/06_graph_topological_sort/problems/*.md; do
    name=$(basename "$f")
    awk '/📝 Explanation/{found=1; lines=0; next} found && /<\/details>/{if(lines<4) printf "  ❌ %s: only %d lines\n", "'"$name"'", lines; else printf "  ✅ %s: %d lines\n", "'"$name"'", lines; found=0} found && /\S/{lines++}' "$f"
done
```

Provide a summary of what was modified.
