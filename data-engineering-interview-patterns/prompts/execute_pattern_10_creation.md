# Execute Pattern 10 (Recursion/Trees) Creation Prompts

Read and execute the following prompt files in order, one at a time. After completing each file, run its verification section and confirm it passes before moving to the next.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

**Important notes for this pattern:**
- Pattern 10 has a shared `tree_node.py` file (created in Part 1) used by ALL problems. Make sure imports work correctly.
- All problem files import `from tree_node import TreeNode, build_tree, tree_to_list`.
- The `conftest.py` adds the parent directory to sys.path to enable this import.
- If imports fail, adjust the sys.path setup in conftest.py so that `uv run pytest` works from the repo root.

## Execution Order

1. `prompts/create_10_part1_readme.md` - Directory setup, TreeNode class, conftest, template, README
2. `prompts/create_10_part2_prob1_2.md` - Max Depth (104), Invert Binary Tree (226)
3. `prompts/create_10_part3_prob3_4.md` - Subtree of Another Tree (572), Lowest Common Ancestor (236)
4. `prompts/create_10_part4_prob5_de1_2.md` - Serialize/Deserialize (297), Org Chart, Category Tree
5. `prompts/create_10_part5_de3_4.md` - Bill of Materials, Pipeline DAG Analysis

## After All 5 Files Are Complete

Run the comprehensive audit:

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== PATTERN 10 CREATION SUMMARY ==="

echo ""
echo "=== Full test suite ==="
uv run pytest patterns/10_recursion_trees/ -v --tb=short 2>&1 | tail -25

echo ""
echo "=== File inventory ==="
echo "Python files:"
find patterns/10_recursion_trees/ -name "*.py" | sort
echo ""
echo "Markdown files:"
find patterns/10_recursion_trees/ -name "*.md" | sort

echo ""
echo "=== README quality ==="
grep "^### " patterns/10_recursion_trees/README.md

echo ""
echo "=== TreeNode class works ==="
uv run python -c "
from patterns.10_recursion_trees.tree_node import TreeNode, build_tree, tree_to_list
t = build_tree([3, 9, 20, None, None, 15, 7])
print(f'Root: {t}, to_list: {tree_to_list(t)}')
assert tree_to_list(t) == [3, 9, 20, None, None, 15, 7]
print('TreeNode: OK')
"

echo ""
echo "=== Worked Example check ==="
for f in patterns/10_recursion_trees/problems/*.md patterns/10_recursion_trees/de_scenarios/*.md; do
    [ -f "$f" ] || continue
    name=$(basename "$f")
    has_we=$(grep -q "## Worked Example" "$f" && echo "Y" || echo "N")
    first=$(awk '/^## Worked Example/{found=1; next} found && /\S/{print; exit}' "$f")
    starts_prose=$(echo "$first" | grep -q '```' && echo "CODE" || echo "PROSE")
    echo "  $name: present=$has_we, starts=$starts_prose"
done

echo ""
echo "=== Approach explanation quality ==="
for f in patterns/10_recursion_trees/problems/*.md; do
    name=$(basename "$f")
    awk '/📝 Explanation/{found=1; lines=0; next} found && /<\/details>/{if(lines<4) printf "  ❌ %s: only %d lines\n", "'"$name"'", lines; else printf "  ✅ %s: %d lines\n", "'"$name"'", lines; found=0} found && /\S/{lines++}' "$f"
done

echo ""
echo "=== DE scenarios run ==="
uv run python -m patterns.10_recursion_trees.de_scenarios.org_chart 2>&1 | tail -3
uv run python -m patterns.10_recursion_trees.de_scenarios.category_tree 2>&1 | tail -3
uv run python -m patterns.10_recursion_trees.de_scenarios.bill_of_materials 2>&1 | tail -3
uv run python -m patterns.10_recursion_trees.de_scenarios.pipeline_dag 2>&1 | tail -3

echo ""
echo "=== Style violations ==="
grep -r "—" patterns/10_recursion_trees/ && echo "❌ Em dashes" || echo "✅ No em dashes"
grep -rn "## Visual Walkthrough" patterns/10_recursion_trees/ && echo "❌ Wrong section names" || echo "✅ Correct section names"

echo ""
echo "=== Cross-pattern test suite ==="
uv run pytest --tb=short 2>&1 | tail -3
```

Provide a comprehensive summary of what was created, test results, and any issues encountered. Pay special attention to import paths - the shared `tree_node.py` file needs to be importable from all problem and test files.
