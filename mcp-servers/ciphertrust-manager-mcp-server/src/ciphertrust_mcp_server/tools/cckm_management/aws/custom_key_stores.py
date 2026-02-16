"""AWS Custom Key Stores operations for CCKM."""
from typing import Any, Dict

def get_custom_key_stores_operations() -> Dict[str, Any]:
    """Return schema and action requirements for AWS Custom Key Stores operations."""
    return {
        "action_requirements": {
            "custom-key-stores-connect": {"required": ["id"], "optional": ["key_store_password"]},
            "custom-key-stores-credentials-delete": {"required": ["custom-key-store-id", "id"], "optional": []},
            "custom-key-stores-credentials-get": {"required": ["custom-key-store-id", "id"], "optional": []},
            "custom-key-stores-credentials-list": {"required": ["id"], "optional": ["limit", "skip", "sort"]},
            "custom-key-stores-delete": {"required": ["id"], "optional": []},
            "custom-key-stores-disable-credential-rotation-job": {"required": ["id"], "optional": []},
            "custom-key-stores-disconnect": {"required": ["id"], "optional": []},
            "custom-key-stores-enable-credential-rotation-job": {"required": ["id", "job-config-id"], "optional": []},
            "custom-key-stores-link": {"required": ["id"], "optional": ["xks-proxy-vpc-endpoint-service-name"]},
            "custom-key-stores-rotate-credential": {"required": ["id"], "optional": []},
            "custom-key-stores-update": {"required": ["id"], "optional": ["cks-name", "partition-id", "health-check-key-id", "mtls-enabled", "xks-proxy-connectivity"]},
            "custom_key_stores_list": {"required": [], "optional": ["limit", "skip"]},
            "custom_key_stores_get": {"required": ["custom_key_store_id"], "optional": []},
            "custom_key_stores_create": {"required": ["custom_key_store_name"], "optional": ["cloudhsm_cluster_id", "trust_anchor_certificate", "key_store_password", "kms_endpoint", "xks_proxy_uri", "xks_proxy_connectivity", "xks_proxy_authentication_credential", "xks_proxy_vpc_endpoint_service_name"]},
            "custom_key_stores_block": {"required": ["custom_key_store_id"], "optional": []},
            "custom_key_stores_unblock": {"required": ["custom_key_store_id"], "optional": []},
        }
    }

def build_custom_key_stores_command(action: str, aws_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given AWS Custom Key Stores operation."""
    cmd = ["cckm", "aws", "custom-key-stores"]
    action_name = action.replace("custom-key-stores-", "").replace("custom_key_stores_", "")
    
    # Add parameters based on action
    if "id" in aws_params:
        cmd.extend(["--id", aws_params["id"]])
        
    if action_name == "connect" and "key_store_password" in aws_params:
        cmd.extend(["--key-store-password", aws_params["key_store_password"]])
        
    return cmd
