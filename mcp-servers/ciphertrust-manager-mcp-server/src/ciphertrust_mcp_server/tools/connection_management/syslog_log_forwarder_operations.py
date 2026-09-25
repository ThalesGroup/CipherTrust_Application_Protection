"""Syslog Log Forwarder connection operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import SYSLOG_LOG_FORWARDER_PARAMETERS, CONNECTION_OPERATIONS


class SyslogLogForwarderOperations(ConnectionOperations):
    """Syslog Log Forwarder connection operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported Syslog Log Forwarder operations."""
        return CONNECTION_OPERATIONS["syslog_log_forwarder"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for Syslog Log Forwarder operations."""
        return {
            "syslog_log_forwarder_params": {
                "type": "object",
                "properties": SYSLOG_LOG_FORWARDER_PARAMETERS,
                "description": "Syslog Log Forwarder-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for Syslog Log Forwarder."""
        return {
            "create": {
                "required": ["name"],
                "optional": ["endpoint_url", "username", "password", "certificate_file", "facility", "priority", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
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
                "optional": ["name", "endpoint_url", "username", "password", "certificate_file", "facility", "priority", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "test": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute Syslog Log Forwarder connection operation."""
        syslog_params = params.get("syslog_log_forwarder_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "log-forwarder", "syslog", action]
        
        # Add action-specific parameters
        if action == "create":
            if syslog_params.get("name"):
                cmd.extend(["--name", syslog_params["name"]])
            if syslog_params.get("endpoint_url"):
                cmd.extend(["--endpoint-url", syslog_params["endpoint_url"]])
            if syslog_params.get("username"):
                cmd.extend(["--username", syslog_params["username"]])
            if syslog_params.get("password"):
                cmd.extend(["--password", syslog_params["password"]])
            if syslog_params.get("certificate_file"):
                cmd.extend(["--certificate-file", syslog_params["certificate_file"]])
            if syslog_params.get("facility"):
                cmd.extend(["--facility", syslog_params["facility"]])
            if syslog_params.get("priority"):
                cmd.extend(["--priority", syslog_params["priority"]])
            if syslog_params.get("products"):
                cmd.extend(["--products", syslog_params["products"]])
            if syslog_params.get("description"):
                cmd.extend(["--description", syslog_params["description"]])
            if syslog_params.get("meta"):
                cmd.extend(["--meta", syslog_params["meta"]])
            if syslog_params.get("labels"):
                cmd.extend(["--labels", syslog_params["labels"]])
            if syslog_params.get("json_file"):
                cmd.extend(["--json-file", syslog_params["json_file"]])
                
        elif action == "list":
            if syslog_params.get("name"):
                cmd.extend(["--name", syslog_params["name"]])
            if syslog_params.get("cloudname"):
                cmd.extend(["--cloudname", syslog_params["cloudname"]])
            if syslog_params.get("category"):
                cmd.extend(["--category", syslog_params["category"]])
            if syslog_params.get("products"):
                cmd.extend(["--products", syslog_params["products"]])
            if syslog_params.get("limit"):
                cmd.extend(["--limit", str(syslog_params["limit"])])
            if syslog_params.get("skip"):
                cmd.extend(["--skip", str(syslog_params["skip"])])
            if syslog_params.get("fields"):
                cmd.extend(["--fields", syslog_params["fields"]])
            if syslog_params.get("labels_query"):
                cmd.extend(["--labels-query", syslog_params["labels_query"]])
            if syslog_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", syslog_params["lastconnectionafter"]])
            if syslog_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", syslog_params["lastconnectionbefore"]])
            if syslog_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", syslog_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", syslog_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", syslog_params["id"]])
            if syslog_params.get("force"):
                cmd.append("--force")
                
        elif action == "modify":
            cmd.extend(["--id", syslog_params["id"]])
            if syslog_params.get("name"):
                cmd.extend(["--name", syslog_params["name"]])
            if syslog_params.get("endpoint_url"):
                cmd.extend(["--endpoint-url", syslog_params["endpoint_url"]])
            if syslog_params.get("username"):
                cmd.extend(["--username", syslog_params["username"]])
            if syslog_params.get("password"):
                cmd.extend(["--password", syslog_params["password"]])
            if syslog_params.get("certificate_file"):
                cmd.extend(["--certificate-file", syslog_params["certificate_file"]])
            if syslog_params.get("facility"):
                cmd.extend(["--facility", syslog_params["facility"]])
            if syslog_params.get("priority"):
                cmd.extend(["--priority", syslog_params["priority"]])
            if syslog_params.get("products"):
                cmd.extend(["--products", syslog_params["products"]])
            if syslog_params.get("description"):
                cmd.extend(["--description", syslog_params["description"]])
            if syslog_params.get("meta"):
                cmd.extend(["--meta", syslog_params["meta"]])
            if syslog_params.get("labels"):
                cmd.extend(["--labels", syslog_params["labels"]])
            if syslog_params.get("json_file"):
                cmd.extend(["--json-file", syslog_params["json_file"]])
                
        elif action == "test":
            cmd.extend(["--id", syslog_params["id"]])
            
        else:
            raise ValueError(f"Unsupported Syslog Log Forwarder action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 