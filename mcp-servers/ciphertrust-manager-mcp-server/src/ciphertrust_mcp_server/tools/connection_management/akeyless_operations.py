"""Akeyless connection operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import AKEYLESS_PARAMETERS, CONNECTION_OPERATIONS


class AkeylessOperations(ConnectionOperations):
    """Akeyless connection operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported Akeyless operations."""
        return CONNECTION_OPERATIONS["akeyless"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for Akeyless operations."""
        return {
            "akeyless_params": {
                "type": "object",
                "properties": AKEYLESS_PARAMETERS,
                "description": "Akeyless-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for Akeyless."""
        return {
            "create": {
                "required": ["name"],
                "optional": ["clientid", "secret", "api_url", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
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
                "optional": ["name", "clientid", "secret", "api_url", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "test": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute Akeyless connection operation."""
        akeyless_params = params.get("akeyless_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "akeyless", action]
        
        # Add action-specific parameters
        if action == "create":
            if akeyless_params.get("name"):
                cmd.extend(["--name", akeyless_params["name"]])
            if akeyless_params.get("clientid"):
                cmd.extend(["--clientid", akeyless_params["clientid"]])
            if akeyless_params.get("secret"):
                cmd.extend(["--secret", akeyless_params["secret"]])
            if akeyless_params.get("api_url"):
                cmd.extend(["--api-url", akeyless_params["api_url"]])
            if akeyless_params.get("products"):
                cmd.extend(["--products", akeyless_params["products"]])
            if akeyless_params.get("description"):
                cmd.extend(["--description", akeyless_params["description"]])
            if akeyless_params.get("meta"):
                cmd.extend(["--meta", akeyless_params["meta"]])
            if akeyless_params.get("labels"):
                cmd.extend(["--labels", akeyless_params["labels"]])
            if akeyless_params.get("json_file"):
                cmd.extend(["--json-file", akeyless_params["json_file"]])
                
        elif action == "list":
            if akeyless_params.get("name"):
                cmd.extend(["--name", akeyless_params["name"]])
            if akeyless_params.get("cloudname"):
                cmd.extend(["--cloudname", akeyless_params["cloudname"]])
            if akeyless_params.get("category"):
                cmd.extend(["--category", akeyless_params["category"]])
            if akeyless_params.get("products"):
                cmd.extend(["--products", akeyless_params["products"]])
            if akeyless_params.get("limit"):
                cmd.extend(["--limit", str(akeyless_params["limit"])])
            if akeyless_params.get("skip"):
                cmd.extend(["--skip", str(akeyless_params["skip"])])
            if akeyless_params.get("fields"):
                cmd.extend(["--fields", akeyless_params["fields"]])
            if akeyless_params.get("labels_query"):
                cmd.extend(["--labels-query", akeyless_params["labels_query"]])
            if akeyless_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", akeyless_params["lastconnectionafter"]])
            if akeyless_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", akeyless_params["lastconnectionbefore"]])
            if akeyless_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", akeyless_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", akeyless_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", akeyless_params["id"]])
            if akeyless_params.get("force"):
                cmd.append("--force")
                
        elif action == "modify":
            cmd.extend(["--id", akeyless_params["id"]])
            if akeyless_params.get("name"):
                cmd.extend(["--name", akeyless_params["name"]])
            if akeyless_params.get("clientid"):
                cmd.extend(["--clientid", akeyless_params["clientid"]])
            if akeyless_params.get("secret"):
                cmd.extend(["--secret", akeyless_params["secret"]])
            if akeyless_params.get("api_url"):
                cmd.extend(["--api-url", akeyless_params["api_url"]])
            if akeyless_params.get("products"):
                cmd.extend(["--products", akeyless_params["products"]])
            if akeyless_params.get("description"):
                cmd.extend(["--description", akeyless_params["description"]])
            if akeyless_params.get("meta"):
                cmd.extend(["--meta", akeyless_params["meta"]])
            if akeyless_params.get("labels"):
                cmd.extend(["--labels", akeyless_params["labels"]])
            if akeyless_params.get("json_file"):
                cmd.extend(["--json-file", akeyless_params["json_file"]])
                
        elif action == "test":
            cmd.extend(["--id", akeyless_params["id"]])
            
        else:
            raise ValueError(f"Unsupported Akeyless action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 