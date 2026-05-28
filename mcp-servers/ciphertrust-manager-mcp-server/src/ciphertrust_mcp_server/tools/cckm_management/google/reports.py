"""Google Cloud Reports operations for CCKM."""
from typing import Any, Dict

def get_reports_operations() -> Dict[str, Any]:
    """Return schema and action requirements for Google Cloud reports operations."""
    return {
        "schema_properties": {
            "google_reports_params": {
                "type": "object",
                "properties": {
                    "report_type": {
                        "type": "string", 
                        "description": "Type of report to generate"
                    },
                    "report_format": {
                        "type": "string", 
                        "description": "Format of the report"
                    },
                    "filters": {
                        "type": "object", 
                        "description": "Report filters"
                    },
                    "job_id": {
                        "type": "string", 
                        "description": "Report job ID"
                    },
                    "file_path": {
                        "type": "string", 
                        "description": "File path for report download"
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
                    }
                }
            }
        },
        "action_requirements": {
            "reports_list": {
                "required": [], 
                "optional": ["limit", "skip", "sort"]
            },
            "reports_get": {
                "required": ["job_id"], 
                "optional": []
            },
            "reports_generate": {
                "required": ["report_type"], 
                "optional": ["report_format", "filters"]
            },
            "reports_download": {
                "required": ["job_id", "file_path"], 
                "optional": []
            },
            "reports_delete": {
                "required": ["job_id"], 
                "optional": []
            },
            "reports_get_report": {
                "required": [], 
                "optional": ["limit", "skip", "sort"]
            }
        }
    }

def build_reports_command(action: str, google_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given Google Cloud reports operation."""
    cmd = ["cckm", "google", "reports"]
    
    # Extract the base operation name (remove 'reports_' prefix)
    base_action = action.replace("reports_", "")
    
    # Simple actions that only need --id parameter
    simple_actions = ["get", "delete"]
    
    if base_action in simple_actions:
        cmd.append(base_action)
        cmd.extend(["--id", google_params["job_id"]])
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
            
    elif base_action == "generate":
        cmd.append("generate-report")
        cmd.extend(["--report-type", google_params["report_type"]])
        if "report_format" in google_params:
            cmd.extend(["--report-format", google_params["report_format"]])
        if "filters" in google_params:
            cmd.extend(["--filters", str(google_params["filters"])])
            
    elif base_action == "download":
        cmd.extend(["download", "--id", google_params["job_id"]])
        cmd.extend(["--file-path", google_params["file_path"]])
        
    elif base_action == "get_report":
        cmd.append("get-report")
        if "limit" in google_params:
            cmd.extend(["--limit", str(google_params["limit"])])
        if "skip" in google_params:
            cmd.extend(["--skip", str(google_params["skip"])])
        if "sort" in google_params:
            cmd.extend(["--sort", google_params["sort"]])
            
    else:
        raise ValueError(f"Unsupported Google Cloud reports action: {action}")
    
    return cmd 