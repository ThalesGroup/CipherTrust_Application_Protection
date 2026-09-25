"""Luna HSM Server operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import LUNA_HSM_SERVER_PARAMETERS, CONNECTION_OPERATIONS


class LunaHSMServerOperations(ConnectionOperations):
    """Luna HSM Server operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported Luna HSM Server operations."""
        return CONNECTION_OPERATIONS["luna_hsm_server"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for Luna HSM Server operations."""
        return {
            "luna_hsm_server_params": {
                "type": "object",
                "properties": LUNA_HSM_SERVER_PARAMETERS,
                "description": "Luna HSM Server-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for Luna HSM Server."""
        return {
            "create": {
                "required": ["name"],
                "optional": ["server_url", "certificate_file", "server_name", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
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
                "optional": ["name", "server_url", "certificate_file", "server_name", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute Luna HSM Server operation."""
        server_params = params.get("luna_hsm_server_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "luna-hsm", "servers", action]
        
        # Add action-specific parameters
        if action == "create":
            if server_params.get("name"):
                cmd.extend(["--name", server_params["name"]])
            if server_params.get("server_url"):
                cmd.extend(["--server-url", server_params["server_url"]])
            if server_params.get("certificate_file"):
                cmd.extend(["--certificate-file", server_params["certificate_file"]])
            if server_params.get("server_name"):
                cmd.extend(["--server-name", server_params["server_name"]])
            if server_params.get("products"):
                cmd.extend(["--products", server_params["products"]])
            if server_params.get("description"):
                cmd.extend(["--description", server_params["description"]])
            if server_params.get("meta"):
                cmd.extend(["--meta", server_params["meta"]])
            if server_params.get("labels"):
                cmd.extend(["--labels", server_params["labels"]])
            if server_params.get("json_file"):
                cmd.extend(["--json-file", server_params["json_file"]])
                
        elif action == "list":
            if server_params.get("name"):
                cmd.extend(["--name", server_params["name"]])
            if server_params.get("cloudname"):
                cmd.extend(["--cloudname", server_params["cloudname"]])
            if server_params.get("category"):
                cmd.extend(["--category", server_params["category"]])
            if server_params.get("products"):
                cmd.extend(["--products", server_params["products"]])
            if server_params.get("limit"):
                cmd.extend(["--limit", str(server_params["limit"])])
            if server_params.get("skip"):
                cmd.extend(["--skip", str(server_params["skip"])])
            if server_params.get("fields"):
                cmd.extend(["--fields", server_params["fields"]])
            if server_params.get("labels_query"):
                cmd.extend(["--labels-query", server_params["labels_query"]])
            if server_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", server_params["lastconnectionafter"]])
            if server_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", server_params["lastconnectionbefore"]])
            if server_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", server_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", server_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", server_params["id"]])
            if server_params.get("force"):
                cmd.append("--force")
                
        elif action == "modify":
            cmd.extend(["--id", server_params["id"]])
            if server_params.get("name"):
                cmd.extend(["--name", server_params["name"]])
            if server_params.get("server_url"):
                cmd.extend(["--server-url", server_params["server_url"]])
            if server_params.get("certificate_file"):
                cmd.extend(["--certificate-file", server_params["certificate_file"]])
            if server_params.get("server_name"):
                cmd.extend(["--server-name", server_params["server_name"]])
            if server_params.get("products"):
                cmd.extend(["--products", server_params["products"]])
            if server_params.get("description"):
                cmd.extend(["--description", server_params["description"]])
            if server_params.get("meta"):
                cmd.extend(["--meta", server_params["meta"]])
            if server_params.get("labels"):
                cmd.extend(["--labels", server_params["labels"]])
            if server_params.get("json_file"):
                cmd.extend(["--json-file", server_params["json_file"]])
                
        else:
            raise ValueError(f"Unsupported Luna HSM Server action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 