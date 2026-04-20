"""Log Forwarder connection operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import LOG_FORWARDER_PARAMETERS, CONNECTION_OPERATIONS


class LogForwarderOperations(ConnectionOperations):
    """Log Forwarder connection operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported Log Forwarder operations."""
        return CONNECTION_OPERATIONS["log_forwarder"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for Log Forwarder operations."""
        return {
            "log_forwarder_params": {
                "type": "object",
                "properties": LOG_FORWARDER_PARAMETERS,
                "description": "Log Forwarder-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for Log Forwarder."""
        return {
            "create": {
                "required": ["name"],
                "optional": ["type", "endpoint_url", "username", "password", "certificate_file", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
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
                "optional": ["name", "type", "endpoint_url", "username", "password", "certificate_file", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "test": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute Log Forwarder connection operation."""
        log_forwarder_params = params.get("log_forwarder_params", {})
        
        # Build base command
        # Note: This is for the generic log-forwarder command
        # For type-specific operations, use the specialized classes
        cmd = ["connectionmgmt", "log-forwarder", action]
        
        # Add action-specific parameters
        if action == "create":
            if log_forwarder_params.get("name"):
                cmd.extend(["--name", log_forwarder_params["name"]])
            if log_forwarder_params.get("type"):
                cmd.extend(["--type", log_forwarder_params["type"]])
            if log_forwarder_params.get("endpoint_url"):
                cmd.extend(["--endpoint-url", log_forwarder_params["endpoint_url"]])
            if log_forwarder_params.get("username"):
                cmd.extend(["--username", log_forwarder_params["username"]])
            if log_forwarder_params.get("password"):
                cmd.extend(["--password", log_forwarder_params["password"]])
            if log_forwarder_params.get("certificate_file"):
                cmd.extend(["--certificate-file", log_forwarder_params["certificate_file"]])
            if log_forwarder_params.get("products"):
                cmd.extend(["--products", log_forwarder_params["products"]])
            if log_forwarder_params.get("description"):
                cmd.extend(["--description", log_forwarder_params["description"]])
            if log_forwarder_params.get("meta"):
                cmd.extend(["--meta", log_forwarder_params["meta"]])
            if log_forwarder_params.get("labels"):
                cmd.extend(["--labels", log_forwarder_params["labels"]])
            if log_forwarder_params.get("json_file"):
                cmd.extend(["--json-file", log_forwarder_params["json_file"]])
                
        elif action == "list":
            if log_forwarder_params.get("name"):
                cmd.extend(["--name", log_forwarder_params["name"]])
            if log_forwarder_params.get("cloudname"):
                cmd.extend(["--cloudname", log_forwarder_params["cloudname"]])
            if log_forwarder_params.get("category"):
                cmd.extend(["--category", log_forwarder_params["category"]])
            if log_forwarder_params.get("products"):
                cmd.extend(["--products", log_forwarder_params["products"]])
            if log_forwarder_params.get("limit"):
                cmd.extend(["--limit", str(log_forwarder_params["limit"])])
            if log_forwarder_params.get("skip"):
                cmd.extend(["--skip", str(log_forwarder_params["skip"])])
            if log_forwarder_params.get("fields"):
                cmd.extend(["--fields", log_forwarder_params["fields"]])
            if log_forwarder_params.get("labels_query"):
                cmd.extend(["--labels-query", log_forwarder_params["labels_query"]])
            if log_forwarder_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", log_forwarder_params["lastconnectionafter"]])
            if log_forwarder_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", log_forwarder_params["lastconnectionbefore"]])
            if log_forwarder_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", log_forwarder_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", log_forwarder_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", log_forwarder_params["id"]])
            if log_forwarder_params.get("force"):
                cmd.append("--force")
                
        elif action == "modify":
            cmd.extend(["--id", log_forwarder_params["id"]])
            if log_forwarder_params.get("name"):
                cmd.extend(["--name", log_forwarder_params["name"]])
            if log_forwarder_params.get("type"):
                cmd.extend(["--type", log_forwarder_params["type"]])
            if log_forwarder_params.get("endpoint_url"):
                cmd.extend(["--endpoint-url", log_forwarder_params["endpoint_url"]])
            if log_forwarder_params.get("username"):
                cmd.extend(["--username", log_forwarder_params["username"]])
            if log_forwarder_params.get("password"):
                cmd.extend(["--password", log_forwarder_params["password"]])
            if log_forwarder_params.get("certificate_file"):
                cmd.extend(["--certificate-file", log_forwarder_params["certificate_file"]])
            if log_forwarder_params.get("products"):
                cmd.extend(["--products", log_forwarder_params["products"]])
            if log_forwarder_params.get("description"):
                cmd.extend(["--description", log_forwarder_params["description"]])
            if log_forwarder_params.get("meta"):
                cmd.extend(["--meta", log_forwarder_params["meta"]])
            if log_forwarder_params.get("labels"):
                cmd.extend(["--labels", log_forwarder_params["labels"]])
            if log_forwarder_params.get("json_file"):
                cmd.extend(["--json-file", log_forwarder_params["json_file"]])
                
        elif action == "test":
            cmd.extend(["--id", log_forwarder_params["id"]])
            
        else:
            raise ValueError(f"Unsupported Log Forwarder action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 