"""Google Cloud operations for CCKM."""

from typing import Any, Dict, List
from .base import CCKMOperations
from .constants import GOOGLE_PARAMETERS, CLOUD_OPERATIONS


class GoogleOperations(CCKMOperations):
    """Google Cloud key operations for CCKM."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported Google Cloud operations."""
        return CLOUD_OPERATIONS["google"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for Google Cloud operations."""
        return {
            "google_params": {
                "type": "object",
                "properties": GOOGLE_PARAMETERS,
                "description": "Google Cloud-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for Google Cloud."""
        return {
            "list": {
                "required": [],
                "optional": ["project_id", "location", "key_ring", "limit", "skip", "domain", "auth_domain"]
            },
            "get": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "create": {
                "required": ["alias", "project_id", "location", "key_ring"],
                "optional": ["protection_level", "algorithm", "purpose", "domain", "auth_domain"]
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
            "destroy": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "restore": {
                "required": ["backup_data"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute Google Cloud operation."""
        google_params = params.get("google_params", {})
        
        # Build base command
        cmd = ["cckm", "google", "keys"]
        
        # Add action-specific command
        if action == "list":
            cmd.append("list")
            if google_params.get("project_id"):
                cmd.extend(["--project-id", google_params["project_id"]])
            if google_params.get("location"):
                cmd.extend(["--location", google_params["location"]])
            if google_params.get("key_ring"):
                cmd.extend(["--key-ring", google_params["key_ring"]])
            if google_params.get("limit"):
                cmd.extend(["--limit", str(google_params["limit"])])
            if google_params.get("skip"):
                cmd.extend(["--skip", str(google_params["skip"])])
                
        elif action == "get":
            cmd.extend(["get", "--id", google_params["id"]])
            
        elif action == "create":
            cmd.extend(["create", 
                       "--alias", google_params["alias"],
                       "--project-id", google_params["project_id"],
                       "--location", google_params["location"],
                       "--key-ring", google_params["key_ring"]])
            if google_params.get("protection_level"):
                cmd.extend(["--protection-level", google_params["protection_level"]])
            if google_params.get("algorithm"):
                cmd.extend(["--algorithm", google_params["algorithm"]])
            if google_params.get("purpose"):
                cmd.extend(["--purpose", google_params["purpose"]])
                
        elif action == "update":
            cmd.extend(["update", "--id", google_params["id"]])
            if google_params.get("alias"):
                cmd.extend(["--alias", google_params["alias"]])
            if google_params.get("description"):
                cmd.extend(["--description", google_params["description"]])
            if google_params.get("enabled") is not None:
                cmd.extend(["--enabled", "yes" if google_params["enabled"] else "no"])
            if google_params.get("tags"):
                cmd.extend(["--tags", str(google_params["tags"])])
                
        elif action == "delete":
            cmd.extend(["delete", "--id", google_params["id"]])
            
        elif action == "enable":
            cmd.extend(["enable", "--id", google_params["id"]])
            
        elif action == "disable":
            cmd.extend(["disable", "--id", google_params["id"]])
            
        elif action == "rotate":
            cmd.extend(["rotate", "--id", google_params["id"]])
            
        elif action == "destroy":
            cmd.extend(["destroy", "--id", google_params["id"]])
            
        elif action == "restore":
            cmd.extend(["restore", "--backup-data", google_params["backup_data"]])
            
        else:
            raise ValueError(f"Unsupported Google Cloud action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 