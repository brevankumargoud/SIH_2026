import ast
import operator
from typing import Dict, Any
from app.schemas.agent import ToolResult
from app.services.tools.base import BaseTool
from app.services.tools.registry import ToolRegistry

# Safe evaluation for basic math expressions
_OP_MAP = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.Pow: operator.pow
}

def _eval_expr(node):
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        return _OP_MAP[type(node.op)](_eval_expr(node.left), _eval_expr(node.right))
    elif isinstance(node, ast.UnaryOp):
        return _OP_MAP[type(node.op)](_eval_expr(node.operand))
    else:
        raise TypeError(node)

def safe_eval(expr: str):
    return _eval_expr(ast.parse(expr, mode='eval').body)

@ToolRegistry.register("calculation")
class CalculationTool(BaseTool):
    def __init__(self, **kwargs):
        pass

    @property
    def name(self) -> str:
        return "Calculation Tool"

    @property
    def description(self) -> str:
        return "Perform deterministic arithmetic calculations. Supports +, -, *, /, **."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "The math expression (e.g., '14 * 5')."}
            },
            "required": ["expression"]
        }

    def execute(self, expression: str, **kwargs) -> ToolResult:
        if not expression:
            return ToolResult(success=False, output=None, error="Expression is required")
        try:
            result = safe_eval(expression)
            return ToolResult(
                success=True,
                output=f"Expression: {expression}\nResult: {result}",
                metadata={"expression": expression, "result": result}
            )
        except Exception as e:
            return ToolResult(success=False, output=None, error=f"Invalid expression: {str(e)}")
