"""Base classes for CCKM operations."""

from typing import Any, Dict, List, Callable
from abc import ABC, abstractmethod


class CCKMOperations(ABC):
    """Base class for CCKM operations."""
    
    def __init__(self, execute_command: Callable):
        self.execute_command = execute_command
    
    @abstractmethod
    def get_operations(self) -> List[str]:
        """Return list of supported operations."""
        pass
    
    @abstractmethod
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for this operation type."""
        pass
    
    @abstractmethod
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements."""
        pass
    
    @abstractmethod
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute the specified operation."""
        pass 