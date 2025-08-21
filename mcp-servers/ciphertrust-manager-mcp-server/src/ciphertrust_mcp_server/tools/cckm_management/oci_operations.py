"""OCI operations for CCKM."""

from typing import Any, Dict, List
from .base import CCKMOperations
from .constants import CLOUD_OPERATIONS
from .oci import (
    get_key_operations, build_key_command,
    get_vault_operations, build_vault_command,
    get_compartment_operations, build_compartment_command,
    get_external_vault_operations, build_external_vault_command,
    get_issuer_operations, build_issuer_command,
    get_region_operations, build_region_command,
    get_tenancy_operations, build_tenancy_command,
    get_reports_operations, build_reports_command,
    OCISmartIDResolver
)


class OCIOperations(CCKMOperations):
    """Handles OCI operations for CCKM by building and executing ksctl commands."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported OCI operations."""
        return CLOUD_OPERATIONS["oci"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for OCI operations."""
        key_ops = get_key_operations()
        vault_ops = get_vault_operations()
        compartment_ops = get_compartment_operations()
        external_vault_ops = get_external_vault_operations()
        issuer_ops = get_issuer_operations()
        region_ops = get_region_operations()
        tenancy_ops = get_tenancy_operations()
        reports_ops = get_reports_operations()
        
        return {
            **key_ops.get("schema_properties", {}),
            **vault_ops.get("schema_properties", {}),
            **compartment_ops.get("schema_properties", {}),
            **external_vault_ops.get("schema_properties", {}),
            **issuer_ops.get("schema_properties", {}),
            **region_ops.get("schema_properties", {}),
            **tenancy_ops.get("schema_properties", {}),
            **reports_ops.get("schema_properties", {}),
        }

    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for OCI."""
        return {
            **get_key_operations()["action_requirements"],
            **get_vault_operations()["action_requirements"],
            **get_compartment_operations()["action_requirements"],
            **get_external_vault_operations()["action_requirements"],
            **get_issuer_operations()["action_requirements"],
            **get_region_operations()["action_requirements"],
            **get_tenancy_operations()["action_requirements"],
            **get_reports_operations()["action_requirements"],
        }

    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute OCI operation."""
        # Start with generic oci_params
        oci_params = params.get("oci_params", {}).copy()
        
        # Merge service-specific params into oci_params
        service_specific_keys = [
            "oci_keys_params",
            "oci_vaults_params",
            "oci_compartments_params",
            "oci_external_vaults_params",
            "oci_issuers_params",
            "oci_regions_params",
            "oci_tenancy_params",
            "oci_reports_params"
        ]
        
        for service_key in service_specific_keys:
            if service_key in params:
                oci_params.update(params[service_key])
        
        # Create smart resolver for ID resolution
        smart_resolver = OCISmartIDResolver(self)
        
        # If user supplied compartment name, resolve to OCID for key create/upload
        if action in ["keys_create", "keys_upload"]:
            if "oci_compartment_id" not in oci_params and "oci_compartment_name" in oci_params:
                try:
                    resolved_comp_ocid = await smart_resolver.resolve_compartment_name_to_ocid(
                        oci_params["oci_compartment_name"],
                        oci_params,
                        params.get("cloud_provider", "oci"),
                        context={"domain": params.get("domain"), "auth_domain": params.get("auth_domain")}
                    )
                    oci_params["oci_compartment_id"] = resolved_comp_ocid
                except Exception as e:
                    raise ValueError(f"Failed to resolve compartment name '{oci_params['oci_compartment_name']}' to OCID for {action}: {str(e)}")
            # Validate that we now have an ID for commands that require it
            if action == "keys_upload" and "oci_compartment_id" not in oci_params:
                raise ValueError("keys_upload requires either 'oci_compartment_id' or 'oci_compartment_name'. Name will be resolved automatically, but one must be provided.")
        
        # Handle vault name to OCID conversion for operations that need OCI vault OCIDs
        # These operations accept CCKM vault UUID or OCI vault OCID. If a display name is provided,
        # it will be resolved to the OCI vault OCID automatically.
        operations_needing_vault_ocid = ["keys_create", "keys_upload", "keys_sync_jobs_start", "keys_download_metadata"]
        if action in operations_needing_vault_ocid and "oci_vault" in oci_params:
            vault_identifier = oci_params["oci_vault"]
            # If it's a CCKM UUID, keep as-is (CLI accepts CCKM UUID for --oci-vault)
            if self._is_uuid(vault_identifier):
                pass
            # If it's not an OCID and not a UUID, resolve display name to OCID
            elif not smart_resolver.is_ocid(vault_identifier):
                try:
                    resolved_vault_ocid = await smart_resolver.resolve_vault_name_to_ocid_for_creation(
                        vault_identifier,
                        oci_params,
                        params.get("cloud_provider", "oci"),
                        context={"domain": params.get("domain"), "auth_domain": params.get("auth_domain")}
                    )
                    oci_params["oci_vault"] = resolved_vault_ocid
                except Exception as e:
                    raise ValueError(
                        f"Failed to resolve vault '{vault_identifier}' to OCID for {action}: {str(e)}"
                    )
        
        # Handle key size conversion for operations that create or upload keys
        operations_needing_size_conversion = ["keys_create", "keys_upload"]
        if action in operations_needing_size_conversion and "length" in oci_params and "oci_algorithm" in oci_params:
            try:
                original_length = oci_params["length"]
                algorithm = oci_params["oci_algorithm"]
                converted_length = smart_resolver.convert_key_size(algorithm, original_length)
                oci_params["length"] = converted_length
            except Exception as e:
                raise ValueError(f"Key size conversion failed: {str(e)}")
        
        # Check if this operation needs ID resolution (for vault operations, key operations, etc.)
        if self._needs_id_resolution(action, oci_params):
            await self._resolve_ids(action, oci_params, smart_resolver, params.get("cloud_provider", "oci"), params)
        
        # Validate vault delete operation has required parameters
        if action == "vaults_delete":
            if "id" not in oci_params and "vault_name" not in oci_params:
                raise ValueError("vaults_delete operation requires either 'id' or 'vault_name' parameter")
            if "id" not in oci_params:
                raise ValueError("Smart ID resolution failed: could not resolve vault_name to id")
        
        # Route to appropriate command builder based on operation type
        if action.startswith("keys_"):
            cmd = build_key_command(action, oci_params)
        elif action.startswith("vaults_"):
            cmd = build_vault_command(action, oci_params)
        elif action.startswith("compartments_"):
            cmd = build_compartment_command(action, oci_params)
        elif action.startswith("external_vaults_"):
            cmd = build_external_vault_command(action, oci_params)
        elif action.startswith("issuers_"):
            cmd = build_issuer_command(action, oci_params)
        elif action.startswith("regions_"):
            cmd = build_region_command(action, oci_params)
        elif action.startswith("tenancy_"):
            cmd = build_tenancy_command(action, oci_params)
        elif action.startswith("reports_"):
            cmd = build_reports_command(action, oci_params)
        else:
            raise ValueError(f"Unsupported OCI action: {action}")
        
        # Execute command
        # Pass domain parameters to execute_command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result
    
    def _needs_id_resolution(self, action: str, oci_params: Dict[str, Any]) -> bool:
        """Check if this operation needs ID resolution."""
        id_operations = [
            "keys_get", "keys_delete", "keys_enable", "keys_disable", "keys_refresh", 
            "keys_restore", "keys_schedule_deletion", "keys_cancel_deletion", 
            "keys_change_compartment", "keys_enable_auto_rotation", "keys_disable_auto_rotation", 
            "keys_delete_backup", "keys_add_version", "keys_get_version", "keys_list_version",
            "keys_schedule_deletion_version", "keys_cancel_schedule_deletion_version", "keys_update",
            "vaults_get", "vaults_delete", "compartments_get", "compartments_delete",
            "external_vaults_block_key", "external_vaults_unblock_key", "external_vaults_block_vault", "external_vaults_unblock_vault",
            "issuers_get", "issuers_update", "issuers_delete",
            "tenancy_get", "tenancy_delete",
            "reports_get", "reports_download", "reports_delete", "reports_get_report"
        ]
        
        # Check for vault operations with vault_name instead of id
        if action.startswith("vaults_") and "vault_name" in oci_params:
            return True
        
        # Check for regular ID resolution
        if action in id_operations and "id" in oci_params:
            # For vault operations, check if the id is actually a vault name that needs resolution
            if action.startswith("vaults_"):
                vault_id = oci_params["id"]
                # If it's not a UUID and not an OCID, treat it as a vault name
                if not self._is_uuid(vault_id) and not self._is_ocid(vault_id):
                    return True
            return True
        
        return False
    
    def _is_uuid(self, identifier: str) -> bool:
        """Check if identifier is a UUID."""
        import re
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
        return bool(uuid_pattern.match(identifier))
    
    def _is_ocid(self, identifier: str) -> bool:
        """Check if identifier is an OCID."""
        return identifier.startswith("ocid1.")
    
    async def _resolve_ids(self, action: str, oci_params: Dict[str, Any], smart_resolver: OCISmartIDResolver, cloud_provider: str, params: Dict[str, Any] = None):
        """Resolve IDs in the parameters."""
        # Create context for smart resolver
        context = {}
        if params:
            if params.get("domain"):
                context["domain"] = params["domain"]
            if params.get("auth_domain"):
                context["auth_domain"] = params["auth_domain"]
        
        # Handle vault operations where user might provide vault_name instead of id
        if action.startswith("vaults_") and "vault_name" in oci_params and "id" not in oci_params:
            # User provided vault_name, resolve it to id
            vault_name = oci_params["vault_name"]
            resolved_id = await smart_resolver.resolve_vault_id(vault_name, oci_params, cloud_provider, context)
            oci_params["id"] = resolved_id
            # Remove vault_name from params since we now have the resolved id
            oci_params.pop("vault_name", None)
        
        # Handle regular ID resolution
        if "id" in oci_params:
            original_id = oci_params["id"]
            
            if action.startswith("keys_"):
                resolved_id = await smart_resolver.resolve_key_id(original_id, oci_params, cloud_provider, context)
            elif action.startswith("vaults_"):
                # For vault operations, check if the id is actually a vault name
                if not self._is_uuid(original_id) and not self._is_ocid(original_id):
                    # Treat it as a vault name and resolve it
                    resolved_id = await smart_resolver.resolve_vault_id(original_id, oci_params, cloud_provider, context)
                else:
                    # It's already a valid ID, just resolve it normally
                    resolved_id = await smart_resolver.resolve_vault_id(original_id, oci_params, cloud_provider, context)
            elif action.startswith("compartments_"):
                resolved_id = await smart_resolver.resolve_compartment_id(original_id, oci_params, cloud_provider, context)
            elif action.startswith("external_vaults_"):
                # For external vault operations, the ID is typically an external key ID
                resolved_id = original_id  # No special resolution needed for external key IDs
            elif action.startswith("issuers_"):
                resolved_id = original_id  # No special resolution needed for issuer IDs
            elif action.startswith("tenancy_"):
                resolved_id = original_id  # No special resolution needed for tenancy IDs
            elif action.startswith("reports_"):
                resolved_id = original_id  # No special resolution needed for report job IDs
            else:
                resolved_id = original_id
            
            oci_params["id"] = resolved_id 