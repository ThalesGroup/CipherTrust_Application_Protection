"""Base classes for CTE sub-tools"""

from typing import Any, Dict, Optional
from abc import ABC, abstractmethod

class CTESubTool(ABC):
    """Base class for CTE sub-tools"""
    
    def __init__(self, execute_with_domain_func):
        self.execute_with_domain = execute_with_domain_func
    
    @abstractmethod
    def get_operations(self) -> list[str]:
        """Return list of operations this sub-tool handles"""
        pass
    
    @abstractmethod
    def get_schema_properties(self) -> dict[str, Any]:
        """Return schema properties specific to this sub-tool"""
        pass
    
    @abstractmethod
    def get_action_requirements(self) -> dict[str, Any]:
        """Return action requirements for this sub-tool's operations"""
        pass
    
    @abstractmethod
    async def execute_operation(self, action: str, **kwargs: Any) -> Any:
        """Execute the specified operation"""
        pass
