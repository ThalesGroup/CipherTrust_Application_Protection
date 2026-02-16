"""Azure operations for CCKM."""

from typing import Any, Dict, List
from .base import CCKMOperations
from .constants import CLOUD_OPERATIONS
from .azure.smart_id_resolver import AzureSmartIDResolver
from .azure import (
    get_key_operations, build_key_command,
    get_certificate_operations, build_certificate_command,
    get_vault_operations, build_vault_command,
    get_secret_operations, build_secret_command,
    get_subscription_operations, get_report_operations, get_bulkjob_operations,
    build_common_command
)


class AzureOperations(CCKMOperations):
    """Handles Azure operations for CCKM by building and executing ksctl commands."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported Azure operations."""
        return CLOUD_OPERATIONS["azure"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for Azure operations."""
        key_ops = get_key_operations()
        cert_ops = get_certificate_operations()
        vault_ops = get_vault_operations()
        secret_ops = get_secret_operations()
        sub_ops = get_subscription_operations()
        report_ops = get_report_operations()
        bulkjob_ops = get_bulkjob_operations()
        
        return {
            **key_ops.get("schema_properties", {}),
            **cert_ops.get("schema_properties", {}),
            **vault_ops.get("schema_properties", {}),
            **secret_ops.get("schema_properties", {}),
            **sub_ops.get("schema_properties", {}),
            **report_ops.get("schema_properties", {}),
            **bulkjob_ops.get("schema_properties", {}),
        }

    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for Azure."""
        return {
            **get_key_operations()["action_requirements"],
            **get_certificate_operations()["action_requirements"],
            **get_vault_operations()["action_requirements"],
            **get_secret_operations()["action_requirements"],
            **get_subscription_operations()["action_requirements"],
            **get_report_operations()["action_requirements"],
            **get_bulkjob_operations()["action_requirements"],
        }

    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute Azure operation."""
        # Get merged parameters for this cloud provider
        azure_params = params.get("azure_params", {})
        
        # Merge service-specific parameters into azure_params
        service_keys = ["azure_keys_params", "azure_certificates_params", "azure_vaults_params", 
                       "azure_secrets_params", "azure_subscriptions_params", "azure_reports_params", 
                       "azure_bulkjob_params", "azure_custom_key_stores_params", "azure_logs_params"]
        
        for service_key in service_keys:
            if service_key in params:
                azure_params.update(params[service_key])
        
        # Create smart resolver for ID resolution
        smart_resolver = AzureSmartIDResolver(self)
        
        # Set subscription context in smart resolver for better resolution
        if action.startswith("vaults_") and "subscription_id" in azure_params and "connection_identifier" in azure_params:
            smart_resolver.set_subscription_context(
                azure_params["subscription_id"], 
                azure_params["connection_identifier"]
            )
        
        # Check if this operation needs ID resolution
        if self._needs_id_resolution(action, azure_params):
            await self._resolve_ids(action, azure_params, smart_resolver, params.get("cloud_provider", "azure"))
        
        # Route to appropriate command builder based on operation type
        if action.startswith("keys_"):
            cmd = build_key_command(action, azure_params)
        elif action.startswith("certificates_"):
            cmd = build_certificate_command(action, azure_params)
        elif action.startswith("vaults_"):
            cmd = build_vault_command(action, azure_params)
        elif action.startswith("secrets_"):
            cmd = build_secret_command(action, azure_params)
        elif action.startswith(("subscriptions_", "reports_", "bulkjob_")):
            cmd = build_common_command(action, azure_params)
        elif action.startswith("cloud_key_backup_"):
            # Handle cloud key backup operations (these are key-related)
            cmd = ["cckm", "azure", "keys", "cloud-key-backup"]
            base_action = action.replace("cloud_key_backup_", "")
            
            if base_action == "list":
                cmd.append("list")
                if "limit" in azure_params:
                    cmd.extend(["--limit", str(azure_params["limit"])])
                if "skip" in azure_params:
                    cmd.extend(["--skip", str(azure_params["skip"])])
            elif base_action == "get":
                cmd.extend(["get", "--id", azure_params["backup_id"]])
            elif base_action == "create":
                cmd.extend(["create", "--id", azure_params["key_id"]])
            elif base_action == "update":
                cmd.extend(["update", "--id", azure_params["key_id"], "--backup-id", azure_params["backup_id"]])
            elif base_action == "delete":
                cmd.extend(["delete", "--id", azure_params["backup_id"]])
            else:
                raise ValueError(f"Unsupported cloud key backup action: {base_action}")
        else:
            raise ValueError(f"Unsupported Azure action: {action}")
        
        # Execute command
        # Pass domain parameters to execute_command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result
    
    def _needs_id_resolution(self, action: str, azure_params: Dict[str, Any]) -> bool:
        """Check if this operation needs ID resolution."""
        id_operations = [
            "keys_get", "keys_update", "keys_delete", "keys_enable", "keys_disable", 
            "keys_rotate", "keys_backup", "keys_export", "keys_hard_delete", "keys_recover", 
            "keys_upload", "keys_enable_backup_job", "keys_enable_rotation_job", "keys_delete_backup",
            "certificates_get", "certificates_update", "certificates_delete", "certificates_recover", 
            "certificates_hard_delete", "certificates_soft_delete",
            "secrets_get", "secrets_update", "secrets_delete", "secrets_recover",
            "vaults_get", "vaults_update", "vaults_delete", "vaults_enable_rotation_job", "vaults_disable_rotation_job"
        ]
        
        return action in id_operations and "id" in azure_params
    
    async def _resolve_ids(self, action: str, azure_params: Dict[str, Any], smart_resolver: AzureSmartIDResolver, cloud_provider: str):
        """Resolve IDs in the parameters."""
        if "id" in azure_params:
            original_id = azure_params["id"]
            
            if action.startswith("keys_"):
                resolved_id = await smart_resolver.resolve_key_id(original_id, azure_params, cloud_provider)
            elif action.startswith("certificates_"):
                resolved_id = await smart_resolver.resolve_certificate_id(original_id, azure_params, cloud_provider)
            elif action.startswith("vaults_"):
                resolved_id = await smart_resolver.resolve_vault_id(original_id, azure_params, cloud_provider)
            elif action.startswith("secrets_"):
                resolved_id = await smart_resolver.resolve_secret_id(original_id, azure_params, cloud_provider)
            else:
                resolved_id = original_id
            
            azure_params["id"] = resolved_id 