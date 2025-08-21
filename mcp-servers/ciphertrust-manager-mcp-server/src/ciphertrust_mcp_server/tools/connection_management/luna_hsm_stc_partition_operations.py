"""Luna HSM STC Partition operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import LUNA_HSM_STC_PARTITION_PARAMETERS, CONNECTION_OPERATIONS


class LunaHSMSTCPartitionOperations(ConnectionOperations):
    """Luna HSM STC Partition operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported Luna HSM STC Partition operations."""
        return CONNECTION_OPERATIONS["luna_hsm_stc_partition"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for Luna HSM STC Partition operations."""
        return {
            "luna_hsm_stc_partition_params": {
                "type": "object",
                "properties": LUNA_HSM_STC_PARTITION_PARAMETERS,
                "description": "Luna HSM STC Partition-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for Luna HSM STC Partition."""
        return {
            "create": {
                "required": ["name", "server_id"],
                "optional": ["partition_name", "partition_password", "certificate_file", "partition_identity", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
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
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute Luna HSM STC Partition operation."""
        stc_params = params.get("luna_hsm_stc_partition_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "luna-hsm", "stc-partition", action]
        
        # Add action-specific parameters
        if action == "create":
            if stc_params.get("name"):
                cmd.extend(["--name", stc_params["name"]])
            if stc_params.get("server_id"):
                cmd.extend(["--server-id", stc_params["server_id"]])
            if stc_params.get("partition_name"):
                cmd.extend(["--partition-name", stc_params["partition_name"]])
            if stc_params.get("partition_password"):
                cmd.extend(["--partition-password", stc_params["partition_password"]])
            if stc_params.get("certificate_file"):
                cmd.extend(["--certificate-file", stc_params["certificate_file"]])
            if stc_params.get("partition_identity"):
                cmd.extend(["--partition-identity", stc_params["partition_identity"]])
            if stc_params.get("products"):
                cmd.extend(["--products", stc_params["products"]])
            if stc_params.get("description"):
                cmd.extend(["--description", stc_params["description"]])
            if stc_params.get("meta"):
                cmd.extend(["--meta", stc_params["meta"]])
            if stc_params.get("labels"):
                cmd.extend(["--labels", stc_params["labels"]])
            if stc_params.get("json_file"):
                cmd.extend(["--json-file", stc_params["json_file"]])
                
        elif action == "list":
            if stc_params.get("name"):
                cmd.extend(["--name", stc_params["name"]])
            if stc_params.get("cloudname"):
                cmd.extend(["--cloudname", stc_params["cloudname"]])
            if stc_params.get("category"):
                cmd.extend(["--category", stc_params["category"]])
            if stc_params.get("products"):
                cmd.extend(["--products", stc_params["products"]])
            if stc_params.get("limit"):
                cmd.extend(["--limit", str(stc_params["limit"])])
            if stc_params.get("skip"):
                cmd.extend(["--skip", str(stc_params["skip"])])
            if stc_params.get("fields"):
                cmd.extend(["--fields", stc_params["fields"]])
            if stc_params.get("labels_query"):
                cmd.extend(["--labels-query", stc_params["labels_query"]])
            if stc_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", stc_params["lastconnectionafter"]])
            if stc_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", stc_params["lastconnectionbefore"]])
            if stc_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", stc_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", stc_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", stc_params["id"]])
            if stc_params.get("force"):
                cmd.append("--force")
                
        else:
            raise ValueError(f"Unsupported Luna HSM STC Partition action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 