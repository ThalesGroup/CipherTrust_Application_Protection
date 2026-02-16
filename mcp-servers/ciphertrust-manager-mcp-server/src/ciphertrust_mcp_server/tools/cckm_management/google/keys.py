"""Google Cloud Keys operations for CCKM."""
from typing import Any, Dict

def validate_key_creation_params(google_params: Dict[str, Any]) -> None:
    """Validate required parameters for key creation operations."""
    required_params = ["key_name", "key_ring", "project_id", "location", "gcp_algorithm", "protection_level", "purpose"]
    missing_params = []
    
    for param in required_params:
        if param not in google_params or google_params[param] is None:
            missing_params.append(param)
    
    if missing_params:
        raise ValueError(f"Missing required parameters for key creation: {', '.join(missing_params)}. "
                        f"Required parameters: {', '.join(required_params)}")
    
    # Validate purpose values
    valid_purposes = ["ENCRYPT_DECRYPT", "ASYMMETRIC_SIGN", "ASYMMETRIC_DECRYPT", "MAC"]
    if google_params.get("purpose") not in valid_purposes:
        raise ValueError(f"Invalid purpose '{google_params.get('purpose')}'. "
                        f"Valid values: {', '.join(valid_purposes)}")
    
    # Validate protection level values
    valid_protection_levels = ["SOFTWARE", "HSM"]
    if google_params.get("protection_level") not in valid_protection_levels:
        raise ValueError(f"Invalid protection_level '{google_params.get('protection_level')}'. "
                        f"Valid values: {', '.join(valid_protection_levels)}")
    
    # Validate algorithm values
    valid_algorithms = [
        "RSA_SIGN_PSS_2048_SHA256", "RSA_SIGN_PSS_3072_SHA256", "RSA_SIGN_PSS_4096_SHA256", 
        "RSA_SIGN_PSS_4096_SHA512", "RSA_SIGN_PKCS1_2048_SHA256", "RSA_SIGN_PKCS1_3072_SHA256", 
        "RSA_SIGN_PKCS1_4096_SHA256", "RSA_SIGN_PKCS1_4096_SHA512", "RSA_DECRYPT_OAEP_2048_SHA256", 
        "RSA_DECRYPT_OAEP_3072_SHA256", "RSA_DECRYPT_OAEP_4096_SHA256", "RSA_DECRYPT_OAEP_4096_SHA512", 
        "EC_SIGN_P256_SHA256", "EC_SIGN_P384_SHA384", "GOOGLE_SYMMETRIC_ENCRYPTION", 
        "EC_SIGN_SECP256K1_SHA256"
    ]
    if google_params.get("gcp_algorithm") not in valid_algorithms:
        raise ValueError(f"Invalid gcp_algorithm '{google_params.get('gcp_algorithm')}'. "
                        f"Valid values: {', '.join(valid_algorithms)}")

def validate_add_version_params(google_params: Dict[str, Any]) -> None:
    """Validate required parameters for add version operations."""
    required_params = ["id"]
    missing_params = []
    
    for param in required_params:
        if param not in google_params or google_params[param] is None:
            missing_params.append(param)
    
    if missing_params:
        raise ValueError(f"Missing required parameters for add version: {', '.join(missing_params)}. "
                        f"Required parameters: {', '.join(required_params)}")
    
    # Validate isNative is boolean if provided
    if "isNative" in google_params and not isinstance(google_params.get("isNative"), bool):
        raise ValueError("isNative parameter must be a boolean value (true/false)")

def validate_scheduler_params(google_params: Dict[str, Any], job_type: str) -> None:
    """Validate parameters for scheduler operations."""
    if job_type == "cckm-synchronization":
        required_params = ["cloud_name", "key_rings"]
        missing_params = []
        
        for param in required_params:
            if param not in google_params or google_params[param] is None:
                missing_params.append(param)
        
        if missing_params:
            raise ValueError(f"Missing required parameters for cckm-synchronization: {', '.join(missing_params)}. "
                            f"Required parameters: {', '.join(required_params)}")
        
        # Validate cloud_name
        valid_clouds = ["aws", "hsm-luna", "dsm", "oci", "sfdc", "gcp", "sap", "AzureCloud"]
        if google_params.get("cloud_name") not in valid_clouds:
            raise ValueError(f"Invalid cloud_name '{google_params.get('cloud_name')}'. "
                            f"Valid values: {', '.join(valid_clouds)}")
    
    elif job_type == "cckm-add-containers":
        required_params = ["cloud_name", "connection_id"]
        missing_params = []
        
        for param in required_params:
            if param not in google_params or google_params[param] is None:
                missing_params.append(param)
        
        if missing_params:
            raise ValueError(f"Missing required parameters for cckm-add-containers: {', '.join(missing_params)}. "
                            f"Required parameters: {', '.join(required_params)}")

def get_key_operations() -> Dict[str, Any]:
    """Return schema and action requirements for Google Cloud key operations."""
    return {
        "schema_properties": {
            "google_keys_params": {
                "type": "object",
                "properties": {
                    # Basic key parameters
                    "key_name": {
                        "type": "string", 
                        "description": "Name of the key to create or manage"
                    },
                    "key_ring": {
                        "type": "string",
                        "description": "Key ring name or ID where the key will be created"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "GCP project ID"
                    },
                    "location": {
                        "type": "string",
                        "description": "GCP location (region) for the key"
                    },
                    "gcp_algorithm": {
                        "type": "string",
                        "description": "Algorithm for the key (e.g., RSA_SIGN_PSS_2048_SHA256)"
                    },
                    "protection_level": {
                        "type": "string",
                        "description": "Protection level: SOFTWARE or HSM"
                    },
                    "purpose": {
                        "type": "string",
                        "description": "Key purpose: ENCRYPT_DECRYPT, ASYMMETRIC_SIGN, ASYMMETRIC_DECRYPT, or MAC"
                    },
                    "id": {
                        "type": "string",
                        "description": "Key ID for operations on existing keys"
                    },
                    "version_id": {
                        "type": "string",
                        "description": "Version ID for version-specific operations"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return"
                    },
                    "skip": {
                        "type": "integer",
                        "description": "Number of results to skip"
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort parameter for results"
                    },
                    "key_ring_id": {
                        "type": "string",
                        "description": "Key ring ID for filtering operations"
                    },
                    "location_id": {
                        "type": "string",
                        "description": "Location ID for filtering operations"
                    },
                    "key_id": {
                        "type": "string",
                        "description": "Key ID for filtering operations"
                    },
                    "name": {
                        "type": "string",
                        "description": "Key name for filtering operations"
                    },
                    "gcp_algorithm": {
                        "type": "string",
                        "description": "Algorithm for the key or filter for list operations"
                    },
                    "protection_level": {
                        "type": "string",
                        "description": "Protection level for the key or filter for list operations"
                    },
                    "purpose": {
                        "type": "string",
                        "description": "Purpose for the key or filter for list operations"
                    },
                    "gcp_key_state": {
                        "type": "string",
                        "description": "GCP key state filter"
                    },
                    "create_status": {
                        "type": "string",
                        "description": "Create status filter"
                    },
                    "job_config_id": {
                        "type": "string",
                        "description": "Job configuration ID filter"
                    },
                    "rotation_job_enabled": {
                        "type": "string",
                        "description": "Rotation job enabled filter"
                    },
                    "organization_name": {
                        "type": "string",
                        "description": "Organization name filter"
                    },
                    "organization_display_name": {
                        "type": "string",
                        "description": "Organization display name filter"
                    },
                    "isNative": {
                        "type": "boolean",
                        "description": "Whether to create key natively or upload"
                    },
                    "source_key_id": {
                        "type": "string",
                        "description": "Source key ID for upload operations"
                    },
                    "source_key_tier": {
                        "type": "string",
                        "description": "Source key tier for upload operations"
                    },
                    "destroy_scheduled_duration": {
                        "type": "string",
                        "description": "Duration before key destruction"
                    },
                    "import_only": {
                        "type": "boolean",
                        "description": "Whether key is import-only"
                    },
                    "next_rotation_time": {
                        "type": "string",
                        "description": "Next rotation time"
                    },
                    "rotation_period": {
                        "type": "string",
                        "description": "Rotation period"
                    },
                    "alias": {
                        "type": "string",
                        "description": "Key alias"
                    },
                    "description": {
                        "type": "string",
                        "description": "Key description"
                    },
                    "enabled": {
                        "type": "boolean",
                        "description": "Whether key is enabled"
                    },
                    "backup_data": {
                        "type": "string",
                        "description": "Backup data for restore operations"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "File path for download operations"
                    },
                    "policy": {
                        "type": "string",
                        "description": "Policy for policy operations"
                    },
                    "version": {
                        "type": "string",
                        "description": "Version for version operations"
                    },
                    "deleted": {
                        "type": "string",
                        "description": "Deleted filter for version operations"
                    },
                    "gone": {
                        "type": "string",
                        "description": "Gone filter for version operations"
                    },
                    "is_primary": {
                        "type": "string",
                        "description": "Primary version filter"
                    },
                    "key_material_origin": {
                        "type": "string",
                        "description": "Key material origin filter"
                    },
                    # JSON file parameters
                    "gcp_keycreate_jsonfile": {
                        "type": "string",
                        "description": "JSON file containing key creation parameters"
                    },
                    "gcp_keyupload_jsonfile": {
                        "type": "string",
                        "description": "JSON file containing key upload parameters"
                    },
                    "gcp_keyaddversion_jsonfile": {
                        "type": "string",
                        "description": "JSON file containing add version parameters"
                    },
                    "gcp_key_params_jsonfile": {
                        "type": "string",
                        "description": "JSON file containing key parameters"
                    },
                    "gcp_keyenable_rotation_job_jsonfile": {
                        "type": "string",
                        "description": "JSON file containing rotation job parameters"
                    },
                    # Synchronization job parameters
                    "key_rings": {
                        "type": "string",
                        "description": "Comma-separated list of key rings for sync operations"
                    },
                    "synchronize_all": {
                        "type": "boolean",
                        "description": "Whether to synchronize all key rings"
                    },
                    "job_id": {
                        "type": "string",
                        "description": "Job ID for sync operations"
                    },
                    "overall_status": {
                        "type": "string",
                        "description": "Overall status filter for sync operations"
                    },
                    "auto_rotate_key_source": {
                        "type": "string",
                        "description": "Auto rotate key source"
                    },
                    "auto_rotate_algorithm": {
                        "type": "string",
                        "description": "Auto rotate algorithm"
                    }
                }
            }
        },
        "action_requirements": {
            # Key creation and management
            "keys_create": {
                "required": ["key_name", "key_ring", "project_id", "location", "gcp_algorithm", "protection_level", "purpose"],
                "optional": ["destroy_scheduled_duration", "import_only", "next_rotation_time", "rotation_period", "gcp_keycreate_jsonfile", "gcp_key_params_jsonfile"]
            },
            "keys_upload": {
                "required": ["key_name", "key_ring", "project_id", "location", "gcp_algorithm", "protection_level", "purpose"],
                "optional": ["source_key_id", "source_key_tier", "destroy_scheduled_duration", "import_only", "next_rotation_time", "rotation_period", "gcp_keyupload_jsonfile", "gcp_key_params_jsonfile"]
            },
            "keys_get": {
                "required": ["id"],
                "optional": []
            },
            "keys_list": {
                "required": [],
                "optional": ["project_id", "location_id", "key_ring_id", "key_id", "name", "gcp_algorithm", "protection_level", "purpose", "gcp_key_state", "create_status", "job_config_id", "rotation_job_enabled", "organization_name", "organization_display_name", "limit", "skip", "sort"]
            },
            "keys_update": {
                "required": ["id"],
                "optional": ["alias", "description", "enabled", "next_rotation_time", "rotation_period"]
            },
            "keys_refresh": {
                "required": ["id"],
                "optional": []
            },
            "keys_download_metadata": {
                "required": [],
                "optional": ["project_id", "location", "key_ring", "limit", "skip", "file_path"]
            },
            "keys_download_public_key": {
                "required": ["id", "version_id"],
                "optional": []
            },
            "keys_get_update_all_versions_status": {
                "required": ["id"],
                "optional": []
            },
            "keys_re_import": {
                "required": ["id", "version_id"],
                "optional": []
            },
            "keys_restore": {
                "required": ["backup_data"],
                "optional": []
            },
            
            # Version management
            "keys_add_version": {
                "required": ["id"],
                "optional": ["isNative", "gcp_algorithm", "source_key_id", "source_key_tier", "gcp_keyaddversion_jsonfile"]
            },
            "keys_list_version": {
                "required": ["id"],
                "optional": ["limit", "skip", "version", "version_id", "name", "gcp_algorithm", "gcp_key_state", "deleted", "gone", "is_primary", "key_material_origin"]
            },
            "keys_get_version": {
                "required": ["id", "version_id"],
                "optional": []
            },
            "keys_enable_version": {
                "required": ["id", "version_id"],
                "optional": []
            },
            "keys_disable_version": {
                "required": ["id", "version_id"],
                "optional": []
            },
            "keys_refresh_version": {
                "required": ["id", "version_id"],
                "optional": []
            },
            "keys_synchronize_version": {
                "required": ["id", "version_id"],
                "optional": []
            },
            
            # Key lifecycle operations
            "keys_enable": {
                "required": ["id"],
                "optional": []
            },
            "keys_disable": {
                "required": ["id"],
                "optional": []
            },
            "keys_rotate": {
                "required": ["id"],
                "optional": ["isNative"]
            },
            "keys_enable_auto_rotation": {
                "required": ["id"],
                "optional": ["next_rotation_time", "rotation_period", "isNative", "auto_rotate_key_source", "auto_rotate_algorithm", "gcp_keyenable_rotation_job_jsonfile"]
            },
            "keys_disable_auto_rotation": {
                "required": ["id"],
                "optional": []
            },
            "keys_update_all_versions_jobs": {
                "required": ["id"],
                "optional": []
            },
            
            # Destruction operations (GCP only supports version destruction, not key deletion)
            "keys_schedule_destroy": {
                "required": ["id", "version_id"],
                "optional": ["destroy_scheduled_duration"]
            },
            "keys_cancel_schedule_destroy": {
                "required": ["id", "version_id"],
                "optional": []
            },
            
            # Policy operations
            "keys_policy": {
                "required": ["id"],
                "optional": ["policy"]
            },
            "keys_policy_get": {
                "required": ["id"],
                "optional": []
            },
            "keys_policy_update": {
                "required": ["id"],
                "optional": ["policy"]
            },
            "keys_policy_get_iam_roles": {
                "required": [],
                "optional": []
            },
            
            # Synchronization operations
            "keys_synchronize": {
                "required": ["id"],
                "optional": []
            },
            "keys_sync_jobs_start": {
                "required": ["key_rings"],
                "optional": ["synchronize_all"]
            },
            "keys_sync_jobs_get": {
                "required": ["job_id"],
                "optional": []
            },
            "keys_sync_jobs_cancel": {
                "required": ["job_id"],
                "optional": []
            },
            "keys_sync_jobs_status": {
                "required": [],
                "optional": ["limit", "skip", "key_rings", "overall_status", "id"]
            }
        }
    }

def validate_required_params(action: str, google_params: Dict[str, Any], action_requirements: Dict[str, Any]) -> None:
    """
    Validate that all required parameters are present for the given action.
    This prevents AI assistants from guessing parameters.
    
    Args:
        action: The operation being performed (e.g., 'keys_get', 'keys_create')
        google_params: The parameters provided by the user
        action_requirements: The requirements dictionary from get_key_operations()
    
    Raises:
        ValueError: If any required parameters are missing or None
    """
    if action not in action_requirements:
        raise ValueError(f"Unknown action: {action}")
    
    required_params = action_requirements[action].get("required", [])
    if not required_params:
        return  # No required parameters for this action
    
    missing_params = []
    for param in required_params:
        if param not in google_params or google_params[param] is None or google_params[param] == "":
            missing_params.append(param)
    
    if missing_params:
        optional_params = action_requirements[action].get("optional", [])
        raise ValueError(
            f"Missing required parameters for '{action}': {', '.join(missing_params)}. "
            f"Required parameters: {', '.join(required_params)}. "
            f"Optional parameters: {', '.join(optional_params) if optional_params else 'None'}. "
            f"Please provide all required parameters - no parameter guessing is allowed."
        )

def build_key_command(action: str, google_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given Google Cloud key operation."""
    cmd = ["cckm", "google", "keys"]
    
    # Get action requirements for validation
    operations_schema = get_key_operations()
    action_requirements = operations_schema['action_requirements']
    
    # MANDATORY: Validate ALL required parameters - prevents AI parameter guessing
    validate_required_params(action, google_params, action_requirements)
    
    # Extract the base operation name (remove 'keys_' prefix)
    base_action = action.replace("keys_", "")
    
    # Additional specific validations for complex operations
    if base_action == "create":
        try:
            validate_key_creation_params(google_params)
        except ValueError as e:
            raise ValueError(f"Key creation validation failed: {str(e)}")
    
    # Validate parameters for add version operations
    if base_action == "add_version":
        try:
            validate_add_version_params(google_params)
        except ValueError as e:
            raise ValueError(f"Add version validation failed: {str(e)}")
    
    # Handle synchronization jobs separately
    if base_action.startswith("sync_jobs_"):
        sync_action = base_action.replace("sync_jobs_", "")
        cmd.extend(["synchronization-jobs", sync_action])
        
        if sync_action == "start":
            if "key_rings" in google_params:
                cmd.extend(["--key-rings", google_params["key_rings"]])
            if "synchronize_all" in google_params and google_params["synchronize_all"]:
                cmd.append("--synchronize-all")
            # Note: project_id is not needed for sync jobs as it's included in the key_rings resource names
        elif sync_action in ["get", "cancel"]:
            cmd.extend(["--id", google_params["job_id"]])
        elif sync_action == "status":
            if "limit" in google_params:
                cmd.extend(["--limit", str(google_params["limit"])])
            if "skip" in google_params:
                cmd.extend(["--skip", str(google_params["skip"])])
            if "sort" in google_params:
                cmd.extend(["--sort", google_params["sort"]])
            if "key_rings" in google_params:
                cmd.extend(["--key-rings", google_params["key_rings"]])
            if "overall_status" in google_params:
                cmd.extend(["--overall-status", google_params["overall_status"]])
            if "id" in google_params:
                cmd.extend(["--id", google_params["id"]])
            # Note: project_id is not needed for sync status as it's included in the key_rings resource names
        
        return cmd
    
    # Handle policy operations separately
    if base_action.startswith("policy"):
        cmd.append("policy")
        if base_action == "policy":
            cmd.extend(["get", "--id", google_params["id"]])
        elif base_action == "policy_get":
            cmd.extend(["get", "--id", google_params["id"]])
        elif base_action == "policy_update":
            cmd.extend(["update", "--id", google_params["id"]])
            if "policy" in google_params:
                cmd.extend(["--policy", google_params["policy"]])
        elif base_action == "policy_get_iam_roles":
            cmd.extend(["get-iam-roles"])
        
        return cmd
    
    # Simple actions that only need --id parameter
    simple_actions = [
        "get", "enable", "disable", "rotate", "destroy", 
        "cancel_schedule_destroy", "disable_auto_rotation",
        "download_public_key", "get_update_all_versions_status", "re_import", 
        "refresh", "synchronize", "update_all_versions_jobs"
    ]
    
    if base_action in simple_actions:
        cmd.append(base_action.replace("_", "-"))
        cmd.extend(["--id", google_params["id"]])
        
        # Add version_id for operations that need it
        if base_action in ["disable_version", "enable_version", "get_version", "refresh_version", "synchronize_version"] and "version_id" in google_params:
            cmd.extend(["--version-id", google_params["version_id"]])
        
        # Add is-native parameter for operations that support it
        if base_action in ["rotate"] and "isNative" in google_params:
            cmd.extend(["--is-native", str(google_params["isNative"]).lower()])
        
        return cmd
    
    # Handle get_version separately since it needs both id and version_id
    if base_action == "get_version":
        cmd.extend(["get-version", "--id", google_params["id"], "--version-id", google_params["version_id"]])
        return cmd
    
    # Handle specific operations
    if base_action == "list":
        cmd.append("list")
        if "project_id" in google_params:
            cmd.extend(["--project-id", google_params["project_id"]])
        if "location_id" in google_params:
            cmd.extend(["--location-id", google_params["location_id"]])
        if "key_ring_id" in google_params:
            cmd.extend(["--key-ring-id", google_params["key_ring_id"]])
        if "key_id" in google_params:
            cmd.extend(["--key-id", google_params["key_id"]])
        if "name" in google_params:
            cmd.extend(["--name", google_params["name"]])
        if "gcp_algorithm" in google_params:
            cmd.extend(["--gcp-algorithm", google_params["gcp_algorithm"]])
        if "protection_level" in google_params:
            cmd.extend(["--protection-level", google_params["protection_level"]])
        if "purpose" in google_params:
            cmd.extend(["--purpose", google_params["purpose"]])
        if "gcp_key_state" in google_params:
            cmd.extend(["--gcp-key-state", google_params["gcp_key_state"]])
        if "create_status" in google_params:
            cmd.extend(["--create-status", google_params["create_status"]])
        if "job_config_id" in google_params:
            cmd.extend(["--job-config-id", google_params["job_config_id"]])
        if "rotation_job_enabled" in google_params:
            cmd.extend(["--rotation-job-enabled", google_params["rotation_job_enabled"]])
        if "organization_name" in google_params:
            cmd.extend(["--organization-name", google_params["organization_name"]])
        if "organization_display_name" in google_params:
            cmd.extend(["--organization-display-name", google_params["organization_display_name"]])
        if "limit" in google_params:
            cmd.extend(["--limit", str(google_params["limit"])])
        if "skip" in google_params:
            cmd.extend(["--skip", str(google_params["skip"])])
        if "sort" in google_params:
            cmd.extend(["--sort", google_params["sort"]])
            
    elif base_action == "create":
        cmd.append("create")
        
        # Handle JSON file parameter first (overrides individual parameters)
        if "gcp_keycreate_jsonfile" in google_params:
            cmd.extend(["--gcp-keycreate-jsonfile", google_params["gcp_keycreate_jsonfile"]])
        else:
            # Individual parameters
            if "key_name" in google_params:
                cmd.extend(["--key-name", google_params["key_name"]])
            if "key_ring" in google_params:
                cmd.extend(["--key-ring", google_params["key_ring"]])
            if "gcp_algorithm" in google_params:
                cmd.extend(["--gcp-algorithm", google_params["gcp_algorithm"]])
            if "protection_level" in google_params:
                cmd.extend(["--protection-level", google_params["protection_level"]])
            if "purpose" in google_params:
                cmd.extend(["--purpose", google_params["purpose"]])
            if "destroy_scheduled_duration" in google_params:
                cmd.extend(["--destroy-scheduled-duration", google_params["destroy_scheduled_duration"]])
            if "import_only" in google_params and google_params["import_only"]:
                cmd.append("--import-only")
            if "next_rotation_time" in google_params:
                cmd.extend(["--next-rotation-time", google_params["next_rotation_time"]])
            if "rotation_period" in google_params:
                cmd.extend(["--rotation-period", google_params["rotation_period"]])
            if "gcp_key_params_jsonfile" in google_params:
                cmd.extend(["--gcp-key-params-jsonfile", google_params["gcp_key_params_jsonfile"]])
                
    elif base_action == "upload":
        cmd.append("upload-key")
        
        # Handle JSON file parameter first (overrides individual parameters)
        if "gcp_keyupload_jsonfile" in google_params:
            cmd.extend(["--gcp-keyupload-jsonfile", google_params["gcp_keyupload_jsonfile"]])
        else:
            # Individual parameters
            if "key_name" in google_params:
                cmd.extend(["--key-name", google_params["key_name"]])
            if "key_ring" in google_params:
                cmd.extend(["--key-ring", google_params["key_ring"]])
            if "gcp_algorithm" in google_params:
                cmd.extend(["--gcp-algorithm", google_params["gcp_algorithm"]])
            if "protection_level" in google_params:
                cmd.extend(["--protection-level", google_params["protection_level"]])
            if "purpose" in google_params:
                cmd.extend(["--purpose", google_params["purpose"]])
            if "source_key_id" in google_params:
                cmd.extend(["--source-key-id", google_params["source_key_id"]])
            if "source_key_tier" in google_params:
                cmd.extend(["--source-key-tier", google_params["source_key_tier"]])
            if "destroy_scheduled_duration" in google_params:
                cmd.extend(["--destroy-scheduled-duration", google_params["destroy_scheduled_duration"]])
            if "import_only" in google_params and google_params["import_only"]:
                cmd.append("--import-only")
            if "next_rotation_time" in google_params:
                cmd.extend(["--next-rotation-time", google_params["next_rotation_time"]])
            if "rotation_period" in google_params:
                cmd.extend(["--rotation-period", google_params["rotation_period"]])
            if "gcp_key_params_jsonfile" in google_params:
                cmd.extend(["--gcp-key-params-jsonfile", google_params["gcp_key_params_jsonfile"]])
                
    elif base_action == "update":
        cmd.extend(["update", "--id", google_params["id"]])
        if "alias" in google_params:
            cmd.extend(["--alias", google_params["alias"]])
        if "description" in google_params:
            cmd.extend(["--description", google_params["description"]])
        if "enabled" in google_params:
            cmd.extend(["--enabled", str(google_params["enabled"]).lower()])
        if "next_rotation_time" in google_params:
            cmd.extend(["--next-rotation-time", google_params["next_rotation_time"]])
        if "rotation_period" in google_params:
            cmd.extend(["--rotation-period", google_params["rotation_period"]])
            
    elif base_action == "restore":
        cmd.extend(["restore", "--backup-data", google_params["backup_data"]])
        
    elif base_action == "enable_auto_rotation":
        cmd.extend(["enable-auto-rotation", "--id", google_params["id"]])
        if "next_rotation_time" in google_params:
            cmd.extend(["--next-rotation-time", google_params["next_rotation_time"]])
        if "rotation_period" in google_params:
            cmd.extend(["--rotation-period", google_params["rotation_period"]])
        if "isNative" in google_params:
            cmd.extend(["--is-native", str(google_params["isNative"]).lower()])
        if "auto_rotate_key_source" in google_params:
            cmd.extend(["--auto-rotate-key-source", google_params["auto_rotate_key_source"]])
        if "auto_rotate_algorithm" in google_params:
            cmd.extend(["--auto-rotate-algorithm", google_params["auto_rotate_algorithm"]])
        if "gcp_keyenable_rotation_job_jsonfile" in google_params:
            cmd.extend(["--gcp-keyenable-rotation-job-jsonfile", google_params["gcp_keyenable_rotation_job_jsonfile"]])
            
    elif base_action == "schedule_destroy":
        # Note: This function builds command for a SINGLE version. 
        # When no version_id is provided, google_operations.py will handle 
        # getting all versions and calling this function multiple times.
        cmd.extend(["schedule-destroy", "--id", google_params["id"]])
        
        # version_id is required for schedule-destroy command
        if "version_id" in google_params:
            cmd.extend(["--version-id", google_params["version_id"]])
        else:
            # This should not happen if google_operations.py handles it correctly
            raise ValueError("version_id is required for schedule-destroy operation")
            
        if "destroy_scheduled_duration" in google_params:
            cmd.extend(["--destroy-scheduled-duration", google_params["destroy_scheduled_duration"]])
            
    elif base_action == "download_metadata":
        cmd.append("download-metadata")
        if "project_id" in google_params:
            cmd.extend(["--project-id", google_params["project_id"]])
        if "location" in google_params:
            cmd.extend(["--location", google_params["location"]])
        if "key_ring" in google_params:
            cmd.extend(["--key-ring", google_params["key_ring"]])
        if "limit" in google_params:
            cmd.extend(["--limit", str(google_params["limit"])])
        if "skip" in google_params:
            cmd.extend(["--skip", str(google_params["skip"])])
        if "file_path" in google_params:
            cmd.extend(["--file-path", google_params["file_path"]])
            
    elif base_action == "add_version":
        cmd.extend(["add-version", "--id", google_params["id"]])
        if "isNative" in google_params:
            cmd.extend(["--is-native", str(google_params["isNative"]).lower()])
        if "gcp_algorithm" in google_params:
            cmd.extend(["--gcp-algorithm", google_params["gcp_algorithm"]])
        if "source_key_id" in google_params:
            cmd.extend(["--source-key-id", google_params["source_key_id"]])
        if "source_key_tier" in google_params:
            cmd.extend(["--source-key-tier", google_params["source_key_tier"]])
        if "gcp_keyaddversion_jsonfile" in google_params:
            cmd.extend(["--gcp-keyaddversion-jsonfile", google_params["gcp_keyaddversion_jsonfile"]])
            
    elif base_action == "list_version":
        cmd.extend(["list-version", "--id", google_params["id"]])
        if "limit" in google_params:
            cmd.extend(["--limit", str(google_params["limit"])])
        if "skip" in google_params:
            cmd.extend(["--skip", str(google_params["skip"])])
        if "version" in google_params:
            cmd.extend(["--version", google_params["version"]])
        if "version_id" in google_params:
            cmd.extend(["--version-id", google_params["version_id"]])
        if "name" in google_params:
            cmd.extend(["--name", google_params["name"]])
        if "gcp_algorithm" in google_params:
            cmd.extend(["--gcp-algorithm", google_params["gcp_algorithm"]])
        if "gcp_key_state" in google_params:
            cmd.extend(["--gcp-key-state", google_params["gcp_key_state"]])
        if "deleted" in google_params:
            cmd.extend(["--deleted", google_params["deleted"]])
        if "gone" in google_params:
            cmd.extend(["--gone", google_params["gone"]])
        if "is_primary" in google_params:
            cmd.extend(["--is-primary", google_params["is_primary"]])
        if "key_material_origin" in google_params:
            cmd.extend(["--key-material-origin", google_params["key_material_origin"]])
            
    else:
        raise ValueError(f"Unsupported Google Cloud keys action: {action}")
    
    return cmd 