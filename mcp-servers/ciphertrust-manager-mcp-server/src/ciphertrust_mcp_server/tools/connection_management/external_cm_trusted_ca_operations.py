"""External CM Trusted CA operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import EXTERNAL_CM_TRUSTED_CA_PARAMETERS, CONNECTION_OPERATIONS


class ExternalCMTrustedCAOperations(ConnectionOperations):
    """External CM Trusted CA operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported External CM Trusted CA operations."""
        return CONNECTION_OPERATIONS["external_cm_trusted_ca"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for External CM Trusted CA operations."""
        return {
            "external_cm_trusted_ca_params": {
                "type": "object",
                "properties": EXTERNAL_CM_TRUSTED_CA_PARAMETERS,
                "description": "External CM Trusted CA-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for External CM Trusted CA."""
        return {
            "add": {
                "required": ["connection_id"],
                "optional": ["ca_certificate", "ca_certificate_file", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "list": {
                "required": ["connection_id"],
                "optional": ["name", "cloudname", "category", "products", "limit", "skip", "fields", "labels_query", "lastconnectionafter", "lastconnectionbefore", "lastconnectionok", "domain", "auth_domain"]
            },
            "get": {
                "required": ["connection_id", "id"],
                "optional": ["domain", "auth_domain"]
            },
            "delete": {
                "required": ["connection_id", "id"],
                "optional": ["force", "domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute External CM Trusted CA operation."""
        trusted_ca_params = params.get("external_cm_trusted_ca_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "external-cm", "trusted-ca", action]
        
        # Add connection ID for all operations
        if trusted_ca_params.get("connection_id"):
            cmd.extend(["--connection-id", trusted_ca_params["connection_id"]])
        
        # Add action-specific parameters
        if action == "add":
            if trusted_ca_params.get("ca_certificate"):
                cmd.extend(["--ca-certificate", trusted_ca_params["ca_certificate"]])
            if trusted_ca_params.get("ca_certificate_file"):
                cmd.extend(["--ca-certificate-file", trusted_ca_params["ca_certificate_file"]])
            if trusted_ca_params.get("products"):
                cmd.extend(["--products", trusted_ca_params["products"]])
            if trusted_ca_params.get("description"):
                cmd.extend(["--description", trusted_ca_params["description"]])
            if trusted_ca_params.get("meta"):
                cmd.extend(["--meta", trusted_ca_params["meta"]])
            if trusted_ca_params.get("labels"):
                cmd.extend(["--labels", trusted_ca_params["labels"]])
            if trusted_ca_params.get("json_file"):
                cmd.extend(["--json-file", trusted_ca_params["json_file"]])
                
        elif action == "list":
            if trusted_ca_params.get("name"):
                cmd.extend(["--name", trusted_ca_params["name"]])
            if trusted_ca_params.get("cloudname"):
                cmd.extend(["--cloudname", trusted_ca_params["cloudname"]])
            if trusted_ca_params.get("category"):
                cmd.extend(["--category", trusted_ca_params["category"]])
            if trusted_ca_params.get("products"):
                cmd.extend(["--products", trusted_ca_params["products"]])
            if trusted_ca_params.get("limit"):
                cmd.extend(["--limit", str(trusted_ca_params["limit"])])
            if trusted_ca_params.get("skip"):
                cmd.extend(["--skip", str(trusted_ca_params["skip"])])
            if trusted_ca_params.get("fields"):
                cmd.extend(["--fields", trusted_ca_params["fields"]])
            if trusted_ca_params.get("labels_query"):
                cmd.extend(["--labels-query", trusted_ca_params["labels_query"]])
            if trusted_ca_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", trusted_ca_params["lastconnectionafter"]])
            if trusted_ca_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", trusted_ca_params["lastconnectionbefore"]])
            if trusted_ca_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", trusted_ca_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", trusted_ca_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", trusted_ca_params["id"]])
            if trusted_ca_params.get("force"):
                cmd.append("--force")
                
        else:
            raise ValueError(f"Unsupported External CM Trusted CA action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 