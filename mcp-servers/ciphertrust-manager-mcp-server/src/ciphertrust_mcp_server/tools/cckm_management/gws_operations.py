"""Google Workspace (GWS) operations for CCKM."""

from typing import Any, Dict, List
from .base import CCKMOperations
from .constants import GWS_PARAMETERS, CLOUD_OPERATIONS


class GWSOperations(CCKMOperations):
    """Google Workspace (GWS) operations for CCKM."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported Google Workspace operations."""
        return CLOUD_OPERATIONS["gws"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for Google Workspace operations."""
        return {
            "gws_params": {
                "type": "object",
                "properties": GWS_PARAMETERS,
                "description": "Google Workspace-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for Google Workspace."""
        return {
            "list": {
                "required": [],
                "optional": ["project_id", "location", "limit", "skip", "domain", "auth_domain"]
            },
            "get": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "create": {
                "required": ["alias", "project_id", "location"],
                "optional": ["endpoint_url", "issuer_id", "description", "enabled", "tags", "domain", "auth_domain"]
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
            "rotate_key": {
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
            "wrap": {
                "required": ["id", "resource_key"],
                "optional": ["domain", "auth_domain"]
            },
            "unwrap": {
                "required": ["id", "wrapped_dek"],
                "optional": ["domain", "auth_domain"]
            },
            "privileged_unwrap": {
                "required": ["id", "wrapped_dek"],
                "optional": ["domain", "auth_domain"]
            },
            "rewrap": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "status": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "certs": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "digest": {
                "required": ["id", "resource_key"],
                "optional": ["domain", "auth_domain"]
            },
            "delegate": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "get_perimeter": {
                "required": ["id"],
                "optional": ["perimeter_id", "domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute Google Workspace operation."""
        gws_params = params.get("gws_params", {})
        
        # Build base command
        cmd = ["cckm", "gws", "endpoint"]
        
        # Add action-specific command
        if action == "list":
            cmd.append("list")
            if gws_params.get("project_id"):
                cmd.extend(["--project-id", gws_params["project_id"]])
            if gws_params.get("location"):
                cmd.extend(["--location", gws_params["location"]])
            if gws_params.get("limit"):
                cmd.extend(["--limit", str(gws_params["limit"])])
            if gws_params.get("skip"):
                cmd.extend(["--skip", str(gws_params["skip"])])
                
        elif action == "get":
            cmd.extend(["get", "--id", gws_params["id"]])
            
        elif action == "create":
            cmd.extend(["create", 
                       "--alias", gws_params["alias"],
                       "--project-id", gws_params["project_id"],
                       "--location", gws_params["location"]])
            if gws_params.get("endpoint_url"):
                cmd.extend(["--endpoint-url", gws_params["endpoint_url"]])
            if gws_params.get("issuer_id"):
                cmd.extend(["--issuer-id", gws_params["issuer_id"]])
            if gws_params.get("description"):
                cmd.extend(["--description", gws_params["description"]])
            if gws_params.get("enabled") is not None:
                cmd.extend(["--enabled", "yes" if gws_params["enabled"] else "no"])
            if gws_params.get("tags"):
                cmd.extend(["--tags", str(gws_params["tags"])])
                
        elif action == "update":
            cmd.extend(["update", "--id", gws_params["id"]])
            if gws_params.get("alias"):
                cmd.extend(["--alias", gws_params["alias"]])
            if gws_params.get("description"):
                cmd.extend(["--description", gws_params["description"]])
            if gws_params.get("enabled") is not None:
                cmd.extend(["--enabled", "yes" if gws_params["enabled"] else "no"])
            if gws_params.get("tags"):
                cmd.extend(["--tags", str(gws_params["tags"])])
            if gws_params.get("endpoint_url"):
                cmd.extend(["--endpoint-url", gws_params["endpoint_url"]])
                
        elif action == "delete":
            cmd.extend(["delete", "--id", gws_params["id"]])
            
        elif action == "enable":
            cmd.extend(["enable", "--id", gws_params["id"]])
            
        elif action == "disable":
            cmd.extend(["disable", "--id", gws_params["id"]])
            
        elif action == "rotate_key":
            cmd.extend(["rotate-key", "--id", gws_params["id"]])
            
        elif action == "archive":
            cmd.extend(["archive", "--id", gws_params["id"]])
            
        elif action == "recover":
            cmd.extend(["recover", "--id", gws_params["id"]])
            
        elif action == "wrap":
            cmd.extend(["wrap", "--id", gws_params["id"], "--resource-key", gws_params["resource_key"]])
            
        elif action == "unwrap":
            cmd.extend(["unwrap", "--id", gws_params["id"], "--wrapped-dek", gws_params["wrapped_dek"]])
            
        elif action == "privileged_unwrap":
            cmd.extend(["privileged-unwrap", "--id", gws_params["id"], "--wrapped-dek", gws_params["wrapped_dek"]])
            
        elif action == "rewrap":
            cmd.extend(["rewrap", "--id", gws_params["id"]])
            
        elif action == "status":
            cmd.extend(["status", "--id", gws_params["id"]])
            
        elif action == "certs":
            cmd.extend(["certs", "--id", gws_params["id"]])
            
        elif action == "digest":
            cmd.extend(["digest", "--id", gws_params["id"], "--resource-key", gws_params["resource_key"]])
            
        elif action == "delegate":
            cmd.extend(["delegate", "--id", gws_params["id"]])
            
        elif action == "get_perimeter":
            cmd.extend(["get-perimeter", "--id", gws_params["id"]])
            if gws_params.get("perimeter_id"):
                cmd.extend(["--perimeter-id", gws_params["perimeter_id"]])
            
        else:
            raise ValueError(f"Unsupported Google Workspace action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 