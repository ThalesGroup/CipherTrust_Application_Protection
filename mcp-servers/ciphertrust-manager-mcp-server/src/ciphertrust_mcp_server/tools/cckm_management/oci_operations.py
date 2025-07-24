"""OCI operations for CCKM."""

from typing import Any, Dict, List
from .base import CCKMOperations
from .constants import OCI_PARAMETERS, CLOUD_OPERATIONS


class OCIOperations(CCKMOperations):
    """OCI key operations for CCKM."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported OCI operations."""
        return CLOUD_OPERATIONS["oci"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for OCI operations."""
        return {
            "oci_params": {
                "type": "object",
                "properties": OCI_PARAMETERS,
                "description": "OCI-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for OCI."""
        return {
            "list": {
                "required": [],
                "optional": ["compartment_id", "vault_id", "limit", "skip", "domain", "auth_domain"]
            },
            "get": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "create": {
                "required": ["alias", "compartment_id", "vault_id"],
                "optional": ["key_shape", "protection_mode", "algorithm", "domain", "auth_domain"]
            },
            "update": {
                "required": ["id"],
                "optional": ["alias", "description", "enabled", "tags", "domain", "auth_domain"]
            },
            "delete": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "enable": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "disable": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "rotate": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "backup": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "restore": {
                "required": ["backup_data"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute OCI operation."""
        oci_params = params.get("oci_params", {})
        
        # Build base command
        cmd = ["cckm", "oci", "keys"]
        
        # Add action-specific command
        if action == "list":
            cmd.append("list")
            if oci_params.get("compartment_id"):
                cmd.extend(["--compartment-id", oci_params["compartment_id"]])
            if oci_params.get("vault_id"):
                cmd.extend(["--vault-id", oci_params["vault_id"]])
            if oci_params.get("limit"):
                cmd.extend(["--limit", str(oci_params["limit"])])
            if oci_params.get("skip"):
                cmd.extend(["--skip", str(oci_params["skip"])])
                
        elif action == "get":
            cmd.extend(["get", "--id", oci_params["id"]])
            
        elif action == "create":
            cmd.extend(["create", 
                       "--alias", oci_params["alias"],
                       "--compartment-id", oci_params["compartment_id"],
                       "--vault-id", oci_params["vault_id"]])
            if oci_params.get("key_shape"):
                cmd.extend(["--key-shape", str(oci_params["key_shape"])])
            if oci_params.get("protection_mode"):
                cmd.extend(["--protection-mode", oci_params["protection_mode"]])
            if oci_params.get("algorithm"):
                cmd.extend(["--algorithm", oci_params["algorithm"]])
                
        elif action == "update":
            cmd.extend(["update", "--id", oci_params["id"]])
            if oci_params.get("alias"):
                cmd.extend(["--alias", oci_params["alias"]])
            if oci_params.get("description"):
                cmd.extend(["--description", oci_params["description"]])
            if oci_params.get("enabled") is not None:
                cmd.extend(["--enabled", "yes" if oci_params["enabled"] else "no"])
            if oci_params.get("tags"):
                cmd.extend(["--tags", str(oci_params["tags"])])
                
        elif action == "delete":
            cmd.extend(["delete", "--id", oci_params["id"]])
            
        elif action == "enable":
            cmd.extend(["enable", "--id", oci_params["id"]])
            
        elif action == "disable":
            cmd.extend(["disable", "--id", oci_params["id"]])
            
        elif action == "rotate":
            cmd.extend(["rotate", "--id", oci_params["id"]])
            
        elif action == "backup":
            cmd.extend(["backup", "--id", oci_params["id"]])
            
        elif action == "restore":
            cmd.extend(["restore", "--backup-data", oci_params["backup_data"]])
            
        else:
            raise ValueError(f"Unsupported OCI action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 