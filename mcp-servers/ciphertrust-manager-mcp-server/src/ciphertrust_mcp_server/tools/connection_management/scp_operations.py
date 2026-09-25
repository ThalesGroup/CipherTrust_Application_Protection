"""SCP connection operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import SCP_PARAMETERS, CONNECTION_OPERATIONS


class SCPOperations(ConnectionOperations):
    """SCP connection operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported SCP operations."""
        return CONNECTION_OPERATIONS["scp"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for SCP operations."""
        return {
            "scp_params": {
                "type": "object",
                "properties": SCP_PARAMETERS,
                "description": "SCP-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for SCP."""
        return {
            "create": {
                "required": ["name"],
                "optional": ["host", "port", "username", "password", "private_key_file", "passphrase", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
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
                "optional": ["name", "host", "port", "username", "password", "private_key_file", "passphrase", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "test": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute SCP connection operation."""
        scp_params = params.get("scp_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "scp", action]
        
        # Add action-specific parameters
        if action == "create":
            if scp_params.get("name"):
                cmd.extend(["--name", scp_params["name"]])
            if scp_params.get("host"):
                cmd.extend(["--host", scp_params["host"]])
            if scp_params.get("port"):
                cmd.extend(["--port", str(scp_params["port"])])
            if scp_params.get("username"):
                cmd.extend(["--username", scp_params["username"]])
            if scp_params.get("password"):
                cmd.extend(["--password", scp_params["password"]])
            if scp_params.get("private_key_file"):
                cmd.extend(["--private-key-file", scp_params["private_key_file"]])
            if scp_params.get("passphrase"):
                cmd.extend(["--passphrase", scp_params["passphrase"]])
            if scp_params.get("products"):
                cmd.extend(["--products", scp_params["products"]])
            if scp_params.get("description"):
                cmd.extend(["--description", scp_params["description"]])
            if scp_params.get("meta"):
                cmd.extend(["--meta", scp_params["meta"]])
            if scp_params.get("labels"):
                cmd.extend(["--labels", scp_params["labels"]])
            if scp_params.get("json_file"):
                cmd.extend(["--json-file", scp_params["json_file"]])
                
        elif action == "list":
            if scp_params.get("name"):
                cmd.extend(["--name", scp_params["name"]])
            if scp_params.get("cloudname"):
                cmd.extend(["--cloudname", scp_params["cloudname"]])
            if scp_params.get("category"):
                cmd.extend(["--category", scp_params["category"]])
            if scp_params.get("products"):
                cmd.extend(["--products", scp_params["products"]])
            if scp_params.get("limit"):
                cmd.extend(["--limit", str(scp_params["limit"])])
            if scp_params.get("skip"):
                cmd.extend(["--skip", str(scp_params["skip"])])
            if scp_params.get("fields"):
                cmd.extend(["--fields", scp_params["fields"]])
            if scp_params.get("labels_query"):
                cmd.extend(["--labels-query", scp_params["labels_query"]])
            if scp_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", scp_params["lastconnectionafter"]])
            if scp_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", scp_params["lastconnectionbefore"]])
            if scp_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", scp_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", scp_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", scp_params["id"]])
            if scp_params.get("force"):
                cmd.append("--force")
                
        elif action == "modify":
            cmd.extend(["--id", scp_params["id"]])
            if scp_params.get("name"):
                cmd.extend(["--name", scp_params["name"]])
            if scp_params.get("host"):
                cmd.extend(["--host", scp_params["host"]])
            if scp_params.get("port"):
                cmd.extend(["--port", str(scp_params["port"])])
            if scp_params.get("username"):
                cmd.extend(["--username", scp_params["username"]])
            if scp_params.get("password"):
                cmd.extend(["--password", scp_params["password"]])
            if scp_params.get("private_key_file"):
                cmd.extend(["--private-key-file", scp_params["private_key_file"]])
            if scp_params.get("passphrase"):
                cmd.extend(["--passphrase", scp_params["passphrase"]])
            if scp_params.get("products"):
                cmd.extend(["--products", scp_params["products"]])
            if scp_params.get("description"):
                cmd.extend(["--description", scp_params["description"]])
            if scp_params.get("meta"):
                cmd.extend(["--meta", scp_params["meta"]])
            if scp_params.get("labels"):
                cmd.extend(["--labels", scp_params["labels"]])
            if scp_params.get("json_file"):
                cmd.extend(["--json-file", scp_params["json_file"]])
                
        elif action == "test":
            cmd.extend(["--id", scp_params["id"]])
            
        else:
            raise ValueError(f"Unsupported SCP action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 