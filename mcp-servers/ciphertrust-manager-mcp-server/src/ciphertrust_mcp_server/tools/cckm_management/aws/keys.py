"""AWS Keys operations for CCKM."""
from typing import Any, Dict

def get_key_operations() -> Dict[str, Any]:
    """Return schema and action requirements for AWS key operations."""
    return {
        "schema_properties": {
            "aws_keys_params": {
                "type": "object",
                "properties": {
                    "customer_masterkey_spec": {"type": "string"},
                    "kms": {"type": "string"},
                    "external_accounts": {"type": "string"},
                    "key_admins": {"type": "string"},
                    "key_users": {"type": "string"},
                    "key_admins_roles": {"type": "string"},
                    "key_users_roles": {"type": "string"},
                    "multiregion": {"type": "boolean"},
                    "policy_template": {"type": "string"},
                    "aws_tags_jsonfile": {
                        "type": "string", 
                        "description": "Path to JSON file containing AWS key tags. Format: [{\"Key\": \"Environment\", \"Value\": \"Production\"}, {\"Key\": \"Project\", \"Value\": \"MyApp\"}]. Use absolute file paths for reliability."
                    },
                    "aws_policy_jsonfile": {
                        "type": "string", 
                        "description": "Path to JSON file containing AWS key policy. Format: {\"Version\": \"2012-10-17\", \"Statement\": [{\"Sid\": \"Enable IAM User Permissions\", \"Effect\": \"Allow\", \"Principal\": {\"AWS\": \"arn:aws:iam::123456789012:root\"}, \"Action\": \"kms:*\", \"Resource\": \"*\"}]}. Use absolute file paths for reliability."
                    },
                    "aws_keycreate_jsonfile": {
                        "type": "string", 
                        "description": "Path to JSON file containing complete AWS key creation parameters. This file overrides individual CLI parameters. Format: {\"alias\": \"my-key\", \"region\": \"us-east-1\", \"kms\": \"my-kms\", \"customer_masterkey_spec\": \"SYMMETRIC_DEFAULT\", \"key_usage\": \"ENCRYPT_DECRYPT\"}. Use absolute file paths for reliability."
                    },
                    "aws_create_key_kms_params_jsonfile": {
                        "type": "string", 
                        "description": "Path to JSON file containing AWS KMS-specific parameters for key creation. Use absolute file paths for reliability."
                    },
                    "aws_importmaterial_jsonfile": {
                        "type": "string", 
                        "description": "Path to JSON file containing AWS key material import parameters. Format includes wrapping key specifications and material. Use absolute file paths for reliability."
                    },
                    "aws_uploadkey_jsonfile": {
                        "type": "string", 
                        "description": "Path to JSON file containing AWS key upload parameters. Format: {\"source_key_identifier\": \"local-key-name\", \"alias\": \"uploaded-key\", \"region\": \"us-east-1\", \"kms\": \"my-kms\"}. Use absolute file paths for reliability."
                    },
                    "aws_key_upload_kms_params_jsonfile": {
                        "type": "string", 
                        "description": "Path to JSON file containing AWS KMS-specific upload parameters. Use absolute file paths for reliability."
                    },
                    
                    # Basic key parameters
                    "days": {
                        "type": "integer", 
                        "description": "Number of days for key deletion schedule (7-30 days)"
                    },
                    "material": {
                        "type": "string", 
                        "description": "Key material for import operations"
                    },
                    "description": {
                        "type": "string", 
                        "description": "Human-readable description of the key"
                    },
                    "enabled": {
                        "type": "boolean", 
                        "description": "Whether the key is enabled for cryptographic operations"
                    },
                    "tags": {
                        "type": "string", 
                        "description": "Key tags in comma-separated format"
                    },
                    "key_usage": {
                        "type": "string", 
                        "description": "Key usage type: ENCRYPT_DECRYPT or SIGN_VERIFY"
                    },
                    "origin": {
                        "type": "string", 
                        "description": "Key origin: AWS_KMS, EXTERNAL, or AWS_CLOUDHSM"
                    },
                    "bypass_policy_lockout_safety_check": {
                        "type": "boolean", 
                        "description": "Bypass policy lockout safety check when updating key policy"
                    },
                    "alias": {
                        "type": "string", 
                        "description": "Key alias name (must start with 'alias/')"
                    },
                    "region": {
                        "type": "string", 
                        "description": "AWS region for key operations (e.g., us-east-1, eu-west-1)"
                    },
                    "id": {
                        "type": "string", 
                        "description": "AWS key ID, ARN, or alias. Smart resolution automatically converts aliases/ARNs to UUIDs. CRITICAL FOR AI ASSISTANTS: Always use this 'id' parameter for key identification operations, even when users specify key names, aliases, or ARNs - never use 'name' or 'alias' parameters."
                    },
                    "limit": {
                        "type": "integer", 
                        "description": "Maximum number of results to return (default: 10)"
                    },
                    "skip": {
                        "type": "integer", 
                        "description": "Number of results to skip for pagination (default: 0)"
                    },
                    "key_state": {
                        "type": "string", 
                        "description": "Filter by key state: Enabled, Disabled, PendingDeletion, etc."
                    },
                    "sort": {
                        "type": "string", 
                        "description": "Sort parameter for ordering results"
                    },
                    "policy_template_name": {
                        "type": "string", 
                        "description": "Name of the policy template"
                    },
                    "aws_policycreate_jsonfile": {
                        "type": "string", 
                        "description": "Path to JSON file containing policy template creation parameters. Use absolute file paths for reliability."
                    },
                    "aws_policyupdate_jsonfile": {
                        "type": "string", 
                        "description": "Path to JSON file containing policy template update parameters. Use absolute file paths for reliability."
                    },
                    "custom_key_store_id": {
                        "type": "string", 
                        "description": "Custom key store ID for CloudHSM or external key stores"
                    },
                    "source_key_tier": {
                        "type": "string", 
                        "description": "Source key tier: local, dsm, hsm-luna, external-cm"
                    },
                    "sourceKey_identifier": {
                        "type": "string", 
                        "description": "Source key identifier (legacy parameter name)"
                    },
                    "source_key_identifier": {
                        "type": "string", 
                        "description": "Source key identifier for upload/import operations"
                    },
                    "blocked": {
                        "type": "string", 
                        "description": "Key blocked status filter"
                    },
                    "linked_state": {
                        "type": "string", 
                        "description": "Key linked state filter"
                    },
                    "arn": {
                        "type": "string", 
                        "description": "AWS key ARN for filtering (format: arn:aws:kms:region:account:key/key-id)"
                    },
                    "key_expiration": {
                        "type": "boolean", 
                        "description": "Enable key expiration for imported key material"
                    },
                    "valid_to": {
                        "type": "string", 
                        "description": "Key expiration time in ISO format (e.g., 2021-04-01T01:00:15Z). Required when key_expiration is true."
                    },
                    "kms_list": {"type": "string", "description": "Name or ID of KMS resources for synchronization/refresh (comma-separated)"},
                    "regions": {"type": "string", "description": "List of AWS regions for synchronization/refresh (comma-separated)"},
                    "synchronize_all": {"type": "boolean", "description": "Synchronize/refresh all keys from all KMS and regions. Note: 'synchronize' and 'refresh' are equivalent terms for this operation."}
                }
            }
        },
        "action_requirements": {
            # CRITICAL FOR AI ASSISTANTS: Parameter usage depends on operation type:
            # - EXISTING key operations (get, delete, enable, disable, update) use 'id' parameter
            # - NEW key operations (create, upload) use specific 'alias' or 'key_name' parameters  
            # - Alias management uses both 'id' (existing key) and 'alias' (alias to manage)
            "keys_create": {"required": ["alias", "region", "kms"], "optional": ["customer_masterkey_spec", "description", "enabled", "tags", "key_usage", "origin", "external_accounts", "key_admins", "key_users", "key_admins_roles", "key_users_roles", "multiregion", "policy_template", "bypass_policy_lockout_safety_check", "aws_tags_jsonfile", "aws_policy_jsonfile", "aws_keycreate_jsonfile", "aws_create_key_kms_params_jsonfile"]},  # alias: name for new key
            "keys_list": {"required": [], "optional": ["alias", "enabled", "limit", "skip", "key_state", "origin", "sort", "region", "kms", "customer_masterkey_spec", "tags", "cloud_name", "gone", "id", "job_config_id", "key_material_origin", "keyid", "kms_id", "multi_region", "multi_region_key_type", "rotation_job_enabled"]},
            "keys_delete": {"required": ["id"], "optional": []},  # id parameter accepts key ID, ARN, or alias
            "keys_schedule_deletion": {"required": ["id", "days"], "optional": []},  # id parameter accepts key ID, ARN, or alias
            "keys_add_tags": {"required": ["id", "aws_tags_jsonfile"], "optional": []},  # id parameter accepts key ID, ARN, or alias
            "keys_policy": {"required": ["id", "aws_policy_jsonfile"], "optional": []},  # id parameter accepts key ID, ARN, or alias
            "keys_import_material": {"required": ["id", "source_key_identifier"], "optional": ["source_key_tier", "key_expiration", "valid_to", "aws_importmaterial_jsonfile"]},
            "keys_enable": {"required": ["id"], "optional": []},  # id parameter accepts key ID, ARN, or alias
            "keys_disable": {"required": ["id"], "optional": []},  # id parameter accepts key ID, ARN, or alias
            "keys_add_alias": {"required": ["id", "alias"], "optional": []},
            "keys_delete_alias": {"required": ["id", "alias"], "optional": []},
            "keys_update_description": {"required": ["id", "description"], "optional": []},
            "keys_get": {"required": ["id"], "optional": []},  # id parameter accepts key ID, ARN, or alias
            "keys_cancel_deletion": {"required": ["id"], "optional": []},
            "keys_delete_material": {"required": ["id"], "optional": []},
            "keys_upload": {"required": ["source_key_identifier", "region", "kms"], "optional": ["alias", "description", "customer_masterkey_spec", "key_usage", "key_expiration", "valid_to", "source_key_tier", "external_accounts", "key_admins", "key_users", "key_admins_roles", "key_users_roles", "multiregion", "policy_template", "bypass_policy_lockout_safety_check", "aws_tags_jsonfile", "aws_policy_jsonfile", "aws_uploadkey_jsonfile", "aws_key_upload_kms_params_jsonfile"]},  # alias: optional name for uploaded key
            "keys_download_public_key": {"required": ["id"], "optional": []},
            "keys_block": {"required": ["id"], "optional": []},
            "keys_unblock": {"required": ["id"], "optional": []},
            "keys_enable_auto_rotation": {"required": ["id"], "optional": []},
            "keys_disable_auto_rotation": {"required": ["id"], "optional": []},
            "keys_enable_rotation_job": {"required": ["id"], "optional": []},
            "keys_disable_rotation_job": {"required": ["id"], "optional": []},
            "keys_list_rotations": {"required": ["id"], "optional": []},
            "keys_link": {"required": ["id"], "optional": []},
            "keys_rotate_material": {"required": ["id"], "optional": []},
            "keys_sync_jobs_start": {"required": [], "optional": ["kms_list", "regions", "synchronize_all", "limit", "skip", "sort", "cloud_name", "gone", "id", "job_config_id", "key_material_origin", "keyid", "kms_id", "multi_region", "multi_region_key_type", "rotation_job_enabled"]},
            "keys_sync_jobs_get": {"required": ["id"], "optional": []},
            "keys_sync_jobs_status": {"required": [], "optional": ["limit", "skip", "sort", "cloud_name", "gone", "id", "job_config_id", "key_material_origin", "keyid", "kms_id", "multi_region", "multi_region_key_type", "rotation_job_enabled"]},
            "keys_sync_jobs_cancel": {"required": ["id"], "optional": []},
            "keys_policy_template_create": {"required": ["policy_template_name"], "optional": ["aws_policycreate_jsonfile"]},
            "keys_policy_template_delete": {"required": ["id"], "optional": []},
            "keys_policy_template_get": {"required": ["id"], "optional": []},
            "keys_policy_template_list": {"required": [], "optional": ["limit", "skip", "sort"]},
            "keys_policy_template_update": {"required": ["id"], "optional": ["aws_policyupdate_jsonfile"]},
            "keys_create_aws_cloudhsm": {"required": ["alias", "custom_key_store_id"], "optional": ["description", "external_accounts", "key_admins", "key_users", "key_admins_roles", "key_users_roles", "policy_template", "source_key_tier", "sourceKey_identifier", "blocked", "linked_state", "aws_policy_jsonfile"]},
            "keys_create_aws_hyok": {"required": ["alias", "custom_key_store_id"], "optional": ["description", "external_accounts", "key_admins", "key_users", "key_admins_roles", "key_users_roles", "policy_template", "source_key_tier", "sourceKey_identifier", "blocked", "linked_state", "aws_policy_jsonfile"]},
        }
    }

def build_key_command(action: str, aws_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given AWS key operation."""
    cmd = ["cckm", "aws", "keys"]
    
    # Extract the base operation name (remove 'keys_' prefix)
    base_action = action.replace("keys_", "")
    
    # Simple actions that only need --id parameter
    simple_actions = ["enable", "disable", "delete", "cancel_deletion", "delete_material", "download_public_key", "block", "unblock", "enable_auto_rotation", "disable_auto_rotation", "enable_rotation_job", "disable_rotation_job", "list_rotations", "link", "rotate_material", "get", "sync_jobs_get", "sync_jobs_cancel", "policy_template_delete", "policy_template_get"]
    
    if base_action in simple_actions:
        cmd.extend([base_action.replace("_", "-"), "--id", aws_params["id"]])
        return cmd

    if base_action == "create":
        cmd.append("create")
        # Required parameters
        cmd.extend(["--alias", aws_params["alias"]])
        cmd.extend(["--region", aws_params["region"]])
        cmd.extend(["--kms", aws_params["kms"]])
        
        # Optional parameters
        if "customer_masterkey_spec" in aws_params:
            cmd.extend(["--customer-masterkey-spec", aws_params["customer_masterkey_spec"]])
        if "description" in aws_params:
            cmd.extend(["--description", aws_params["description"]])
        if "enabled" in aws_params:
            cmd.extend(["--enabled", str(aws_params["enabled"]).lower()])
        if "tags" in aws_params:
            cmd.extend(["--tags", aws_params["tags"]])
        if "key_usage" in aws_params:
            cmd.extend(["--key-usage", aws_params["key_usage"]])
        if "origin" in aws_params:
            cmd.extend(["--origin", aws_params["origin"]])
        if "external_accounts" in aws_params:
            cmd.extend(["--external-accounts", aws_params["external_accounts"]])
        if "key_admins" in aws_params:
            cmd.extend(["--key-admins", aws_params["key_admins"]])
        if "key_users" in aws_params:
            cmd.extend(["--key-users", aws_params["key_users"]])
        if "key_admins_roles" in aws_params:
            cmd.extend(["--key-admins-roles", aws_params["key_admins_roles"]])
        if "key_users_roles" in aws_params:
            cmd.extend(["--key-users-roles", aws_params["key_users_roles"]])
        if "multiregion" in aws_params and aws_params["multiregion"]:
            cmd.append("--multiregion")
        if "policy_template" in aws_params:
            cmd.extend(["--policy-template", aws_params["policy_template"]])
        if "bypass_policy_lockout_safety_check" in aws_params and aws_params["bypass_policy_lockout_safety_check"]:
            cmd.append("--bypass-policy-lockout-safety-check")
        if "aws_tags_jsonfile" in aws_params:
            cmd.extend(["--aws-tags-jsonfile", aws_params["aws_tags_jsonfile"]])
        if "aws_policy_jsonfile" in aws_params:
            cmd.extend(["--aws-policy-jsonfile", aws_params["aws_policy_jsonfile"]])
        if "aws_keycreate_jsonfile" in aws_params:
            cmd.extend(["--aws-keycreate-jsonfile", aws_params["aws_keycreate_jsonfile"]])
        if "aws_create_key_kms_params_jsonfile" in aws_params:
            cmd.extend(["--aws-create-key-kms-params-jsonfile", aws_params["aws_create_key_kms_params_jsonfile"]])
            
    elif base_action == "list":
        cmd.append("list")
        # Optional parameters for list
        if "alias" in aws_params:
            cmd.extend(["--alias", aws_params["alias"]])
        if "enabled" in aws_params:
            cmd.extend(["--enabled", str(aws_params["enabled"]).lower()])
        if "limit" in aws_params:
            cmd.extend(["--limit", str(aws_params["limit"])])
        if "skip" in aws_params:
            cmd.extend(["--skip", str(aws_params["skip"])])
        if "key_state" in aws_params:
            cmd.extend(["--key-state", aws_params["key_state"]])
        if "origin" in aws_params:
            cmd.extend(["--origin", aws_params["origin"]])
        if "sort" in aws_params:
            cmd.extend(["--sort", aws_params["sort"]])
        if "region" in aws_params:
            cmd.extend(["--region", aws_params["region"]])
        if "kms" in aws_params:
            cmd.extend(["--kms", aws_params["kms"]])
        if "arn" in aws_params:
            cmd.extend(["--arn", aws_params["arn"]])
        if "customer_masterkey_spec" in aws_params:
            cmd.extend(["--customer-masterkey-spec", aws_params["customer_masterkey_spec"]])
        if "tags" in aws_params:
            cmd.extend(["--tags", aws_params["tags"]])
        if "cloud_name" in aws_params:
            cmd.extend(["--cloud-name", aws_params["cloud_name"]])
        if "gone" in aws_params:
            cmd.extend(["--gone", aws_params["gone"]])
        if "id" in aws_params:
            cmd.extend(["--id", aws_params["id"]])
        if "job_config_id" in aws_params:
            cmd.extend(["--job-config-id", aws_params["job_config_id"]])
        if "key_material_origin" in aws_params:
            cmd.extend(["--key-material-origin", aws_params["key_material_origin"]])
        if "keyid" in aws_params:
            cmd.extend(["--keyid", aws_params["keyid"]])
        if "kms_id" in aws_params:
            cmd.extend(["--kms-id", aws_params["kms_id"]])
        if "multi_region" in aws_params:
            cmd.extend(["--multi-region", aws_params["multi_region"]])
        if "multi_region_key_type" in aws_params:
            cmd.extend(["--multi-region-key-type", aws_params["multi_region_key_type"]])
        if "rotation_job_enabled" in aws_params:
            cmd.extend(["--rotation-job-enabled", aws_params["rotation_job_enabled"]])
            
    elif base_action == "schedule_deletion":
        cmd.extend(["schedule-deletion", "--id", aws_params["id"], "--days", str(aws_params["days"])])
    elif base_action == "add_tags":
        cmd.extend(["add-tags", "--id", aws_params["id"], "--aws-tags-jsonfile", aws_params["aws_tags_jsonfile"]])
    elif base_action == "policy":
        cmd.extend(["policy", "--id", aws_params["id"], "--aws-policy-jsonfile", aws_params["aws_policy_jsonfile"]])
    elif base_action == "add_alias":
        cmd.extend(["add-alias", "--id", aws_params["id"], "--alias", aws_params["alias"]])
    elif base_action == "delete_alias":
        cmd.extend(["delete-alias", "--id", aws_params["id"], "--alias", aws_params["alias"]])
    elif base_action == "update_description":
        cmd.extend(["update-description", "--id", aws_params["id"], "--description", aws_params["description"]])
    elif base_action == "update_primary_region":
        cmd.extend(["update-primary-region", "--id", aws_params["id"], "--primary-region", aws_params["primary_region"]])
    elif base_action == "verify_alias":
        cmd.extend(["verify-alias", "--id", aws_params["id"], "--alias", aws_params["alias"]])
    elif base_action == "replicate_key":
        cmd.extend(["replicate-key", "--id", aws_params["id"], "--region", aws_params["region"]])
    elif base_action == "import_material":
        cmd.extend(["import-material", "--id", aws_params["id"], "--source-key-identifier", aws_params["source_key_identifier"]])
        # Optional parameters
        if "source_key_tier" in aws_params:
            cmd.extend(["--source-key-tier", aws_params["source_key_tier"]])
        if "key_expiration" in aws_params:
            if aws_params["key_expiration"]:
                cmd.append("--key-expiration")
        if "valid_to" in aws_params:
            cmd.extend(["--valid-to", aws_params["valid_to"]])
        if "aws_importmaterial_jsonfile" in aws_params:
            cmd.extend(["--aws-importmaterial-jsonfile", aws_params["aws_importmaterial_jsonfile"]])
    elif base_action == "rotate":
        cmd.extend(["rotate", "--id", aws_params["id"]])
    elif base_action == "sync_jobs_start":
        cmd.extend(["synchronization-jobs", "start"])
        # Required parameters (mutually exclusive groups)
        if "kms_list" in aws_params:
            cmd.extend(["--kms-list", aws_params["kms_list"]])
        if "regions" in aws_params:
            cmd.extend(["--regions", aws_params["regions"]])
        if "synchronize_all" in aws_params and aws_params["synchronize_all"]:
            cmd.append("--synchronize-all")
        # Optional parameters
        if "limit" in aws_params:
            cmd.extend(["--limit", str(aws_params["limit"])])
        if "skip" in aws_params:
            cmd.extend(["--skip", str(aws_params["skip"])])
        if "sort" in aws_params:
            cmd.extend(["--sort", aws_params["sort"]])
        if "cloud_name" in aws_params:
            cmd.extend(["--cloud-name", aws_params["cloud_name"]])
        if "gone" in aws_params:
            cmd.extend(["--gone", aws_params["gone"]])
        if "id" in aws_params:
            cmd.extend(["--id", aws_params["id"]])
        if "job_config_id" in aws_params:
            cmd.extend(["--job-config-id", aws_params["job_config_id"]])
        if "key_material_origin" in aws_params:
            cmd.extend(["--key-material-origin", aws_params["key_material_origin"]])
        if "keyid" in aws_params:
            cmd.extend(["--keyid", aws_params["keyid"]])
        if "kms_id" in aws_params:
            cmd.extend(["--kms-id", aws_params["kms_id"]])
        if "multi_region" in aws_params:
            cmd.extend(["--multi-region", aws_params["multi_region"]])
        if "multi_region_key_type" in aws_params:
            cmd.extend(["--multi-region-key-type", aws_params["multi_region_key_type"]])
        if "rotation_job_enabled" in aws_params:
            cmd.extend(["--rotation-job-enabled", aws_params["rotation_job_enabled"]])
    elif base_action == "sync_jobs_status":
        cmd.extend(["synchronization-jobs", "status"])
        # Optional parameters
        if "limit" in aws_params:
            cmd.extend(["--limit", str(aws_params["limit"])])
        if "skip" in aws_params:
            cmd.extend(["--skip", str(aws_params["skip"])])
        if "sort" in aws_params:
            cmd.extend(["--sort", aws_params["sort"]])
        if "cloud_name" in aws_params:
            cmd.extend(["--cloud-name", aws_params["cloud_name"]])
        if "gone" in aws_params:
            cmd.extend(["--gone", aws_params["gone"]])
        if "id" in aws_params:
            cmd.extend(["--id", aws_params["id"]])
        if "job_config_id" in aws_params:
            cmd.extend(["--job-config-id", aws_params["job_config_id"]])
        if "key_material_origin" in aws_params:
            cmd.extend(["--key-material-origin", aws_params["key_material_origin"]])
        if "keyid" in aws_params:
            cmd.extend(["--keyid", aws_params["keyid"]])
        if "kms_id" in aws_params:
            cmd.extend(["--kms-id", aws_params["kms_id"]])
        if "multi_region" in aws_params:
            cmd.extend(["--multi-region", aws_params["multi_region"]])
        if "multi_region_key_type" in aws_params:
            cmd.extend(["--multi-region-key-type", aws_params["multi_region_key_type"]])
        if "rotation_job_enabled" in aws_params:
            cmd.extend(["--rotation-job-enabled", aws_params["rotation_job_enabled"]])
    elif base_action == "sync_jobs_get":
        cmd.extend(["synchronization-jobs", "get", "--id", aws_params["id"]])
    elif base_action == "sync_jobs_cancel":
        cmd.extend(["synchronization-jobs", "cancel", "--id", aws_params["id"]])
    elif base_action == "policy_template_create":
        cmd.extend(["policy-template", "create"])
        cmd.extend(["--policy-template-name", aws_params["policy_template_name"]])
        if "aws_policycreate_jsonfile" in aws_params:
            cmd.extend(["--aws-policycreate-jsonfile", aws_params["aws_policycreate_jsonfile"]])
    elif base_action == "policy_template_list":
        cmd.extend(["policy-template", "list"])
        if "limit" in aws_params:
            cmd.extend(["--limit", str(aws_params["limit"])])
        if "skip" in aws_params:
            cmd.extend(["--skip", str(aws_params["skip"])])
        if "sort" in aws_params:
            cmd.extend(["--sort", aws_params["sort"]])
    elif base_action == "policy_template_update":
        cmd.extend(["policy-template", "update", "--id", aws_params["id"]])
        if "aws_policyupdate_jsonfile" in aws_params:
            cmd.extend(["--aws-policyupdate-jsonfile", aws_params["aws_policyupdate_jsonfile"]])
    elif base_action == "create_aws_cloudhsm":
        cmd.append("create-aws-cloudhsm-keys")
        cmd.extend(["--alias", aws_params["alias"]])
        cmd.extend(["--custom-key-store-id", aws_params["custom_key_store_id"]])
        # Optional parameters
        if "description" in aws_params:
            cmd.extend(["--description", aws_params["description"]])
        if "external_accounts" in aws_params:
            cmd.extend(["--external-accounts", aws_params["external_accounts"]])
        if "key_admins" in aws_params:
            cmd.extend(["--key-admins", aws_params["key_admins"]])
        if "key_users" in aws_params:
            cmd.extend(["--key-users", aws_params["key_users"]])
        if "key_admins_roles" in aws_params:
            cmd.extend(["--key-admins-roles", aws_params["key_admins_roles"]])
        if "key_users_roles" in aws_params:
            cmd.extend(["--key-users-roles", aws_params["key_users_roles"]])
        if "policy_template" in aws_params:
            cmd.extend(["--policy-template", aws_params["policy_template"]])
        if "source_key_tier" in aws_params:
            cmd.extend(["--source-key-tier", aws_params["source_key_tier"]])
        if "sourceKey_identifier" in aws_params:
            cmd.extend(["--sourceKey-identifier", aws_params["sourceKey_identifier"]])
        if "blocked" in aws_params:
            cmd.extend(["--blocked", aws_params["blocked"]])
        if "linked_state" in aws_params:
            cmd.extend(["--linked-state", aws_params["linked_state"]])
        if "aws_policy_jsonfile" in aws_params:
            cmd.extend(["--aws-policy-jsonfile", aws_params["aws_policy_jsonfile"]])
    elif base_action == "create_aws_hyok":
        cmd.append("create-aws-hyok-keys")
        cmd.extend(["--alias", aws_params["alias"]])
        cmd.extend(["--custom-key-store-id", aws_params["custom_key_store_id"]])
        # Optional parameters
        if "description" in aws_params:
            cmd.extend(["--description", aws_params["description"]])
        if "external_accounts" in aws_params:
            cmd.extend(["--external-accounts", aws_params["external_accounts"]])
        if "key_admins" in aws_params:
            cmd.extend(["--key-admins", aws_params["key_admins"]])
        if "key_users" in aws_params:
            cmd.extend(["--key-users", aws_params["key_users"]])
        if "key_admins_roles" in aws_params:
            cmd.extend(["--key-admins-roles", aws_params["key_admins_roles"]])
        if "key_users_roles" in aws_params:
            cmd.extend(["--key-users-roles", aws_params["key_users_roles"]])
        if "policy_template" in aws_params:
            cmd.extend(["--policy-template", aws_params["policy_template"]])
        if "source_key_tier" in aws_params:
            cmd.extend(["--source-key-tier", aws_params["source_key_tier"]])
        if "sourceKey_identifier" in aws_params:
            cmd.extend(["--sourceKey-identifier", aws_params["sourceKey_identifier"]])
        if "blocked" in aws_params:
            cmd.extend(["--blocked", aws_params["blocked"]])
        if "linked_state" in aws_params:
            cmd.extend(["--linked-state", aws_params["linked_state"]])
        if "aws_policy_jsonfile" in aws_params:
            cmd.extend(["--aws-policy-jsonfile", aws_params["aws_policy_jsonfile"]])
    elif base_action == "upload":
        cmd.append("upload")
        # Required parameters
        source_key_id = aws_params.get("source_key_identifier") or aws_params.get("sourceKey_identifier")
        cmd.extend(["--source-key-identifier", source_key_id])
        cmd.extend(["--region", aws_params["region"]])
        cmd.extend(["--kms", aws_params["kms"]])
        
        # Optional parameters
        if "alias" in aws_params:
            cmd.extend(["--alias", aws_params["alias"]])
        if "description" in aws_params:
            cmd.extend(["--description", aws_params["description"]])
        if "customer_masterkey_spec" in aws_params:
            cmd.extend(["--customer-masterkey-spec", aws_params["customer_masterkey_spec"]])
        if "key_usage" in aws_params:
            cmd.extend(["--key-usage", aws_params["key_usage"]])
        if "source_key_tier" in aws_params:
            cmd.extend(["--source-key-tier", aws_params["source_key_tier"]])
        if "external_accounts" in aws_params:
            cmd.extend(["--external-accounts", aws_params["external_accounts"]])
        if "key_admins" in aws_params:
            cmd.extend(["--key-admins", aws_params["key_admins"]])
        if "key_users" in aws_params:
            cmd.extend(["--key-users", aws_params["key_users"]])
        if "key_admins_roles" in aws_params:
            cmd.extend(["--key-admins-roles", aws_params["key_admins_roles"]])
        if "key_users_roles" in aws_params:
            cmd.extend(["--key-users-roles", aws_params["key_users_roles"]])
        if "multiregion" in aws_params and aws_params["multiregion"]:
            cmd.append("--multiregion")
        if "policy_template" in aws_params:
            cmd.extend(["--policy-template", aws_params["policy_template"]])
        if "bypass_policy_lockout_safety_check" in aws_params and aws_params["bypass_policy_lockout_safety_check"]:
            cmd.append("--bypass-policy-lockout-safety-check")
        if "key_expiration" in aws_params:
            if aws_params["key_expiration"]:
                cmd.append("--key-expiration")
        if "valid_to" in aws_params:
            cmd.extend(["--valid-to", aws_params["valid_to"]])
        if "aws_tags_jsonfile" in aws_params:
            cmd.extend(["--aws-tags-jsonfile", aws_params["aws_tags_jsonfile"]])
        if "aws_policy_jsonfile" in aws_params:
            cmd.extend(["--aws-policy-jsonfile", aws_params["aws_policy_jsonfile"]])
        if "aws_uploadkey_jsonfile" in aws_params:
            cmd.extend(["--aws-uploadkey-jsonfile", aws_params["aws_uploadkey_jsonfile"]])
        if "aws_key_upload_kms_params_jsonfile" in aws_params:
            cmd.extend(["--aws-key-upload-kms-params-jsonfile", aws_params["aws_key_upload_kms_params_jsonfile"]])
    else:
        raise ValueError(f"Unsupported key action: {action}")
    
    return cmd
