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
        "description": "Domain for the operation"
    },
    "auth_domain": {
        "type": "string", 
        "description": "Authentication domain for the operation"
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
    "pending_window_in_days": {"type": "integer", "description": "Pending deletion window in days"}
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

# Operation mappings for each cloud provider
CLOUD_OPERATIONS = {
    "aws": ["list", "get", "create", "update", "delete", "enable", "disable", "rotate", "add_alias", "delete_alias", "add_tags", "remove_tags", "schedule_deletion", "cancel_deletion", "import_material", "delete_material", "upload", "download_public_key", "policy", "replicate_key", "block", "unblock"],
    "azure": ["list", "get", "create", "update", "delete", "enable", "disable", "rotate", "backup", "restore", "import", "export"],
    "google": ["list", "get", "create", "update", "delete", "enable", "disable", "rotate", "destroy", "restore"],
    "oci": ["list", "get", "create", "update", "delete", "enable", "disable", "rotate", "backup", "restore"],
    "microsoft": ["list", "get", "create", "update", "delete", "enable", "disable", "rotate", "archive", "recover", "enable_rotation_job", "disable_rotation_job"],
    "ekm": ["list", "get", "create", "update", "delete", "enable", "disable", "rotate", "destroy", "policy"],
    "gws": ["list", "get", "create", "update", "delete", "enable", "disable", "rotate_key", "archive", "recover", "wrap", "unwrap", "privileged_unwrap", "rewrap", "status", "certs", "digest", "delegate", "get_perimeter"],
    "sap-dc": ["list", "get", "create", "update", "delete"],
    "salesforce": ["list", "get", "create", "update", "delete"],
    "virtual": ["list", "get", "create", "update", "delete"],
    "hsm": ["list", "get", "create", "update", "delete"],
    "external-cm": ["list", "get", "create", "update", "delete"],
    "dsm": ["list", "get", "create", "update", "delete"]
} 