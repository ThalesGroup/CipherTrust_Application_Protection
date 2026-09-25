"""LDAP connection operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import LDAP_PARAMETERS, CONNECTION_OPERATIONS


class LDAPOperations(ConnectionOperations):
    """LDAP connection operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported LDAP operations."""
        return CONNECTION_OPERATIONS["ldap"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for LDAP operations."""
        return {
            "ldap_params": {
                "type": "object",
                "properties": LDAP_PARAMETERS,
                "description": "LDAP-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for LDAP."""
        return {
            "create": {
                "required": ["name"],
                "optional": ["server_url", "bind_dn", "bind_password", "search_base", "certificate_file", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
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
                "optional": ["name", "server_url", "bind_dn", "bind_password", "search_base", "certificate_file", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "test": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute LDAP connection operation."""
        ldap_params = params.get("ldap_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "ldap", action]
        
        # Add action-specific parameters
        if action == "create":
            if ldap_params.get("name"):
                cmd.extend(["--name", ldap_params["name"]])
            if ldap_params.get("server_url"):
                cmd.extend(["--server-url", ldap_params["server_url"]])
            if ldap_params.get("bind_dn"):
                cmd.extend(["--bind-dn", ldap_params["bind_dn"]])
            if ldap_params.get("bind_password"):
                cmd.extend(["--bind-password", ldap_params["bind_password"]])
            if ldap_params.get("search_base"):
                cmd.extend(["--search-base", ldap_params["search_base"]])
            if ldap_params.get("certificate_file"):
                cmd.extend(["--certificate-file", ldap_params["certificate_file"]])
            if ldap_params.get("products"):
                cmd.extend(["--products", ldap_params["products"]])
            if ldap_params.get("description"):
                cmd.extend(["--description", ldap_params["description"]])
            if ldap_params.get("meta"):
                cmd.extend(["--meta", ldap_params["meta"]])
            if ldap_params.get("labels"):
                cmd.extend(["--labels", ldap_params["labels"]])
            if ldap_params.get("json_file"):
                cmd.extend(["--json-file", ldap_params["json_file"]])
                
        elif action == "list":
            if ldap_params.get("name"):
                cmd.extend(["--name", ldap_params["name"]])
            if ldap_params.get("cloudname"):
                cmd.extend(["--cloudname", ldap_params["cloudname"]])
            if ldap_params.get("category"):
                cmd.extend(["--category", ldap_params["category"]])
            if ldap_params.get("products"):
                cmd.extend(["--products", ldap_params["products"]])
            if ldap_params.get("limit"):
                cmd.extend(["--limit", str(ldap_params["limit"])])
            if ldap_params.get("skip"):
                cmd.extend(["--skip", str(ldap_params["skip"])])
            if ldap_params.get("fields"):
                cmd.extend(["--fields", ldap_params["fields"]])
            if ldap_params.get("labels_query"):
                cmd.extend(["--labels-query", ldap_params["labels_query"]])
            if ldap_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", ldap_params["lastconnectionafter"]])
            if ldap_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", ldap_params["lastconnectionbefore"]])
            if ldap_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", ldap_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", ldap_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", ldap_params["id"]])
            if ldap_params.get("force"):
                cmd.append("--force")
                
        elif action == "modify":
            cmd.extend(["--id", ldap_params["id"]])
            if ldap_params.get("name"):
                cmd.extend(["--name", ldap_params["name"]])
            if ldap_params.get("server_url"):
                cmd.extend(["--server-url", ldap_params["server_url"]])
            if ldap_params.get("bind_dn"):
                cmd.extend(["--bind-dn", ldap_params["bind_dn"]])
            if ldap_params.get("bind_password"):
                cmd.extend(["--bind-password", ldap_params["bind_password"]])
            if ldap_params.get("search_base"):
                cmd.extend(["--search-base", ldap_params["search_base"]])
            if ldap_params.get("certificate_file"):
                cmd.extend(["--certificate-file", ldap_params["certificate_file"]])
            if ldap_params.get("products"):
                cmd.extend(["--products", ldap_params["products"]])
            if ldap_params.get("description"):
                cmd.extend(["--description", ldap_params["description"]])
            if ldap_params.get("meta"):
                cmd.extend(["--meta", ldap_params["meta"]])
            if ldap_params.get("labels"):
                cmd.extend(["--labels", ldap_params["labels"]])
            if ldap_params.get("json_file"):
                cmd.extend(["--json-file", ldap_params["json_file"]])
                
        elif action == "test":
            cmd.extend(["--id", ldap_params["id"]])
            
        else:
            raise ValueError(f"Unsupported LDAP action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 