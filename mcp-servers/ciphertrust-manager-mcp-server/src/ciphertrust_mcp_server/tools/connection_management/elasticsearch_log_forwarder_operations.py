"""Elasticsearch Log Forwarder connection operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import ELASTICSEARCH_LOG_FORWARDER_PARAMETERS, CONNECTION_OPERATIONS


class ElasticsearchLogForwarderOperations(ConnectionOperations):
    """Elasticsearch Log Forwarder connection operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported Elasticsearch Log Forwarder operations."""
        return CONNECTION_OPERATIONS["elasticsearch_log_forwarder"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for Elasticsearch Log Forwarder operations."""
        return {
            "elasticsearch_log_forwarder_params": {
                "type": "object",
                "properties": ELASTICSEARCH_LOG_FORWARDER_PARAMETERS,
                "description": "Elasticsearch Log Forwarder-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for Elasticsearch Log Forwarder."""
        return {
            "create": {
                "required": ["name"],
                "optional": ["endpoint_url", "username", "password", "certificate_file", "index_name", "ssl_verify", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
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
                "optional": ["name", "endpoint_url", "username", "password", "certificate_file", "index_name", "ssl_verify", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "test": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute Elasticsearch Log Forwarder connection operation."""
        elasticsearch_params = params.get("elasticsearch_log_forwarder_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "log-forwarder", "elasticsearch", action]
        
        # Add action-specific parameters
        if action == "create":
            if elasticsearch_params.get("name"):
                cmd.extend(["--name", elasticsearch_params["name"]])
            if elasticsearch_params.get("endpoint_url"):
                cmd.extend(["--endpoint-url", elasticsearch_params["endpoint_url"]])
            if elasticsearch_params.get("username"):
                cmd.extend(["--username", elasticsearch_params["username"]])
            if elasticsearch_params.get("password"):
                cmd.extend(["--password", elasticsearch_params["password"]])
            if elasticsearch_params.get("certificate_file"):
                cmd.extend(["--certificate-file", elasticsearch_params["certificate_file"]])
            if elasticsearch_params.get("index_name"):
                cmd.extend(["--index-name", elasticsearch_params["index_name"]])
            if elasticsearch_params.get("ssl_verify") is not None:
                cmd.extend(["--ssl-verify", str(elasticsearch_params["ssl_verify"]).lower()])
            if elasticsearch_params.get("products"):
                cmd.extend(["--products", elasticsearch_params["products"]])
            if elasticsearch_params.get("description"):
                cmd.extend(["--description", elasticsearch_params["description"]])
            if elasticsearch_params.get("meta"):
                cmd.extend(["--meta", elasticsearch_params["meta"]])
            if elasticsearch_params.get("labels"):
                cmd.extend(["--labels", elasticsearch_params["labels"]])
            if elasticsearch_params.get("json_file"):
                cmd.extend(["--json-file", elasticsearch_params["json_file"]])
                
        elif action == "list":
            if elasticsearch_params.get("name"):
                cmd.extend(["--name", elasticsearch_params["name"]])
            if elasticsearch_params.get("cloudname"):
                cmd.extend(["--cloudname", elasticsearch_params["cloudname"]])
            if elasticsearch_params.get("category"):
                cmd.extend(["--category", elasticsearch_params["category"]])
            if elasticsearch_params.get("products"):
                cmd.extend(["--products", elasticsearch_params["products"]])
            if elasticsearch_params.get("limit"):
                cmd.extend(["--limit", str(elasticsearch_params["limit"])])
            if elasticsearch_params.get("skip"):
                cmd.extend(["--skip", str(elasticsearch_params["skip"])])
            if elasticsearch_params.get("fields"):
                cmd.extend(["--fields", elasticsearch_params["fields"]])
            if elasticsearch_params.get("labels_query"):
                cmd.extend(["--labels-query", elasticsearch_params["labels_query"]])
            if elasticsearch_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", elasticsearch_params["lastconnectionafter"]])
            if elasticsearch_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", elasticsearch_params["lastconnectionbefore"]])
            if elasticsearch_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", elasticsearch_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", elasticsearch_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", elasticsearch_params["id"]])
            if elasticsearch_params.get("force"):
                cmd.append("--force")
                
        elif action == "modify":
            cmd.extend(["--id", elasticsearch_params["id"]])
            if elasticsearch_params.get("name"):
                cmd.extend(["--name", elasticsearch_params["name"]])
            if elasticsearch_params.get("endpoint_url"):
                cmd.extend(["--endpoint-url", elasticsearch_params["endpoint_url"]])
            if elasticsearch_params.get("username"):
                cmd.extend(["--username", elasticsearch_params["username"]])
            if elasticsearch_params.get("password"):
                cmd.extend(["--password", elasticsearch_params["password"]])
            if elasticsearch_params.get("certificate_file"):
                cmd.extend(["--certificate-file", elasticsearch_params["certificate_file"]])
            if elasticsearch_params.get("index_name"):
                cmd.extend(["--index-name", elasticsearch_params["index_name"]])
            if elasticsearch_params.get("ssl_verify") is not None:
                cmd.extend(["--ssl-verify", str(elasticsearch_params["ssl_verify"]).lower()])
            if elasticsearch_params.get("products"):
                cmd.extend(["--products", elasticsearch_params["products"]])
            if elasticsearch_params.get("description"):
                cmd.extend(["--description", elasticsearch_params["description"]])
            if elasticsearch_params.get("meta"):
                cmd.extend(["--meta", elasticsearch_params["meta"]])
            if elasticsearch_params.get("labels"):
                cmd.extend(["--labels", elasticsearch_params["labels"]])
            if elasticsearch_params.get("json_file"):
                cmd.extend(["--json-file", elasticsearch_params["json_file"]])
                
        elif action == "test":
            cmd.extend(["--id", elasticsearch_params["id"]])
            
        else:
            raise ValueError(f"Unsupported Elasticsearch Log Forwarder action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 