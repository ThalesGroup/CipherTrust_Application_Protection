"""Azure Vaults operations for CCKM."""

from typing import Any, Dict


def get_vault_operations() -> Dict[str, Any]:
    """Return schema and action requirements for Azure vault operations."""
    return {
        "schema_properties": {
            "azure_vaults_params": {
                "type": "object",
                "properties": {
                    # Basic vault parameters
                    "vault_name": {"type": "string", "description": "Name for the vault"},
                    "subscription_id": {"type": "string", "description": "Azure subscription ID"},
                    "resource_group": {"type": "string", "description": "Azure resource group"},
                    "location": {"type": "string", "description": "Azure location"},
                    "sku": {"type": "string", "description": "Vault SKU (standard or premium)"},
                    
                    # Vault configuration
                    "tenant_id": {"type": "string", "description": "Azure tenant ID"},
                    "access_policies": {"type": "object", "description": "Access policies"},
                    "enabled_for_deployment": {"type": "boolean", "description": "Enable for deployment"},
                    "enabled_for_disk_encryption": {"type": "boolean", "description": "Enable for disk encryption"},
                    "enabled_for_template_deployment": {"type": "boolean", "description": "Enable for template deployment"},
                    
                    # Common parameters
                    "id": {"type": "string", "description": "Vault ID"},
                    "vault_id": {"type": "string", "description": "Vault ID"},
                    "tags": {"type": "object", "description": "Vault tags"},
                    
                    # List parameters
                    "limit": {"type": "integer", "description": "Maximum number of results"},
                    "skip": {"type": "integer", "description": "Number of results to skip"},
                    
                    # JSON file parameters
                    "azure_vaultcreate_jsonfile": {"type": "string", "description": "Azure vault create parameters in JSON file"},
                    "azure_vaultupdate_jsonfile": {"type": "string", "description": "Azure vault update parameters in JSON file"},
                    # Azure docs-specific JSON file parameters
                    "azure_vaults_jsonfile": {"type": "string", "description": "Azure vaults parameters in JSON file for add operation"},
                    "azure_vaults_add_jsonfile": {"type": "string", "description": "Azure add vaults parameters in JSON file (complete structure)"},
                    
                    # Connection parameters
                    "connection_identifier": {"type": "string", "description": "Connection identifier"},
                    "regions": {"type": "array", "items": {"type": "string"}, "description": "Azure regions"},
                    
                    # Job parameters
                    "enable_rotation": {"type": "boolean", "description": "Enable rotation job"},
                }
            }
        },
        "action_requirements": {
            "vaults_list": {"required": [], "optional": ["limit", "skip", "subscription_id"]},
            "vaults_get": {"required": ["id"], "optional": []},
            "vaults_create": {"required": ["vault_name", "subscription_id", "resource_group", "location"], "optional": ["sku", "tenant_id", "access_policies", "enabled_for_deployment", "enabled_for_disk_encryption", "enabled_for_template_deployment", "azure_vaultcreate_jsonfile"]},
            "vaults_add": {"required": ["subscription_id", "connection_identifier"], "optional": ["regions", "azure_vaults_jsonfile", "azure_vaults_add_jsonfile"]},
            "vaults_update": {"required": ["id"], "optional": ["access_policies", "enabled_for_deployment", "enabled_for_disk_encryption", "enabled_for_template_deployment", "azure_vaultupdate_jsonfile"]},
            "vaults_delete": {"required": ["id"], "optional": []},
            "vaults_get_vaults": {"required": ["subscription_id", "connection_identifier"], "optional": []},
            "vaults_get_managed_hsms": {"required": ["subscription_id", "connection_identifier"], "optional": []},
            "vaults_enable_rotation_job": {"required": ["id"], "optional": []},
            "vaults_disable_rotation_job": {"required": ["id"], "optional": []},
        }
    }


def build_vault_command(action: str, azure_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given Azure vault operation."""
    cmd = ["cckm", "azure", "vaults"]
    
    # Extract the base operation name (remove 'vaults_' prefix)
    base_action = action.replace("vaults_", "")
    
    # Simple actions that only need --id parameter
    simple_actions = ["get", "delete", "enable_rotation_job", "disable_rotation_job"]
    
    if base_action in simple_actions:
        cmd.extend([base_action.replace("_", "-"), "--id", azure_params["id"]])
        return cmd
    
    if base_action == "list":
        cmd.append("list")
        if "limit" in azure_params:
            cmd.extend(["--limit", str(azure_params["limit"])])
        if "skip" in azure_params:
            cmd.extend(["--skip", str(azure_params["skip"])])
        if "subscription_id" in azure_params:
            cmd.extend(["--subscription-id", azure_params["subscription_id"]])
            
    elif base_action == "create":
        cmd.append("create")
        # Required parameters
        cmd.extend(["--vault-name", azure_params["vault_name"]])
        cmd.extend(["--subscription-id", azure_params["subscription_id"]])
        cmd.extend(["--resource-group", azure_params["resource_group"]])
        cmd.extend(["--location", azure_params["location"]])
        
        # Optional parameters
        if "sku" in azure_params:
            cmd.extend(["--sku", azure_params["sku"]])
        if "tenant_id" in azure_params:
            cmd.extend(["--tenant-id", azure_params["tenant_id"]])
        if "enabled_for_deployment" in azure_params:
            cmd.extend(["--enabled-for-deployment", str(azure_params["enabled_for_deployment"]).lower()])
        if "enabled_for_disk_encryption" in azure_params:
            cmd.extend(["--enabled-for-disk-encryption", str(azure_params["enabled_for_disk_encryption"]).lower()])
        if "enabled_for_template_deployment" in azure_params:
            cmd.extend(["--enabled-for-template-deployment", str(azure_params["enabled_for_template_deployment"]).lower()])
        if "azure_vaultcreate_jsonfile" in azure_params:
            cmd.extend(["--azure-vaultcreate-jsonfile", azure_params["azure_vaultcreate_jsonfile"]])
            
    elif base_action == "add":
        cmd.append("add")
        cmd.extend(["--subscription-id", azure_params["subscription_id"]])
        cmd.extend(["--connection-identifier", azure_params["connection_identifier"]])
        if "regions" in azure_params:
            if isinstance(azure_params["regions"], list):
                cmd.extend(["--regions", ",".join(azure_params["regions"])])
            else:
                cmd.extend(["--regions", azure_params["regions"]])
        # Azure docs-specific JSON file parameters
        if "azure_vaults_jsonfile" in azure_params:
            cmd.extend(["--azure-vaults-jsonfile", azure_params["azure_vaults_jsonfile"]])
        if "azure_vaults_add_jsonfile" in azure_params:
            cmd.extend(["--azure-vaults-add-jsonfile", azure_params["azure_vaults_add_jsonfile"]])
            
    elif base_action == "update":
        cmd.extend(["update", "--id", azure_params["id"]])
        if "enabled_for_deployment" in azure_params:
            cmd.extend(["--enabled-for-deployment", str(azure_params["enabled_for_deployment"]).lower()])
        if "enabled_for_disk_encryption" in azure_params:
            cmd.extend(["--enabled-for-disk-encryption", str(azure_params["enabled_for_disk_encryption"]).lower()])
        if "enabled_for_template_deployment" in azure_params:
            cmd.extend(["--enabled-for-template-deployment", str(azure_params["enabled_for_template_deployment"]).lower()])
        if "azure_vaultupdate_jsonfile" in azure_params:
            cmd.extend(["--azure-vaultupdate-jsonfile", azure_params["azure_vaultupdate_jsonfile"]])
            
    elif base_action == "get_vaults":
        cmd.extend(["get-vaults", "--subscription-id", azure_params["subscription_id"]])
        if "connection_identifier" in azure_params:
            cmd.extend(["--connection-identifier", azure_params["connection_identifier"]])
        
    elif base_action == "get_managed_hsms":
        cmd.extend(["get-managed-hsms", "--subscription-id", azure_params["subscription_id"]])
        if "connection_identifier" in azure_params:
            cmd.extend(["--connection-identifier", azure_params["connection_identifier"]])
        
    else:
        raise ValueError(f"Unsupported Azure vaults action: {action}")
    
    return cmd 