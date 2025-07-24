"""Microsoft DKE operations for CCKM."""

from typing import Any, Dict, List
from .base import CCKMOperations
from .constants import MICROSOFT_PARAMETERS, CLOUD_OPERATIONS


class MicrosoftOperations(CCKMOperations):
    """Microsoft DKE operations for CCKM."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported Microsoft DKE operations."""
        return CLOUD_OPERATIONS["microsoft"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for Microsoft DKE operations."""
        return {
            "microsoft_params": {
                "type": "object",
                "properties": MICROSOFT_PARAMETERS,
                "description": "Microsoft DKE-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for Microsoft DKE."""
        return {
            "list": {
                "required": [],
                "optional": ["tenant_id", "limit", "skip", "domain", "auth_domain"]
            },
            "get": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "create": {
                "required": ["alias", "tenant_id", "client_id", "client_secret"],
                "optional": ["endpoint_url", "description", "enabled", "tags", "domain", "auth_domain"]
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
            "archive": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "recover": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "enable_rotation_job": {
                "required": ["id", "rotation_schedule"],
                "optional": ["domain", "auth_domain"]
            },
            "disable_rotation_job": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute Microsoft DKE operation."""
        microsoft_params = params.get("microsoft_params", {})
        
        # Build base command
        cmd = ["cckm", "microsoft", "dke", "endpoints"]
        
        # Add action-specific command
        if action == "list":
            cmd.append("list")
            if microsoft_params.get("tenant_id"):
                cmd.extend(["--tenant-id", microsoft_params["tenant_id"]])
            if microsoft_params.get("limit"):
                cmd.extend(["--limit", str(microsoft_params["limit"])])
            if microsoft_params.get("skip"):
                cmd.extend(["--skip", str(microsoft_params["skip"])])
                
        elif action == "get":
            cmd.extend(["get", "--id", microsoft_params["id"]])
            
        elif action == "create":
            cmd.extend(["create", 
                       "--alias", microsoft_params["alias"],
                       "--tenant-id", microsoft_params["tenant_id"],
                       "--client-id", microsoft_params["client_id"],
                       "--client-secret", microsoft_params["client_secret"]])
            if microsoft_params.get("endpoint_url"):
                cmd.extend(["--endpoint-url", microsoft_params["endpoint_url"]])
            if microsoft_params.get("description"):
                cmd.extend(["--description", microsoft_params["description"]])
            if microsoft_params.get("enabled") is not None:
                cmd.extend(["--enabled", "yes" if microsoft_params["enabled"] else "no"])
            if microsoft_params.get("tags"):
                cmd.extend(["--tags", str(microsoft_params["tags"])])
                
        elif action == "update":
            cmd.extend(["update", "--id", microsoft_params["id"]])
            if microsoft_params.get("alias"):
                cmd.extend(["--alias", microsoft_params["alias"]])
            if microsoft_params.get("description"):
                cmd.extend(["--description", microsoft_params["description"]])
            if microsoft_params.get("enabled") is not None:
                cmd.extend(["--enabled", "yes" if microsoft_params["enabled"] else "no"])
            if microsoft_params.get("tags"):
                cmd.extend(["--tags", str(microsoft_params["tags"])])
            if microsoft_params.get("endpoint_url"):
                cmd.extend(["--endpoint-url", microsoft_params["endpoint_url"]])
                
        elif action == "delete":
            cmd.extend(["delete", "--id", microsoft_params["id"]])
            
        elif action == "enable":
            cmd.extend(["enable", "--id", microsoft_params["id"]])
            
        elif action == "disable":
            cmd.extend(["disable", "--id", microsoft_params["id"]])
            
        elif action == "rotate":
            cmd.extend(["rotate", "--id", microsoft_params["id"]])
            
        elif action == "archive":
            cmd.extend(["archive", "--id", microsoft_params["id"]])
            
        elif action == "recover":
            cmd.extend(["recover", "--id", microsoft_params["id"]])
            
        elif action == "enable_rotation_job":
            cmd.extend(["enable-rotation-job", "--id", microsoft_params["id"], 
                       "--rotation-schedule", microsoft_params["rotation_schedule"]])
            
        elif action == "disable_rotation_job":
            cmd.extend(["disable-rotation-job", "--id", microsoft_params["id"]])
            
        else:
            raise ValueError(f"Unsupported Microsoft DKE action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 