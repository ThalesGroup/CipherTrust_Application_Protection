"""Smart ID resolution for CCKM operations.

This module provides functionality to automatically resolve key aliases and ARNs
to their corresponding key IDs, making the tools more user-friendly.
"""
import re
import json
from typing import Dict, Any, Optional, Tuple, Protocol


class OperationsProtocol(Protocol):
    """Protocol for operations that can execute commands."""
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute an operation."""
        ...


class SmartIDResolver:
    """Resolves key aliases and ARNs to key IDs automatically."""
    
    def __init__(self, operations: OperationsProtocol):
        self.operations = operations
    
    def is_uuid(self, key_id: str) -> bool:
        """Check if a string is a UUID format."""
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, key_id.lower()))
    
    def is_arn(self, key_id: str) -> bool:
        """Check if a string is an AWS ARN format."""
        return key_id.startswith('arn:aws:kms:')
    
    def is_alias(self, key_id: str) -> bool:
        """Check if a string looks like an alias (not UUID or ARN)."""
        return not self.is_uuid(key_id) and not self.is_arn(key_id)
    
    def extract_key_id_from_arn(self, arn: str) -> str:
        """Extract the key ID from an AWS ARN."""
        # ARN format: arn:aws:kms:region:account:key/key-id
        match = re.search(r'/key/([^/]+)$', arn)
        if match:
            return match.group(1)
        raise ValueError(f"Could not extract key ID from ARN: {arn}")
    
    async def resolve_key_id(self, key_identifier: str, cloud_provider: str, aws_params: Dict[str, Any]) -> str:
        """Resolve a key identifier (alias, ARN, or UUID) to a key ID."""
        
        # If it's already a UUID, return it as is
        if self.is_uuid(key_identifier):
            return key_identifier
        
        # Prepare the list parameters
        list_params = {
            "cloud_provider": cloud_provider,
            "aws_keys_params": {}
        }
        
        # Determine the filter to use
        if self.is_arn(key_identifier):
            # Use ARN filter
            list_params["aws_keys_params"]["arn"] = key_identifier
        else:
            # Use alias filter
            list_params["aws_keys_params"]["alias"] = key_identifier
        
        # Add any additional filters that might help
        if "region" in aws_params:
            list_params["aws_keys_params"]["region"] = aws_params["region"]
        if "kms" in aws_params:
            list_params["aws_keys_params"]["kms"] = aws_params["kms"]
        
        # Call the list operation
        try:
            result = await self.operations.execute_operation("keys_list", list_params)
            
            # Parse the result
            if isinstance(result, str):
                result_data = json.loads(result)
            else:
                result_data = result
            
            # Extract the key ID from the response
            resources = result_data.get("resources", [])
            
            if not resources:
                raise ValueError(f"No key found for identifier: {key_identifier}")
            
            if len(resources) > 1:
                raise ValueError(f"Multiple keys found for identifier: {key_identifier}. Please be more specific.")
            
            key_id = resources[0].get("id")
            if not key_id:
                raise ValueError(f"Key found but no ID in response for: {key_identifier}")
            
            return key_id
            
        except Exception as e:
            raise ValueError(f"Failed to resolve key ID for {key_identifier}: {str(e)}")
    
    def needs_resolution(self, key_identifier: str) -> bool:
        """Check if a key identifier needs resolution (not a UUID)."""
        return not self.is_uuid(key_identifier)
    
    def get_resolution_type(self, key_identifier: str) -> str:
        """Get the type of resolution needed."""
        if self.is_arn(key_identifier):
            return "arn"
        elif self.is_alias(key_identifier):
            return "alias"
        else:
            return "uuid"


def create_smart_resolver(operations: OperationsProtocol) -> SmartIDResolver:
    """Create a smart ID resolver instance."""
    return SmartIDResolver(operations) 