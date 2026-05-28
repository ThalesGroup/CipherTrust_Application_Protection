"""Hadoop connection operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import HADOOP_PARAMETERS, CONNECTION_OPERATIONS


class HadoopOperations(ConnectionOperations):
    """Hadoop connection operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported Hadoop operations."""
        return CONNECTION_OPERATIONS["hadoop"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for Hadoop operations."""
        return {
            "hadoop_params": {
                "type": "object",
                "properties": HADOOP_PARAMETERS,
                "description": "Hadoop-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for Hadoop."""
        return {
            "create": {
                "required": ["name"],
                "optional": ["namenode_url", "username", "password", "kerberos_principal", "keytab_file", "nodes_json_file", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
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
                "optional": ["name", "namenode_url", "username", "password", "kerberos_principal", "keytab_file", "nodes_json_file", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "test": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute Hadoop connection operation."""
        hadoop_params = params.get("hadoop_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "hadoop", action]
        
        # Add action-specific parameters
        if action == "create":
            if hadoop_params.get("name"):
                cmd.extend(["--name", hadoop_params["name"]])
            if hadoop_params.get("namenode_url"):
                cmd.extend(["--namenode-url", hadoop_params["namenode_url"]])
            if hadoop_params.get("username"):
                cmd.extend(["--username", hadoop_params["username"]])
            if hadoop_params.get("password"):
                cmd.extend(["--password", hadoop_params["password"]])
            if hadoop_params.get("kerberos_principal"):
                cmd.extend(["--kerberos-principal", hadoop_params["kerberos_principal"]])
            if hadoop_params.get("keytab_file"):
                cmd.extend(["--keytab-file", hadoop_params["keytab_file"]])
            if hadoop_params.get("nodes_json_file"):
                cmd.extend(["--nodes-json-file", hadoop_params["nodes_json_file"]])
            if hadoop_params.get("products"):
                cmd.extend(["--products", hadoop_params["products"]])
            if hadoop_params.get("description"):
                cmd.extend(["--description", hadoop_params["description"]])
            if hadoop_params.get("meta"):
                cmd.extend(["--meta", hadoop_params["meta"]])
            if hadoop_params.get("labels"):
                cmd.extend(["--labels", hadoop_params["labels"]])
            if hadoop_params.get("json_file"):
                cmd.extend(["--json-file", hadoop_params["json_file"]])
                
        elif action == "list":
            if hadoop_params.get("name"):
                cmd.extend(["--name", hadoop_params["name"]])
            if hadoop_params.get("cloudname"):
                cmd.extend(["--cloudname", hadoop_params["cloudname"]])
            if hadoop_params.get("category"):
                cmd.extend(["--category", hadoop_params["category"]])
            if hadoop_params.get("products"):
                cmd.extend(["--products", hadoop_params["products"]])
            if hadoop_params.get("limit"):
                cmd.extend(["--limit", str(hadoop_params["limit"])])
            if hadoop_params.get("skip"):
                cmd.extend(["--skip", str(hadoop_params["skip"])])
            if hadoop_params.get("fields"):
                cmd.extend(["--fields", hadoop_params["fields"]])
            if hadoop_params.get("labels_query"):
                cmd.extend(["--labels-query", hadoop_params["labels_query"]])
            if hadoop_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", hadoop_params["lastconnectionafter"]])
            if hadoop_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", hadoop_params["lastconnectionbefore"]])
            if hadoop_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", hadoop_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", hadoop_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", hadoop_params["id"]])
            if hadoop_params.get("force"):
                cmd.append("--force")
                
        elif action == "modify":
            cmd.extend(["--id", hadoop_params["id"]])
            if hadoop_params.get("name"):
                cmd.extend(["--name", hadoop_params["name"]])
            if hadoop_params.get("namenode_url"):
                cmd.extend(["--namenode-url", hadoop_params["namenode_url"]])
            if hadoop_params.get("username"):
                cmd.extend(["--username", hadoop_params["username"]])
            if hadoop_params.get("password"):
                cmd.extend(["--password", hadoop_params["password"]])
            if hadoop_params.get("kerberos_principal"):
                cmd.extend(["--kerberos-principal", hadoop_params["kerberos_principal"]])
            if hadoop_params.get("keytab_file"):
                cmd.extend(["--keytab-file", hadoop_params["keytab_file"]])
            if hadoop_params.get("nodes_json_file"):
                cmd.extend(["--nodes-json-file", hadoop_params["nodes_json_file"]])
            if hadoop_params.get("products"):
                cmd.extend(["--products", hadoop_params["products"]])
            if hadoop_params.get("description"):
                cmd.extend(["--description", hadoop_params["description"]])
            if hadoop_params.get("meta"):
                cmd.extend(["--meta", hadoop_params["meta"]])
            if hadoop_params.get("labels"):
                cmd.extend(["--labels", hadoop_params["labels"]])
            if hadoop_params.get("json_file"):
                cmd.extend(["--json-file", hadoop_params["json_file"]])
                
        elif action == "test":
            cmd.extend(["--id", hadoop_params["id"]])
            
        else:
            raise ValueError(f"Unsupported Hadoop action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 