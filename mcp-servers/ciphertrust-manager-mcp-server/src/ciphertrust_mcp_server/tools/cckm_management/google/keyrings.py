"""Google Cloud Key Rings operations for CCKM."""
from typing import Any, Dict, List
import tempfile
import json
import os

def construct_gcp_resource_name(resource_type: str, project_id: str, location: str, resource_name: str) -> str:
    """
    Construct full GCP resource name in the format:
    projects/{project_id}/locations/{location}/{resource_type}/{resource_name}
    
    Args:
        resource_type: The resource type (e.g., 'keyRings', 'cryptoKeys')
        project_id: GCP project ID
        location: GCP location (e.g., 'global', 'us-central1')
        resource_name: The resource name
    
    Returns:
        Full GCP resource name
    """
    return f"projects/{project_id}/locations/{location}/{resource_type}/{resource_name}"

def create_keyrings_json_file(keyrings_data: List[Dict[str, str]], project_id: str, connection_identifier: str) -> str:
    """
    Create a temporary JSON file with keyring data for add-key-rings operation.
    
    Args:
        keyrings_data: List of keyring data with 'name' field containing keyring names or full resource names
        project_id: GCP project ID
        connection_identifier: GCP connection identifier (required for add operations)
    
    Returns:
        Path to the temporary JSON file
    """
    if not connection_identifier:
        raise ValueError("connection_identifier is required for creating keyring JSON files")
    
    # Construct the JSON structure expected by the CLI
    json_data = {
        "connection": connection_identifier,
        "key_rings": [],
        "project_id": project_id
    }
    
    for keyring in keyrings_data:
        keyring_name = keyring.get("name", "")
        if keyring_name:
            # For add-key-rings, we pass keyring names as-is since they're discovered from GCP
            json_data["key_rings"].append({
                "name": keyring_name
            })
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(json_data, temp_file, indent=2)
    temp_file.close()
    
    return temp_file.name

def get_keyring_operations() -> Dict[str, Any]:
    """Return schema and action requirements for Google Cloud key ring operations."""
    return {
        "schema_properties": {
            "google_keyrings_params": {
                "type": "object",
                "properties": {
                    # Basic key ring parameters
                    "keyring_name": {
                        "type": "string", 
                        "description": "Name of the key ring for ADD operations. SMART RESOLUTION: Use either 1) Short name (e.g., 'my-keyring-01') + location parameter + project_id, or 2) Full resource name (e.g., 'projects/my-project/locations/global/keyRings/my-keyring-01'). For multiple keyrings in SAME location, make separate calls. For different locations, make separate calls with different location parameter."
                    },
                    "id": {
                        "type": "string", 
                        "description": "Key ring ID or full resource name for get/delete/update operations. Smart resolution automatically converts to full resource name when project_id and location are provided."
                    },
                    "project_id": {
                        "type": "string", 
                        "description": "GCP Project ID - required for most operations and used for smart resolution"
                    },
                    "location": {
                        "type": "string", 
                        "description": "GCP location/region for the key ring - used for smart resolution and filtering. CRITICAL: When user says 'list keyrings from global location' or 'list keyrings in global' → ALWAYS include this parameter as 'location': 'global'. When user says 'list keyrings from us-central1 location' → use 'location': 'us-central1'. This parameter is REQUIRED for filtering by location."
                    },
                    "connection_identifier": {
                        "type": "string", 
                        "description": "Name or ID of the connection which has been created earlier - required for discovery and add operations. For add operations, connection names are always used by default with automatic fallback to UUID if needed."
                    },
                    
                    # List and pagination parameters  
                    "limit": {
                        "type": "integer", 
                        "description": "Maximum number of results to return"
                    },
                    "skip": {
                        "type": "integer", 
                        "description": "Number of results to skip"
                    },
                    "sort": {
                        "type": "string", 
                        "description": "Sort parameter"
                    },
                    "name": {
                        "type": "string", 
                        "description": "Filter results by name"
                    },
                    "cloud_name": {
                        "type": "string", 
                        "description": "Filter resources on the basis of cloud name"
                    },
                    "organization_display_name": {
                        "type": "string", 
                        "description": "Filter by organization display name"
                    },
                    "organization_name": {
                        "type": "string", 
                        "description": "Filter by organization name"
                    },

                    # Get-key-rings (discovery) parameters
                    "page_size": {
                        "type": "integer", 
                        "description": "Number of key rings to view (for get-key-rings operation)"
                    },
                    "page_token": {
                        "type": "string", 
                        "description": "Token for pagination (for get-key-rings operation)"
                    },

                    # JSON file parameters for add-key-rings
                    "gcp_addkeyrings_jsonfile": {
                        "type": "string", 
                        "description": "Path to JSON file containing complete add key rings parameters. Format: {\"connection\": \"connection-name\", \"key_rings\": [{\"name\": \"keyring-name\"}], \"project_id\": \"project-id\"}. Use absolute file paths for reliability."
                    },
                    "gcp_keyrings_jsonfile": {
                        "type": "string", 
                        "description": "Path to JSON file containing key rings list only. Format: [{\"name\": \"keyring-name\"}]. Requires connection_identifier and project_id as separate parameters. Use absolute file paths for reliability."
                    },
                    "gcp_getkeyrings_jsonfile": {
                        "type": "string", 
                        "description": "Path to JSON file containing get key rings parameters. Format: {\"connection\": \"connection-name\", \"location\": \"location\", \"project_id\": \"project-id\", \"page_size\": 100, \"page_token\": \"token\"}. Use absolute file paths for reliability."
                    },

                    # ACL parameters
                    "applyacls_jsonfile": {
                        "type": "string", 
                        "description": "Path to JSON file containing ACL parameters. Format: {\"acls\": [{\"actions\": [\"action\"], \"group\": \"group\", \"permit\": true, \"user_id\": \"user\"}]}. Use absolute file paths for reliability."
                    }
                }
            }
        },
        "action_requirements": {
            "keyrings_list": {
                "required": [],
                "optional": ["connection_identifier", "project_id", "location", "name", "cloud_name", "organization_display_name", "organization_name", "id", "limit", "skip", "sort"]
            },
            "keyrings_get": {
                "required": ["id"],
                "optional": []
            },
            "keyrings_delete": {
                "required": ["id"],
                "optional": []
            },
            "keyrings_update": {
                "required": ["id", "connection_identifier"],
                "optional": []
            },
            "keyrings_update_acls": {
                "required": ["id", "applyacls_jsonfile"],
                "optional": []
            },
            "keyrings_get_key_rings": {
                "required": ["connection_identifier", "project_id", "location"],
                "optional": ["page_size", "page_token", "gcp_getkeyrings_jsonfile"]
            },
            "keyrings_add_key_rings": {
                "required": ["connection_identifier", "project_id"],
                "optional": ["keyring_name", "location", "gcp_addkeyrings_jsonfile", "gcp_keyrings_jsonfile"]
            }
        }
    }

def build_keyring_command(action: str, google_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given Google Cloud key ring operation."""
    cmd = ["cckm", "google", "key-rings"]
    
    # Extract the base operation name (remove 'keyrings_' prefix)
    base_action = action.replace("keyrings_", "")
    
    # Simple actions that only need --id parameter
    simple_id_actions = ["get", "delete"]
    
    if base_action in simple_id_actions:
        cmd.append(base_action)
        cmd.extend(["--id", google_params["id"]])
        return cmd
    
    # Handle specific operations based on ksctl documentation
    if base_action == "list":
        cmd.append("list")
        # Optional filters - only add if provided
        if "connection_identifier" in google_params:
            cmd.extend(["--connection-identifier", google_params["connection_identifier"]])
        if "project_id" in google_params:
            cmd.extend(["--project-id", google_params["project_id"]])
        if "location" in google_params:
            cmd.extend(["--location", google_params["location"]])
        if "name" in google_params:
            cmd.extend(["--name", google_params["name"]])
        if "cloud_name" in google_params:
            cmd.extend(["--cloud-name", google_params["cloud_name"]])
        if "organization_display_name" in google_params:
            cmd.extend(["--organization-display-name", google_params["organization_display_name"]])
        if "organization_name" in google_params:
            cmd.extend(["--organization-name", google_params["organization_name"]])
        if "id" in google_params:
            cmd.extend(["--id", google_params["id"]])
        if "limit" in google_params:
            cmd.extend(["--limit", str(google_params["limit"])])
        if "skip" in google_params:
            cmd.extend(["--skip", str(google_params["skip"])])
        if "sort" in google_params:
            cmd.extend(["--sort", google_params["sort"]])
            
    elif base_action == "update":
        cmd.extend(["update", "--id", google_params["id"]])
        cmd.extend(["--connection-identifier", google_params["connection_identifier"]])
        
    elif base_action == "update_acls":
        cmd.extend(["update-acls", "--id", google_params["id"]])
        cmd.extend(["--applyacls-jsonfile", google_params["applyacls_jsonfile"]])
        
    elif base_action == "get_key_rings":
        cmd.append("get-key-rings")
        
        # Handle JSON file parameter first
        if "gcp_getkeyrings_jsonfile" in google_params:
            cmd.extend(["--gcp-getkeyrings-jsonfile", google_params["gcp_getkeyrings_jsonfile"]])
        else:
            # Individual parameters - all required according to documentation
            cmd.extend(["--connection-identifier", google_params["connection_identifier"]])
            cmd.extend(["--project-id", google_params["project_id"]])
            cmd.extend(["--location", google_params["location"]])
            if "page_size" in google_params:
                cmd.extend(["--page-size", str(google_params["page_size"])])
            if "page_token" in google_params:
                cmd.extend(["--page-token", google_params["page_token"]])
        
    elif base_action == "add_key_rings":
        cmd.append("add-key-rings")
        
        # Handle JSON file parameters - check in priority order
        if "gcp_addkeyrings_jsonfile" in google_params:
            # Complete format with connection and project context
            cmd.extend(["--gcp-addkeyrings-jsonfile", google_params["gcp_addkeyrings_jsonfile"]])
        elif "gcp_keyrings_jsonfile" in google_params:
            # Key rings only format - requires connection_identifier and project_id as separate parameters
            cmd.extend(["--gcp-keyrings-jsonfile", google_params["gcp_keyrings_jsonfile"]])
            if "connection_identifier" in google_params:
                cmd.extend(["--connection-identifier", google_params["connection_identifier"]])
            if "project_id" in google_params:
                cmd.extend(["--project-id", google_params["project_id"]])
        elif "keyring_name" in google_params:
            # Auto-create JSON file from keyring_name parameter
            project_id = google_params.get("project_id")
            connection_identifier = google_params.get("connection_identifier")
            
            if not project_id:
                raise ValueError("project_id is required when using keyring_name parameter")
            if not connection_identifier:
                raise ValueError("connection_identifier is required when using keyring_name parameter")
            
            # Create keyring data - use keyring_name as-is for add operation
            keyrings_data = [{"name": google_params["keyring_name"]}]
            
            # Create temporary JSON file with proper connection identifier
            # Always use connection name by default for add operations
            json_file_path = create_keyrings_json_file(keyrings_data, project_id, connection_identifier)
            
            cmd.extend(["--gcp-addkeyrings-jsonfile", json_file_path])
        else:
            # Individual parameters (fallback)
            if "connection_identifier" in google_params:
                cmd.extend(["--connection-identifier", google_params["connection_identifier"]])
            if "project_id" in google_params:
                cmd.extend(["--project-id", google_params["project_id"]])
    else:
        raise ValueError(f"Unsupported keyring action: {action}")
    
    return cmd 