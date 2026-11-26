"""Azure Certificates operations for CCKM."""

from typing import Any, Dict


def get_certificate_operations() -> Dict[str, Any]:
    """Return schema and action requirements for Azure certificate operations."""
    return {
        "schema_properties": {
            "azure_certificates_params": {
                "type": "object",
                "properties": {
                    # Basic certificate parameters
                    "certificate_name": {"type": "string", "description": "Name for the certificate"},
                    "key_vault": {"type": "string", "description": "Name or ID of the key vault"},
                    "certificate_keyprop_kty": {"type": "string", "description": "Key type for certificate"},
                    "certificate_x509_subject": {"type": "string", "description": "X.509 subject"},
                    
                    # Certificate attributes
                    "enabled": {"type": "boolean", "description": "Status of certificate (true/false)"},
                    "exp": {"type": "integer", "description": "Expiration date in Unix Epoch time format"},
                    "nbf": {"type": "integer", "description": "Activation date in Unix Epoch time format"},
                    
                    # Common parameters
                    "id": {"type": "string", "description": "Certificate ID"},
                    "certificate_id": {"type": "string", "description": "Certificate ID"},
                    "tags": {"type": "object", "description": "Certificate tags"},
                    
                    # List parameters
                    "vault_name": {"type": "string", "description": "Vault name for filtering"},
                    "limit": {"type": "integer", "description": "Maximum number of results"},
                    "skip": {"type": "integer", "description": "Number of results to skip"},
                    
                    # JSON file parameters
                    "azure_certificatecreate_jsonfile": {"type": "string", "description": "Azure certificate create parameters in JSON file"},
                    "azure_tags_jsonfile": {"type": "string", "description": "Azure tags in JSON file"},
                    "azure_updatecertificate_params": {"type": "string", "description": "Azure update certificate parameters in JSON file"},
                    
                    # Import and restore
                    "pfx_base64": {"type": "string", "description": "Base64 encoded PFX certificate"},
                    "pfx_password": {"type": "string", "description": "PFX certificate password"},
                    "backup_data": {"type": "string", "description": "Backup data for restore operations"},
                    
                    # Job operations
                    "job_id": {"type": "string", "description": "Job ID for sync operations"},
                    "key_vaults": {"type": "string", "description": "Comma-separated list of vault names for sync"},
                    "synchronize_all": {"type": "boolean", "description": "Synchronize all certificates from all vaults"}
                }
            }
        },
        "action_requirements": {
            "certificates_list": {"required": [], "optional": ["vault_name", "limit", "skip"]},
            "certificates_get": {"required": ["id"], "optional": []},
            "certificates_create": {"required": [], "optional": ["certificate_name", "key_vault", "certificate_keyprop_kty", "certificate_x509_subject", "enabled", "exp", "nbf", "azure_certificatecreate_jsonfile", "azure_tags_jsonfile"]},
            "certificates_update": {"required": ["id"], "optional": ["enabled", "exp", "nbf", "tags", "azure_updatecertificate_params"]},
            "certificates_delete": {"required": ["id"], "optional": []},
            "certificates_import": {"required": ["certificate_name", "key_vault", "pfx_base64"], "optional": ["pfx_password"]},
            "certificates_restore": {"required": ["backup_data"], "optional": []},
            "certificates_recover": {"required": ["id"], "optional": []},
            "certificates_hard_delete": {"required": ["id"], "optional": []},
            "certificates_soft_delete": {"required": ["id"], "optional": []},
            "certificates_sync_jobs_start": {"required": [], "optional": ["key_vaults", "synchronize_all"]},
            "certificates_sync_jobs_get": {"required": ["job_id"], "optional": []},
            "certificates_sync_jobs_status": {"required": [], "optional": []},
            "certificates_sync_jobs_cancel": {"required": ["job_id"], "optional": []},
        }
    }


def build_certificate_command(action: str, azure_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given Azure certificate operation."""
    cmd = ["cckm", "azure", "certificates"]
    
    # Extract the base operation name (remove 'certificates_' prefix)
    base_action = action.replace("certificates_", "")
    
    # Simple actions that only need --id parameter
    simple_actions = ["get", "delete", "recover", "hard_delete", "soft_delete"]
    
    if base_action in simple_actions:
        cmd.extend([base_action.replace("_", "-"), "--id", azure_params["id"]])
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
        
        # Check if using JSON file approach
        if "azure_certificatecreate_jsonfile" in azure_params:
            cmd.extend(["--azure-certificatecreate-jsonfile", azure_params["azure_certificatecreate_jsonfile"]])
            if "azure_tags_jsonfile" in azure_params:
                cmd.extend(["--azure-tags-jsonfile", azure_params["azure_tags_jsonfile"]])
        else:
            # Use individual parameters approach
            required_individual_params = ["certificate_name", "key_vault", "certificate_keyprop_kty", "certificate_x509_subject"]
            for param in required_individual_params:
                if param not in azure_params:
                    raise ValueError(f"Missing required parameter for certificates_create: {param} (or provide azure_certificatecreate_jsonfile)")
                    
            cmd.extend(["--certificate-name", azure_params["certificate_name"]])
            cmd.extend(["--key-vault", azure_params["key_vault"]])
            cmd.extend(["--certificate-keyprop-kty", azure_params["certificate_keyprop_kty"]])
            cmd.extend(["--certificate-x509-subject", azure_params["certificate_x509_subject"]])
            
            # Optional parameters
            if "enabled" in azure_params:
                cmd.extend(["--enabled", str(azure_params["enabled"]).lower()])
            if "exp" in azure_params:
                cmd.extend(["--exp", str(azure_params["exp"])])
            if "nbf" in azure_params:
                cmd.extend(["--nbf", str(azure_params["nbf"])])
            if "azure_tags_jsonfile" in azure_params:
                cmd.extend(["--azure-tags-jsonfile", azure_params["azure_tags_jsonfile"]])
            
    elif base_action == "update":
        cmd.extend(["update", "--id", azure_params["id"]])
        if "enabled" in azure_params:
            cmd.extend(["--enabled", str(azure_params["enabled"]).lower()])
        if "exp" in azure_params:
            cmd.extend(["--exp", str(azure_params["exp"])])
        if "nbf" in azure_params:
            cmd.extend(["--nbf", str(azure_params["nbf"])])
        if "azure_updatecertificate_params" in azure_params:
            cmd.extend(["--azure-updatecertificate-params", azure_params["azure_updatecertificate_params"]])
            
    elif base_action == "import":
        cmd.append("import")
        cmd.extend(["--certificate-name", azure_params["certificate_name"]])
        cmd.extend(["--key-vault", azure_params["key_vault"]])
        cmd.extend(["--pfx-base64", azure_params["pfx_base64"]])
        if "pfx_password" in azure_params:
            cmd.extend(["--pfx-password", azure_params["pfx_password"]])
            
    elif base_action == "restore":
        cmd.extend(["restore", "--backup-data", azure_params["backup_data"]])
        
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
        raise ValueError(f"Unsupported Azure certificates action: {action}")
    
    return cmd 