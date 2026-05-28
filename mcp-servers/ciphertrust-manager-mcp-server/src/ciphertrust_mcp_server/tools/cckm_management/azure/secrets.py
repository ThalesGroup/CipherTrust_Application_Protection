"""Azure Secrets operations for CCKM."""

from typing import Any, Dict


def get_secret_operations() -> Dict[str, Any]:
    """Return schema and action requirements for Azure secret operations."""
    return {
        "schema_properties": {
            "azure_secrets_params": {
                "type": "object",
                "properties": {
                    # Basic secret parameters
                    "secret_name": {"type": "string", "description": "Name for the secret"},
                    "key_vault": {"type": "string", "description": "Name or ID of the key vault"},
                    "secret_value": {"type": "string", "description": "Secret value"},
                    "content_type": {"type": "string", "description": "Secret content type"},
                    
                    # Secret attributes
                    "enabled": {"type": "boolean", "description": "Status of secret (true/false)"},
                    "exp": {"type": "integer", "description": "Expiration date in Unix Epoch time format"},
                    "nbf": {"type": "integer", "description": "Activation date in Unix Epoch time format"},
                    
                    # Common parameters
                    "id": {"type": "string", "description": "Secret ID"},
                    "secret_id": {"type": "string", "description": "Secret ID"},
                    "tags": {"type": "object", "description": "Secret tags"},
                    
                    # List parameters
                    "vault_name": {"type": "string", "description": "Vault name for filtering"},
                    "limit": {"type": "integer", "description": "Maximum number of results"},
                    "skip": {"type": "integer", "description": "Number of results to skip"},
                    
                    # Job operations
                    "job_id": {"type": "string", "description": "Job ID for sync operations"},
                    "key_vaults": {"type": "string", "description": "Comma-separated list of vault names for sync"},
                    "synchronize_all": {"type": "boolean", "description": "Synchronize all secrets from all vaults"}
                }
            }
        },
        "action_requirements": {
            "secrets_list": {"required": [], "optional": ["vault_name", "limit", "skip"]},
            "secrets_get": {"required": ["id"], "optional": []},
            "secrets_create": {"required": ["secret_name", "key_vault", "secret_value"], "optional": ["content_type", "enabled", "exp", "nbf", "tags"]},
            "secrets_update": {"required": ["id"], "optional": ["secret_value", "content_type", "enabled", "exp", "nbf", "tags"]},
            "secrets_delete": {"required": ["id"], "optional": []},
            "secrets_recover": {"required": ["id"], "optional": []},
            "secrets_sync_jobs_start": {"required": [], "optional": ["key_vaults", "synchronize_all"]},
            "secrets_sync_jobs_get": {"required": ["job_id"], "optional": []},
            "secrets_sync_jobs_status": {"required": [], "optional": []},
            "secrets_sync_jobs_cancel": {"required": ["job_id"], "optional": []},
        }
    }


def build_secret_command(action: str, azure_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given Azure secret operation."""
    cmd = ["cckm", "azure", "secrets"]
    
    # Extract the base operation name (remove 'secrets_' prefix)
    base_action = action.replace("secrets_", "")
    
    # Simple actions that only need --id parameter
    simple_actions = ["get", "delete", "recover"]
    
    if base_action in simple_actions:
        cmd.extend([base_action, "--id", azure_params["id"]])
        return cmd
    
    if base_action == "list":
        cmd.append("list")
        if "vault_name" in azure_params:
            cmd.extend(["--vault-name", azure_params["vault_name"]])
        if "limit" in azure_params:
            cmd.extend(["--limit", str(azure_params["limit"])])
        if "skip" in azure_params:
            cmd.extend(["--skip", str(azure_params["skip"])])
            
    elif base_action == "create":
        cmd.append("create")
        cmd.extend(["--secret-name", azure_params["secret_name"]])
        cmd.extend(["--key-vault", azure_params["key_vault"]])
        cmd.extend(["--secret-value", azure_params["secret_value"]])
        
        if "content_type" in azure_params:
            cmd.extend(["--content-type", azure_params["content_type"]])
        if "enabled" in azure_params:
            cmd.extend(["--secret-enabled", str(azure_params["enabled"]).lower()])
        if "exp" in azure_params:
            cmd.extend(["--exp", str(azure_params["exp"])])
        if "nbf" in azure_params:
            cmd.extend(["--nbf", str(azure_params["nbf"])])
            
    elif base_action == "update":
        cmd.extend(["update", "--id", azure_params["id"]])
        if "secret_value" in azure_params:
            cmd.extend(["--secret-value", azure_params["secret_value"]])
        if "content_type" in azure_params:
            cmd.extend(["--content-type", azure_params["content_type"]])
        if "enabled" in azure_params:
            cmd.extend(["--secret-enabled", str(azure_params["enabled"]).lower()])
        if "exp" in azure_params:
            cmd.extend(["--exp", str(azure_params["exp"])])
        if "nbf" in azure_params:
            cmd.extend(["--nbf", str(azure_params["nbf"])])
            
    elif base_action == "sync_jobs_start":
        cmd.extend(["synchronization-jobs", "start"])
        if "key_vaults" in azure_params:
            cmd.extend(["--key-vaults", azure_params["key_vaults"]])
        if "synchronize_all" in azure_params and azure_params["synchronize_all"]:
            cmd.append("--synchronize-all")
            
    elif base_action == "sync_jobs_get":
        cmd.extend(["synchronization-jobs", "get", "--id", azure_params["job_id"]])
        
    elif base_action == "sync_jobs_status":
        cmd.extend(["synchronization-jobs", "status"])
        
    elif base_action == "sync_jobs_cancel":
        cmd.extend(["synchronization-jobs", "cancel", "--id", azure_params["job_id"]])
        
    else:
        raise ValueError(f"Unsupported Azure secrets action: {action}")
    
    return cmd 