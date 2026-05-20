from __future__ import annotations
import ast
from typing import Dict
import pandas as pd
from .operators import ALLOWED_OPERATORS, ALLOWED_FIELDS


class UnsafeExpressionError(ValueError):
    pass


class SafeExpressionEvaluator(ast.NodeVisitor):
    """Safely evaluates a small alpha-expression DSL against market matrices."""

    def __init__(self, context: Dict[str, pd.DataFrame]):
        self.context = context

    def visit_Expression(self, node: ast.Expression):
        return self.visit(node.body)

    def visit_Name(self, node: ast.Name):
        if node.id in ALLOWED_FIELDS:
            return self.context[node.id]
        if node.id in ALLOWED_OPERATORS:
            return ALLOWED_OPERATORS[node.id]
        raise UnsafeExpressionError(f"Unknown symbol: {node.id}")

    def visit_Call(self, node: ast.Call):
        func = self.visit(node.func)
        if func not in ALLOWED_OPERATORS.values():
            raise UnsafeExpressionError("Only whitelisted operators can be called")
        args = [self.visit(a) for a in node.args]
        if node.keywords:
            raise UnsafeExpressionError("Keyword arguments are not allowed")
        return func(*args)

    def visit_Constant(self, node: ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise UnsafeExpressionError("Only numeric constants are allowed")

    def visit_UnaryOp(self, node: ast.UnaryOp):
        val = self.visit(node.operand)
        if isinstance(node.op, ast.USub):
            return -val
        if isinstance(node.op, ast.UAdd):
            return val
        raise UnsafeExpressionError("Unsupported unary operator")

    def visit_BinOp(self, node: ast.BinOp):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        raise UnsafeExpressionError("Unsupported binary operator")

    def generic_visit(self, node):
        raise UnsafeExpressionError(f"Unsupported expression node: {type(node).__name__}")


def evaluate_expression(expression: str, context: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    tree = ast.parse(expression, mode="eval")
    evaluator = SafeExpressionEvaluator(context)
    result = evaluator.visit(tree)
    if not isinstance(result, pd.DataFrame):
        raise UnsafeExpressionError("Expression must return a DataFrame signal")
    return result.replace([float("inf"), float("-inf")], 0.0).fillna(0.0)
