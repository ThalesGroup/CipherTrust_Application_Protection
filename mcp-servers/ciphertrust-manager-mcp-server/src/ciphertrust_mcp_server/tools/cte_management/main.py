from typing import Any, Optional, Dict, List
from pydantic import BaseModel, Field
from ..base import BaseTool

from .constants import JSON_EXAMPLES, COMMON_SCHEMA_PROPERTIES
from .policy_operations import PolicyOperations
from .user_set_operations import UserSetOperations
from .process_set_operations import ProcessSetOperations
from .resource_set_operations import ResourceSetOperations
from .client_operations import ClientOperations
from .client_group_operations import ClientGroupOperations
from .profile_operations import ProfileOperations
from .csi_operations import CSIOperations

class CTEManagementTool(BaseTool):
    """Unified CTE Management Tool that delegates to specialized sub-tools.
    
    This tool provides a single interface for all CTE operations while internally
    organizing functionality into logical sub-tools for better maintainability.
    """
    
    def __init__(self):
        super().__init__()
        # Initialize all sub-tools with the execute_with_domain method
        self.sub_tools = {
            'policy': PolicyOperations(self.execute_with_domain),
            'user_set': UserSetOperations(self.execute_with_domain),
            'process_set': ProcessSetOperations(self.execute_with_domain),
            'resource_set': ResourceSetOperations(self.execute_with_domain),
            'client': ClientOperations(self.execute_with_domain),
            'client_group': ClientGroupOperations(self.execute_with_domain),
            'profile': ProfileOperations(self.execute_with_domain),
            'csi': CSIOperations(self.execute_with_domain)
        }
        
        # Build operation mapping
        self.operation_mapping = {}
        for tool_name, tool in self.sub_tools.items():
            for operation in tool.get_operations():
                self.operation_mapping[operation] = tool
    
    @property
    def name(self) -> str:
        return "cte_management"
    
    @property
    def description(self) -> str:
        return (
            "CTE (CipherTrust Transparent Encryption) management operations. "
            "Supports policies, user sets, process sets, resource sets, clients, profiles, and CSI storage groups. "
            "Each action has specific required and optional parameters - see action_requirements in schema for details."
        )
    
    def get_schema(self) -> dict[str, Any]:
        """Build complete schema from all sub-tools"""
        # Collect all operations
        all_operations = []
        for tool in self.sub_tools.values():
            all_operations.extend(tool.get_operations())
        
        # Start with common properties
        properties = {
            "action": {
                "type": "string",
                "enum": sorted(all_operations),
                "description": "The CTE operation to perform. Choose based on what you want to accomplish."
            },
            **COMMON_SCHEMA_PROPERTIES
        }
        
        # Add properties from each sub-tool
        for tool in self.sub_tools.values():
            properties.update(tool.get_schema_properties())
        
        # Collect action requirements from all sub-tools
        action_requirements = {}
        for tool in self.sub_tools.values():
            action_requirements.update(tool.get_action_requirements())
        
        return {
            "type": "object",
            "properties": properties,
            "required": ["action"],
            "additionalProperties": False,
            "action_requirements": action_requirements
        }
    
    async def execute(self, action: str, **kwargs: Any) -> Any:
        """Execute CTE operation by delegating to appropriate sub-tool"""
        # Find the appropriate sub-tool for this action
        if action not in self.operation_mapping:
            return {"error": f"Unknown action: {action}"}
        
        sub_tool = self.operation_mapping[action]
        
        # Validate action-specific requirements
        if not self._validate_action_params(action, kwargs):
            schema = self.get_schema()
            requirements = schema.get("action_requirements", {}).get(action, {})
            required_params = requirements.get("required", [])
            example = requirements.get("example", {})
            return {
                "error": f"Missing required parameters for action '{action}'",
                "required": required_params,
                "example": example
            }
        
        # Delegate to the appropriate sub-tool
        try:
            return await sub_tool.execute_operation(action, **kwargs)
        except Exception as e:
            return {"error": f"Failed to execute {action}: {str(e)}"}
    
    def _validate_action_params(self, action: str, params: dict) -> bool:
        """Validate that required parameters are present for the action"""
        schema = self.get_schema()
        requirements = schema.get("action_requirements", {}).get(action, {})
        required_params = requirements.get("required", [])
        
        # Special case for user_set_create: allow either user_json or user_json_file
        if action == "user_set_create":
            if not (params.get("user_json") or params.get("user_json_file")):
                return False
            return True
        
        for param in required_params:
            if param not in params or params[param] is None:
                return False
        return True