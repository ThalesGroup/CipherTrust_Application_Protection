"""Hadoop Node operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import HADOOP_NODE_PARAMETERS, CONNECTION_OPERATIONS


class HadoopNodeOperations(ConnectionOperations):
    """Hadoop Node operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported Hadoop Node operations."""
        return CONNECTION_OPERATIONS["hadoop_node"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for Hadoop Node operations."""
        return {
            "hadoop_node_params": {
                "type": "object",
                "properties": HADOOP_NODE_PARAMETERS,
                "description": "Hadoop Node-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for Hadoop Node."""
        return {
            "add": {
                "required": ["connection_id", "node_url"],
                "optional": ["node_type", "username", "password", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "list": {
                "required": ["connection_id"],
                "optional": ["name", "cloudname", "category", "products", "limit", "skip", "fields", "labels_query", "lastconnectionafter", "lastconnectionbefore", "lastconnectionok", "domain", "auth_domain"]
            },
            "get": {
                "required": ["connection_id", "id"],
                "optional": ["domain", "auth_domain"]
            },
            "delete": {
                "required": ["connection_id", "id"],
                "optional": ["force", "domain", "auth_domain"]
            },
            "modify": {
                "required": ["connection_id", "id"],
                "optional": ["node_url", "node_type", "username", "password", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute Hadoop Node operation."""
        node_params = params.get("hadoop_node_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "hadoop", "node", action]
        
        # Add connection ID for all operations
        if node_params.get("connection_id"):
            cmd.extend(["--connection-id", node_params["connection_id"]])
        
        # Add action-specific parameters
        if action == "add":
            if node_params.get("node_url"):
                cmd.extend(["--node-url", node_params["node_url"]])
            if node_params.get("node_type"):
                cmd.extend(["--node-type", node_params["node_type"]])
            if node_params.get("username"):
                cmd.extend(["--username", node_params["username"]])
            if node_params.get("password"):
                cmd.extend(["--password", node_params["password"]])
            if node_params.get("products"):
                cmd.extend(["--products", node_params["products"]])
            if node_params.get("description"):
                cmd.extend(["--description", node_params["description"]])
            if node_params.get("meta"):
                cmd.extend(["--meta", node_params["meta"]])
            if node_params.get("labels"):
                cmd.extend(["--labels", node_params["labels"]])
            if node_params.get("json_file"):
                cmd.extend(["--json-file", node_params["json_file"]])
                
        elif action == "list":
            if node_params.get("name"):
                cmd.extend(["--name", node_params["name"]])
            if node_params.get("cloudname"):
                cmd.extend(["--cloudname", node_params["cloudname"]])
            if node_params.get("category"):
                cmd.extend(["--category", node_params["category"]])
            if node_params.get("products"):
                cmd.extend(["--products", node_params["products"]])
            if node_params.get("limit"):
                cmd.extend(["--limit", str(node_params["limit"])])
            if node_params.get("skip"):
                cmd.extend(["--skip", str(node_params["skip"])])
            if node_params.get("fields"):
                cmd.extend(["--fields", node_params["fields"]])
            if node_params.get("labels_query"):
                cmd.extend(["--labels-query", node_params["labels_query"]])
            if node_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", node_params["lastconnectionafter"]])
            if node_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", node_params["lastconnectionbefore"]])
            if node_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", node_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", node_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", node_params["id"]])
            if node_params.get("force"):
                cmd.append("--force")
                
        elif action == "modify":
            cmd.extend(["--id", node_params["id"]])
            if node_params.get("node_url"):
                cmd.extend(["--node-url", node_params["node_url"]])
            if node_params.get("node_type"):
                cmd.extend(["--node-type", node_params["node_type"]])
            if node_params.get("username"):
                cmd.extend(["--username", node_params["username"]])
            if node_params.get("password"):
                cmd.extend(["--password", node_params["password"]])
            if node_params.get("products"):
                cmd.extend(["--products", node_params["products"]])
            if node_params.get("description"):
                cmd.extend(["--description", node_params["description"]])
            if node_params.get("meta"):
                cmd.extend(["--meta", node_params["meta"]])
            if node_params.get("labels"):
                cmd.extend(["--labels", node_params["labels"]])
            if node_params.get("json_file"):
                cmd.extend(["--json-file", node_params["json_file"]])
                
        else:
            raise ValueError(f"Unsupported Hadoop Node action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 