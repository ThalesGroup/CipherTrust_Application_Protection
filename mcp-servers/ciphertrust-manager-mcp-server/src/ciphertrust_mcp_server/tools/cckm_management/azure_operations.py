"""Azure operations for CCKM."""

from typing import Any, Dict, List
from .base import CCKMOperations
from .constants import AZURE_PARAMETERS, CLOUD_OPERATIONS


class AzureOperations(CCKMOperations):
    """Azure key operations for CCKM."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported Azure operations."""
        return CLOUD_OPERATIONS["azure"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for Azure operations."""
        return {
            "azure_params": {
                "type": "object",
                "properties": AZURE_PARAMETERS,
                "description": "Azure-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for Azure."""
        return {
            "list": {
                "required": [],
                "optional": ["vault_name", "limit", "skip", "domain", "auth_domain"]
            },
            "get": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "create": {
                "required": ["alias", "vault_name", "key_type"],
                "optional": ["key_size", "curve", "key_ops", "exp", "nbf", "domain", "auth_domain"]
            },
            "update": {
                "required": ["id"],
                "optional": ["alias", "description", "enabled", "tags", "exp", "nbf", "domain", "auth_domain"]
            },
            "delete": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "enable": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "disable": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "rotate": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "backup": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "restore": {
                "required": ["backup_data"],
                "optional": ["domain", "auth_domain"]
            },
            "import": {
                "required": ["id", "material"],
                "optional": ["domain", "auth_domain"]
            },
            "export": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute Azure operation."""
        azure_params = params.get("azure_params", {})
        
        # Build base command
        cmd = ["cckm", "azure", "keys"]
        
        # Add action-specific command
        if action == "list":
            cmd.append("list")
            if azure_params.get("vault_name"):
                cmd.extend(["--vault-name", azure_params["vault_name"]])
            if azure_params.get("limit"):
                cmd.extend(["--limit", str(azure_params["limit"])])
            if azure_params.get("skip"):
                cmd.extend(["--skip", str(azure_params["skip"])])
                
        elif action == "get":
            cmd.extend(["get", "--id", azure_params["id"]])
            
        elif action == "create":
            cmd.extend(["create", 
                       "--alias", azure_params["alias"],
                       "--vault-name", azure_params["vault_name"],
                       "--key-type", azure_params["key_type"]])
            if azure_params.get("key_size"):
                cmd.extend(["--key-size", str(azure_params["key_size"])])
            if azure_params.get("curve"):
                cmd.extend(["--curve", azure_params["curve"]])
            if azure_params.get("key_ops"):
                cmd.extend(["--key-ops", str(azure_params["key_ops"])])
            if azure_params.get("exp"):
                cmd.extend(["--exp", azure_params["exp"]])
            if azure_params.get("nbf"):
                cmd.extend(["--nbf", azure_params["nbf"]])
                
        elif action == "update":
            cmd.extend(["update", "--id", azure_params["id"]])
            if azure_params.get("alias"):
                cmd.extend(["--alias", azure_params["alias"]])
            if azure_params.get("description"):
                cmd.extend(["--description", azure_params["description"]])
            if azure_params.get("enabled") is not None:
                cmd.extend(["--enabled", "yes" if azure_params["enabled"] else "no"])
            if azure_params.get("tags"):
                cmd.extend(["--tags", str(azure_params["tags"])])
            if azure_params.get("exp"):
                cmd.extend(["--exp", azure_params["exp"]])
            if azure_params.get("nbf"):
                cmd.extend(["--nbf", azure_params["nbf"]])
                
        elif action == "delete":
            cmd.extend(["delete", "--id", azure_params["id"]])
            
        elif action == "enable":
            cmd.extend(["enable", "--id", azure_params["id"]])
            
        elif action == "disable":
            cmd.extend(["disable", "--id", azure_params["id"]])
            
        elif action == "rotate":
            cmd.extend(["rotate", "--id", azure_params["id"]])
            
        elif action == "backup":
            cmd.extend(["backup", "--id", azure_params["id"]])
            
        elif action == "restore":
            cmd.extend(["restore", "--backup-data", azure_params["backup_data"]])
            
        elif action == "import":
            cmd.extend(["import", "--id", azure_params["id"], "--material", azure_params["material"]])
            
        elif action == "export":
            cmd.extend(["export", "--id", azure_params["id"]])
            
        else:
            raise ValueError(f"Unsupported Azure action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 