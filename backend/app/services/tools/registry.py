from typing import Dict, Type
from .base import BaseTool

class ToolRegistry:
    _tools: Dict[str, Type[BaseTool]] = {}

    @classmethod
    def register(cls, tool_type: str):
        def decorator(tool_cls: Type[BaseTool]):
            cls._tools[tool_type] = tool_cls
            return tool_cls
        return decorator

    @classmethod
    def get_tool(cls, tool_type: str, **kwargs) -> BaseTool:
        tool_cls = cls._tools.get(tool_type)
        if not tool_cls:
            raise ValueError(f"Unknown tool type: {tool_type}")
        return tool_cls(**kwargs)
