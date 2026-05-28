"""SMB connection operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import SMB_PARAMETERS, CONNECTION_OPERATIONS


class SMBOperations(ConnectionOperations):
    """SMB connection operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported SMB operations."""
        return CONNECTION_OPERATIONS["smb"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for SMB operations."""
        return {
            "smb_params": {
                "type": "object",
                "properties": SMB_PARAMETERS,
                "description": "SMB-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for SMB."""
        return {
            "create": {
                "required": ["name"],
                "optional": ["server", "share", "username", "password", "domain", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
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
                "optional": ["name", "server", "share", "username", "password", "domain", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "test": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute SMB connection operation."""
        smb_params = params.get("smb_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "smb", action]
        
        # Add action-specific parameters
        if action == "create":
            if smb_params.get("name"):
                cmd.extend(["--name", smb_params["name"]])
            if smb_params.get("server"):
                cmd.extend(["--server", smb_params["server"]])
            if smb_params.get("share"):
                cmd.extend(["--share", smb_params["share"]])
            if smb_params.get("username"):
                cmd.extend(["--username", smb_params["username"]])
            if smb_params.get("password"):
                cmd.extend(["--password", smb_params["password"]])
            if smb_params.get("domain"):
                cmd.extend(["--domain", smb_params["domain"]])
            if smb_params.get("products"):
                cmd.extend(["--products", smb_params["products"]])
            if smb_params.get("description"):
                cmd.extend(["--description", smb_params["description"]])
            if smb_params.get("meta"):
                cmd.extend(["--meta", smb_params["meta"]])
            if smb_params.get("labels"):
                cmd.extend(["--labels", smb_params["labels"]])
            if smb_params.get("json_file"):
                cmd.extend(["--json-file", smb_params["json_file"]])
                
        elif action == "list":
            if smb_params.get("name"):
                cmd.extend(["--name", smb_params["name"]])
            if smb_params.get("cloudname"):
                cmd.extend(["--cloudname", smb_params["cloudname"]])
            if smb_params.get("category"):
                cmd.extend(["--category", smb_params["category"]])
            if smb_params.get("products"):
                cmd.extend(["--products", smb_params["products"]])
            if smb_params.get("limit"):
                cmd.extend(["--limit", str(smb_params["limit"])])
            if smb_params.get("skip"):
                cmd.extend(["--skip", str(smb_params["skip"])])
            if smb_params.get("fields"):
                cmd.extend(["--fields", smb_params["fields"]])
            if smb_params.get("labels_query"):
                cmd.extend(["--labels-query", smb_params["labels_query"]])
            if smb_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", smb_params["lastconnectionafter"]])
            if smb_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", smb_params["lastconnectionbefore"]])
            if smb_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", smb_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", smb_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", smb_params["id"]])
            if smb_params.get("force"):
                cmd.append("--force")
                
        elif action == "modify":
            cmd.extend(["--id", smb_params["id"]])
            if smb_params.get("name"):
                cmd.extend(["--name", smb_params["name"]])
            if smb_params.get("server"):
                cmd.extend(["--server", smb_params["server"]])
            if smb_params.get("share"):
                cmd.extend(["--share", smb_params["share"]])
            if smb_params.get("username"):
                cmd.extend(["--username", smb_params["username"]])
            if smb_params.get("password"):
                cmd.extend(["--password", smb_params["password"]])
            if smb_params.get("domain"):
                cmd.extend(["--domain", smb_params["domain"]])
            if smb_params.get("products"):
                cmd.extend(["--products", smb_params["products"]])
            if smb_params.get("description"):
                cmd.extend(["--description", smb_params["description"]])
            if smb_params.get("meta"):
                cmd.extend(["--meta", smb_params["meta"]])
            if smb_params.get("labels"):
                cmd.extend(["--labels", smb_params["labels"]])
            if smb_params.get("json_file"):
                cmd.extend(["--json-file", smb_params["json_file"]])
                
        elif action == "test":
            cmd.extend(["--id", smb_params["id"]])
            
        else:
            raise ValueError(f"Unsupported SMB action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 