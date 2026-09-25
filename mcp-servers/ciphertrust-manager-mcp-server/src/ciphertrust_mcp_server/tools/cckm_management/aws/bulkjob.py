"""AWS Bulk Job operations for CCKM."""
from typing import Any, Dict

def get_bulkjob_operations() -> Dict[str, Any]:
    """Return schema and action requirements for AWS bulk job operations."""
    return {
        "schema_properties": {
            "aws_bulkjob_params": {
                "type": "object",
                "properties": {
                    "bulkjob_keys_id": {"type": "string", "description": "ID of the keys for the bulk job"},
                    "bulkjob_operation": {"type": "string", "description": "Operation to be performed in the bulk job"},
                    "days": {"type": "integer", "description": "Days parameter for bulk job operations"},
                    "policy_template_id": {"type": "string", "description": "ID of the policy template to apply"},
                    "job_id": {"type": "string", "description": "Bulk job ID"},
                    "limit": {"type": "integer", "description": "Maximum number of results to return"},
                    "skip": {"type": "integer", "description": "Number of results to skip"},
                    "sort": {"type": "string", "description": "Sort parameter"},
                    "cloud_name": {"type": "string", "description": "Filter by cloud name"},
                    "overall_status": {"type": "string", "description": "Filter by overall status"},
                    "id": {"type": "string", "description": "Resource identifier for filtering"}
                }
            }
        },
        "action_requirements": {
            "bulkjob_list": {"required": [], "optional": ["limit", "skip", "sort", "cloud_name", "overall_status", "id"]},
            "bulkjob_get": {"required": ["job_id"], "optional": []},
            "bulkjob_create": {
                "required": ["bulkjob_keys_id", "bulkjob_operation"],
                "optional": ["days", "policy_template_id"]
            },
            "bulkjob_cancel": {"required": ["job_id"], "optional": []},
        }
    }

def build_bulkjob_command(action: str, aws_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given AWS bulk job operation."""
    cmd = ["cckm", "aws", "bulkjob"]
    
    # Extract the base operation name (remove 'bulkjob_' prefix)
    base_action = action.replace("bulkjob_", "")
    
    # Simple actions that only need --id parameter
    simple_actions = ["get", "cancel"]
    
    if base_action in simple_actions:
        cmd.extend([base_action, "--id", aws_params["job_id"]])
        return cmd
    
    if base_action == "list":
        cmd.append("list")
        if "limit" in aws_params:
            cmd.extend(["--limit", str(aws_params["limit"])])
        if "skip" in aws_params:
            cmd.extend(["--skip", str(aws_params["skip"])])
        if "sort" in aws_params:
            cmd.extend(["--sort", aws_params["sort"]])
        if "cloud_name" in aws_params:
            cmd.extend(["--cloud-name", aws_params["cloud_name"]])
        if "overall_status" in aws_params:
            cmd.extend(["--overall-status", aws_params["overall_status"]])
        if "id" in aws_params:
            cmd.extend(["--id", aws_params["id"]])
            
    elif base_action == "create":
        cmd.append("create")
        cmd.extend(["--bulkjob-keys-id", aws_params["bulkjob_keys_id"]])
        cmd.extend(["--bulkjob-operation", aws_params["bulkjob_operation"]])
        
        if "days" in aws_params:
            cmd.extend(["--days", str(aws_params["days"])])
        if "policy_template_id" in aws_params:
            cmd.extend(["--policy-template-id", aws_params["policy_template_id"]])
    else:
        raise ValueError(f"Unsupported bulk job action: {action}")
        
    return cmd
