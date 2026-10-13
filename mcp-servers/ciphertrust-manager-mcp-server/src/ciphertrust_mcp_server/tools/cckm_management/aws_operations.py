"""Manages AWS operations for CipherTrust Cloud Key Manager (CCKM).

This module provides the `AWSOperations` class, which handles various AWS-related
operations within CCKM. It is responsible for building and executing `ksctl` commands
for managing keys, custom key stores, IAM, KMS, reports, and bulk jobs.
"""
from typing import Any, Dict, List
from .base import CCKMOperations
from .constants import CLOUD_OPERATIONS
from .aws import (
    get_key_operations, build_key_command,
    get_kms_operations, build_kms_command,
    get_iam_operations, build_iam_command,
    get_reports_operations, build_reports_command,
    get_bulkjob_operations, build_bulkjob_command,
    get_custom_key_stores_operations, build_custom_key_stores_command,
    get_logs_operations, build_logs_command,
    create_smart_resolver
)

class AWSOperations(CCKMOperations):
    """Handles AWS operations for CCKM by building and executing ksctl commands."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported AWS operations."""
        return CLOUD_OPERATIONS["aws"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for AWS operations."""
        key_ops = get_key_operations()
        kms_ops = get_kms_operations()
        iam_ops = get_iam_operations()
        reports_ops = get_reports_operations()
        bulkjob_ops = get_bulkjob_operations()
        custom_key_stores_ops = get_custom_key_stores_operations()
        logs_ops = get_logs_operations()
        return {
            **key_ops.get("schema_properties", {}),
            **kms_ops.get("schema_properties", {}),
            **iam_ops.get("schema_properties", {}),
            **reports_ops.get("schema_properties", {}),
            **bulkjob_ops.get("schema_properties", {}),
            **custom_key_stores_ops.get("schema_properties", {}),
            **logs_ops.get("schema_properties", {})
        }

    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for AWS."""
        return {
            **get_key_operations()["action_requirements"],
            **get_kms_operations()["action_requirements"],
            **get_iam_operations()["action_requirements"],
            **get_reports_operations()["action_requirements"],
            **get_bulkjob_operations()["action_requirements"],
            **get_custom_key_stores_operations()["action_requirements"],
            **get_logs_operations()["action_requirements"],
        }

    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute AWS operation."""
        # Start with generic aws_params
        aws_params = params.get("aws_params", {}).copy()
        
        # Merge service-specific params into aws_params
        service_specific_keys = [
            "aws_kms_params",
            "aws_iam_params", 
            "aws_key_params",
            "aws_keys_params",
            "aws_reports_params",
            "aws_bulkjob_params",
            "aws_custom_key_stores_params",
            "aws_logs_params"
        ]
        
        for service_key in service_specific_keys:
            if service_key in params:
                aws_params.update(params[service_key])
        
        cmd = []
        
        # Create smart resolver for ID resolution
        smart_resolver = create_smart_resolver(self)
        
        # Check if this operation needs key ID resolution
        if self._needs_key_id_resolution(action, aws_params):
            await self._resolve_key_ids(action, aws_params, smart_resolver, params.get("cloud_provider", "aws"))
        
        # Route to appropriate command builder based on operation type
        if action in ["keys_list", "keys_get", "keys_create", "keys_delete", "keys_enable", "keys_disable", "keys_rotate", "keys_add_alias", "keys_delete_alias", 
                      "keys_add_tags", "keys_remove_tags", "keys_schedule_deletion", "keys_cancel_deletion", "keys_import_material", "keys_delete_material", 
                      "keys_upload", "keys_download_public_key", "keys_policy", "keys_replicate_key", "keys_block", "keys_unblock", "keys_enable_auto_rotation", 
                      "keys_disable_auto_rotation", "keys_enable_rotation_job", "keys_disable_rotation_job", "keys_list_rotations", "keys_verify_alias",
                      "keys_link", "keys_update_description", "keys_update_primary_region", "keys_rotate_material", "keys_download_metadata",
                      "keys_create_aws_cloudhsm", "keys_create_aws_hyok", "keys_policy_template_create", "keys_policy_template_delete",
                      "keys_policy_template_get", "keys_policy_template_list", "keys_policy_template_update", "keys_sync_jobs_start", "keys_sync_jobs_cancel",
                      "keys_sync_jobs_get", "keys_sync_jobs_status"]:
            # Extract the base operation name (remove 'keys_' prefix)
            base_action = action.replace("keys_", "")
            cmd = build_key_command(base_action, aws_params)
        elif action.startswith("kms_"):
            cmd = build_kms_command(action, aws_params)
        elif action.startswith("iam_"):
            cmd = build_iam_command(action, aws_params)
        elif action.startswith("reports_"):
            cmd = build_reports_command(action, aws_params)
        elif action.startswith("bulkjob_"):
            cmd = build_bulkjob_command(action, aws_params)
        elif action.startswith("custom_key_stores_"):
            cmd = build_custom_key_stores_command(action, aws_params)
        elif action == "logs_get_groups":
            cmd = build_logs_command("get_log_groups", aws_params)
        else:
            raise ValueError(f"Unsupported AWS action: {action}")
            
        # Pass domain parameters to execute_command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _needs_key_id_resolution(self, action: str, aws_params: Dict[str, Any]) -> bool:
        """Check if the operation needs key ID resolution."""
        # Operations that require a key ID
        id_required_actions = [
            "keys_get", "keys_delete", "keys_enable", "keys_disable", "keys_rotate",
            "keys_add_alias", "keys_delete_alias", "keys_add_tags", "keys_remove_tags",
            "keys_schedule_deletion", "keys_cancel_deletion", "keys_import_material",
            "keys_delete_material", "keys_download_public_key", "keys_policy",
            "keys_replicate_key", "keys_block", "keys_unblock", "keys_enable_auto_rotation",
            "keys_disable_auto_rotation", "keys_enable_rotation_job", "keys_disable_rotation_job",
            "keys_list_rotations", "keys_verify_alias", "keys_link", "keys_update_description",
            "keys_update_primary_region", "keys_rotate_material", "keys_download_metadata",
            "keys_policy_template_delete", "keys_policy_template_get", "keys_policy_template_update",
            "keys_sync_jobs_get", "keys_sync_jobs_cancel"
        ]
        
        # Bulk job operations that need key ID resolution
        bulkjob_id_required_actions = [
            "bulkjob_create"
        ]
        
        if action in id_required_actions:
            # Check if the operation has an 'id' parameter that needs resolution
            if "id" in aws_params:
                from .aws import SmartIDResolver
                resolver = SmartIDResolver(self)
                return resolver.needs_resolution(aws_params["id"])
        
        elif action in bulkjob_id_required_actions:
            # Check if the operation has a 'bulkjob_keys_id' parameter that needs resolution
            if "bulkjob_keys_id" in aws_params:
                from .aws import SmartIDResolver
                resolver = SmartIDResolver(self)
                # Check if any of the comma-separated key IDs need resolution
                key_ids = aws_params["bulkjob_keys_id"].split(",")
                for key_id in key_ids:
                    if resolver.needs_resolution(key_id.strip()):
                        return True
        
        return False
    
    async def _resolve_key_ids(self, action: str, aws_params: Dict[str, Any], smart_resolver, cloud_provider: str):
        """Resolve key IDs using the smart resolver."""
        if "id" in aws_params:
            try:
                resolved_id = await smart_resolver.resolve_key_id(
                    aws_params["id"], 
                    cloud_provider, 
                    aws_params
                )
                aws_params["id"] = resolved_id
            except Exception as e:
                raise ValueError(f"Failed to resolve key ID for operation {action}: {str(e)}")
        
        elif "bulkjob_keys_id" in aws_params:
            try:
                # Split the comma-separated key IDs
                key_ids = aws_params["bulkjob_keys_id"].split(",")
                resolved_key_ids = []
                
                for key_id in key_ids:
                    key_id = key_id.strip()
                    if smart_resolver.needs_resolution(key_id):
                        # Resolve this key ID
                        resolved_id = await smart_resolver.resolve_key_id(
                            key_id, 
                            cloud_provider, 
                            aws_params
                        )
                        resolved_key_ids.append(resolved_id)
                    else:
                        # No resolution needed, keep as is
                        resolved_key_ids.append(key_id)
                
                # Update the bulkjob_keys_id with resolved IDs
                aws_params["bulkjob_keys_id"] = ",".join(resolved_key_ids)
                
            except Exception as e:
                raise ValueError(f"Failed to resolve bulk job key IDs for operation {action}: {str(e)}") 