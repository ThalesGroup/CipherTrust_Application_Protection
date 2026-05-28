"""Constants for CCKM operations."""

# Common schema properties for all CCKM operations
COMMON_SCHEMA_PROPERTIES = {
    "cloud_provider": {
        "type": "string",
        "enum": [
            "aws", "azure", "google", "oci", "sap-dc", "salesforce",
            "microsoft", "virtual", "hsm", "gws", "ekm", "external-cm", "dsm"
        ],
        "description": "The cloud provider to manage keys for"
    },
    "domain": {
        "type": "string",
        "description": "The CipherTrust Manager domain where the action, operation, or execution will be performed. This specifies the target environment for the command."
    },
    "auth_domain": {
        "type": "string", 
        "description": "The CipherTrust Manager domain where the user is created and authenticated. Unless explicitly specified, this defaults to 'root'. This is used for access control and does not affect the command's execution target."
    }
}

# Common parameters for key operations
COMMON_KEY_PARAMETERS = {
    "id": {"type": "string", "description": "Key ID for get/delete operations"},
    "alias": {"type": "string", "description": "Key alias for create/update operations"},
    "description": {"type": "string", "description": "Key description"},
    "enabled": {"type": "boolean", "description": "Whether the key is enabled"},
    "tags": {"type": "object", "description": "Key tags"},
    "limit": {"type": "integer", "description": "Maximum number of results to return"},
    "skip": {"type": "integer", "description": "Number of results to skip"}
}

# Cloud provider specific parameters
AWS_PARAMETERS = {
    **COMMON_KEY_PARAMETERS,
    "region": {"type": "string", "description": "AWS region for key operations"},
    "key_spec": {"type": "string", "description": "Key specification (e.g., AES_256, RSA_2048)"},
    "key_usage": {"type": "string", "description": "Key usage (ENCRYPT_DECRYPT, SIGN_VERIFY)"},
    "origin": {"type": "string", "description": "Key origin (AWS_KMS, EXTERNAL, AWS_CLOUDHSM)"},
    "bypass_policy_lockout_safety_check": {"type": "boolean", "description": "Bypass policy lockout safety check"},
    "policy": {"type": "string", "description": "Key policy in JSON format"},
    "pending_window_in_days": {"type": "integer", "description": "Pending deletion window in days"},
    "customer_masterkey_spec": {"type": "string", "description": "Customer master key spec"},
    "aws_key_users": {"type": "string", "description": "AWS key users"},
    "aws_kms_name": {"type": "string", "description": "AWS KMS name"},
    "aws_policy_jsonfile": {"type": "string", "description": "AWS policy JSON file"},
    "multiregion": {"type": "boolean", "description": "Flag for multi-region"},
    "policy_template": {"type": "string", "description": "Policy template"},
    "key_state": {"type": "string", "description": "State of the key"},
    "aws_tags_jsonfile": {"type": "string", "description": "AWS tags JSON file"},
    "days": {"type": "integer", "description": "Number of days"},
    "material": {"type": "string", "description": "Key material"}
}

AZURE_PARAMETERS = {
    **COMMON_KEY_PARAMETERS,
    "vault_name": {"type": "string", "description": "Azure Key Vault name"},
    "key_type": {"type": "string", "description": "Key type (RSA, RSA-HSM, EC, EC-HSM, oct)"},
    "key_size": {"type": "integer", "description": "Key size in bits"},
    "curve": {"type": "string", "description": "Elliptic curve name for EC keys"},
    "key_ops": {"type": "array", "items": {"type": "string"}, "description": "Key operations"},
    "exp": {"type": "string", "description": "Expiration date"},
    "nbf": {"type": "string", "description": "Not before date"}
}

GOOGLE_PARAMETERS = {
    **COMMON_KEY_PARAMETERS,
    "project_id": {"type": "string", "description": "Google Cloud project ID"},
    "location": {"type": "string", "description": "Google Cloud location"},
    "key_ring": {"type": "string", "description": "Key ring name"},
    "protection_level": {"type": "string", "description": "Protection level (SOFTWARE, HSM)"},
    "algorithm": {"type": "string", "description": "Algorithm (GOOGLE_SYMMETRIC_ENCRYPTION, RSA_SIGN_PSS_2048_SHA256, etc.)"},
    "purpose": {"type": "string", "description": "Key purpose (ENCRYPT_DECRYPT, ASYMMETRIC_SIGN, ASYMMETRIC_DECRYPT)"}
}

OCI_PARAMETERS = {
    **COMMON_KEY_PARAMETERS,
    "compartment_id": {"type": "string", "description": "OCI compartment ID"},
    "vault_id": {"type": "string", "description": "OCI vault ID"},
    "key_shape": {"type": "object", "description": "Key shape configuration"},
    "protection_mode": {"type": "string", "description": "Protection mode (HSM, SOFTWARE)"},
    "algorithm": {"type": "string", "description": "Algorithm (AES, RSA, ECDSA)"}
}

# Microsoft DKE parameters
MICROSOFT_PARAMETERS = {
    **COMMON_KEY_PARAMETERS,
    "tenant_id": {"type": "string", "description": "Microsoft tenant ID"},
    "client_id": {"type": "string", "description": "Microsoft client ID"},
    "client_secret": {"type": "string", "description": "Microsoft client secret"},
    "endpoint_url": {"type": "string", "description": "DKE endpoint URL"},
    "key_id": {"type": "string", "description": "Key ID for DKE operations"},
    "rotation_schedule": {"type": "string", "description": "Key rotation schedule"}
}

# Google EKM parameters
EKM_PARAMETERS = {
    **COMMON_KEY_PARAMETERS,
    "project_id": {"type": "string", "description": "Google Cloud project ID"},
    "location": {"type": "string", "description": "Google Cloud location"},
    "cryptospace_id": {"type": "string", "description": "EKM cryptospace ID"},
    "endpoint_url": {"type": "string", "description": "EKM endpoint URL"},
    "policy": {"type": "string", "description": "EKM endpoint policy"}
}

# Google Workspace (GWS) parameters
GWS_PARAMETERS = {
    **COMMON_KEY_PARAMETERS,
    "project_id": {"type": "string", "description": "Google Cloud project ID"},
    "location": {"type": "string", "description": "Google Cloud location"},
    "endpoint_url": {"type": "string", "description": "GWS endpoint URL"},
    "issuer_id": {"type": "string", "description": "JWT issuer ID"},
    "resource_key": {"type": "string", "description": "Resource key for GWS operations"},
    "wrapped_dek": {"type": "string", "description": "Wrapped DEK for unwrap operations"},
    "perimeter_id": {"type": "string", "description": "Perimeter ID for access policy"}
}

# AWS Custom Key Store parameters
AWS_CUSTOM_KEY_STORE_PARAMETERS = {
    "custom_key_store_id": {"type": "string", "description": "Custom key store ID"},
    "cloudhsm_cluster_id": {"type": "string", "description": "CloudHSM cluster ID"},
    "trust_anchor_certificate": {"type": "string", "description": "Trust anchor certificate"},
    "key_store_password": {"type": "string", "description": "Key store password"},
    "kms_endpoint": {"type": "string", "description": "KMS endpoint URL"},
    "xks_proxy_uri": {"type": "string", "description": "XKS proxy URI"},
    "xks_proxy_connectivity": {"type": "string", "description": "XKS proxy connectivity type"},
    "xks_proxy_authentication_credential": {"type": "string", "description": "XKS proxy authentication credential"},
    "xks_proxy_vpc_endpoint_service_name": {"type": "string", "description": "XKS proxy VPC endpoint service name"},
    "job_config_id": {"type": "string", "description": "Job config ID"},
    "cks_name": {"type": "string", "description": "Custom key store name"},
    "partition_id": {"type": "string", "description": "Partition ID"},
    "health_check_key_id": {"type": "string", "description": "Health check key ID"},
    "mtls_enabled": {"type": "boolean", "description": "Enable MTLS"}
}

# AWS IAM parameters
AWS_IAM_PARAMETERS = {
    "user_name": {"type": "string", "description": "AWS IAM user name"},
    "role_name": {"type": "string", "description": "AWS IAM role name"},
    "path": {"type": "string", "description": "IAM path"},
    "max_items": {"type": "integer", "description": "Maximum number of items to return"},
    "kms": {"type": "string", "description": "Name or ID of the KMS"},
    "path_prefix": {"type": "string", "description": "Path prefix for filtering"},
    "marker": {"type": "string", "description": "Pagination marker"}
}

# AWS KMS parameters
AWS_KMS_PARAMETERS = {
    "account_id": {"type": "string", "description": "AWS account ID"},
    "regions": {"type": "array", "items": {"type": "string"}, "description": "AWS regions"},
    "name": {"type": "string", "description": "Unique name for the resource"},
    "connection_identifier": {"type": "string", "description": "Name or ID of the connection"},
    "access_key_id": {"type": "string", "description": "AWS access key ID"},
    "secret_access_key": {"type": "string", "description": "AWS secret access key"},
    "session_token": {"type": "string", "description": "AWS session token"},
    "assume_role_arn": {"type": "string", "description": "ARN of the Assume Role"},
    "assume_role_ext_id": {"type": "string", "description": "External ID of the Assume Role"}
}

# AWS Synchronization Job parameters
AWS_SYNC_JOB_PARAMETERS = {
    "kms_list": {"type": "string", "description": "Name or ID of KMS resources"},
    "regions": {"type": "string", "description": "List of AWS regions"},
    "synchronize_all": {"type": "boolean", "description": "Synchronize all keys from all KMS and regions"}
}

# AWS Reports parameters
AWS_REPORTS_PARAMETERS = {
    "report_type": {"type": "string", "description": "Report type (keys, usage, etc.)"},
    "report_format": {"type": "string", "description": "Report format (CSV, JSON, etc.)"},
    "filters": {"type": "object", "description": "Report filters"},
    "job_id": {"type": "string", "description": "Report job ID"},
    "file_path": {"type": "string", "description": "File path for download"},
    "name": {"type": "string", "description": "Name of the report"},
    "start_time": {"type": "string", "description": "Start time for the report"},
    "end_time": {"type": "string", "description": "End time for the report"}
}

# AWS Bulk Job parameters
AWS_BULK_JOB_PARAMETERS = {
    "bulkjob_keys_id": {"type": "string", "description": "ID of the keys for the bulk job"},
    "bulkjob_operation": {"type": "string", "description": "Operation to be performed in the bulk job"},
    "days": {"type": "integer", "description": "Number of days for schedule key deletion"},
    "policy_template_id": {"type": "string", "description": "ID of the policy template"}
}

# OCI Compartment parameters
OCI_COMPARTMENT_PARAMETERS = {
    "compartment_id": {"type": "string", "description": "OCI compartment ID"},
    "compartment_name": {"type": "string", "description": "OCI compartment name"},
    "description": {"type": "string", "description": "Compartment description"},
    "defined_tags": {"type": "object", "description": "OCI defined tags"},
    "freeform_tags": {"type": "object", "description": "OCI freeform tags"}
}

# OCI External Vault parameters
OCI_EXTERNAL_VAULT_PARAMETERS = {
    "external_vault_id": {"type": "string", "description": "External vault ID"},
    "external_key_id": {"type": "string", "description": "External key ID"},
    "vault_name": {"type": "string", "description": "External vault name"},
    "endpoint": {"type": "string", "description": "External vault endpoint"},
    "certificate": {"type": "string", "description": "Certificate for external vault"},
    "private_key": {"type": "string", "description": "Private key for external vault"}
}

# OCI Issuer parameters
OCI_ISSUER_PARAMETERS = {
    "issuer_id": {"type": "string", "description": "OCI issuer ID"},
    "issuer_name": {"type": "string", "description": "OCI issuer name"},
    "issuer_type": {"type": "string", "description": "OCI issuer type"},
    "certificate": {"type": "string", "description": "Issuer certificate"},
    "private_key": {"type": "string", "description": "Issuer private key"}
}

# OCI Tenancy parameters
OCI_TENANCY_PARAMETERS = {
    "tenancy_id": {"type": "string", "description": "OCI tenancy ID"},
    "tenancy_name": {"type": "string", "description": "OCI tenancy name"},
    "description": {"type": "string", "description": "Tenancy description"}
}

# OCI Vault parameters
OCI_VAULT_PARAMETERS = {
    "vault_id": {"type": "string", "description": "OCI vault ID"},
    "vault_name": {"type": "string", "description": "OCI vault name"},
    "compartment_id": {"type": "string", "description": "OCI compartment ID"},
    "vault_type": {"type": "string", "description": "Vault type (VIRTUAL_PRIVATE, DEFAULT)"},
    "display_name": {"type": "string", "description": "Vault display name"}
}

# OCI Reports parameters
OCI_REPORTS_PARAMETERS = {
    "report_type": {"type": "string", "description": "Report type"},
    "report_format": {"type": "string", "description": "Report format"},
    "filters": {"type": "object", "description": "Report filters"},
    "job_id": {"type": "string", "description": "Report job ID"},
    "file_path": {"type": "string", "description": "File path for download"}
}

# Azure Certificate parameters
AZURE_CERTIFICATE_PARAMETERS = {
    "certificate_id": {"type": "string", "description": "Azure certificate ID"},
    "certificate_name": {"type": "string", "description": "Azure certificate name"},
    "certificate_type": {"type": "string", "description": "Azure certificate type"},
    "certificate_data": {"type": "string", "description": "Certificate data"},
    "certificate_password": {"type": "string", "description": "Certificate password"},
    "policy": {"type": "object", "description": "Certificate policy"}
}

# Azure Secret parameters
AZURE_SECRET_PARAMETERS = {
    "secret_id": {"type": "string", "description": "Azure secret ID"},
    "secret_name": {"type": "string", "description": "Azure secret name"},
    "secret_value": {"type": "string", "description": "Secret value"},
    "content_type": {"type": "string", "description": "Secret content type"},
    "attributes": {"type": "object", "description": "Secret attributes"}
}

# Azure Vault parameters
AZURE_VAULT_PARAMETERS = {
    "vault_id": {"type": "string", "description": "Azure vault ID"},
    "vault_name": {"type": "string", "description": "Azure vault name"},
    "resource_group": {"type": "string", "description": "Azure resource group"},
    "location": {"type": "string", "description": "Azure location"},
    "sku": {"type": "string", "description": "Vault SKU"},
    "tenant_id": {"type": "string", "description": "Azure tenant ID"},
    "access_policies": {"type": "object", "description": "Access policies"}
}

# Azure Subscription parameters
AZURE_SUBSCRIPTION_PARAMETERS = {
    "subscription_id": {"type": "string", "description": "Azure subscription ID"},
    "subscription_name": {"type": "string", "description": "Azure subscription name"},
    "tenant_id": {"type": "string", "description": "Azure tenant ID"},
    "state": {"type": "string", "description": "Subscription state"}
}

# Azure Reports parameters
AZURE_REPORTS_PARAMETERS = {
    "report_type": {"type": "string", "description": "Report type"},
    "report_format": {"type": "string", "description": "Report format"},
    "filters": {"type": "object", "description": "Report filters"},
    "job_id": {"type": "string", "description": "Report job ID"},
    "file_path": {"type": "string", "description": "File path for download"}
}

# Azure Bulk Job parameters
AZURE_BULKJOB_PARAMETERS = {
    "job_id": {"type": "string", "description": "Bulk job ID"},
    "operation": {"type": "string", "description": "Bulk job operation"},
    "parameters": {"type": "object", "description": "Bulk job parameters"},
    "status": {"type": "string", "description": "Job status"}
}

# Google Cloud Key Ring parameters
GOOGLE_KEYRING_PARAMETERS = {
    "keyring_id": {"type": "string", "description": "Google Cloud key ring ID"},
    "keyring_name": {"type": "string", "description": "Google Cloud key ring name"},
    "project_id": {"type": "string", "description": "Google Cloud project ID"},
    "location": {"type": "string", "description": "Google Cloud location"},
    "acls": {"type": "object", "description": "Access control lists"}
}

# Google Cloud Location parameters
GOOGLE_LOCATION_PARAMETERS = {
    "location_id": {"type": "string", "description": "Google Cloud location ID"},
    "location_name": {"type": "string", "description": "Google Cloud location name"}
}

# Google Cloud Project parameters
GOOGLE_PROJECT_PARAMETERS = {
    "project_id": {"type": "string", "description": "Google Cloud project ID"},
    "project_name": {"type": "string", "description": "Google Cloud project name"},
    "project_number": {"type": "string", "description": "Google Cloud project number"},
    "acls": {"type": "object", "description": "Access control lists"}
}

# Google Cloud Reports parameters
GOOGLE_REPORTS_PARAMETERS = {
    "report_type": {"type": "string", "description": "Report type"},
    "report_format": {"type": "string", "description": "Report format"},
    "filters": {"type": "object", "description": "Report filters"},
    "job_id": {"type": "string", "description": "Report job ID"},
    "file_path": {"type": "string", "description": "File path for download"}
}

# Operation mappings for each cloud provider
CLOUD_OPERATIONS = {
    "aws": [
        # Key operations
        "keys_list", "keys_get", "keys_create", "keys_delete", "keys_enable", "keys_disable", "keys_rotate", "keys_add_alias", "keys_delete_alias", 
        "keys_add_tags", "keys_remove_tags", "keys_schedule_deletion", "keys_cancel_deletion", "keys_import_material", "keys_delete_material", 
        "keys_upload", "keys_download_public_key", "keys_policy", "keys_replicate_key", "keys_block", "keys_unblock", "keys_enable_auto_rotation", 
        "keys_disable_auto_rotation", "keys_enable_rotation_job", "keys_disable_rotation_job", "keys_list_rotations", "keys_verify_alias",
        "keys_link", "keys_update_description", "keys_update_primary_region", "keys_rotate_material", "keys_download_metadata",
        "keys_create_aws_cloudhsm", "keys_create_aws_hyok", "keys_policy_template_create", "keys_policy_template_delete",
        "keys_policy_template_get", "keys_policy_template_list", "keys_policy_template_update", "keys_sync_jobs_cancel",
        "keys_sync_jobs_get", "keys_sync_jobs_status",
        # Custom Key Store operations
        "custom_key_stores_list", "custom_key_stores_get", "custom_key_stores_create", "custom_key_stores_block", 
        "custom_key_stores_unblock", "custom_key_stores_credentials_get", "custom_key_stores_get_unused_cloudhsm_clusters",
        "custom_key_stores_sync_jobs_start", "custom_key_stores_sync_jobs_get", "custom_key_stores_sync_jobs_status", 
        "custom_key_stores_sync_jobs_cancel", "custom_key_stores_connect", "custom_key_stores_credentials_delete",
        "custom_key_stores_credentials_get", "custom_key_stores_credentials_list", "custom_key_stores_delete",
        "custom_key_stores_disable_credential_rotation_job", "custom_key_stores_disconnect",
        "custom_key_stores_enable_credential_rotation_job", "custom_key_stores_link", "custom_key_stores_rotate_credential",
        "custom_key_stores_update",
        # Key synchronization operations
        "keys_sync_jobs_start",
        # IAM operations
        "iam_get_roles", "iam_get_users",
        # KMS operations
        "kms_list", "kms_get", "kms_add", "kms_update", "kms_delete", "kms_archive", "kms_recover", 
        "kms_get_account", "kms_get_all_regions", "kms_update_acls",
        # Reports operations
        "reports_list", "reports_get", "reports_get_report", "reports_generate", "reports_download", "reports_delete", "reports_get_reports",
        # Bulk job operations
        "bulkjob_list", "bulkjob_get", "bulkjob_create", "bulkjob_cancel",
        # Log groups operations
        "logs_get_groups"
    ],
    "azure": [
        # Key operations
        "keys_list", "keys_get", "keys_create", "keys_update", "keys_delete", "keys_enable", "keys_disable", "keys_rotate", "keys_backup", "keys_restore", "keys_import", "keys_export",
        "keys_hard_delete", "keys_recover", "keys_upload", "keys_download_metadata", "keys_enable_backup_job", "keys_enable_rotation_job", "keys_delete_backup",
        # Key synchronization operations
        "keys_sync_jobs_start", "keys_sync_jobs_get", "keys_sync_jobs_status", "keys_sync_jobs_cancel",
        # Cloud key backup operations
        "cloud_key_backup_list", "cloud_key_backup_get", "cloud_key_backup_create", "cloud_key_backup_update", "cloud_key_backup_delete",
        # Certificate operations
        "certificates_list", "certificates_get", "certificates_create", "certificates_update", "certificates_delete", "certificates_import", "certificates_restore", "certificates_recover", "certificates_hard_delete", "certificates_soft_delete",
        # Certificate synchronization operations
        "certificates_sync_jobs_start", "certificates_sync_jobs_get", "certificates_sync_jobs_status", "certificates_sync_jobs_cancel",
        # Secret operations
        "secrets_list", "secrets_get", "secrets_create", "secrets_update", "secrets_delete", "secrets_recover",
        # Secret synchronization operations
        "secrets_sync_jobs_start", "secrets_sync_jobs_get", "secrets_sync_jobs_status", "secrets_sync_jobs_cancel",
        # Vault operations
        "vaults_list", "vaults_get", "vaults_create", "vaults_add", "vaults_update", "vaults_delete", "vaults_get_vaults", "vaults_get_managed_hsms", "vaults_enable_rotation_job", "vaults_disable_rotation_job",
        # Subscription operations
        "subscriptions_list", "subscriptions_get", "subscriptions_get_subscriptions",
        # Reports operations
        "reports_list", "reports_get", "reports_generate", "reports_download", "reports_delete", "reports_get_report",
        # Bulk job operations
        "bulkjob_list", "bulkjob_get", "bulkjob_create", "bulkjob_cancel", "bulkjob_delete"
    ],
    "google": [
        # Key operations
        "keys_list", "keys_get", "keys_create", "keys_update", "keys_enable", "keys_disable", "keys_rotate", "keys_restore",
        "keys_add_version", "keys_cancel_schedule_destroy", "keys_disable_auto_rotation", "keys_disable_version", "keys_download_metadata", 
        "keys_download_public_key", "keys_enable_auto_rotation", "keys_enable_version", "keys_get_update_all_versions_status", 
        "keys_get_version", "keys_list_version", "keys_policy", "keys_policy_get", "keys_policy_update", "keys_policy_get_iam_roles",
        "keys_re_import", "keys_refresh", "keys_refresh_version", "keys_schedule_destroy", 
        "keys_upload", "keys_update_all_versions_jobs",
        "keys_synchronize", "keys_synchronize_version",
        # Key synchronization operations
        "keys_sync_jobs_start", "keys_sync_jobs_get", "keys_sync_jobs_status", "keys_sync_jobs_cancel",
        # Key ring operations
        "keyrings_list", "keyrings_get", "keyrings_delete", "keyrings_update", "keyrings_update_acls",
        "keyrings_add_key_rings", "keyrings_get_key_rings",
        # Location operations
        "locations_get_locations",
        # Project operations
        "projects_list", "projects_get", "projects_add", "projects_update", "projects_delete", "projects_get_project", "projects_update_acls",
        # Reports operations
        "reports_list", "reports_get", "reports_generate", "reports_download", "reports_delete", "reports_get_report"
    ],
    "oci": [
        # Key operations
        "keys_list", "keys_get", "keys_create", "keys_update", "keys_delete", "keys_enable", "keys_disable", "keys_rotate", "keys_backup", "keys_restore",
        "keys_enable_auto_rotation", "keys_disable_auto_rotation", "keys_cancel_deletion", "keys_change_compartment", "keys_delete_backup",
        "keys_add_version", "keys_get_version", "keys_list_version", "keys_refresh", "keys_schedule_deletion", "keys_schedule_deletion_version", 
        "keys_cancel_schedule_deletion_version", "keys_upload", "keys_update",
        # Key synchronization operations
        "keys_sync_jobs_start", "keys_sync_jobs_get", "keys_sync_jobs_status", "keys_sync_jobs_cancel",
        # Compartment operations
        "compartments_list", "compartments_get", "compartments_add", "compartments_delete", "compartments_get_compartments",
        "compartments_get_defined_tags", "compartments_add_compartments",
        # External vault operations
        "external_vaults_create", "external_vaults_block_key", "external_vaults_unblock_key", 
        "external_vaults_block_vault", "external_vaults_unblock_vault",
        # Issuer operations
        "issuers_list", "issuers_get", "issuers_create", "issuers_update", "issuers_delete",
        # Region operations
        "regions_get_subscribed",
        # Reports operations
        "reports_list", "reports_get", "reports_generate", "reports_download", "reports_delete", "reports_get_report",
        # Tenancy operations
        "tenancy_list", "tenancy_get", "tenancy_add", "tenancy_delete",
        # Vault operations
        "vaults_list", "vaults_get", "vaults_add", "vaults_update", "vaults_delete", "vaults_get_vaults", "vaults_update_acls",
        "vaults_add_vaults"
    ],
    "microsoft": [
        # Key operations
        "keys_list", "keys_get", "keys_create", "keys_update", "keys_delete", "keys_enable", "keys_disable", "keys_rotate", "keys_archive", "keys_recover", 
        "keys_enable_rotation_job", "keys_disable_rotation_job",
        # DKE endpoint operations
        "dke_endpoints_list", "dke_endpoints_get", "dke_endpoints_create", "dke_endpoints_update", "dke_endpoints_delete"
    ],
    "ekm": [
        # Endpoint operations
        "endpoints_list", "endpoints_get", "endpoints_create", "endpoints_update", "endpoints_delete", "endpoints_enable", "endpoints_disable", "endpoints_rotate", "endpoints_destroy", "endpoints_policy"
    ],
    "gws": [
        # Endpoint operations
        "endpoints_list", "endpoints_get", "endpoints_create", "endpoints_update", "endpoints_delete", "endpoints_enable", "endpoints_disable", "endpoints_rotate_key", "endpoints_archive", "endpoints_recover", 
        "endpoints_wrap", "endpoints_unwrap", "endpoints_privileged_unwrap", "endpoints_rewrap", "endpoints_status", "endpoints_certs", "endpoints_digest", "endpoints_delegate", "endpoints_get_perimeter"
    ],
    "sap-dc": ["keys_list", "keys_get", "keys_create", "keys_update", "keys_delete"],
    "salesforce": ["keys_list", "keys_get", "keys_create", "keys_update", "keys_delete"],
    "virtual": ["keys_list", "keys_get", "keys_create", "keys_update", "keys_delete"],
    "hsm": ["keys_list", "keys_get", "keys_create", "keys_update", "keys_delete"],
    "external-cm": ["keys_list", "keys_get", "keys_create", "keys_update", "keys_delete"],
    "dsm": ["keys_list", "keys_get", "keys_create", "keys_update", "keys_delete"]
} 