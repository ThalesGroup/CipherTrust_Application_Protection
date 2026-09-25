"""OCI External Vault operations for CCKM."""

from typing import Any, Dict


def get_external_vault_operations() -> Dict[str, Any]:
    """Return schema and action requirements for OCI external vault operations."""
    return {
        "schema_properties": {
            "oci_external_vaults_params": {
                "type": "object",
                "properties": {
                    # Basic external vault parameters
                    "id": {
                        "type": "string", 
                        "description": "OCI external key ID for block/unblock operations. CRITICAL FOR AI ASSISTANTS: Always use this 'id' parameter for external key identification operations."
                    },
                    
                    # External vault creation parameters
                    "connection_identifier": {"type": "string", "description": "Name or ID of the connection which has been created earlier"},
                    "oci_endpoint_url_hostname": {"type": "string", "description": "Specify the hostname for the OCI external key store endpoint URI"},
                    "oci_issuer_id": {"type": "string", "description": "Specify the Issuer ID"},
                    "oci_compartment_id": {"type": "string", "description": "OCI compartment ID"},
                    "oci_external_vault_name": {"type": "string", "description": "Specify name for the OCI External Vault"},
                    "oci_client_application_id": {"type": "string", "description": "Client Application ID of the OCI KMS application as registered on third-party IDP"},
                    "enable_success_audit_event": {"type": "boolean", "description": "Enable or disable audit recording of successful operations within an external vault. Default value is 'true'"},
                    
                    # External key creation parameters
                    "oci_source_key_id": {"type": "string", "description": "The key ID which will be uploaded from the key source"},
                    "oci_source_key_tier": {"type": "string", "description": "Source Key-Tier of an existing sourceKey. Only 'hsm-luna' and 'local' source key-tiers are allowed"},
                    "oci_hyok_partition_id": {"type": "string", "description": "Luna slot partition ID - Required if 'hsm-luna' is selected as source_key_tier"},
                    "oci_hyok_vault_name": {"type": "string", "description": "Specify name for the OCI External Vault"},
                    
                    # Tenancy parameter
                    "tenancy": {"type": "string", "description": "Name or OCID or the tenancy. Required - in-case, 'connection' is not provided"},
                    
                    # JSON file parameters
                    "external_key_vault_json_file": {"type": "string", "description": "Parameters for creating external key vault"},
                    "oci_external_policy_jsonfile": {"type": "string", "description": "The key policy to attach to the OCI External Key"}
                }
            }
        },
        "action_requirements": {
            "external_vaults_create": {"required": ["connection_identifier", "oci_endpoint_url_hostname", "oci_issuer_id", "oci_compartment_id", "oci_external_vault_name", "oci_client_application_id"], "optional": ["enable_success_audit_event", "external_key_vault_json_file", "tenancy", "oci_external_policy_jsonfile", "oci_source_key_id", "oci_source_key_tier", "oci_hyok_partition_id", "oci_hyok_vault_name"]},
            "external_vaults_block_key": {"required": ["id"], "optional": []},
            "external_vaults_unblock_key": {"required": ["id"], "optional": []},
            "external_vaults_block_vault": {"required": ["id"], "optional": []},
            "external_vaults_unblock_vault": {"required": ["id"], "optional": []},
        }
    }


def build_external_vault_command(action: str, oci_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given OCI external vault operation."""
    cmd = ["cckm", "oci", "external-vaults"]
    
    # Extract the base operation name (remove 'external_vaults_' prefix)
    base_action = action.replace("external_vaults_", "")
    
    # Simple actions that only need --id parameter
    simple_actions = ["block_key", "unblock_key", "block_vault", "unblock_vault"]
    
    if base_action in simple_actions:
        cmd.extend([base_action.replace("_", "-"), "--id", oci_params["id"]])
        return cmd
    
    elif base_action == "create":
        cmd.append("create-external-vault")
        
        # Handle JSON file parameter first (overrides individual parameters)
        if "external_key_vault_json_file" in oci_params:
            cmd.extend(["--external-key-vault-json-file", oci_params["external_key_vault_json_file"]])
        else:
            # Required parameters
            cmd.extend(["--connection-identifier", oci_params["connection_identifier"]])
            cmd.extend(["--oci-endpoint-url-hostname", oci_params["oci_endpoint_url_hostname"]])
            cmd.extend(["--oci-issuer-id", oci_params["oci_issuer_id"]])
            cmd.extend(["--oci-compartment-id", oci_params["oci_compartment_id"]])
            cmd.extend(["--oci-external-vault-name", oci_params["oci_external_vault_name"]])
            cmd.extend(["--oci-client-application-id", oci_params["oci_client_application_id"]])
            
            # Optional parameters
            if "enable_success_audit_event" in oci_params:
                cmd.extend(["--enable-success-audit-event", str(oci_params["enable_success_audit_event"]).lower()])
            if "tenancy" in oci_params:
                cmd.extend(["--tenancy", oci_params["tenancy"]])
            if "oci_external_policy_jsonfile" in oci_params:
                cmd.extend(["--oci-external-policy-jsonfile", oci_params["oci_external_policy_jsonfile"]])
            if "oci_source_key_id" in oci_params:
                cmd.extend(["--oci-source-key-id", oci_params["oci_source_key_id"]])
            if "oci_source_key_tier" in oci_params:
                cmd.extend(["--oci-source-key-tier", oci_params["oci_source_key_tier"]])
            if "oci_hyok_partition_id" in oci_params:
                cmd.extend(["--oci-hyok-partition-id", oci_params["oci_hyok_partition_id"]])
            if "oci_hyok_vault_name" in oci_params:
                cmd.extend(["--oci-hyok-vault-name", oci_params["oci_hyok_vault_name"]])
        
    else:
        raise ValueError(f"Unsupported OCI external vaults action: {action}")
    
    return cmd 