"""Luna HSM connection operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import LUNA_HSM_PARAMETERS, CONNECTION_OPERATIONS


class LunaHSMOperations(ConnectionOperations):
    """Luna HSM connection operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported Luna HSM operations."""
        return CONNECTION_OPERATIONS["luna_hsm"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for Luna HSM operations."""
        return {
            "luna_hsm_params": {
                "type": "object",
                "properties": LUNA_HSM_PARAMETERS,
                "description": "Luna HSM-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for Luna HSM."""
        return {
            "create": {
                "required": ["name"],
                "optional": ["server_url", "partition_name", "partition_password", "certificate_file", "partitions_json_file", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
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
                "optional": ["name", "server_url", "partition_name", "partition_password", "certificate_file", "partitions_json_file", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "test": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute Luna HSM connection operation."""
        luna_hsm_params = params.get("luna_hsm_params", {})
        
        # Build base command
        # Note: This is for the luna-hsm connections command
        # For server and stc-partition operations, use the specialized classes
        cmd = ["connectionmgmt", "luna-hsm", "connections", action]
        
        # Add action-specific parameters
        if action == "create":
            if luna_hsm_params.get("name"):
                cmd.extend(["--name", luna_hsm_params["name"]])
            if luna_hsm_params.get("server_url"):
                cmd.extend(["--server-url", luna_hsm_params["server_url"]])
            if luna_hsm_params.get("partition_name"):
                cmd.extend(["--partition-name", luna_hsm_params["partition_name"]])
            if luna_hsm_params.get("partition_password"):
                cmd.extend(["--partition-password", luna_hsm_params["partition_password"]])
            if luna_hsm_params.get("certificate_file"):
                cmd.extend(["--certificate-file", luna_hsm_params["certificate_file"]])
            if luna_hsm_params.get("partitions_json_file"):
                cmd.extend(["--partitions-json-file", luna_hsm_params["partitions_json_file"]])
            if luna_hsm_params.get("products"):
                cmd.extend(["--products", luna_hsm_params["products"]])
            if luna_hsm_params.get("description"):
                cmd.extend(["--description", luna_hsm_params["description"]])
            if luna_hsm_params.get("meta"):
                cmd.extend(["--meta", luna_hsm_params["meta"]])
            if luna_hsm_params.get("labels"):
                cmd.extend(["--labels", luna_hsm_params["labels"]])
            if luna_hsm_params.get("json_file"):
                cmd.extend(["--json-file", luna_hsm_params["json_file"]])
                
        elif action == "list":
            if luna_hsm_params.get("name"):
                cmd.extend(["--name", luna_hsm_params["name"]])
            if luna_hsm_params.get("cloudname"):
                cmd.extend(["--cloudname", luna_hsm_params["cloudname"]])
            if luna_hsm_params.get("category"):
                cmd.extend(["--category", luna_hsm_params["category"]])
            if luna_hsm_params.get("products"):
                cmd.extend(["--products", luna_hsm_params["products"]])
            if luna_hsm_params.get("limit"):
                cmd.extend(["--limit", str(luna_hsm_params["limit"])])
            if luna_hsm_params.get("skip"):
                cmd.extend(["--skip", str(luna_hsm_params["skip"])])
            if luna_hsm_params.get("fields"):
                cmd.extend(["--fields", luna_hsm_params["fields"]])
            if luna_hsm_params.get("labels_query"):
                cmd.extend(["--labels-query", luna_hsm_params["labels_query"]])
            if luna_hsm_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", luna_hsm_params["lastconnectionafter"]])
            if luna_hsm_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", luna_hsm_params["lastconnectionbefore"]])
            if luna_hsm_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", luna_hsm_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", luna_hsm_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", luna_hsm_params["id"]])
            if luna_hsm_params.get("force"):
                cmd.append("--force")
                
        elif action == "modify":
            cmd.extend(["--id", luna_hsm_params["id"]])
            if luna_hsm_params.get("name"):
                cmd.extend(["--name", luna_hsm_params["name"]])
            if luna_hsm_params.get("server_url"):
                cmd.extend(["--server-url", luna_hsm_params["server_url"]])
            if luna_hsm_params.get("partition_name"):
                cmd.extend(["--partition-name", luna_hsm_params["partition_name"]])
            if luna_hsm_params.get("partition_password"):
                cmd.extend(["--partition-password", luna_hsm_params["partition_password"]])
            if luna_hsm_params.get("certificate_file"):
                cmd.extend(["--certificate-file", luna_hsm_params["certificate_file"]])
            if luna_hsm_params.get("partitions_json_file"):
                cmd.extend(["--partitions-json-file", luna_hsm_params["partitions_json_file"]])
            if luna_hsm_params.get("products"):
                cmd.extend(["--products", luna_hsm_params["products"]])
            if luna_hsm_params.get("description"):
                cmd.extend(["--description", luna_hsm_params["description"]])
            if luna_hsm_params.get("meta"):
                cmd.extend(["--meta", luna_hsm_params["meta"]])
            if luna_hsm_params.get("labels"):
                cmd.extend(["--labels", luna_hsm_params["labels"]])
            if luna_hsm_params.get("json_file"):
                cmd.extend(["--json-file", luna_hsm_params["json_file"]])
                
        elif action == "test":
            cmd.extend(["--id", luna_hsm_params["id"]])
            
        else:
            raise ValueError(f"Unsupported Luna HSM action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 