"""Salesforce connection operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import SALESFORCE_PARAMETERS, CONNECTION_OPERATIONS


class SalesforceOperations(ConnectionOperations):
    """Salesforce connection operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported Salesforce operations."""
        return CONNECTION_OPERATIONS["salesforce"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for Salesforce operations."""
        return {
            "salesforce_params": {
                "type": "object",
                "properties": SALESFORCE_PARAMETERS,
                "description": "Salesforce-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for Salesforce."""
        return {
            "create": {
                "required": ["name"],
                "optional": ["clientid", "secret", "username", "password", "security_token", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
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
                "optional": ["name", "clientid", "secret", "username", "password", "security_token", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "test": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute Salesforce connection operation."""
        salesforce_params = params.get("salesforce_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "salesforce", action]
        
        # Add action-specific parameters
        if action == "create":
            if salesforce_params.get("name"):
                cmd.extend(["--name", salesforce_params["name"]])
            if salesforce_params.get("clientid"):
                cmd.extend(["--clientid", salesforce_params["clientid"]])
            if salesforce_params.get("secret"):
                cmd.extend(["--secret", salesforce_params["secret"]])
            if salesforce_params.get("username"):
                cmd.extend(["--username", salesforce_params["username"]])
            if salesforce_params.get("password"):
                cmd.extend(["--password", salesforce_params["password"]])
            if salesforce_params.get("security_token"):
                cmd.extend(["--security-token", salesforce_params["security_token"]])
            if salesforce_params.get("products"):
                cmd.extend(["--products", salesforce_params["products"]])
            if salesforce_params.get("description"):
                cmd.extend(["--description", salesforce_params["description"]])
            if salesforce_params.get("meta"):
                cmd.extend(["--meta", salesforce_params["meta"]])
            if salesforce_params.get("labels"):
                cmd.extend(["--labels", salesforce_params["labels"]])
            if salesforce_params.get("json_file"):
                cmd.extend(["--json-file", salesforce_params["json_file"]])
                
        elif action == "list":
            if salesforce_params.get("name"):
                cmd.extend(["--name", salesforce_params["name"]])
            if salesforce_params.get("cloudname"):
                cmd.extend(["--cloudname", salesforce_params["cloudname"]])
            if salesforce_params.get("category"):
                cmd.extend(["--category", salesforce_params["category"]])
            if salesforce_params.get("products"):
                cmd.extend(["--products", salesforce_params["products"]])
            if salesforce_params.get("limit"):
                cmd.extend(["--limit", str(salesforce_params["limit"])])
            if salesforce_params.get("skip"):
                cmd.extend(["--skip", str(salesforce_params["skip"])])
            if salesforce_params.get("fields"):
                cmd.extend(["--fields", salesforce_params["fields"]])
            if salesforce_params.get("labels_query"):
                cmd.extend(["--labels-query", salesforce_params["labels_query"]])
            if salesforce_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", salesforce_params["lastconnectionafter"]])
            if salesforce_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", salesforce_params["lastconnectionbefore"]])
            if salesforce_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", salesforce_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", salesforce_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", salesforce_params["id"]])
            if salesforce_params.get("force"):
                cmd.append("--force")
                
        elif action == "modify":
            cmd.extend(["--id", salesforce_params["id"]])
            if salesforce_params.get("name"):
                cmd.extend(["--name", salesforce_params["name"]])
            if salesforce_params.get("clientid"):
                cmd.extend(["--clientid", salesforce_params["clientid"]])
            if salesforce_params.get("secret"):
                cmd.extend(["--secret", salesforce_params["secret"]])
            if salesforce_params.get("username"):
                cmd.extend(["--username", salesforce_params["username"]])
            if salesforce_params.get("password"):
                cmd.extend(["--password", salesforce_params["password"]])
            if salesforce_params.get("security_token"):
                cmd.extend(["--security-token", salesforce_params["security_token"]])
            if salesforce_params.get("products"):
                cmd.extend(["--products", salesforce_params["products"]])
            if salesforce_params.get("description"):
                cmd.extend(["--description", salesforce_params["description"]])
            if salesforce_params.get("meta"):
                cmd.extend(["--meta", salesforce_params["meta"]])
            if salesforce_params.get("labels"):
                cmd.extend(["--labels", salesforce_params["labels"]])
            if salesforce_params.get("json_file"):
                cmd.extend(["--json-file", salesforce_params["json_file"]])
                
        elif action == "test":
            cmd.extend(["--id", salesforce_params["id"]])
            
        else:
            raise ValueError(f"Unsupported Salesforce action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 