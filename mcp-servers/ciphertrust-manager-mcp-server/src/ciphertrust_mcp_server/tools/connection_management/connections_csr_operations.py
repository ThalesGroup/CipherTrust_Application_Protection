"""Connections CSR operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import CONNECTIONS_CSR_PARAMETERS, CONNECTION_OPERATIONS


class ConnectionsCSROperations(ConnectionOperations):
    """Connections CSR operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported Connections CSR operations."""
        return CONNECTION_OPERATIONS["connections_csr"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for Connections CSR operations."""
        return {
            "connections_csr_params": {
                "type": "object",
                "properties": CONNECTIONS_CSR_PARAMETERS,
                "description": "Connections CSR-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for Connections CSR."""
        return {
            "create": {
                "required": ["common_name"],
                "optional": ["country", "state", "locality", "organization", "organizational_unit", "email", "key_size", "output_file", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute Connections CSR operation."""
        csr_params = params.get("connections_csr_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "connections", "csr", action]
        
        # Add action-specific parameters
        if action == "create":
            if csr_params.get("common_name"):
                cmd.extend(["--common-name", csr_params["common_name"]])
            if csr_params.get("country"):
                cmd.extend(["--country", csr_params["country"]])
            if csr_params.get("state"):
                cmd.extend(["--state", csr_params["state"]])
            if csr_params.get("locality"):
                cmd.extend(["--locality", csr_params["locality"]])
            if csr_params.get("organization"):
                cmd.extend(["--organization", csr_params["organization"]])
            if csr_params.get("organizational_unit"):
                cmd.extend(["--organizational-unit", csr_params["organizational_unit"]])
            if csr_params.get("email"):
                cmd.extend(["--email", csr_params["email"]])
            if csr_params.get("key_size"):
                cmd.extend(["--key-size", str(csr_params["key_size"])])
            if csr_params.get("output_file"):
                cmd.extend(["--output-file", csr_params["output_file"]])
            if csr_params.get("products"):
                cmd.extend(["--products", csr_params["products"]])
            if csr_params.get("description"):
                cmd.extend(["--description", csr_params["description"]])
            if csr_params.get("meta"):
                cmd.extend(["--meta", csr_params["meta"]])
            if csr_params.get("labels"):
                cmd.extend(["--labels", csr_params["labels"]])
            if csr_params.get("json_file"):
                cmd.extend(["--json-file", csr_params["json_file"]])
                
        else:
            raise ValueError(f"Unsupported Connections CSR action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 