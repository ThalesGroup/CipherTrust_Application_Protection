"""AWS operations for CCKM."""

from typing import Any, Dict, List
from .base import CCKMOperations
from .constants import AWS_PARAMETERS, CLOUD_OPERATIONS


class AWSOperations(CCKMOperations):
    """AWS key operations for CCKM."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported AWS operations."""
        return CLOUD_OPERATIONS["aws"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for AWS operations."""
        return {
            "aws_params": {
                "type": "object",
                "properties": AWS_PARAMETERS,
                "description": "AWS-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for AWS."""
        return {
            "list": {
                "required": [],
                "optional": ["alias", "enabled", "limit", "skip", "domain", "auth_domain"]
            },
            "get": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "create": {
                "required": ["alias", "region", "key_spec"],
                "optional": ["description", "enabled", "tags", "key_usage", "origin", "domain", "auth_domain"]
            },
            "update": {
                "required": ["id"],
                "optional": ["alias", "description", "enabled", "tags", "domain", "auth_domain"]
            },
            "delete": {
                "required": ["id"],
                "optional": ["pending_window_in_days", "domain", "auth_domain"]
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
            "add_alias": {
                "required": ["id", "alias"],
                "optional": ["domain", "auth_domain"]
            },
            "delete_alias": {
                "required": ["id", "alias"],
                "optional": ["domain", "auth_domain"]
            },
            "add_tags": {
                "required": ["id", "tags"],
                "optional": ["domain", "auth_domain"]
            },
            "remove_tags": {
                "required": ["id", "tags"],
                "optional": ["domain", "auth_domain"]
            },
            "schedule_deletion": {
                "required": ["id", "pending_window_in_days"],
                "optional": ["domain", "auth_domain"]
            },
            "cancel_deletion": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "import_material": {
                "required": ["id", "material"],
                "optional": ["domain", "auth_domain"]
            },
            "delete_material": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "upload": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "download_public_key": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "policy": {
                "required": ["id", "policy"],
                "optional": ["bypass_policy_lockout_safety_check", "domain", "auth_domain"]
            },
            "replicate_key": {
                "required": ["id", "region"],
                "optional": ["domain", "auth_domain"]
            },
            "block": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "unblock": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute AWS operation."""
        aws_params = params.get("aws_params", {})
        
        # Build base command
        cmd = ["cckm", "aws", "keys"]
        
        # Add action-specific command
        if action == "list":
            cmd.append("list")
            if aws_params.get("alias"):
                cmd.extend(["--alias", aws_params["alias"]])
            if aws_params.get("enabled") is not None:
                cmd.extend(["--enabled", "yes" if aws_params["enabled"] else "no"])
            if aws_params.get("limit"):
                cmd.extend(["--limit", str(aws_params["limit"])])
            if aws_params.get("skip"):
                cmd.extend(["--skip", str(aws_params["skip"])])
                
        elif action == "get":
            cmd.extend(["get", "--id", aws_params["id"]])
            
        elif action == "create":
            cmd.extend(["create", 
                       "--alias", aws_params["alias"],
                       "--region", aws_params["region"],
                       "--key-spec", aws_params["key_spec"]])
            if aws_params.get("description"):
                cmd.extend(["--description", aws_params["description"]])
            if aws_params.get("enabled") is not None:
                cmd.extend(["--enabled", "yes" if aws_params["enabled"] else "no"])
            if aws_params.get("tags"):
                cmd.extend(["--tags", str(aws_params["tags"])])
            if aws_params.get("key_usage"):
                cmd.extend(["--key-usage", aws_params["key_usage"]])
            if aws_params.get("origin"):
                cmd.extend(["--origin", aws_params["origin"]])
                
        elif action == "update":
            cmd.extend(["update", "--id", aws_params["id"]])
            if aws_params.get("alias"):
                cmd.extend(["--alias", aws_params["alias"]])
            if aws_params.get("description"):
                cmd.extend(["--description", aws_params["description"]])
            if aws_params.get("enabled") is not None:
                cmd.extend(["--enabled", "yes" if aws_params["enabled"] else "no"])
            if aws_params.get("tags"):
                cmd.extend(["--tags", str(aws_params["tags"])])
                
        elif action == "delete":
            cmd.extend(["delete", "--id", aws_params["id"]])
            if aws_params.get("pending_window_in_days"):
                cmd.extend(["--pending-window-in-days", str(aws_params["pending_window_in_days"])])
                
        elif action == "enable":
            cmd.extend(["enable", "--id", aws_params["id"]])
            
        elif action == "disable":
            cmd.extend(["disable", "--id", aws_params["id"]])
            
        elif action == "rotate":
            cmd.extend(["rotate", "--id", aws_params["id"]])
            
        elif action == "add_alias":
            cmd.extend(["add-alias", "--id", aws_params["id"], "--alias", aws_params["alias"]])
            
        elif action == "delete_alias":
            cmd.extend(["delete-alias", "--id", aws_params["id"], "--alias", aws_params["alias"]])
            
        elif action == "add_tags":
            cmd.extend(["add-tags", "--id", aws_params["id"], "--tags", str(aws_params["tags"])])
            
        elif action == "remove_tags":
            cmd.extend(["remove-tags", "--id", aws_params["id"], "--tags", str(aws_params["tags"])])
            
        elif action == "schedule_deletion":
            cmd.extend(["schedule-deletion", "--id", aws_params["id"], 
                       "--pending-window-in-days", str(aws_params["pending_window_in_days"])])
            
        elif action == "cancel_deletion":
            cmd.extend(["cancel-deletion", "--id", aws_params["id"]])
            
        elif action == "import_material":
            cmd.extend(["import-material", "--id", aws_params["id"], "--material", aws_params["material"]])
            
        elif action == "delete_material":
            cmd.extend(["delete-material", "--id", aws_params["id"]])
            
        elif action == "upload":
            cmd.extend(["upload", "--id", aws_params["id"]])
            
        elif action == "download_public_key":
            cmd.extend(["download-public-key", "--id", aws_params["id"]])
            
        elif action == "policy":
            cmd.extend(["policy", "--id", aws_params["id"], "--policy", aws_params["policy"]])
            if aws_params.get("bypass_policy_lockout_safety_check"):
                cmd.append("--bypass-policy-lockout-safety-check")
                
        elif action == "replicate_key":
            cmd.extend(["replicate-key", "--id", aws_params["id"], "--region", aws_params["region"]])
            
        elif action == "block":
            cmd.extend(["block", "--id", aws_params["id"]])
            
        elif action == "unblock":
            cmd.extend(["unblock", "--id", aws_params["id"]])
            
        else:
            raise ValueError(f"Unsupported AWS action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 