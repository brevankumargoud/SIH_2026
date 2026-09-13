from abc import ABC, abstractmethod
from typing import Dict, Any
from app.schemas.agent import ToolResult

class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        """JSON schema representation of expected arguments"""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        pass
