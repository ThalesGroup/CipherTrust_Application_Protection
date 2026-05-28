"""Google Cloud Locations operations for CCKM."""
from typing import Any, Dict

def get_location_operations() -> Dict[str, Any]:
    """Return schema and action requirements for Google Cloud location operations."""
    return {
        "schema_properties": {
            "google_locations_params": {
                "type": "object",
                "properties": {
                    "connection_identifier": {
                        "type": "string", 
                        "description": "Name or ID of the connection which has been created earlier"
                    },
                    "project_id": {
                        "type": "string", 
                        "description": "GCP Project ID"
                    },
                    "page_size": {
                        "type": "integer", 
                        "description": "Number of locations to view (optional parameter)"
                    },
                    "page_token": {
                        "type": "string", 
                        "description": "Token to get remaining locations beyond page_size (optional parameter)"
                    }
                }
            }
        },
        "action_requirements": {
            "locations_get_locations": {
                "required": ["connection_identifier", "project_id"], 
                "optional": ["page_size", "page_token"]
            }
        }
    }

def build_location_command(action: str, google_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given Google Cloud location operation."""
    cmd = ["cckm", "google", "locations"]
    
    # Extract the base operation name (remove 'locations_' prefix)
    base_action = action.replace("locations_", "")
    
    if base_action == "get_locations":
        cmd.append("get-locations")
        cmd.extend(["--connection-identifier", google_params["connection_identifier"]])
        cmd.extend(["--project-id", google_params["project_id"]])
        if "page_size" in google_params:
            cmd.extend(["--page-size", str(google_params["page_size"])])
        if "page_token" in google_params:
            cmd.extend(["--page-token", google_params["page_token"]])
    else:
        raise ValueError(f"Unsupported Google Cloud locations action: {action}")
    
    return cmd 