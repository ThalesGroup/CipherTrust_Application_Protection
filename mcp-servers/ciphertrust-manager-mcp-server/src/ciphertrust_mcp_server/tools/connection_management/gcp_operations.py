"""GCP connection operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import GCP_PARAMETERS, CONNECTION_OPERATIONS


class GCPOperations(ConnectionOperations):
    """GCP connection operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported GCP operations."""
        return CONNECTION_OPERATIONS["gcp"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for GCP operations."""
        return {
            "gcp_params": {
                "type": "object",
                "properties": GCP_PARAMETERS,
                "description": "GCP-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for GCP."""
        return {
            "create": {
                "required": ["name"],
                "optional": ["key_file", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
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
                "optional": ["name", "key_file", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "test": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute GCP connection operation."""
        gcp_params = params.get("gcp_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "gcp", action]
        
        # Add action-specific parameters
        if action == "create":
            if gcp_params.get("name"):
                cmd.extend(["--name", gcp_params["name"]])
            if gcp_params.get("key_file"):
                cmd.extend(["--key-file", gcp_params["key_file"]])
            if gcp_params.get("products"):
                cmd.extend(["--products", gcp_params["products"]])
            if gcp_params.get("description"):
                cmd.extend(["--description", gcp_params["description"]])
            if gcp_params.get("meta"):
                cmd.extend(["--meta", gcp_params["meta"]])
            if gcp_params.get("labels"):
                cmd.extend(["--labels", gcp_params["labels"]])
            if gcp_params.get("json_file"):
                cmd.extend(["--json-file", gcp_params["json_file"]])
                
        elif action == "list":
            if gcp_params.get("name"):
                cmd.extend(["--name", gcp_params["name"]])
            if gcp_params.get("cloudname"):
                cmd.extend(["--cloudname", gcp_params["cloudname"]])
            if gcp_params.get("category"):
                cmd.extend(["--category", gcp_params["category"]])
            if gcp_params.get("products"):
                cmd.extend(["--products", gcp_params["products"]])
            if gcp_params.get("limit"):
                cmd.extend(["--limit", str(gcp_params["limit"])])
            if gcp_params.get("skip"):
                cmd.extend(["--skip", str(gcp_params["skip"])])
            if gcp_params.get("fields"):
                cmd.extend(["--fields", gcp_params["fields"]])
            if gcp_params.get("labels_query"):
                cmd.extend(["--labels-query", gcp_params["labels_query"]])
            if gcp_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", gcp_params["lastconnectionafter"]])
            if gcp_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", gcp_params["lastconnectionbefore"]])
            if gcp_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", gcp_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", gcp_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", gcp_params["id"]])
            if gcp_params.get("force"):
                cmd.append("--force")
                
        elif action == "modify":
            cmd.extend(["--id", gcp_params["id"]])
            if gcp_params.get("name"):
                cmd.extend(["--name", gcp_params["name"]])
            if gcp_params.get("key_file"):
                cmd.extend(["--key-file", gcp_params["key_file"]])
            if gcp_params.get("products"):
                cmd.extend(["--products", gcp_params["products"]])
            if gcp_params.get("description"):
                cmd.extend(["--description", gcp_params["description"]])
            if gcp_params.get("meta"):
                cmd.extend(["--meta", gcp_params["meta"]])
            if gcp_params.get("labels"):
                cmd.extend(["--labels", gcp_params["labels"]])
            if gcp_params.get("json_file"):
                cmd.extend(["--json-file", gcp_params["json_file"]])
                
        elif action == "test":
            cmd.extend(["--id", gcp_params["id"]])
            
        else:
            raise ValueError(f"Unsupported GCP action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 