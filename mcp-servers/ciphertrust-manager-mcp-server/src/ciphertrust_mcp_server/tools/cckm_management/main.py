"""Main CCKM Management Tool."""

from typing import Any, Dict, List
from ..base import BaseTool
from .constants import COMMON_SCHEMA_PROPERTIES, CLOUD_OPERATIONS
from .aws_operations import AWSOperations
from .azure_operations import AzureOperations
from .oci_operations import OCIOperations
from .google_operations import GoogleOperations
from .microsoft_operations import MicrosoftOperations
from .ekm_operations import EKMOperations
from .gws_operations import GWSOperations


class CCKMManagementTool(BaseTool):
    """Unified CCKM Management Tool that delegates to specialized cloud provider operations.
    
    This tool provides a single interface for all CCKM operations while internally
    organizing functionality by cloud provider for better maintainability.
    """
    
    def __init__(self):
        super().__init__()
        # Initialize all cloud provider operations
        self.cloud_operations = {
            'aws': AWSOperations(self.execute_with_domain),
            'azure': AzureOperations(self.execute_with_domain),
            'oci': OCIOperations(self.execute_with_domain),
            'google': GoogleOperations(self.execute_with_domain),
            'microsoft': MicrosoftOperations(self.execute_with_domain),
            'ekm': EKMOperations(self.execute_with_domain),
            'gws': GWSOperations(self.execute_with_domain),
            # TODO: Add other cloud providers as they are implemented
            # 'sap-dc': SAPDCOperations(self.execute_with_domain),
            # 'salesforce': SalesforceOperations(self.execute_with_domain),
            # 'virtual': VirtualOperations(self.execute_with_domain),
            # 'hsm': HSMOperations(self.execute_with_domain),
            # 'external-cm': ExternalCMOperations(self.execute_with_domain),
            # 'dsm': DSMOperations(self.execute_with_domain),
        }
        
        # Build operation mapping
        self.operation_mapping = {}
        for cloud_provider, operations in self.cloud_operations.items():
            for operation in operations.get_operations():
                self.operation_mapping[f"{cloud_provider}_{operation}"] = (cloud_provider, operation)
    
    @property
    def name(self) -> str:
        return "cckm_management"
    
    @property
    def description(self) -> str:
        return (
            "CCKM (CipherTrust Cloud Key Manager) operations for managing cloud keys across various providers. "
            "Supports AWS, Azure, Google Cloud, OCI, SAP Data Custodian, Salesforce, Microsoft DKE, Virtual, HSM, GWS, EKM, External CM, and DSM. "
            "Each cloud provider has specific operations and parameters - see action_requirements in schema for details."
        )
    
    def get_schema(self) -> dict[str, Any]:
        """Build complete schema from all cloud providers"""
        # Collect all operations
        all_operations = []
        for cloud_provider, operations in self.cloud_operations.items():
            for operation in operations.get_operations():
                all_operations.append(f"{cloud_provider}_{operation}")
        
        # Start with common properties
        properties = {
            "action": {
                "type": "string",
                "enum": sorted(all_operations),
                "description": "The CCKM operation to perform. Format: {cloud_provider}_{operation} (e.g., aws_list, azure_create)"
            },
            **COMMON_SCHEMA_PROPERTIES
        }
        
        # Add properties from each cloud provider
        for cloud_provider, operations in self.cloud_operations.items():
            properties.update(operations.get_schema_properties())
        
        # Collect action requirements from all cloud providers
        action_requirements = {}
        for cloud_provider, operations in self.cloud_operations.items():
            cloud_requirements = operations.get_action_requirements()
            for operation, requirements in cloud_requirements.items():
                action_requirements[f"{cloud_provider}_{operation}"] = requirements
        
        return {
            "type": "object",
            "properties": properties,
            "required": ["action"],
            "additionalProperties": False,
            "action_requirements": action_requirements
        }
    
    async def execute(self, action: str, **kwargs: Any) -> Any:
        """Execute CCKM operation by delegating to appropriate cloud provider."""
        # Parse action to get cloud provider and operation
        if action not in self.operation_mapping:
            return {"error": f"Unknown action: {action}. Available actions: {list(self.operation_mapping.keys())}"}
        
        cloud_provider, operation = self.operation_mapping[action]
        
        # Get the appropriate cloud operations handler
        if cloud_provider not in self.cloud_operations:
            return {"error": f"Cloud provider {cloud_provider} not implemented yet"}
        
        cloud_ops = self.cloud_operations[cloud_provider]
        
        # Validate action-specific requirements
        if not self._validate_action_params(action, kwargs):
            schema = self.get_schema()
            requirements = schema.get("action_requirements", {}).get(action, {})
            required_params = requirements.get("required", [])
            return {"error": f"Missing required parameters for {action}: {required_params}"}
        
        # Execute the operation
        try:
            return await cloud_ops.execute_operation(operation, kwargs)
        except Exception as e:
            return {"error": f"Failed to execute {action}: {str(e)}"}
    
    def _validate_action_params(self, action: str, params: dict) -> bool:
        """Validate that required parameters are present for the action."""
        schema = self.get_schema()
        requirements = schema.get("action_requirements", {}).get(action, {})
        required_params = requirements.get("required", [])
        
        # Check if all required parameters are present
        for param in required_params:
            # Check in the main params and in cloud-specific params
            cloud_provider = action.split("_")[0]
            cloud_params_key = f"{cloud_provider}_params"
            
            if param not in params and (cloud_params_key not in params or param not in params[cloud_params_key]):
                return False
        
        return True 