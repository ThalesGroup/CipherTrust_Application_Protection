"""Google Cloud operations for CCKM."""

from typing import Any, Dict, List
import asyncio
import json
import re
from .base import CCKMOperations
from .constants import CLOUD_OPERATIONS
from .google import (
    get_key_operations, build_key_command,
    get_keyring_operations, build_keyring_command,
    get_project_operations, build_project_command,
    get_location_operations, build_location_command,
    get_reports_operations, build_reports_command
)
from .google.smart_id_resolver import create_google_smart_resolver


class GoogleOperations(CCKMOperations):
    """
    Google Cloud Key Management operations for CCKM.
    
    Supports comprehensive Google Cloud KMS operations including:
    - Keys: Create, manage, rotate, and synchronize/refresh encryption keys
    - Key Rings: Manage key ring containers and access controls  
    - Projects: Manage GCP project integrations
    - Locations: Query available GCP regions and zones
    - Reports: Generate and download key usage and compliance reports
    
    Features smart ID resolution - automatically converts key names and partial paths 
    to full Google Cloud resource URLs for seamless operation.
    
    Note: 'synchronize' and 'refresh' are equivalent terms for key synchronization operations.
    """
    
    def get_operations(self) -> List[str]:
        """Return list of supported Google Cloud operations."""
        return CLOUD_OPERATIONS["google"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for Google Cloud operations."""
        return {
            **get_key_operations()["schema_properties"],
            **get_keyring_operations()["schema_properties"],
            **get_project_operations()["schema_properties"],
            **get_location_operations()["schema_properties"],
            **get_reports_operations()["schema_properties"]
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action requirements for Google Cloud operations."""
        return {
            **get_key_operations()["action_requirements"],
            **get_keyring_operations()["action_requirements"],
            **get_project_operations()["action_requirements"],
            **get_location_operations()["action_requirements"],
            **get_reports_operations()["action_requirements"]
        }

    def is_uuid(self, identifier: str) -> bool:
        """Check if the identifier is a UUID."""
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, identifier.lower()))

    async def _get_connection_uuid_by_name(self, connection_name: str) -> str:
        """Get connection UUID by name using connection management."""
        try:
            # Use connection management to get connection details
            cmd = ["connectionmgmt", "gcp", "get", "--id", connection_name]
            result = self.execute_command(cmd)
            
            if isinstance(result, str):
                result_data = json.loads(result)
            else:
                result_data = result
            
            # Extract the connection ID from the response
            if "data" in result_data:
                return result_data["data"].get("id", connection_name)
            elif "id" in result_data:
                return result_data["id"]
            else:
                return connection_name
                
        except Exception:
            # If we can't get the UUID, return the original name
            return connection_name

    async def _resolve_connection_identifier(self, connection_identifier: str) -> str:
        """Resolve connection identifier to UUID if it's a name."""
        # If it's already a UUID, return as is
        if self.is_uuid(connection_identifier):
            return connection_identifier
        
        # If it's a name, try to get the UUID
        return await self._get_connection_uuid_by_name(connection_identifier)

    def _needs_key_id_resolution(self, action: str, google_params: Dict[str, Any]) -> bool:
        """Check if this operation needs key ID resolution."""
        # Operations that work with key IDs and might need resolution  
        key_operations = [
            "keys_get", "keys_update", "keys_enable", "keys_disable", "keys_rotate", 
            "keys_enable_auto_rotation", "keys_disable_auto_rotation", "keys_refresh", 
            "keys_download_public_key", "keys_get_update_all_versions_status", 
            "keys_re_import", "keys_update_all_versions_jobs", "keys_synchronize",
            "keys_add_version", "keys_list_version", "keys_get_version", 
            "keys_enable_version", "keys_disable_version", "keys_refresh_version", 
            "keys_synchronize_version", "keys_schedule_destroy", "keys_cancel_schedule_destroy",
            "keys_policy", "keys_policy_get", "keys_policy_update"
        ]
        
        if action in key_operations and "id" in google_params:
            return True
        
        return False

    def _needs_keyring_id_resolution(self, action: str, google_params: Dict[str, Any]) -> bool:
        """Check if this operation needs keyring ID resolution."""
        # Operations that work with keyring IDs and might need resolution
        keyring_id_operations = [
            "keyrings_get", "keyrings_delete", "keyrings_update", "keyrings_update_acls"
        ]
        
        if action in keyring_id_operations and "id" in google_params:
            return True
        
        return False

    def _needs_keyring_list_resolution(self, action: str, google_params: Dict[str, Any]) -> bool:
        """Check if this operation needs keyring list resolution."""
        # Operations that work with keyring lists and might need resolution
        keyring_list_operations = [
            "keys_sync_jobs_status"
        ]
        
        if action in keyring_list_operations and "key_rings" in google_params:
            return True
        
        return False

    def _needs_keyring_name_resolution(self, action: str, google_params: Dict[str, Any]) -> bool:
        """Check if this operation needs keyring name resolution."""
        # Operations that work with keyring names and might need resolution
        keyring_name_operations = [
            "keyrings_add_key_rings"
        ]
        
        if action in keyring_name_operations and "keyring_name" in google_params:
            return True
        
        return False

    def _needs_keyring_param_resolution(self, action: str, google_params: Dict[str, Any]) -> bool:
        """Check if this operation needs keyring parameter resolution."""
        # Operations that work with keyring parameters and might need resolution
        keyring_param_operations = [
            "keys_create", "keys_list", "keys_upload", "keys_download_metadata"
        ]
        
        if action in keyring_param_operations and "key_ring" in google_params:
            return True
        
        return False

    def _needs_keyring_sync_resolution(self, action: str, google_params: Dict[str, Any]) -> bool:
        """Check if this operation needs keyring synchronization resolution."""
        # Operations that work with keyring synchronization and might need resolution
        sync_operations = [
            "keys_sync_jobs_start"
        ]
        
        if action in sync_operations and "key_rings" in google_params:
            return True
        
        return False

    async def _resolve_key_ids(self, action: str, google_params: Dict[str, Any], smart_resolver, cloud_provider: str):
        """Resolve key IDs using the smart resolver."""
        if "id" in google_params:
            # Extract context from google_params for resolution
            context_params = {}
            for key in ["project_id", "location", "connection_identifier", "key_ring"]:
                if key in google_params:
                    context_params[key] = google_params[key]
            
            # Resolve the key ID
            resolved_id = await smart_resolver.resolve_key_id(
                google_params["id"], cloud_provider, context_params
            )
            google_params["id"] = resolved_id

    async def _resolve_keyring_ids(self, action: str, google_params: Dict[str, Any], smart_resolver, cloud_provider: str):
        """Resolve keyring IDs using the smart resolver."""
        if "id" in google_params:
            # Extract context from google_params for resolution
            context_params = {}
            for key in ["project_id", "location", "connection_identifier"]:
                if key in google_params:
                    context_params[key] = google_params[key]
            
            # Resolve the keyring ID
            resolved_id = await smart_resolver.resolve_keyring_id(
                google_params["id"], cloud_provider, context_params
            )
            google_params["id"] = resolved_id

    async def _resolve_keyring_params(self, action: str, google_params: Dict[str, Any], smart_resolver, cloud_provider: str):
        """Resolve key_ring parameters using the smart resolver."""
        if "key_ring" in google_params:
            # Extract context from google_params for resolution
            context_params = {}
            for key in ["project_id", "location", "connection_identifier"]:
                if key in google_params:
                    context_params[key] = google_params[key]
            
            # Resolve the keyring name to UUID
            resolved_keyring = await smart_resolver.resolve_keyring_id(
                google_params["key_ring"], cloud_provider, context_params
            )
            google_params["key_ring"] = resolved_keyring

    async def _resolve_keyring_lists(self, action: str, google_params: Dict[str, Any], smart_resolver, cloud_provider: str):
        """Resolve keyring lists using the smart resolver."""
        if action == "keyrings_list":
            # Special case: handled by _handle_keyrings_list_with_connection_resolution
            return await self._handle_keyrings_list_with_connection_resolution(google_params)
        
        if "key_rings" in google_params:
            # Extract context from google_params for resolution
            context_params = {}
            for key in ["project_id", "location"]:
                if key in google_params:
                    context_params[key] = google_params[key]
            
            # Resolve the keyring list
            resolved_list = await smart_resolver.resolve_keyring_list(
                google_params["key_rings"], cloud_provider, context_params
            )
            google_params["key_rings"] = resolved_list

    async def _resolve_keyring_names(self, action: str, google_params: Dict[str, Any], smart_resolver, cloud_provider: str):
        """Resolve keyring names using the smart resolver."""
        if "keyring_name" in google_params:
            # Extract context from google_params for resolution
            context_params = {}
            for key in ["project_id", "location", "connection_identifier"]:
                if key in google_params:
                    context_params[key] = google_params[key]
            
            # Resolve the keyring name
            resolved_name = await smart_resolver.resolve_keyring_id(
                google_params["keyring_name"], cloud_provider, context_params
            )
            google_params["keyring_name"] = resolved_name

    async def _resolve_keyring_sync(self, action: str, google_params: Dict[str, Any], smart_resolver, cloud_provider: str):
        """Resolve keyring names for synchronization operations using the smart resolver."""
        if "key_rings" in google_params:
            # Extract context from google_params for resolution
            context_params = {}
            for key in ["project_id", "location", "connection_identifier"]:
                if key in google_params:
                    context_params[key] = google_params[key]
            
            # Check if we have simple keyring names without location that need special handling
            keyring_list = google_params["key_rings"]
            keyring_items = [item.strip() for item in keyring_list.split(',')]
            has_simple_names_without_location = False
            
            for item in keyring_items:
                # Check if it's a simple keyring name (no slashes, not a full resource URL)
                if (not item.startswith('projects/') and 
                    '/' not in item and 
                    "location" not in context_params):
                    has_simple_names_without_location = True
                    break
            
            if has_simple_names_without_location and "project_id" in context_params:
                # Handle simple keyring names without location by searching across locations
                resolved_keyrings = []
                
                for item in keyring_items:
                    # Skip if it's already a full resource URL
                    if item.startswith('projects/'):
                        resolved_keyrings.append(item)
                        continue
                    
                    # Skip if it has location prefix (will be handled by resolve_keyring_list)
                    if '/' in item and not item.startswith('projects/'):
                        resolved_keyrings.append(item)
                        continue
                    
                    # For simple keyring names, try to find across locations
                    try:
                        found_keyring = await smart_resolver.find_keyring_across_locations(
                            item, 
                            context_params["project_id"],
                            context_params.get("connection_identifier")
                        )
                        if found_keyring:
                            resolved_keyrings.append(found_keyring)
                        else:
                            # If not found, try with 'global' location as fallback
                            full_resource_name = smart_resolver.construct_full_resource_name(
                                'keyRings', 
                                context_params["project_id"], 
                                'global', 
                                item
                            )
                            resolved_keyrings.append(full_resource_name)
                    except Exception:
                        # If resolution fails, try with 'global' location as fallback
                        full_resource_name = smart_resolver.construct_full_resource_name(
                            'keyRings', 
                            context_params["project_id"], 
                            'global', 
                            item
                        )
                        resolved_keyrings.append(full_resource_name)
                
                google_params["key_rings"] = ','.join(resolved_keyrings)
            else:
                # Use the existing resolve_keyring_list method for all other cases
                resolved_list = await smart_resolver.resolve_keyring_list(
                    google_params["key_rings"], cloud_provider, context_params
                )
                google_params["key_rings"] = resolved_list

    def _needs_version_resolution(self, action: str, google_params: Dict[str, Any]) -> bool:
        """Check if this operation needs version resolution."""
        # Operations that work with versions and might need resolution
        version_operations = [
            "keys_get_version", "keys_enable_version", "keys_disable_version",
            "keys_refresh_version", "keys_synchronize_version", "keys_schedule_destroy"
        ]
        
        if action in version_operations and "version" in google_params:
            return True
        
        return False

    async def _resolve_versions_and_execute(self, action: str, google_params: Dict[str, Any]) -> Any:
        """Resolve versions and execute the operation."""
        # For version operations, we need to get the key first to find available versions
        if "id" not in google_params:
            raise ValueError("Key ID is required for version operations")
        
        # Get the key to find available versions
        key_cmd = build_key_command("keys_get", {"id": google_params["id"]})
        key_result = self.execute_command(key_cmd)
        
        if isinstance(key_result, str):
            key_data = json.loads(key_result)
        else:
            key_data = key_result
        
        # Extract versions from key data
        versions = key_data.get("versions", [])
        if not versions:
            return {"error": "No versions found for this key"}
        
        # Find the requested version
        requested_version = google_params.get("version")
        if not requested_version:
            return {"error": "Version parameter is required"}
        
        # Try to match version by name or number
        for version in versions:
            if (version.get("name") == requested_version or 
                str(version.get("version_number")) == requested_version or
                version.get("id") == requested_version):
                # Update the parameters with the correct version ID
                google_params["version"] = version.get("id", requested_version)
                break
        
        # Now execute the original operation with resolved version
        cmd = build_key_command(action, google_params)
        return self.execute_command(cmd)

    async def _handle_keyrings_list_with_connection_resolution(self, google_params: Dict[str, Any]) -> Any:
        """Handle keyrings list with smart connection resolution and combination."""
        debug_info = []
        
        # Default behavior: show all keyrings without filters
        if not google_params.get("connection_identifier"):
            # No connection filter - show all keyrings with any other filters
            cmd = build_keyring_command("keyrings_list", google_params)
            debug_info.append(f"DEBUG: Executing command: {' '.join(cmd)}")
            result = self.execute_command(cmd)
            
            if isinstance(result, dict):
                # Result is a dict with status, stdout, stderr - parse stdout
                if result.get("stdout"):
                    result_data = json.loads(result["stdout"])
                else:
                    result_data = result.get("data", {})
            elif isinstance(result, str):
                result_data = json.loads(result)
            else:
                result_data = result
            
            debug_info.append(f"DEBUG: Command returned {result_data.get('total', 0)} results")
            result_data["debug_info"] = debug_info
            return result_data
        
        # Connection identifier provided - get results from both connection name AND UUID
        connection_identifier = google_params["connection_identifier"]
        all_results = []
        
        # First attempt: try with connection name
        try:
            cmd = build_keyring_command("keyrings_list", google_params)
            debug_info.append(f"DEBUG: First attempt - Executing command: {' '.join(cmd)}")
            result = self.execute_command(cmd)
            debug_info.append(f"DEBUG: Raw result type: {type(result)}")
            debug_info.append(f"DEBUG: Raw result preview: {str(result)[:200]}...")
            
            if isinstance(result, dict):
                # Result is a dict with status, stdout, stderr - parse stdout
                if result.get("stdout"):
                    result_data = json.loads(result["stdout"])
                else:
                    result_data = result.get("data", {})
            elif isinstance(result, str):
                result_data = json.loads(result)
            else:
                result_data = result
            
            # Get results from connection name
            name_results = result_data.get("resources", [])
            total_name = result_data.get("total", 0)
            debug_info.append(f"DEBUG: First attempt returned {total_name} results")
            all_results.extend(name_results)
            
        except Exception as e:
            debug_info.append(f"DEBUG: First attempt failed: {e}")
        
        # Second attempt: try with connection UUID if it's different
        try:
            if not self.is_uuid(connection_identifier):
                connection_uuid = await self._resolve_connection_identifier(connection_identifier)
                if connection_uuid != connection_identifier:  # Only if we got a different UUID
                    # Create new params with UUID but preserve all other filters
                    fallback_params = google_params.copy()
                    fallback_params["connection_identifier"] = connection_uuid
                    
                    cmd = build_keyring_command("keyrings_list", fallback_params)
                    debug_info.append(f"DEBUG: Second attempt - Executing command: {' '.join(cmd)}")
                    result = self.execute_command(cmd)
                    debug_info.append(f"DEBUG: Raw result type: {type(result)}")
                    debug_info.append(f"DEBUG: Raw result preview: {str(result)[:200]}...")
                    
                    if isinstance(result, dict):
                        # Result is a dict with status, stdout, stderr - parse stdout
                        if result.get("stdout"):
                            result_data = json.loads(result["stdout"])
                        else:
                            result_data = result.get("data", {})
                    elif isinstance(result, str):
                        result_data = json.loads(result)
                    else:
                        result_data = result
                    
                    # Get results from connection UUID
                    uuid_results = result_data.get("resources", [])
                    total_uuid = result_data.get("total", 0)
                    debug_info.append(f"DEBUG: Second attempt returned {total_uuid} results")
                    all_results.extend(uuid_results)
                else:
                    debug_info.append(f"DEBUG: Connection identifier is already a UUID, skipping second attempt")
            else:
                debug_info.append(f"DEBUG: Connection identifier is a UUID, skipping second attempt")
                
        except Exception as e:
            debug_info.append(f"DEBUG: Second attempt failed: {e}")
        
        # Remove duplicates by keyring ID
        seen_ids = set()
        unique_results = []
        for keyring in all_results:
            keyring_id = keyring.get("id")
            if keyring_id and keyring_id not in seen_ids:
                seen_ids.add(keyring_id)
                unique_results.append(keyring)
        
        # Return combined results
        combined_result = {
            "skip": 0,
            "limit": 10,
            "total": len(unique_results),
            "resources": unique_results,
            "debug_info": debug_info
        }
        
        debug_info.append(f"DEBUG: Combined total: {len(unique_results)} unique keyrings")
        return combined_result

    async def _handle_keys_list_with_proper_filtering(self, google_params: Dict[str, Any]) -> Any:
        """Handle keys list with proper filtering logic - show all keys by default, filter only when specified."""
        debug_info = []
        
        # Default behavior: show all keys without filters unless specific filters are provided
        # This matches the keyring operations pattern
        
        # Build the command with all provided parameters
        cmd = build_key_command("keys_list", google_params)
        debug_info.append(f"DEBUG: Executing command: {' '.join(cmd)}")
        result = self.execute_command(cmd)
        
        if isinstance(result, dict):
            # Result is a dict with status, stdout, stderr - parse stdout
            if result.get("stdout"):
                result_data = json.loads(result["stdout"])
            else:
                result_data = result.get("data", {})
        elif isinstance(result, str):
            result_data = json.loads(result)
        else:
            result_data = result
        
        debug_info.append(f"DEBUG: Command returned {result_data.get('total', 0)} results")
        result_data["debug_info"] = debug_info
        return result_data

    def _merge_keyring_list_results(self, result1: Dict[str, Any], result2: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two keyring list results."""
        # Extract resources from both results
        resources1 = result1.get("resources", [])
        resources2 = result2.get("resources", [])
        
        # Combine resources
        combined_resources = resources1 + resources2
        
        # Calculate totals
        total1 = result1.get("total", 0)
        total2 = result2.get("total", 0)
        combined_total = total1 + total2
        
        # Return merged result
        return {
            "skip": result1.get("skip", 0),
            "limit": result1.get("limit", 10),
            "total": combined_total,
            "resources": combined_resources
        }

    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute Google Cloud operation with smart resolution."""
        # Start with generic google_params
        google_params = params.get("google_params", {}).copy()

        # Merge service-specific parameters into google_params
        service_specific_keys = [
            "google_keys_params",
            "google_keyrings_params",
            "google_projects_params",
            "google_locations_params",
            "google_reports_params"
        ]

        for service_key in service_specific_keys:
            if service_key in params:
                google_params.update(params[service_key])

        cloud_provider = "google"

        # Debug: Show what parameters we received
        debug_info = [f"DEBUG: Action={action}, merged_google_params={google_params}"]

        # Create smart resolver
        smart_resolver = create_google_smart_resolver(self)

        # Handle special case for keyrings_list with connection resolution
        if action == "keyrings_list" and "connection_identifier" in google_params:
            return await self._handle_keyrings_list_with_connection_resolution(google_params)

        # Handle connection identifier resolution for other keyring operations
        if action in ["keyrings_add_key_rings", "keyrings_get_key_rings"]:
            if "connection_identifier" in google_params:
                # Always try with connection name first, fallback to UUID if needed
                connection_identifier = google_params["connection_identifier"]

                # For add operations, always use connection name by default
                if action == "keyrings_add_key_rings":
                    # Keep using connection name for add operations
                    pass
                else:
                    # For other operations, try name first, then UUID
                    try:
                        # First attempt with connection name
                        cmd = build_keyring_command(action, google_params)
                        result = self.execute_command(cmd)

                        if isinstance(result, dict):
                            # Result is a dict with status, stdout, stderr - parse stdout
                            if result.get("stdout"):
                                result_data = json.loads(result["stdout"])
                            else:
                                result_data = result.get("data", {})
                        elif isinstance(result, str):
                            result_data = json.loads(result)
                        else:
                            result_data = result

                        # Check if operation was successful
                        if "error" not in result_data:
                            return result_data

                    except Exception as e:
                        debug_info.append(f"DEBUG: First attempt failed: {e}")

                    # Fallback to UUID if name failed
                    connection_uuid = await self._resolve_connection_identifier(connection_identifier)
                    if connection_uuid != connection_identifier:
                        google_params["connection_identifier"] = connection_uuid

        # Handle version resolution
        if self._needs_version_resolution(action, google_params):
            return await self._resolve_versions_and_execute(action, google_params)

        # Handle other resolutions
        if self._needs_key_id_resolution(action, google_params):
            await self._resolve_key_ids(action, google_params, smart_resolver, cloud_provider)

        if self._needs_keyring_id_resolution(action, google_params):
            await self._resolve_keyring_ids(action, google_params, smart_resolver, cloud_provider)

        if self._needs_keyring_param_resolution(action, google_params):
            await self._resolve_keyring_params(action, google_params, smart_resolver, cloud_provider)

        if self._needs_keyring_list_resolution(action, google_params):
            return await self._resolve_keyring_lists(action, google_params, smart_resolver, cloud_provider)

        if self._needs_keyring_name_resolution(action, google_params):
            await self._resolve_keyring_names(action, google_params, smart_resolver, cloud_provider)

        # Handle keyring synchronization resolution
        if self._needs_keyring_sync_resolution(action, google_params):
            await self._resolve_keyring_sync(action, google_params, smart_resolver, cloud_provider)

        # Robust parameter validation for sync operations (after resolution)
        if action == "keys_sync_jobs_start":
            validation_result = self._validate_sync_jobs_start_params(google_params)
            if validation_result.get("error"):
                return validation_result

        # Handle keys_list with proper filtering logic (similar to keyrings_list)
        if action == "keys_list":
            return await self._handle_keys_list_with_proper_filtering(google_params)

        # Build and execute command
        if action.startswith("keys_"):
            cmd = build_key_command(action, google_params)
        elif action.startswith("keyrings_"):
            cmd = build_keyring_command(action, google_params)
        elif action.startswith("projects_"):
            cmd = build_project_command(action, google_params)
        elif action.startswith("locations_"):
            cmd = build_location_command(action, google_params)
        elif action.startswith("reports_"):
            cmd = build_reports_command(action, google_params)
        else:
            raise ValueError(f"Unsupported action: {action}")

        debug_info.append(f"DEBUG: Executing command: {' '.join(cmd)}")
        result = self.execute_command(cmd)

        if isinstance(result, dict):
            # Result is a dict with status, stdout, stderr - parse stdout
            if result.get("stdout"):
                result_data = json.loads(result["stdout"])
            else:
                result_data = result.get("data", {})
        elif isinstance(result, str):
            result_data = json.loads(result)
        else:
            result_data = result

        result_data["debug_info"] = debug_info
        return result_data

    def _validate_sync_jobs_start_params(self, google_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced validation for keys_sync_jobs_start parameters.
        Provides clear guidance on correct parameter usage.
        """
        # Check for conflicting parameters
        has_key_rings = "key_rings" in google_params and google_params["key_rings"]
        has_synchronize_all = "synchronize_all" in google_params and google_params["synchronize_all"]
        
        if has_key_rings and has_synchronize_all:
            return {
                "error": "Parameter conflict detected",
                "message": "Cannot use both 'key_rings' and 'synchronize_all' parameters together. They are mutually exclusive.",
                "guidance": {
                    "for_specific_keyrings": "Use: {'key_rings': 'keyring1,keyring2'}",
                    "for_all_keyrings": "Use: {'synchronize_all': True}",
                    "examples": [
                        "Single keyring: {'key_rings': 'my-keyring'}",
                        "Multiple keyrings: {'key_rings': 'keyring1,keyring2,keyring3'}",
                        "Location-prefixed: {'key_rings': 'global/keyring1,us-central1/keyring2'}",
                        "All keyrings: {'synchronize_all': True}"
                    ]
                }
            }
        
        # Validate key_rings parameter format
        if has_key_rings:
            key_rings_value = google_params["key_rings"]
            if not isinstance(key_rings_value, str):
                return {
                    "error": "Invalid key_rings parameter type",
                    "message": "The 'key_rings' parameter must be a string with comma-separated values.",
                    "correct_format": "Use comma-separated keyring names: 'keyring1,keyring2,keyring3'"
                }
            
            # Check for common mistakes - only flag keyring_name, allow location and project_id for context
            if "keyring_name" in google_params:
                return {
                    "error": "Incorrect parameter usage",
                    "message": "For keys_sync_jobs_start, use 'key_rings' parameter instead of 'keyring_name'.",
                    "correct_usage": {
                        "instead_of": {
                            "keyring_name": "my-keyring"
                        },
                        "use": {
                            "key_rings": "my-keyring"
                        },
                        "for_multiple_locations": {
                            "key_rings": "global/my-keyring,us-central1/another-keyring"
                        }
                    }
                }
        
        # Validate synchronize_all parameter
        if has_synchronize_all and not isinstance(google_params["synchronize_all"], bool):
            return {
                "error": "Invalid synchronize_all parameter type",
                "message": "The 'synchronize_all' parameter must be a boolean value.",
                "correct_usage": {
                    "synchronize_all": True
                }
            }
        
        # If no parameters provided, suggest options
        if not has_key_rings and not has_synchronize_all:
            return {
                "error": "Missing required parameters",
                "message": "For keys_sync_jobs_start, you must specify either 'key_rings' or 'synchronize_all'.",
                "options": {
                    "option_1": {
                        "description": "Sync specific keyrings",
                        "parameters": {"key_rings": "keyring1,keyring2"}
                    },
                    "option_2": {
                        "description": "Sync all keyrings",
                        "parameters": {"synchronize_all": True}
                    }
                },
                "examples": [
                    "Sync specific keyrings: {'key_rings': 'my-keyring,another-keyring'}",
                    "Sync all keyrings: {'synchronize_all': True}"
                ]
            }
        
        # All validations passed
        return {"valid": True} 