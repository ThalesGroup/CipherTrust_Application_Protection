"""OIDC connection operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import OIDC_PARAMETERS, CONNECTION_OPERATIONS


class OIDCOperations(ConnectionOperations):
    """OIDC connection operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported OIDC operations."""
        return CONNECTION_OPERATIONS["oidc"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for OIDC operations."""
        return {
            "oidc_params": {
                "type": "object",
                "properties": OIDC_PARAMETERS,
                "description": "OIDC-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for OIDC."""
        return {
            "create": {
                "required": ["name"],
                "optional": ["clientid", "secret", "issuer_url", "redirect_uri", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
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
                "optional": ["name", "clientid", "secret", "issuer_url", "redirect_uri", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "test": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute OIDC connection operation."""
        oidc_params = params.get("oidc_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "oidc", action]
        
        # Add action-specific parameters
        if action == "create":
            if oidc_params.get("name"):
                cmd.extend(["--name", oidc_params["name"]])
            if oidc_params.get("clientid"):
                cmd.extend(["--clientid", oidc_params["clientid"]])
            if oidc_params.get("secret"):
                cmd.extend(["--secret", oidc_params["secret"]])
            if oidc_params.get("issuer_url"):
                cmd.extend(["--issuer-url", oidc_params["issuer_url"]])
            if oidc_params.get("redirect_uri"):
                cmd.extend(["--redirect-uri", oidc_params["redirect_uri"]])
            if oidc_params.get("products"):
                cmd.extend(["--products", oidc_params["products"]])
            if oidc_params.get("description"):
                cmd.extend(["--description", oidc_params["description"]])
            if oidc_params.get("meta"):
                cmd.extend(["--meta", oidc_params["meta"]])
            if oidc_params.get("labels"):
                cmd.extend(["--labels", oidc_params["labels"]])
            if oidc_params.get("json_file"):
                cmd.extend(["--json-file", oidc_params["json_file"]])
                
        elif action == "list":
            if oidc_params.get("name"):
                cmd.extend(["--name", oidc_params["name"]])
            if oidc_params.get("cloudname"):
                cmd.extend(["--cloudname", oidc_params["cloudname"]])
            if oidc_params.get("category"):
                cmd.extend(["--category", oidc_params["category"]])
            if oidc_params.get("products"):
                cmd.extend(["--products", oidc_params["products"]])
            if oidc_params.get("limit"):
                cmd.extend(["--limit", str(oidc_params["limit"])])
            if oidc_params.get("skip"):
                cmd.extend(["--skip", str(oidc_params["skip"])])
            if oidc_params.get("fields"):
                cmd.extend(["--fields", oidc_params["fields"]])
            if oidc_params.get("labels_query"):
                cmd.extend(["--labels-query", oidc_params["labels_query"]])
            if oidc_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", oidc_params["lastconnectionafter"]])
            if oidc_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", oidc_params["lastconnectionbefore"]])
            if oidc_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", oidc_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", oidc_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", oidc_params["id"]])
            if oidc_params.get("force"):
                cmd.append("--force")
                
        elif action == "modify":
            cmd.extend(["--id", oidc_params["id"]])
            if oidc_params.get("name"):
                cmd.extend(["--name", oidc_params["name"]])
            if oidc_params.get("clientid"):
                cmd.extend(["--clientid", oidc_params["clientid"]])
            if oidc_params.get("secret"):
                cmd.extend(["--secret", oidc_params["secret"]])
            if oidc_params.get("issuer_url"):
                cmd.extend(["--issuer-url", oidc_params["issuer_url"]])
            if oidc_params.get("redirect_uri"):
                cmd.extend(["--redirect-uri", oidc_params["redirect_uri"]])
            if oidc_params.get("products"):
                cmd.extend(["--products", oidc_params["products"]])
            if oidc_params.get("description"):
                cmd.extend(["--description", oidc_params["description"]])
            if oidc_params.get("meta"):
                cmd.extend(["--meta", oidc_params["meta"]])
            if oidc_params.get("labels"):
                cmd.extend(["--labels", oidc_params["labels"]])
            if oidc_params.get("json_file"):
                cmd.extend(["--json-file", oidc_params["json_file"]])
                
        elif action == "test":
            cmd.extend(["--id", oidc_params["id"]])
            
        else:
            raise ValueError(f"Unsupported OIDC action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 