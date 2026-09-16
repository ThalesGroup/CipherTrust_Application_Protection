"""CM connection operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import CM_PARAMETERS, CONNECTION_OPERATIONS


class CMOperations(ConnectionOperations):
    """CM connection operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported CM operations."""
        return CONNECTION_OPERATIONS["cm"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for CM operations."""
        return {
            "cm_params": {
                "type": "object",
                "properties": CM_PARAMETERS,
                "description": "CM-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for CM."""
        return {
            "create": {
                "required": ["name"],
                "optional": ["server_url", "username", "password", "certificate_file", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
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
                "optional": ["name", "server_url", "username", "password", "certificate_file", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "test": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute CM connection operation."""
        cm_params = params.get("cm_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "cm", action]
        
        # Add action-specific parameters
        if action == "create":
            if cm_params.get("name"):
                cmd.extend(["--name", cm_params["name"]])
            if cm_params.get("server_url"):
                cmd.extend(["--server-url", cm_params["server_url"]])
            if cm_params.get("username"):
                cmd.extend(["--username", cm_params["username"]])
            if cm_params.get("password"):
                cmd.extend(["--password", cm_params["password"]])
            if cm_params.get("certificate_file"):
                cmd.extend(["--certificate-file", cm_params["certificate_file"]])
            if cm_params.get("products"):
                cmd.extend(["--products", cm_params["products"]])
            if cm_params.get("description"):
                cmd.extend(["--description", cm_params["description"]])
            if cm_params.get("meta"):
                cmd.extend(["--meta", cm_params["meta"]])
            if cm_params.get("labels"):
                cmd.extend(["--labels", cm_params["labels"]])
            if cm_params.get("json_file"):
                cmd.extend(["--json-file", cm_params["json_file"]])
                
        elif action == "list":
            if cm_params.get("name"):
                cmd.extend(["--name", cm_params["name"]])
            if cm_params.get("cloudname"):
                cmd.extend(["--cloudname", cm_params["cloudname"]])
            if cm_params.get("category"):
                cmd.extend(["--category", cm_params["category"]])
            if cm_params.get("products"):
                cmd.extend(["--products", cm_params["products"]])
            if cm_params.get("limit"):
                cmd.extend(["--limit", str(cm_params["limit"])])
            if cm_params.get("skip"):
                cmd.extend(["--skip", str(cm_params["skip"])])
            if cm_params.get("fields"):
                cmd.extend(["--fields", cm_params["fields"]])
            if cm_params.get("labels_query"):
                cmd.extend(["--labels-query", cm_params["labels_query"]])
            if cm_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", cm_params["lastconnectionafter"]])
            if cm_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", cm_params["lastconnectionbefore"]])
            if cm_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", cm_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", cm_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", cm_params["id"]])
            if cm_params.get("force"):
                cmd.append("--force")
                
        elif action == "modify":
            cmd.extend(["--id", cm_params["id"]])
            if cm_params.get("name"):
                cmd.extend(["--name", cm_params["name"]])
            if cm_params.get("server_url"):
                cmd.extend(["--server-url", cm_params["server_url"]])
            if cm_params.get("username"):
                cmd.extend(["--username", cm_params["username"]])
            if cm_params.get("password"):
                cmd.extend(["--password", cm_params["password"]])
            if cm_params.get("certificate_file"):
                cmd.extend(["--certificate-file", cm_params["certificate_file"]])
            if cm_params.get("products"):
                cmd.extend(["--products", cm_params["products"]])
            if cm_params.get("description"):
                cmd.extend(["--description", cm_params["description"]])
            if cm_params.get("meta"):
                cmd.extend(["--meta", cm_params["meta"]])
            if cm_params.get("labels"):
                cmd.extend(["--labels", cm_params["labels"]])
            if cm_params.get("json_file"):
                cmd.extend(["--json-file", cm_params["json_file"]])
                
        elif action == "test":
            cmd.extend(["--id", cm_params["id"]])
            
        else:
            raise ValueError(f"Unsupported CM action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 