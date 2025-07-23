"""Google EKM operations for CCKM."""

from typing import Any, Dict, List
from .base import CCKMOperations
from .constants import EKM_PARAMETERS, CLOUD_OPERATIONS


class EKMOperations(CCKMOperations):
    """Google EKM operations for CCKM."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported Google EKM operations."""
        return CLOUD_OPERATIONS["ekm"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for Google EKM operations."""
        return {
            "ekm_params": {
                "type": "object",
                "properties": EKM_PARAMETERS,
                "description": "Google EKM-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for Google EKM."""
        return {
            "list": {
                "required": [],
                "optional": ["project_id", "location", "cryptospace_id", "limit", "skip", "domain", "auth_domain"]
            },
            "get": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "create": {
                "required": ["alias", "project_id", "location"],
                "optional": ["cryptospace_id", "endpoint_url", "description", "enabled", "tags", "domain", "auth_domain"]
            },
            "update": {
                "required": ["id"],
                "optional": ["alias", "description", "enabled", "tags", "endpoint_url", "domain", "auth_domain"]
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
            "policy": {
                "required": ["id", "policy"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute Google EKM operation."""
        ekm_params = params.get("ekm_params", {})
        
        # Build base command
        cmd = ["cckm", "ekm", "endpoints"]
        
        # Add action-specific command
        if action == "list":
            cmd.append("list")
            if ekm_params.get("project_id"):
                cmd.extend(["--project-id", ekm_params["project_id"]])
            if ekm_params.get("location"):
                cmd.extend(["--location", ekm_params["location"]])
            if ekm_params.get("cryptospace_id"):
                cmd.extend(["--cryptospace-id", ekm_params["cryptospace_id"]])
            if ekm_params.get("limit"):
                cmd.extend(["--limit", str(ekm_params["limit"])])
            if ekm_params.get("skip"):
                cmd.extend(["--skip", str(ekm_params["skip"])])
                
        elif action == "get":
            cmd.extend(["get", "--id", ekm_params["id"]])
            
        elif action == "create":
            cmd.extend(["create", 
                       "--alias", ekm_params["alias"],
                       "--project-id", ekm_params["project_id"],
                       "--location", ekm_params["location"]])
            if ekm_params.get("cryptospace_id"):
                cmd.extend(["--cryptospace-id", ekm_params["cryptospace_id"]])
            if ekm_params.get("endpoint_url"):
                cmd.extend(["--endpoint-url", ekm_params["endpoint_url"]])
            if ekm_params.get("description"):
                cmd.extend(["--description", ekm_params["description"]])
            if ekm_params.get("enabled") is not None:
                cmd.extend(["--enabled", "yes" if ekm_params["enabled"] else "no"])
            if ekm_params.get("tags"):
                cmd.extend(["--tags", str(ekm_params["tags"])])
                
        elif action == "update":
            cmd.extend(["update", "--id", ekm_params["id"]])
            if ekm_params.get("alias"):
                cmd.extend(["--alias", ekm_params["alias"]])
            if ekm_params.get("description"):
                cmd.extend(["--description", ekm_params["description"]])
            if ekm_params.get("enabled") is not None:
                cmd.extend(["--enabled", "yes" if ekm_params["enabled"] else "no"])
            if ekm_params.get("tags"):
                cmd.extend(["--tags", str(ekm_params["tags"])])
            if ekm_params.get("endpoint_url"):
                cmd.extend(["--endpoint-url", ekm_params["endpoint_url"]])
                
        elif action == "delete":
            cmd.extend(["delete", "--id", ekm_params["id"]])
            
        elif action == "enable":
            cmd.extend(["enable", "--id", ekm_params["id"]])
            
        elif action == "disable":
            cmd.extend(["disable", "--id", ekm_params["id"]])
            
        elif action == "rotate":
            cmd.extend(["rotate", "--id", ekm_params["id"]])
            
        elif action == "destroy":
            cmd.extend(["destroy", "--id", ekm_params["id"]])
            
        elif action == "policy":
            cmd.extend(["policy", "--id", ekm_params["id"], "--policy", ekm_params["policy"]])
            
        else:
            raise ValueError(f"Unsupported Google EKM action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 