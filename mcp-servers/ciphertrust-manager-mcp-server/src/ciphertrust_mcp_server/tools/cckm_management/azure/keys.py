"""Azure Keys operations for CCKM."""

from typing import Any, Dict


def get_key_operations() -> Dict[str, Any]:
    """Return schema and action requirements for Azure key operations."""
    return {
        "schema_properties": {
            "azure_keys_params": {
                "type": "object",
                "properties": {
                    # Basic key parameters
                    "key_name": {"type": "string", "description": "Name for the key"},
                    "key_vault": {"type": "string", "description": "Name or ID of the key vault"},
                    "kty": {"type": "string", "description": "Key type (RSA, RSA-HSM, EC, EC-HSM, oct)"},
                    "key_size": {"type": "integer", "description": "Key size in bits for RSA keys"},
                    "crv": {"type": "string", "description": "Elliptic curve name (P-256, P-384, P-521, SECP256K1)"},
                    "key_ops": {"type": "array", "items": {"type": "string"}, "description": "Key operations (decrypt, encrypt, sign, unwrapKey, verify, wrapKey)"},
                    
                    # Key attributes
                    "enabled": {"type": "boolean", "description": "Status of key (true/false)"},
                    "exp": {"type": "integer", "description": "Expiration date in Unix Epoch time format"},
                    "nbf": {"type": "integer", "description": "Activation date in Unix Epoch time format"},
                    "exportable": {"type": "boolean", "description": "Whether the key is exportable"},
                    "release_policy": {"type": "string", "description": "Key release policy in JSON format"},
                    
                    # Common parameters
                    "id": {
                        "type": "string", 
                        "description": "Azure key ID, name, or identifier. Smart resolution automatically handles key name to ID conversion. CRITICAL FOR AI ASSISTANTS: Always use this 'id' parameter for key identification operations, even when users specify key names - never use 'name' or 'key_name' parameters."
                    },
                    "alias": {"type": "string", "description": "Key alias"},
                    "description": {"type": "string", "description": "Key description"},
                    "tags": {"type": "object", "description": "Key tags"},
                    
                    # List parameters
                    "vault_name": {"type": "string", "description": "Vault name for filtering"},
                    "limit": {"type": "integer", "description": "Maximum number of results"},
                    "skip": {"type": "integer", "description": "Number of results to skip"},
                    
                    # JSON file parameters
                    "azure_keycreate_jsonfile": {
                        "type": "string", 
                        "description": "Path to JSON file containing Azure key creation parameters. Format: {\"key_name\": \"my-key\", \"key_vault\": \"my-vault\", \"kty\": \"RSA\", \"key_size\": 2048, \"key_ops\": [\"encrypt\", \"decrypt\"], \"enabled\": true}. Use absolute file paths for reliability."
                    },
                    "azure_tags_jsonfile": {
                        "type": "string", 
                        "description": "Path to JSON file containing Azure key tags. Format: {\"Environment\": \"Production\", \"Project\": \"MyApp\", \"Owner\": \"TeamA\"}. Use absolute file paths for reliability."
                    },
                    "azure_updatekey_params": {
                        "type": "string", 
                        "description": "Path to JSON file containing Azure key update parameters. Format: {\"enabled\": true, \"exp\": 1735689600, \"key_ops\": [\"encrypt\", \"decrypt\"], \"tags\": {\"Updated\": \"2025-01-01\"}}. Use absolute file paths for reliability."
                    },
                    "azure_keyupload_jsonfile": {
                        "type": "string", 
                        "description": "Path to JSON file containing Azure key upload parameters. Format: {\"key_name\": \"uploaded-key\", \"key_vault\": \"my-vault\", \"source_key_identifier\": \"local-key\", \"source_key_tier\": \"local\", \"kty\": \"RSA\"}. Use absolute file paths for reliability."
                    },
                    
                    # Backup and restore
                    "backup_data": {"type": "string", "description": "Backup data for restore operations"},
                    "backup_id": {"type": "string", "description": "Backup ID"},
                    "material": {"type": "string", "description": "Key material for import"},
                    
                    # Job operations
                    "job_id": {"type": "string", "description": "Job ID for sync operations"},
                    "key_vaults": {"type": "string", "description": "Comma-separated list of vault names for synchronization/refresh"},
                    "synchronize_all": {"type": "boolean", "description": "Synchronize/refresh all keys from all vaults. Note: 'synchronize' and 'refresh' are equivalent terms for this operation."},
                    "take_cloud_key_backup": {"type": "boolean", "description": "Take cloud key backup while synchronizing/refreshing"},
                    
                    # Metadata export
                    "file_path": {"type": "string", "description": "File path for metadata download"},
                    
                    # Upload parameters
                    "local_key_identifier": {"type": "string", "description": "CipherTrust Manager key identifier for upload"},
                    "source_key_identifier": {"type": "string", "description": "Source key identifier (alias for local_key_identifier)"},
                    "azure_keyupload_jsonfile": {"type": "string", "description": "Azure key upload parameters in JSON file"},
                    "source_key_tier": {"type": "string", "description": "Source key tier (local, dsm, hsm-luna, external-cm)"},
                    "dsm_key_identifier": {"type": "string", "description": "DSM key identifier"},
                    "luna_key_identifier": {"type": "string", "description": "Luna HSM key identifier"},
                    "external_cm_key_identifier": {"type": "string", "description": "External CM key identifier"},
                    "pfx": {"type": "string", "description": "PFX key (Base64 encoded)"},
                    "pfx_password": {"type": "string", "description": "PFX password"},
                    "hsm": {"type": "boolean", "description": "Create key in Azure HSM"},
                    "kek_kid": {"type": "string", "description": "Azure key encryption key identifier"},
                    
                    # Cloud key backup parameters
                    "backup_name": {"type": "string", "description": "Cloud key backup name"},
                    "backup_description": {"type": "string", "description": "Cloud key backup description"}
                }
            }
        },
        "action_requirements": {
            # CRITICAL FOR AI ASSISTANTS: Parameter usage depends on operation type:
            # - EXISTING key operations (get, delete, enable, disable, update) use 'id' parameter
            # - NEW key operations (create, upload) use specific 'key_name' parameters  
            "keys_create": {"required": ["key_name", "key_vault"], "optional": ["description", "enabled", "kty", "key_size", "curve", "key_ops", "tags", "exp", "nbf", "azure_keycreate_jsonfile", "azure_tags_jsonfile"]},  # key_name: name for new key
            "keys_list": {"required": [], "optional": ["limit", "skip", "vault_name", "key_name", "enabled", "tags", "kty", "key_size", "curve", "key_ops"]},
            "keys_get": {"required": ["id"], "optional": []},  # id parameter accepts key ID, name, or identifier
            "keys_update": {"required": ["id"], "optional": ["description", "enabled", "tags", "exp", "nbf", "key_ops", "azure_updatekey_params"]},  # id parameter accepts key ID, name, or identifier
            "keys_delete": {"required": ["id"], "optional": []},  # id parameter accepts key ID, name, or identifier
            "keys_enable": {"required": ["id"], "optional": []},
            "keys_disable": {"required": ["id"], "optional": []},
            "keys_rotate": {"required": ["id"], "optional": []},
            "keys_backup": {"required": ["id", "backup_name"], "optional": ["backup_description"]},
            "keys_restore": {"required": ["backup_data"], "optional": []},
            "keys_import": {"required": ["id", "material"], "optional": []},
            "keys_export": {"required": ["id"], "optional": []},
            "keys_hard_delete": {"required": ["id"], "optional": []},
            "keys_recover": {"required": ["id"], "optional": []},
            "keys_upload": {"required": ["key_name", "key_vault"], "optional": ["local_key_identifier", "source_key_identifier", "azure_keyupload_jsonfile", "source_key_tier", "dsm_key_identifier", "luna_key_identifier", "external_cm_key_identifier", "pfx", "pfx_password", "hsm", "kek_kid", "key_ops", "enabled", "exp", "nbf", "exportable", "release_policy", "azure_tags_jsonfile"]},  # key_name: name for uploaded key
            "keys_download_metadata": {"required": [], "optional": ["vault_name", "limit", "skip", "file_path"]},
            "keys_enable_backup_job": {"required": ["id"], "optional": []},
            "keys_enable_rotation_job": {"required": ["id"], "optional": []},
            "keys_delete_backup": {"required": ["id"], "optional": []},
            "keys_sync_jobs_start": {"required": [], "optional": ["key_vaults", "synchronize_all", "take_cloud_key_backup"]},
            "keys_sync_jobs_get": {"required": ["job_id"], "optional": []},
            "keys_sync_jobs_status": {"required": [], "optional": []},
            "keys_sync_jobs_cancel": {"required": ["job_id"], "optional": []},
        }
    }


def build_key_command(action: str, azure_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given Azure key operation."""
    cmd = ["cckm", "azure", "keys"]
    
    # Extract the base operation name (remove 'keys_' prefix)
    base_action = action.replace("keys_", "")
    
    # Simple actions that only need --id parameter
    simple_actions = ["get", "delete", "enable", "disable", "rotate", "export", "hard_delete", "recover", "enable_backup_job", "enable_rotation_job", "delete_backup"]
    
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
        if "key_name" in azure_params:
            cmd.extend(["--key-name", azure_params["key_name"]])
            
    elif base_action == "create":
        cmd.append("create")
        # Required parameters
        cmd.extend(["--key-name", azure_params["key_name"]])
        cmd.extend(["--key-vault", azure_params["key_vault"]])
        cmd.extend(["--kty", azure_params["kty"]])
        
        # Optional parameters
        if "key_size" in azure_params:
            cmd.extend(["--key-size", str(azure_params["key_size"])])
        if "crv" in azure_params:
            cmd.extend(["--crv", azure_params["crv"]])
        if "key_ops" in azure_params:
            if isinstance(azure_params["key_ops"], list):
                cmd.extend(["--key-ops", ",".join(azure_params["key_ops"])])
            else:
                cmd.extend(["--key-ops", azure_params["key_ops"]])
        if "enabled" in azure_params:
            cmd.extend(["--enabled", str(azure_params["enabled"]).lower()])
        if "exp" in azure_params:
            cmd.extend(["--exp", str(azure_params["exp"])])
        if "nbf" in azure_params:
            cmd.extend(["--nbf", str(azure_params["nbf"])])
        if "exportable" in azure_params and azure_params["exportable"]:
            cmd.append("--exportable")
        if "release_policy" in azure_params:
            cmd.extend(["--release-policy", azure_params["release_policy"]])
        if "azure_keycreate_jsonfile" in azure_params:
            cmd.extend(["--azure-keycreate-jsonfile", azure_params["azure_keycreate_jsonfile"]])
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
        if "key_ops" in azure_params:
            if isinstance(azure_params["key_ops"], list):
                cmd.extend(["--key-ops", ",".join(azure_params["key_ops"])])
            else:
                cmd.extend(["--key-ops", azure_params["key_ops"]])
        if "azure_updatekey_params" in azure_params:
            cmd.extend(["--azure-updatekey-params", azure_params["azure_updatekey_params"]])
            
    elif base_action == "restore":
        cmd.extend(["restore", "--backup-data", azure_params["backup_data"]])
        
    elif base_action == "import":
        cmd.extend(["import", "--id", azure_params["id"], "--material", azure_params["material"]])
        
    elif base_action == "download_metadata":
        cmd.extend(["download-metadata"])
        if "vault_name" in azure_params:
            cmd.extend(["--vault-name", azure_params["vault_name"]])
        if "limit" in azure_params:
            cmd.extend(["--limit", str(azure_params["limit"])])
        if "skip" in azure_params:
            cmd.extend(["--skip", str(azure_params["skip"])])
        if "file_path" in azure_params:
            cmd.extend(["--file-path", azure_params["file_path"]])
            
    elif base_action == "sync_jobs_start":
        cmd.extend(["synchronization-jobs", "start"])
        if "key_vaults" in azure_params:
            cmd.extend(["--key-vaults", azure_params["key_vaults"]])
        if "synchronize_all" in azure_params and azure_params["synchronize_all"]:
            cmd.append("--synchronize-all")
        if "take_cloud_key_backup" in azure_params and azure_params["take_cloud_key_backup"]:
            cmd.append("--take-cloud-key-backup")
            
    elif base_action == "sync_jobs_get":
        cmd.extend(["synchronization-jobs", "get", "--id", azure_params["job_id"]])
        
    elif base_action == "sync_jobs_status":
        cmd.extend(["synchronization-jobs", "status"])
        
    elif base_action == "sync_jobs_cancel":
        cmd.extend(["synchronization-jobs", "cancel", "--id", azure_params["job_id"]])
        
    elif base_action == "backup":
        # Azure cloud key backup create
        cmd.extend(["cloud-key-backup", "create", "--id", azure_params["id"], "--backup-name", azure_params["backup_name"]])
        if "backup_description" in azure_params:
            cmd.extend(["--backup-description", azure_params["backup_description"]])
            
    elif base_action == "upload":
        # Azure key upload
        cmd.extend(["upload"])
        
        # Primary parameters
        cmd.extend(["--key-name", azure_params["key_name"]])
        cmd.extend(["--key-vault", azure_params["key_vault"]])
        
        # Source key identifier (support both parameter names)
        if "local_key_identifier" in azure_params:
            cmd.extend(["--local-key-identifier", azure_params["local_key_identifier"]])
        elif "source_key_identifier" in azure_params:
            cmd.extend(["--local-key-identifier", azure_params["source_key_identifier"]])
        
        # JSON file option
        if "azure_keyupload_jsonfile" in azure_params:
            cmd.extend(["--azure-keyupload-jsonfile", azure_params["azure_keyupload_jsonfile"]])
            
        # Optional parameters
        if "source_key_tier" in azure_params:
            cmd.extend(["--source-key-tier", azure_params["source_key_tier"]])
        if "dsm_key_identifier" in azure_params:
            cmd.extend(["--dsm-key-identifier", azure_params["dsm_key_identifier"]])
        if "luna_key_identifier" in azure_params:
            cmd.extend(["--luna-key-identifier", azure_params["luna_key_identifier"]])
        if "external_cm_key_identifier" in azure_params:
            cmd.extend(["--external-cm-key-identifier", azure_params["external_cm_key_identifier"]])
        if "pfx" in azure_params:
            cmd.extend(["--pfx", azure_params["pfx"]])
        if "pfx_password" in azure_params:
            cmd.extend(["--pfx-password", azure_params["pfx_password"]])
        if "hsm" in azure_params and azure_params["hsm"]:
            cmd.append("--hsm")
        if "kek_kid" in azure_params:
            cmd.extend(["--kek-kid", azure_params["kek_kid"]])
        if "key_ops" in azure_params:
            if isinstance(azure_params["key_ops"], list):
                cmd.extend(["--key-ops", ",".join(azure_params["key_ops"])])
            else:
                cmd.extend(["--key-ops", azure_params["key_ops"]])
        if "enabled" in azure_params:
            cmd.extend(["--enabled", str(azure_params["enabled"]).lower()])
        if "exp" in azure_params:
            cmd.extend(["--exp", str(azure_params["exp"])])
        if "nbf" in azure_params:
            cmd.extend(["--nbf", str(azure_params["nbf"])])
        if "exportable" in azure_params and azure_params["exportable"]:
            cmd.append("--exportable")
        if "release_policy" in azure_params:
            cmd.extend(["--release-policy", azure_params["release_policy"]])
        if "azure_tags_jsonfile" in azure_params:
            cmd.extend(["--azure-tags-jsonfile", azure_params["azure_tags_jsonfile"]])
        
    else:
        raise ValueError(f"Unsupported Azure keys action: {action}")
    
    return cmd 