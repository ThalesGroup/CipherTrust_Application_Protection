"""OCI Reports operations for CCKM."""

from typing import Any, Dict


def get_reports_operations() -> Dict[str, Any]:
    """Return schema and action requirements for OCI reports operations."""
    return {
        "schema_properties": {
            "oci_reports_params": {
                "type": "object",
                "properties": {
                    # Basic report parameters
                    "id": {
                        "type": "string", 
                        "description": "OCI report job ID. CRITICAL FOR AI ASSISTANTS: Always use this 'id' parameter for report identification operations."
                    },
                    "report_name": {"type": "string", "description": "Name of your report (for generate-report) or filter by report name (for list)"},
                    "report_type": {"type": "string", "description": "Type of report to be generated. Available options: service-report, key-report, reconciliation-report, key-aging"},
                    
                    # Time parameters
                    "start_time": {"type": "string", "description": "Start time from where report to be generated. Format: ISO 8601 (e.g., '2020-08-05T09:20:48Z')"},
                    "end_time": {"type": "string", "description": "End time for reports. Format: ISO 8601 (e.g., '2020-08-06T09:20:48Z')"},
                    
                    # Common parameters
                    "limit": {"type": "integer", "description": "Maximum number of results"},
                    "skip": {"type": "integer", "description": "Number of results to skip"},
                    "sort": {"type": "string", "description": "Sort the resources on the basis of the provided parameter"},
                    
                    # Filter parameters
                    "overall_status": {"type": "string", "description": "Filter the results based on overall status parameter"},
                    "key_name": {"type": "string", "description": "Filter the results by key name"},
                    "key_activity": {"type": "string", "description": "Filter the get report results based on OCI key activity"},
                    "oci_key_id": {"type": "string", "description": "Filter the result by OCI key display name"},
                    "oci_vault_id": {"type": "string", "description": "Filter the result based on OCI vault ID"},
                    "user_name": {"type": "string", "description": "Filter resources on the basis of user name"},
                    
                    # JSON file parameters
                    "oci_report_jobs_jsonfile": {
                        "type": "string", 
                        "description": "OCI report jobs parameters passed in JSON format via a file. Use absolute file paths for reliability."
                    },
                    "oci_cloud_params_jsonfile": {
                        "type": "string", 
                        "description": "OCI cloud parameters passed in JSON format via a file. Use absolute file paths for reliability."
                    }
                }
            }
        },
        "action_requirements": {
            "reports_list": {"required": [], "optional": ["limit", "skip", "sort", "overall_status", "report_name", "report_type"]},
            "reports_get": {"required": ["id"], "optional": []},
            "reports_generate": {"required": [], "optional": ["report_name", "report_type", "start_time", "end_time", "oci_report_jobs_jsonfile", "oci_cloud_params_jsonfile"]},
            "reports_download": {"required": ["id"], "optional": []},
            "reports_delete": {"required": ["id"], "optional": []},
            "reports_get_report": {"required": ["id"], "optional": ["limit", "skip", "sort", "key_name", "key_activity", "oci_key_id", "oci_vault_id", "user_name"]},
        }
    }


def build_reports_command(action: str, oci_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given OCI reports operation."""
    cmd = ["cckm", "oci", "reports"]
    
    # Extract the base operation name (remove 'reports_' prefix)
    base_action = action.replace("reports_", "")
    
    # Simple actions that only need --id parameter
    simple_actions = ["get", "download", "delete"]
    
    if base_action in simple_actions:
        cmd.extend([base_action, "--id", oci_params["id"]])
        return cmd
    
    if base_action == "list":
        cmd.append("list")
        if "limit" in oci_params:
            cmd.extend(["--limit", str(oci_params["limit"])])
        if "skip" in oci_params:
            cmd.extend(["--skip", str(oci_params["skip"])])
        if "sort" in oci_params:
            cmd.extend(["--sort", oci_params["sort"]])
        if "overall_status" in oci_params:
            cmd.extend(["--overall-status", oci_params["overall_status"]])
        if "report_name" in oci_params:
            cmd.extend(["--report-name", oci_params["report_name"]])
        if "report_type" in oci_params:
            cmd.extend(["--report-type", oci_params["report_type"]])
            
    elif base_action == "generate":
        cmd.append("generate-report")
        
        # Handle JSON file parameter first (overrides individual parameters)
        if "oci_report_jobs_jsonfile" in oci_params:
            cmd.extend(["--oci-report-jobs-jsonfile", oci_params["oci_report_jobs_jsonfile"]])
        if "oci_cloud_params_jsonfile" in oci_params:
            cmd.extend(["--oci-cloud-params-jsonfile", oci_params["oci_cloud_params_jsonfile"]])
        
        # Individual parameters (only if JSON files not provided)
        if "oci_report_jobs_jsonfile" not in oci_params:
            if "report_name" in oci_params:
                cmd.extend(["--report-name", oci_params["report_name"]])
            if "report_type" in oci_params:
                cmd.extend(["--report-type", oci_params["report_type"]])
            if "start_time" in oci_params:
                cmd.extend(["--start-time", oci_params["start_time"]])
            if "end_time" in oci_params:
                cmd.extend(["--end-time", oci_params["end_time"]])
            
    elif base_action == "get_report":
        cmd.extend(["get-report", "--id", oci_params["id"]])
        if "limit" in oci_params:
            cmd.extend(["--limit", str(oci_params["limit"])])
        if "skip" in oci_params:
            cmd.extend(["--skip", str(oci_params["skip"])])
        if "sort" in oci_params:
            cmd.extend(["--sort", oci_params["sort"]])
        if "key_name" in oci_params:
            cmd.extend(["--key-name", oci_params["key_name"]])
        if "key_activity" in oci_params:
            cmd.extend(["--key_activity", oci_params["key_activity"]])
        if "oci_key_id" in oci_params:
            cmd.extend(["--oci-key-id", oci_params["oci_key_id"]])
        if "oci_vault_id" in oci_params:
            cmd.extend(["--oci-vault-id", oci_params["oci_vault_id"]])
        if "user_name" in oci_params:
            cmd.extend(["--user-name", oci_params["user_name"]])
        
    else:
        raise ValueError(f"Unsupported OCI reports action: {action}")
    
    return cmd 