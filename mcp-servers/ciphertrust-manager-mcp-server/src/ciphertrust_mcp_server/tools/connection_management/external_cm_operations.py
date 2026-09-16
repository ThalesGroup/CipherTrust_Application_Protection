"""External CM connection operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import EXTERNAL_CM_PARAMETERS, CONNECTION_OPERATIONS


class ExternalCMOperations(ConnectionOperations):
    """External CM connection operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported External CM operations."""
        return CONNECTION_OPERATIONS["external_cm"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for External CM operations."""
        return {
            "external_cm_params": {
                "type": "object",
                "properties": EXTERNAL_CM_PARAMETERS,
                "description": "External CM-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for External CM."""
        return {
            "create": {
                "required": ["name"],
                "optional": ["server_url", "username", "password", "certificate_file", "nodes_json_file", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
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
                "optional": ["name", "server_url", "username", "password", "certificate_file", "nodes_json_file", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "test": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute External CM connection operation."""
        external_cm_params = params.get("external_cm_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "external-cm", action]
        
        # Add action-specific parameters
        if action == "create":
            if external_cm_params.get("name"):
                cmd.extend(["--name", external_cm_params["name"]])
            if external_cm_params.get("server_url"):
                cmd.extend(["--server-url", external_cm_params["server_url"]])
            if external_cm_params.get("username"):
                cmd.extend(["--username", external_cm_params["username"]])
            if external_cm_params.get("password"):
                cmd.extend(["--password", external_cm_params["password"]])
            if external_cm_params.get("certificate_file"):
                cmd.extend(["--certificate-file", external_cm_params["certificate_file"]])
            if external_cm_params.get("nodes_json_file"):
                cmd.extend(["--nodes-json-file", external_cm_params["nodes_json_file"]])
            if external_cm_params.get("products"):
                cmd.extend(["--products", external_cm_params["products"]])
            if external_cm_params.get("description"):
                cmd.extend(["--description", external_cm_params["description"]])
            if external_cm_params.get("meta"):
                cmd.extend(["--meta", external_cm_params["meta"]])
            if external_cm_params.get("labels"):
                cmd.extend(["--labels", external_cm_params["labels"]])
            if external_cm_params.get("json_file"):
                cmd.extend(["--json-file", external_cm_params["json_file"]])
                
        elif action == "list":
            if external_cm_params.get("name"):
                cmd.extend(["--name", external_cm_params["name"]])
            if external_cm_params.get("cloudname"):
                cmd.extend(["--cloudname", external_cm_params["cloudname"]])
            if external_cm_params.get("category"):
                cmd.extend(["--category", external_cm_params["category"]])
            if external_cm_params.get("products"):
                cmd.extend(["--products", external_cm_params["products"]])
            if external_cm_params.get("limit"):
                cmd.extend(["--limit", str(external_cm_params["limit"])])
            if external_cm_params.get("skip"):
                cmd.extend(["--skip", str(external_cm_params["skip"])])
            if external_cm_params.get("fields"):
                cmd.extend(["--fields", external_cm_params["fields"]])
            if external_cm_params.get("labels_query"):
                cmd.extend(["--labels-query", external_cm_params["labels_query"]])
            if external_cm_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", external_cm_params["lastconnectionafter"]])
            if external_cm_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", external_cm_params["lastconnectionbefore"]])
            if external_cm_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", external_cm_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", external_cm_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", external_cm_params["id"]])
            if external_cm_params.get("force"):
                cmd.append("--force")
                
        elif action == "modify":
            cmd.extend(["--id", external_cm_params["id"]])
            if external_cm_params.get("name"):
                cmd.extend(["--name", external_cm_params["name"]])
            if external_cm_params.get("server_url"):
                cmd.extend(["--server-url", external_cm_params["server_url"]])
            if external_cm_params.get("username"):
                cmd.extend(["--username", external_cm_params["username"]])
            if external_cm_params.get("password"):
                cmd.extend(["--password", external_cm_params["password"]])
            if external_cm_params.get("certificate_file"):
                cmd.extend(["--certificate-file", external_cm_params["certificate_file"]])
            if external_cm_params.get("nodes_json_file"):
                cmd.extend(["--nodes-json-file", external_cm_params["nodes_json_file"]])
            if external_cm_params.get("products"):
                cmd.extend(["--products", external_cm_params["products"]])
            if external_cm_params.get("description"):
                cmd.extend(["--description", external_cm_params["description"]])
            if external_cm_params.get("meta"):
                cmd.extend(["--meta", external_cm_params["meta"]])
            if external_cm_params.get("labels"):
                cmd.extend(["--labels", external_cm_params["labels"]])
            if external_cm_params.get("json_file"):
                cmd.extend(["--json-file", external_cm_params["json_file"]])
                
        elif action == "test":
            cmd.extend(["--id", external_cm_params["id"]])
            
        else:
            raise ValueError(f"Unsupported External CM action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 