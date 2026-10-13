"""Google Cloud Projects operations for CCKM."""
from typing import Any, Dict

def get_project_operations() -> Dict[str, Any]:
    """Return schema and action requirements for Google Cloud project operations."""
    return {
        "schema_properties": {
            "google_projects_params": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string", 
                        "description": "GCP Project ID"
                    },
                    "connection_identifier": {
                        "type": "string", 
                        "description": "Name or ID of the connection which has been created earlier"
                    },
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
                    "acls": {
                        "type": "string", 
                        "description": "Access control list for project"
                    }
                }
            }
        },
        "action_requirements": {
            "projects_list": {
                "required": [], 
                "optional": ["limit", "skip", "sort"]
            },
            "projects_get": {
                "required": ["project_id"], 
                "optional": []
            },
            "projects_add": {
                "required": ["project_id", "connection_identifier"], 
                "optional": []
            },
            "projects_update": {
                "required": ["project_id"], 
                "optional": []
            },
            "projects_delete": {
                "required": ["project_id"], 
                "optional": []
            },
            "projects_get_project": {
                "required": ["connection_identifier"], 
                "optional": []
            },
            "projects_update_acls": {
                "required": ["project_id", "acls"], 
                "optional": []
            }
        }
    }

def build_project_command(action: str, google_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given Google Cloud project operation."""
    cmd = ["cckm", "google", "projects"]
    
    # Extract the base operation name (remove 'projects_' prefix)
    base_action = action.replace("projects_", "")
    
    # Simple actions that only need --id parameter
    simple_actions = ["get", "delete"]
    
    if base_action in simple_actions:
        cmd.append(base_action)
        cmd.extend(["--id", google_params["project_id"]])
        return cmd
    
    # Handle specific operations
    if base_action == "list":
        cmd.append("list")
        if "limit" in google_params:
            cmd.extend(["--limit", str(google_params["limit"])])
        if "skip" in google_params:
            cmd.extend(["--skip", str(google_params["skip"])])
        if "sort" in google_params:
            cmd.extend(["--sort", google_params["sort"]])
            
    elif base_action == "add":
        cmd.append("add")
        cmd.extend(["--project_id", google_params["project_id"]])
        cmd.extend(["--connection-identifier", google_params["connection_identifier"]])
            
    elif base_action == "update":
        cmd.extend(["update", "--project_id", google_params["project_id"]])
        
    elif base_action == "get_project":
        cmd.append("get-project")
        cmd.extend(["--connection-identifier", google_params["connection_identifier"]])
        
    elif base_action == "update_acls":
        cmd.extend(["update-acls", "--project_id", google_params["project_id"]])
        cmd.extend(["--acls", google_params["acls"]])
        
    else:
        raise ValueError(f"Unsupported Google Cloud projects action: {action}")
    
    return cmd 