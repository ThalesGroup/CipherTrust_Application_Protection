"""Confidential Computing connection operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import CONFIDENTIAL_COMPUTING_PARAMETERS, CONNECTION_OPERATIONS


class ConfidentialComputingOperations(ConnectionOperations):
    """Confidential Computing connection operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported Confidential Computing operations."""
        return CONNECTION_OPERATIONS["confidential_computing"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for Confidential Computing operations."""
        return {
            "confidential_computing_params": {
                "type": "object",
                "properties": CONFIDENTIAL_COMPUTING_PARAMETERS,
                "description": "Confidential Computing-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for Confidential Computing."""
        return {
            "create": {
                "required": ["name"],
                "optional": ["clientid", "secret", "endpoint_url", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "list": {
                "required": [],
                "optional": ["name", "cloudname", "category", "products", "limit", "skip", "fields", "labels_query", "lastconnectionafter", "lastconnectionbefore", "lastconnectionok", "domain", "auth_domain"]
            },
            "get": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "delete": {
                "required": ["id"],
                "optional": ["force", "domain", "auth_domain"]
            },
            "modify": {
                "required": ["id"],
                "optional": ["name", "clientid", "secret", "endpoint_url", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "test": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute Confidential Computing connection operation."""
        confidential_computing_params = params.get("confidential_computing_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "confidential-computing", action]
        
        # Add action-specific parameters
        if action == "create":
            if confidential_computing_params.get("name"):
                cmd.extend(["--name", confidential_computing_params["name"]])
            if confidential_computing_params.get("clientid"):
                cmd.extend(["--clientid", confidential_computing_params["clientid"]])
            if confidential_computing_params.get("secret"):
                cmd.extend(["--secret", confidential_computing_params["secret"]])
            if confidential_computing_params.get("endpoint_url"):
                cmd.extend(["--endpoint-url", confidential_computing_params["endpoint_url"]])
            if confidential_computing_params.get("products"):
                cmd.extend(["--products", confidential_computing_params["products"]])
            if confidential_computing_params.get("description"):
                cmd.extend(["--description", confidential_computing_params["description"]])
            if confidential_computing_params.get("meta"):
                cmd.extend(["--meta", confidential_computing_params["meta"]])
            if confidential_computing_params.get("labels"):
                cmd.extend(["--labels", confidential_computing_params["labels"]])
            if confidential_computing_params.get("json_file"):
                cmd.extend(["--json-file", confidential_computing_params["json_file"]])
                
        elif action == "list":
            if confidential_computing_params.get("name"):
                cmd.extend(["--name", confidential_computing_params["name"]])
            if confidential_computing_params.get("cloudname"):
                cmd.extend(["--cloudname", confidential_computing_params["cloudname"]])
            if confidential_computing_params.get("category"):
                cmd.extend(["--category", confidential_computing_params["category"]])
            if confidential_computing_params.get("products"):
                cmd.extend(["--products", confidential_computing_params["products"]])
            if confidential_computing_params.get("limit"):
                cmd.extend(["--limit", str(confidential_computing_params["limit"])])
            if confidential_computing_params.get("skip"):
                cmd.extend(["--skip", str(confidential_computing_params["skip"])])
            if confidential_computing_params.get("fields"):
                cmd.extend(["--fields", confidential_computing_params["fields"]])
            if confidential_computing_params.get("labels_query"):
                cmd.extend(["--labels-query", confidential_computing_params["labels_query"]])
            if confidential_computing_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", confidential_computing_params["lastconnectionafter"]])
            if confidential_computing_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", confidential_computing_params["lastconnectionbefore"]])
            if confidential_computing_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", confidential_computing_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", confidential_computing_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", confidential_computing_params["id"]])
            if confidential_computing_params.get("force"):
                cmd.append("--force")
                
        elif action == "modify":
            cmd.extend(["--id", confidential_computing_params["id"]])
            if confidential_computing_params.get("name"):
                cmd.extend(["--name", confidential_computing_params["name"]])
            if confidential_computing_params.get("clientid"):
                cmd.extend(["--clientid", confidential_computing_params["clientid"]])
            if confidential_computing_params.get("secret"):
                cmd.extend(["--secret", confidential_computing_params["secret"]])
            if confidential_computing_params.get("endpoint_url"):
                cmd.extend(["--endpoint-url", confidential_computing_params["endpoint_url"]])
            if confidential_computing_params.get("products"):
                cmd.extend(["--products", confidential_computing_params["products"]])
            if confidential_computing_params.get("description"):
                cmd.extend(["--description", confidential_computing_params["description"]])
            if confidential_computing_params.get("meta"):
                cmd.extend(["--meta", confidential_computing_params["meta"]])
            if confidential_computing_params.get("labels"):
                cmd.extend(["--labels", confidential_computing_params["labels"]])
            if confidential_computing_params.get("json_file"):
                cmd.extend(["--json-file", confidential_computing_params["json_file"]])
                
        elif action == "test":
            cmd.extend(["--id", confidential_computing_params["id"]])
            
        else:
            raise ValueError(f"Unsupported Confidential Computing action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 