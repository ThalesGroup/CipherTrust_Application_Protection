"""Loki Log Forwarder connection operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import LOKI_LOG_FORWARDER_PARAMETERS, CONNECTION_OPERATIONS


class LokiLogForwarderOperations(ConnectionOperations):
    """Loki Log Forwarder connection operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported Loki Log Forwarder operations."""
        return CONNECTION_OPERATIONS["loki_log_forwarder"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for Loki Log Forwarder operations."""
        return {
            "loki_log_forwarder_params": {
                "type": "object",
                "properties": LOKI_LOG_FORWARDER_PARAMETERS,
                "description": "Loki Log Forwarder-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for Loki Log Forwarder."""
        return {
            "create": {
                "required": ["name"],
                "optional": ["endpoint_url", "username", "password", "certificate_file", "tenant_id", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
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
                "optional": ["name", "endpoint_url", "username", "password", "certificate_file", "tenant_id", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "test": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute Loki Log Forwarder connection operation."""
        loki_params = params.get("loki_log_forwarder_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "log-forwarder", "loki", action]
        
        # Add action-specific parameters
        if action == "create":
            if loki_params.get("name"):
                cmd.extend(["--name", loki_params["name"]])
            if loki_params.get("endpoint_url"):
                cmd.extend(["--endpoint-url", loki_params["endpoint_url"]])
            if loki_params.get("username"):
                cmd.extend(["--username", loki_params["username"]])
            if loki_params.get("password"):
                cmd.extend(["--password", loki_params["password"]])
            if loki_params.get("certificate_file"):
                cmd.extend(["--certificate-file", loki_params["certificate_file"]])
            if loki_params.get("tenant_id"):
                cmd.extend(["--tenant-id", loki_params["tenant_id"]])
            if loki_params.get("products"):
                cmd.extend(["--products", loki_params["products"]])
            if loki_params.get("description"):
                cmd.extend(["--description", loki_params["description"]])
            if loki_params.get("meta"):
                cmd.extend(["--meta", loki_params["meta"]])
            if loki_params.get("labels"):
                cmd.extend(["--labels", loki_params["labels"]])
            if loki_params.get("json_file"):
                cmd.extend(["--json-file", loki_params["json_file"]])
                
        elif action == "list":
            if loki_params.get("name"):
                cmd.extend(["--name", loki_params["name"]])
            if loki_params.get("cloudname"):
                cmd.extend(["--cloudname", loki_params["cloudname"]])
            if loki_params.get("category"):
                cmd.extend(["--category", loki_params["category"]])
            if loki_params.get("products"):
                cmd.extend(["--products", loki_params["products"]])
            if loki_params.get("limit"):
                cmd.extend(["--limit", str(loki_params["limit"])])
            if loki_params.get("skip"):
                cmd.extend(["--skip", str(loki_params["skip"])])
            if loki_params.get("fields"):
                cmd.extend(["--fields", loki_params["fields"]])
            if loki_params.get("labels_query"):
                cmd.extend(["--labels-query", loki_params["labels_query"]])
            if loki_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", loki_params["lastconnectionafter"]])
            if loki_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", loki_params["lastconnectionbefore"]])
            if loki_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", loki_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", loki_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", loki_params["id"]])
            if loki_params.get("force"):
                cmd.append("--force")
                
        elif action == "modify":
            cmd.extend(["--id", loki_params["id"]])
            if loki_params.get("name"):
                cmd.extend(["--name", loki_params["name"]])
            if loki_params.get("endpoint_url"):
                cmd.extend(["--endpoint-url", loki_params["endpoint_url"]])
            if loki_params.get("username"):
                cmd.extend(["--username", loki_params["username"]])
            if loki_params.get("password"):
                cmd.extend(["--password", loki_params["password"]])
            if loki_params.get("certificate_file"):
                cmd.extend(["--certificate-file", loki_params["certificate_file"]])
            if loki_params.get("tenant_id"):
                cmd.extend(["--tenant-id", loki_params["tenant_id"]])
            if loki_params.get("products"):
                cmd.extend(["--products", loki_params["products"]])
            if loki_params.get("description"):
                cmd.extend(["--description", loki_params["description"]])
            if loki_params.get("meta"):
                cmd.extend(["--meta", loki_params["meta"]])
            if loki_params.get("labels"):
                cmd.extend(["--labels", loki_params["labels"]])
            if loki_params.get("json_file"):
                cmd.extend(["--json-file", loki_params["json_file"]])
                
        elif action == "test":
            cmd.extend(["--id", loki_params["id"]])
            
        else:
            raise ValueError(f"Unsupported Loki Log Forwarder action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 