"""
DE Scenario: Evaluate config-driven pipeline expressions.

Real-world application: computed columns, filter expressions,
and conditional logic in config-driven data pipelines.

Run: uv run python -m patterns.08_stack.de_scenarios.expression_eval
"""


def evaluate_config_expression(
    expression: str, variables: dict[str, float]
) -> float:
    """
    Evaluate a simple config expression with variables.

    Supports: +, -, *, / operators, parentheses, and variable substitution.
    Uses the shunting-yard algorithm (infix to postfix) then evaluates.
    """
    tokens = _tokenize(expression, variables)
    postfix = _to_postfix(tokens)
    return _eval_postfix(postfix)


def _tokenize(
    expression: str, variables: dict[str, float]
) -> list[str | float]:
    """Tokenize an expression, substituting variables."""
    tokens: list[str | float] = []
    i = 0
    while i < len(expression):
        if expression[i].isspace():
            i += 1
        elif expression[i] in "+-*/()":
            tokens.append(expression[i])
            i += 1
        elif expression[i].isdigit() or expression[i] == ".":
            j = i
            while j < len(expression) and (expression[j].isdigit() or expression[j] == "."):
                j += 1
            tokens.append(float(expression[i:j]))
            i = j
        elif expression[i].isalpha() or expression[i] == "_":
            j = i
            while j < len(expression) and (expression[j].isalnum() or expression[j] == "_"):
                j += 1
            var_name = expression[i:j]
            if var_name not in variables:
                raise ValueError(f"Unknown variable: {var_name}")
            tokens.append(float(variables[var_name]))
            i = j
        else:
            raise ValueError(f"Unexpected character: {expression[i]}")
    return tokens


def _to_postfix(tokens: list[str | float]) -> list[str | float]:
    """Convert infix tokens to postfix using shunting-yard algorithm."""
    output: list[str | float] = []
    op_stack: list[str] = []
    precedence = {"+": 1, "-": 1, "*": 2, "/": 2}

    for token in tokens:
        if isinstance(token, float):
            output.append(token)
        elif token == "(":
            op_stack.append(token)
        elif token == ")":
            while op_stack and op_stack[-1] != "(":
                output.append(op_stack.pop())
            if op_stack:
                op_stack.pop()  # remove the "("
        elif token in precedence:
            while (
                op_stack
                and op_stack[-1] != "("
                and op_stack[-1] in precedence
                and precedence[op_stack[-1]] >= precedence[token]
            ):
                output.append(op_stack.pop())
            op_stack.append(token)

    while op_stack:
        output.append(op_stack.pop())

    return output


def _eval_postfix(tokens: list[str | float]) -> float:
    """Evaluate a postfix expression."""
    stack: list[float] = []
    ops = {
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
        "/": lambda a, b: a / b,
    }

    for token in tokens:
        if isinstance(token, float):
            stack.append(token)
        else:
            b = stack.pop()
            a = stack.pop()
            stack.append(ops[token](a, b))

    return stack[0]


if __name__ == "__main__":
    print("=== Config Expression Evaluation ===")

    variables = {
        "revenue": 1000000,
        "cost": 750000,
        "tax_rate": 0.21,
        "discount": 50000,
    }

    expressions = [
        ("revenue - cost", 250000),
        ("(revenue - cost) * tax_rate", 52500),
        ("revenue - cost - discount", 200000),
        ("(revenue - cost - discount) * (1 + tax_rate)", 242000),
    ]

    for expr, expected in expressions:
        result = evaluate_config_expression(expr, variables)
        status = "PASS" if abs(result - expected) < 0.01 else "FAIL"
        print(f"  [{status}] {expr} = {result} (expected {expected})")
