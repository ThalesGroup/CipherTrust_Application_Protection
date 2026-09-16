"""Main CCKM Management Tool."""

from typing import Any, Dict, List
from ..base import BaseTool
from .constants import COMMON_SCHEMA_PROPERTIES, CLOUD_OPERATIONS
from .aws_operations import AWSOperations
from .azure_operations import AzureOperations
from .oci_operations import OCIOperations
from .google_operations import GoogleOperations
from .microsoft_operations import MicrosoftOperations
from .ekm_operations import EKMOperations
from .gws_operations import GWSOperations


class CCKMManagementTool(BaseTool):
    """Unified CCKM Management Tool that delegates to specialized cloud provider operations.
    
    This tool provides a single interface for all CCKM operations while internally
    organizing functionality by cloud provider for better maintainability.
    """
    
    def __init__(self):
        super().__init__()
        # Initialize all cloud provider operations
        self.cloud_operations = {
            'aws': AWSOperations(self.execute_with_domain),
            'azure': AzureOperations(self.execute_with_domain),
            'oci': OCIOperations(self.execute_with_domain),
            'google': GoogleOperations(self.execute_with_domain),
            'microsoft': MicrosoftOperations(self.execute_with_domain),
            'ekm': EKMOperations(self.execute_with_domain),
            'gws': GWSOperations(self.execute_with_domain),
            # Additional cloud providers can be added as needed
            # 'sap-dc': SAPDCOperations(self.execute_with_domain),
            # 'salesforce': SalesforceOperations(self.execute_with_domain),
            # 'virtual': VirtualOperations(self.execute_with_domain),
            # 'hsm': HSMOperations(self.execute_with_domain),
            # 'external-cm': ExternalCMOperations(self.execute_with_domain),
            # 'dsm': DSMOperations(self.execute_with_domain),
        }
        
    @property
    def name(self) -> str:
        return "cckm_management"
    
    @property
    def description(self) -> str:
        return (
            "CCKM (CipherTrust Cloud Key Manager) operations for managing cloud keys and related resources across various providers. "
            "Supports comprehensive operations for AWS, Azure, Google Cloud, OCI, SAP Data Custodian, Salesforce, Microsoft DKE, Virtual, HSM, GWS, EKM, External CM, and DSM. "
            
            "Key Features for AI Assistants: "
            "1. SMART ID RESOLUTION: Automatically converts key aliases, ARNs, and resource names to proper IDs. "
            "2. COMPREHENSIVE FILE SUPPORT: All JSON file parameters include format examples and absolute path requirements. "
            "3. SYNCHRONIZE/REFRESH EQUIVALENCE: Both terms trigger the same key synchronization operations. "
            "4. DETAILED PARAMETER VALIDATION: Each parameter includes usage examples, format specifications, and default values. "
            "5. CRITICAL PARAMETER MAPPING: For EXISTING key operations (get, delete, enable, disable, update), always use 'id' parameter even when users specify names/aliases. For NEW key operations (create, upload), use the specific 'alias' or 'key_name' parameters as required. "
            
            "Operations by Cloud Provider: "
            "AWS: Keys (synchronize/refresh), Custom Key Stores (XKS), IAM management, KMS account management, Reports, Bulk jobs, Log groups; "
            "Azure: Keys (synchronize/refresh), Certificates, Secrets, Vaults, Subscriptions, Reports, Bulk jobs, Synchronization jobs; "
            "Google Cloud: Keys (synchronize/refresh), Key Rings, Projects, Locations, Reports, Synchronization jobs; "
            "OCI: Keys (synchronize/refresh), Compartments, External Vaults, Issuers, Regions, Reports, Tenancy, Vaults; "
            "Microsoft: Keys, DKE endpoints; "
            "EKM: Endpoints; "
            "GWS: Endpoints with wrap/unwrap operations. "
            
            "File-Based Operations Guide: "
            "- JSON files override individual CLI parameters when provided "
            "- Always use absolute file paths for reliability "
            "- File format examples are provided in each parameter description "
            "- Common file types: *_jsonfile parameters for configuration, tags, policies, and bulk operations "
            
            "Smart ID Resolution Examples: "
            "- AWS: Converts 'alias/my-key' or 'arn:aws:kms:...' to UUID automatically "
            "- Google: Converts 'my-key' or 'keyring/key' to full resource URL. SMART RESOLUTION: Supports location-prefixed keyrings (e.g., 'us-central1/keyring1,global/keyring2') and location context for same-location scenarios! "
            "- Azure: Resolves key names to vault-specific identifiers "
            "- OCI: Resolves vault names to CCKM vault UUIDs for delete operations. When user says: 'delete vault my-vault-name' → Use: {'action': 'vaults_delete', 'oci_vaults_params': {'vault_name': 'my-vault-name'}} "
            
            "CRITICAL PARAMETER MAPPING EXAMPLES FOR AI ASSISTANTS: "
            "EXISTING KEY OPERATIONS (use 'id' parameter): "
            "When user says: 'get details of AWS key my-key-name' → Use: {'action': 'keys_get', 'aws_keys_params': {'id': 'my-key-name'}} "
            "When user says: 'delete Google key my-encryption-key' → Use: {'action': 'keys_delete', 'google_keys_params': {'id': 'my-encryption-key'}} "
            "When user says: 'enable Azure key prod-key' → Use: {'action': 'keys_enable', 'azure_keys_params': {'id': 'prod-key'}} "
            
                       "GOOGLE CLOUD SMART KEYRING RESOLUTION: "
           "Scenario 1: 'synchronize keyring my-keyring-1 in global' → Use: {'action': 'keys_sync_jobs_start', 'google_keys_params': {'key_rings': 'my-keyring-1'}} "
           "Scenario 2: 'synchronize keyrings my-keyring-1 and my-keyring-2 in us-central1' → Use: {'action': 'keys_sync_jobs_start', 'google_keys_params': {'key_rings': 'my-keyring-1,my-keyring-2'}} "
           "Scenario 3: 'synchronize my-keyring-1 in global and my-keyring-2 in us-central1' → Use: {'action': 'keys_sync_jobs_start', 'google_keys_params': {'key_rings': 'global/my-keyring-1,us-central1/my-keyring-2'}} "
           "CRITICAL: For multiple keyrings in different locations, use 'location/keyring-name' format in key_rings parameter! "
           "ENHANCED VALIDATION: The tool now validates sync parameters and provides clear error messages for common mistakes like using 'keyring_name' instead of 'key_rings' or missing required parameters. "
            
            "NEW KEY OPERATIONS (use specific name/alias parameters): "
            "When user says: 'create AWS key with alias my-new-key' → Use: {'action': 'keys_create', 'aws_keys_params': {'alias': 'my-new-key', 'region': '...', 'kms': '...'}} "
            "When user says: 'create Google key named secure-key' → Use: {'action': 'keys_create', 'google_keys_params': {'key_name': 'secure-key', 'key_ring': '...'}} "
            "When user says: 'upload Azure key called backup-key' → Use: {'action': 'keys_upload', 'azure_keys_params': {'key_name': 'backup-key', 'key_vault': '...'}} "
            "When user says: 'upload Google key called backup-key' → Use: {'action': 'keys_upload', 'google_keys_params': {'key_name': 'backup-key', 'key_ring': '...'}} "
            
            "ALIAS MANAGEMENT (use both 'id' + 'alias'): "
            "When user says: 'add alias new-alias to AWS key existing-key' → Use: {'action': 'keys_add_alias', 'aws_keys_params': {'id': 'existing-key', 'alias': 'new-alias'}} "
            
            "CRITICAL OPERATION NAME MAPPING FOR AI ASSISTANTS: "
            "AWS: keys_upload (upload keys from local/HSM to AWS KMS) "
            "Azure: keys_upload (upload keys from local/HSM to Azure Key Vault) "
            "Google Cloud: keys_upload (upload keys from local/HSM to Google Cloud KMS) "
            "OCI: keys_upload (upload keys from local/HSM to OCI Vault) "
            "GOOGLE CLOUD KEYRING OPERATIONS: "
            "When user says: 'list all keyrings' → Use: {'action': 'keyrings_list', 'google_keyrings_params': {}} "
            "When user says: 'list keyrings from global location' → Use: {'action': 'keyrings_list', 'google_keyrings_params': {'location': 'global'}} "
            "When user says: 'list keyrings from [connection-name] connection' → Use: {'action': 'keyrings_list', 'google_keyrings_params': {'connection_identifier': '[connection-name]'}} "
            "When user says: 'list keyrings from [location] location' → Use: {'action': 'keyrings_list', 'google_keyrings_params': {'location': '[location]'}} "
            "GOOGLE CLOUD DELETE OPERATIONS: "
            "Google Cloud does not support direct key deletion. Instead use keys_delete or keys_schedule_destroy - both schedule destruction of key versions. "
            "- To delete specific version: provide version_id parameter "
            "- To delete all versions: omit version_id parameter (system will automatically get all versions and schedule destruction for each) "
            "Smart resolution handles version discovery when no version_id is provided. "
            "Note: 'synchronize' and 'refresh' are equivalent terms for key synchronization operations - both trigger the same synchronization process. "
            "Each cloud provider has specific operations and parameters - see action_requirements in schema for details."
        )
    
    def get_schema(self) -> dict[str, Any]:
        """Build complete schema from all cloud providers"""
        # Collect all unique operations across all cloud providers
        all_operations = set()
        for cloud_provider, operations in self.cloud_operations.items():
            for operation in operations.get_operations():
                all_operations.add(operation)
        
        # Start with common properties
        properties = {
            "action": {
                "type": "string",
                "enum": sorted(all_operations),
                "description": (
                    "The CCKM operation to perform. Examples: keys_create, keys_list, keys_get, keys_sync_jobs_start, keyrings_list, keyrings_get_key_rings, keyrings_add_key_rings, reports_generate. "
                    "IMPORTANT NOTES FOR AI ASSISTANTS: "
                    "1. Use 'keys_sync_jobs_start' for both 'synchronize' and 'refresh' operations (they are equivalent). "
                    "2. Smart ID resolution automatically handles key aliases, ARNs, and resource names. "
                    "3. JSON file parameters (*_jsonfile) override individual parameters and require absolute file paths. "
                    "4. The cloud_provider parameter determines which cloud provider to use and which parameters are available. "
                    "5. CRITICAL PARAMETER USAGE: For EXISTING key operations (get, delete, enable, disable, update), use 'id' parameter even when users specify names/aliases. For NEW key operations (create, upload), use the specific 'alias' or 'key_name' parameters as required by the operation. For alias management, use both 'id' (existing key) and 'alias' (alias to add/remove). "
                    "6. For Google Cloud KeyRings: Use 'keyrings_list' to list keyrings in CCKM database, 'keyrings_get_key_rings' to discover keyrings from GCP, and 'keyrings_add_key_rings' to add discovered keyrings to CCKM. IMPORTANT: For add operations, use single keyring names and make separate calls for different locations. The location/keyring-name format is ONLY for synchronization operations."
                )
            },
            **COMMON_SCHEMA_PROPERTIES
        }
        
        # Add properties from each cloud provider
        for cloud_provider, operations in self.cloud_operations.items():
            properties.update(operations.get_schema_properties())
        
        # Build action requirements
        action_requirements = {}
        for cloud_provider, operations in self.cloud_operations.items():
            action_requirements.update(operations.get_action_requirements())
        
        # Add special guidance for keyring operations
        if "keyrings_list" in action_requirements:
            action_requirements["keyrings_list"]["description"] = "LIST keyrings already in CCKM database. Use this to see what keyrings are currently managed by CCKM. No required parameters - lists all keyrings by default. Optional filters: connection_identifier, location, name, etc. PARAMETER MAPPING: When user says 'list keyrings from [location] location' → Use {'location': '[location]'}. When user says 'list keyrings from [connection-name] connection' → Use {'connection_identifier': '[connection-name]'}."
        
        if "keyrings_get_key_rings" in action_requirements:
            action_requirements["keyrings_get_key_rings"]["description"] = "DISCOVER keyrings from Google Cloud Platform. Use this to find keyrings that exist in GCP but are not yet added to CCKM. REQUIRES: connection_identifier, project_id, location. This is for discovery only - use keyrings_add_key_rings to add discovered keyrings to CCKM."
        
        if "keyrings_add_key_rings" in action_requirements:
            action_requirements["keyrings_add_key_rings"]["description"] = "ADD discovered keyrings to CCKM database. Use this after discovering keyrings with keyrings_get_key_rings. REQUIRES: connection_identifier, project_id. Optional: keyring_name, location. Always uses connection names by default with automatic UUID fallback."
        
        return {
            "type": "object",
            "properties": properties,
            "required": ["action", "cloud_provider"],
            "additionalProperties": True,
            "action_requirements": action_requirements
        }
    
    async def discover_and_add_gcp_keyrings(self, connection_identifier: str, project_id: str, location: str = "global") -> Dict[str, Any]:
        """Discover and add all keyrings available under a GCP project."""
        try:
            # Step 1: Get all available keyrings from the project
            discover_params = {
                "action": "keyrings_get_key_rings",
                "cloud_provider": "google",
                "google_keyrings_params": {
                    "connection_identifier": connection_identifier,
                    "project_id": project_id,
                    "location": location
                }
            }
            
            discover_result = await self.execute("keyrings_get_key_rings", **discover_params)
            
            if "error" in discover_result:
                return {"error": f"Failed to discover keyrings: {discover_result['error']}"}
            
            # Extract keyrings from the result
            keyrings_data = discover_result.get("data", {})
            keyrings = keyrings_data.get("key_rings", [])
            
            if not keyrings:
                return {"message": "No keyrings found in the project", "keyrings": []}
            
            # Step 2: Add each keyring to CCKM
            added_keyrings = []
            failed_keyrings = []
            
            for keyring in keyrings:
                keyring_name = keyring.get("name")
                
                if not keyring_name:
                    continue
                
                # Extract keyring name from full resource path
                # Format: projects/project-id/locations/location/keyRings/keyring-name
                if "/keyRings/" in keyring_name:
                    keyring_short_name = keyring_name.split("/keyRings/")[-1]
                else:
                    keyring_short_name = keyring_name
                
                add_params = {
                    "action": "keyrings_add_key_rings",
                    "cloud_provider": "google",
                    "google_keyrings_params": {
                        "connection_identifier": connection_identifier,
                        "project_id": project_id,
                        "gcp_keyrings_jsonfile": self._create_keyrings_json_file([{"name": keyring_short_name}])
                    }
                }
                
                add_result = await self.execute("keyrings_add_key_rings", **add_params)
                
                if "error" in add_result:
                    failed_keyrings.append({
                        "keyring_name": keyring_short_name,
                        "full_name": keyring_name,
                        "error": add_result["error"]
                    })
                else:
                    added_keyrings.append({
                        "keyring_name": keyring_short_name,
                        "full_name": keyring_name,
                        "result": add_result.get("data", {})
                    })
            
            return {
                "message": f"Discovered {len(keyrings)} keyrings, added {len(added_keyrings)}, failed {len(failed_keyrings)}",
                "total_discovered": len(keyrings),
                "added_keyrings": added_keyrings,
                "failed_keyrings": failed_keyrings
            }
            
        except Exception as e:
            return {"error": f"Failed to discover and add keyrings: {str(e)}"}

    async def add_gcp_keyring(self, connection_identifier: str, project_id: str, keyring_name: str, location: str = "global") -> Dict[str, Any]:
        """Add a single GCP keyring to CCKM with automatic resource name construction."""
        try:
            add_params = {
                "action": "keyrings_add_key_rings",
                "cloud_provider": "google",
                "google_keyrings_params": {
                    "connection_identifier": connection_identifier,
                    "project_id": project_id,
                    "keyring_name": keyring_name,
                    "location": location
                }
            }
            
            result = await self.execute("keyrings_add_key_rings", **add_params)
            
            if "error" in result:
                return {"error": f"Failed to add keyring '{keyring_name}': {result['error']}"}
            
            return {
                "message": f"Successfully added keyring '{keyring_name}' to CCKM",
                "keyring_name": keyring_name,
                "project_id": project_id,
                "location": location,
                "result": result.get("data", {})
            }
            
        except Exception as e:
            return {"error": f"Failed to add keyring '{keyring_name}': {str(e)}"}

    def _create_keyrings_json_file(self, keyrings: List[Dict[str, str]]) -> str:
        """Create a temporary JSON file with keyring data."""
        import tempfile
        import json
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(keyrings, temp_file)
        temp_file.close()
        
        return temp_file.name

    async def discover_and_add_gcp_projects(self, connection_identifier: str) -> Dict[str, Any]:
        """Discover and add all projects available under a GCP connection."""
        try:
            # Step 1: Get all available projects from the connection
            discover_params = {
                "action": "projects_get_project",
                "cloud_provider": "google",
                "google_projects_params": {
                    "connection_identifier": connection_identifier
                }
            }
            
            discover_result = await self.execute("projects_get_project", **discover_params)
            
            if "error" in discover_result:
                return {"error": f"Failed to discover projects: {discover_result['error']}"}
            
            # Extract projects from the result
            projects_data = discover_result.get("data", {})
            projects = projects_data.get("projects", [])
            
            if not projects:
                return {"message": "No projects found in the connection", "projects": []}
            
            # Step 2: Add each project to CCKM
            added_projects = []
            failed_projects = []
            
            for project in projects:
                project_id = project.get("project_id")
                project_name = project.get("display_name", project_id)
                
                if not project_id:
                    continue
                
                add_params = {
                    "action": "projects_add",
                    "cloud_provider": "google",
                    "google_projects_params": {
                        "project_id": project_id,
                        "connection_identifier": connection_identifier
                    }
                }
                
                add_result = await self.execute("projects_add", **add_params)
                
                if "error" in add_result:
                    failed_projects.append({
                        "project_id": project_id,
                        "project_name": project_name,
                        "error": add_result["error"]
                    })
                else:
                    added_projects.append({
                        "project_id": project_id,
                        "project_name": project_name,
                        "result": add_result.get("data", {})
                    })
            
            return {
                "message": f"Discovered {len(projects)} projects, added {len(added_projects)}, failed {len(failed_projects)}",
                "total_discovered": len(projects),
                "added_projects": added_projects,
                "failed_projects": failed_projects
            }
            
        except Exception as e:
            return {"error": f"Failed to discover and add projects: {str(e)}"}

    async def execute(self, action: str, **kwargs: Any) -> Any:
        """Execute CCKM operation by delegating to appropriate cloud provider."""
        # Robust parameter validation and guidance for common mistakes
        validation_result = self._validate_common_parameter_mistakes(action, kwargs)
        if validation_result.get("error"):
            return validation_result
        
        # Get cloud provider from parameters
        cloud_provider = kwargs.get("cloud_provider")
        if not cloud_provider:
            return {"error": "Missing required parameter: cloud_provider"}
        
        # Get the appropriate cloud operations handler
        if cloud_provider not in self.cloud_operations:
            return {"error": f"Cloud provider {cloud_provider} not implemented yet"}
        
        cloud_ops = self.cloud_operations[cloud_provider]
        
        # Check if the operation is supported by this cloud provider
        if action not in cloud_ops.get_operations():
            return {"error": f"Operation {action} not supported for cloud provider {cloud_provider}"}
        
        # Validate action-specific requirements using cloud-specific requirements
        # Skip validation for operations that support smart ID resolution
        if action not in ["vaults_delete"]:  # Add other smart ID resolution operations here
            if not self._validate_action_params(action, kwargs, cloud_ops):
                cloud_requirements = cloud_ops.get_action_requirements().get(action, {})
                required_params = cloud_requirements.get("required", [])
                return {"error": f"Missing required parameters for {action}: {required_params}"}
        
        # Execute the operation
        try:
            return await cloud_ops.execute_operation(action, kwargs)
        except Exception as e:
            return {"error": f"Failed to execute {action}: {str(e)}"}

    def _validate_common_parameter_mistakes(self, action: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate for common parameter mistakes and provide helpful guidance.
        """
        # Check for Google Cloud sync operation parameter mistakes
        if action == "keys_sync_jobs_start":
            # Check in google_keys_params
            if "google_keys_params" in kwargs:
                google_params = kwargs["google_keys_params"]
                
                # Check for wrong parameter names
                if "keyring_name" in google_params:
                    return {
                        "error": "Incorrect parameter name",
                        "message": "You used 'keyring_name' but the correct parameter is 'key_rings'",
                        "correction": {
                            "incorrect": {"keyring_name": google_params["keyring_name"]},
                            "correct": {"key_rings": google_params["keyring_name"]}
                        },
                        "examples": [
                            "Single keyring: {'key_rings': 'my-keyring'}",
                            "Multiple keyrings: {'key_rings': 'keyring1,keyring2'}",
                            "Location-prefixed: {'key_rings': 'global/keyring1,us-central1/keyring2'}"
                        ]
                    }
                
                # Check for missing required parameters
                if not any(key in google_params for key in ["key_rings", "synchronize_all"]):
                    return {
                        "error": "Missing required parameters",
                        "message": "For keys_sync_jobs_start, you must specify either 'key_rings' or 'synchronize_all'",
                        "options": {
                            "sync_specific": {"key_rings": "keyring1,keyring2"},
                            "sync_all": {"synchronize_all": True}
                        }
                    }
            
            # Check in google_params (wrong parameter structure)
            elif "google_params" in kwargs:
                return {
                    "error": "Incorrect parameter structure",
                    "message": "You used 'google_params' but the correct parameter is 'google_keys_params'",
                    "correction": {
                        "incorrect": "google_params",
                        "correct": "google_keys_params"
                    }
                }
        
        # Check for wrong parameter structure in other operations
        if action.startswith("keys_") and "google_params" in kwargs:
            return {
                "error": "Incorrect parameter structure",
                "message": "You used 'google_params' but the correct parameter is 'google_keys_params'",
                "correction": {
                    "incorrect": "google_params",
                    "correct": "google_keys_params"
                }
            }
        
        # All validations passed
        return {"valid": True}
    
    def _validate_action_params(self, action: str, params: dict, cloud_ops=None) -> bool:
        """Validate that required parameters are present for the action."""
        if cloud_ops:
            # Use cloud-specific requirements
            requirements = cloud_ops.get_action_requirements().get(action, {})
        else:
            # Fallback to global schema requirements
            schema = self.get_schema()
            requirements = schema.get("action_requirements", {}).get(action, {})
        required_params = requirements.get("required", [])
        
        # Special validation for tenancy_add operation
        if action == "tenancy_add":
            return self._validate_tenancy_add_params(params)
        
        # Special validation for vault operations that support smart ID resolution
        if action == "vaults_delete":
            return self._validate_vault_delete_params(params)
        
        # Check if all required parameters are present
        for param in required_params:
            # Check in the main params first
            if param in params:
                continue
                
            # Check in cloud-specific params (e.g., aws_params, azure_params, etc.)
            cloud_provider = params.get("cloud_provider")
            if cloud_provider:
                # Generic cloud params pattern (e.g., aws_params)
                cloud_params_key = f"{cloud_provider}_params"
                if cloud_params_key in params and param in params[cloud_params_key]:
                    continue
                
                # Check service-specific params (e.g., aws_kms_params, aws_iam_params, etc.)
                service_specific_keys = [
                    f"{cloud_provider}_kms_params",
                    f"{cloud_provider}_iam_params", 
                    f"{cloud_provider}_key_params",
                    f"{cloud_provider}_keys_params",
                    f"{cloud_provider}_keyrings_params",
                    f"{cloud_provider}_projects_params",
                    f"{cloud_provider}_locations_params",
                    f"{cloud_provider}_reports_params",
                    f"{cloud_provider}_bulkjob_params",
                    f"{cloud_provider}_custom_key_stores_params",
                    f"{cloud_provider}_logs_params",
                    f"{cloud_provider}_certificates_params",
                    f"{cloud_provider}_vaults_params",
                    f"{cloud_provider}_secrets_params",
                    f"{cloud_provider}_subscriptions_params",
                    f"{cloud_provider}_compartments_params",
                    f"{cloud_provider}_tenancy_params"
                ]
                
                param_found = False
                for service_key in service_specific_keys:
                    if service_key in params and param in params[service_key]:
                        param_found = True
                        break
                
                if param_found:
                    continue
                
                # Special case: Check for alternative parameter names
                if param == "source_key_identifier":
                    # Check for sourceKey_identifier alternative
                    for service_key in service_specific_keys:
                        if service_key in params and "sourceKey_identifier" in params[service_key]:
                            param_found = True
                            break
                    if param_found:
                        continue
                
            # Parameter not found
            return False
        
        return True
    
    def _validate_tenancy_add_params(self, params: dict) -> bool:
        """Special validation for tenancy_add operation which has two valid parameter combinations."""
        cloud_provider = params.get("cloud_provider")
        if not cloud_provider:
            return False
            
        # Check in main params
        has_connection_identifier = "connection_identifier" in params
        has_oci_tenancy = "oci_tenancy" in params
        has_tenancy_ocid = "tenancy_ocid" in params
        
        # Check in cloud-specific params
        cloud_params_key = f"{cloud_provider}_params"
        if cloud_params_key in params:
            cloud_params = params[cloud_params_key]
            has_connection_identifier = has_connection_identifier or "connection_identifier" in cloud_params
            has_oci_tenancy = has_oci_tenancy or "oci_tenancy" in cloud_params
            has_tenancy_ocid = has_tenancy_ocid or "tenancy_ocid" in cloud_params
        
        # Check in service-specific params
        service_specific_key = f"{cloud_provider}_tenancy_params"
        if service_specific_key in params:
            tenancy_params = params[service_specific_key]
            has_connection_identifier = has_connection_identifier or "connection_identifier" in tenancy_params
            has_oci_tenancy = has_oci_tenancy or "oci_tenancy" in tenancy_params
            has_tenancy_ocid = has_tenancy_ocid or "tenancy_ocid" in tenancy_params
        
        # Valid combinations:
        # 1. connection_identifier only (use existing connection)
        # 2. oci_tenancy + tenancy_ocid (add without connection)
        return (has_connection_identifier and not has_oci_tenancy and not has_tenancy_ocid) or \
               (not has_connection_identifier and has_oci_tenancy and has_tenancy_ocid)
    
    def _validate_vault_delete_params(self, params: dict) -> bool:
        """Special validation for vaults_delete operation which supports both id and vault_name parameters."""
        cloud_provider = params.get("cloud_provider")
        if not cloud_provider:
            return False
            
        # Check in main params
        has_id = "id" in params
        has_vault_name = "vault_name" in params
        
        # Check in cloud-specific params
        cloud_params_key = f"{cloud_provider}_params"
        if cloud_params_key in params:
            cloud_params = params[cloud_params_key]
            has_id = has_id or "id" in cloud_params
            has_vault_name = has_vault_name or "vault_name" in cloud_params
        
        # Check in service-specific params
        service_specific_keys = [
            f"{cloud_provider}_vaults_params",
            f"{cloud_provider}_keys_params"
        ]
        
        for service_key in service_specific_keys:
            if service_key in params:
                service_params = params[service_key]
                has_id = has_id or "id" in service_params
                has_vault_name = has_vault_name or "vault_name" in service_params
        
        # Valid: either id OR vault_name must be provided
        return has_id or has_vault_name 