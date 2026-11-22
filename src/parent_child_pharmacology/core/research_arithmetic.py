"""Bounded arithmetic for aggregate-data clients; no Python execution or file access."""

import ast
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation, localcontext

SCHEMA = {
    "type": "function",
    "function": {
        "name": "calculate_aggregate_expression",
        "description": "Compute arithmetic on retrieved aggregate research numbers, not a personal dose or clinical recommendation. Use explicit parentheses and each row's own denominator. No evidence lookup is performed.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "maxLength": 2048},
                "decimal_places": {"type": "integer", "minimum": 0, "maximum": 8},
            },
            "required": ["expression", "decimal_places"],
            "additionalProperties": False,
        },
    },
}


def calculate(expression, decimal_places):
    if not isinstance(expression, str) or len(expression) > 2048:
        raise ValueError("Expression must be a bounded string")
    if type(decimal_places) is not int or not 0 <= decimal_places <= 8:
        raise ValueError("Use zero to eight decimal places")
    tree = ast.parse(expression, mode="eval")
    if sum(1 for _ in ast.walk(tree)) > 100:
        raise ValueError("Expression is too complex")

    def visit(node, depth=0):
        if depth > 16:
            raise ValueError("Expression is too deep")
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            token = ast.get_source_segment(expression, node)
            if len(token) > 32:
                raise ValueError("Numeric literal is too long")
            value = Decimal(token)
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand, depth + 1)
            if isinstance(node.op, ast.USub):
                value = -value
        elif isinstance(node, ast.BinOp) and isinstance(
            node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)
        ):
            left, right = visit(node.left, depth + 1), visit(node.right, depth + 1)
            if isinstance(node.op, ast.Add):
                value = left + right
            elif isinstance(node.op, ast.Sub):
                value = left - right
            elif isinstance(node.op, ast.Mult):
                value = left * right
            else:
                if not right:
                    raise ValueError("Denominator must not be zero")
                value = left / right
        else:
            raise ValueError("Only numeric literals, parentheses and + - * / are allowed")
        if not value.is_finite() or abs(value) > Decimal("1e20"):
            raise ValueError("Numeric result is outside the allowed range")
        return value

    with localcontext() as context:
        context.prec = 50
        try:
            result = visit(tree.body).quantize(
                Decimal(1).scaleb(-decimal_places), rounding=ROUND_HALF_UP
            )
        except InvalidOperation as exc:
            raise ValueError("Invalid arithmetic") from exc
    return {
        "expression": expression,
        "result": format(result, f".{decimal_places}f"),
        "decimal_places": decimal_places,
        "scope": "Arithmetic only; not an evidence or causation judgment",
    }
