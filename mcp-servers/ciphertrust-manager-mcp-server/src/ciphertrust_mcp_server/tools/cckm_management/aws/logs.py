"""AWS Logs operations for CCKM."""
from typing import Any, Dict

def get_logs_operations() -> Dict[str, Any]:
    """Return schema and action requirements for AWS log operations."""
    return {
        "schema_properties": {
            "aws_logs_params": {
                "type": "object",
                "properties": {
                    "kms": {"type": "string", "description": "AWS KMS name or ID"},
                    "region": {"type": "string", "description": "AWS region"},
                    "limit": {"type": "integer", "description": "Maximum number of results to return"},
                    "logGroupNamePrefix": {"type": "string", "description": "Prefix to match log group names"},
                    "nextToken": {"type": "string", "description": "Token for pagination"},
                    "cloud_watch_params_json": {"type": "string", "description": "CloudWatch parameters in JSON format"},
                    "list_log_group_jsonfile": {"type": "string", "description": "List log groups parameters in JSON file"}
                }
            }
        },
        "action_requirements": {
            "logs_get_groups": {"required": ["kms", "region"], "optional": ["limit", "logGroupNamePrefix", "nextToken", "cloud_watch_params_json", "list_log_group_jsonfile"]}
        }
    }

def build_logs_command(action: str, aws_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given AWS log operation."""
    cmd = ["cckm", "aws"]
    
    if action == "get_log_groups":
        cmd.append("get-log-groups")
        cmd.extend(["--kms", aws_params["kms"]])
        cmd.extend(["--region", aws_params["region"]])
        
        if "limit" in aws_params:
            cmd.extend(["--limit", str(aws_params["limit"])])
        if "logGroupNamePrefix" in aws_params:
            cmd.extend(["--logGroupNamePrefix", aws_params["logGroupNamePrefix"]])
        if "nextToken" in aws_params:
            cmd.extend(["--nextToken", aws_params["nextToken"]])
        if "cloud_watch_params_json" in aws_params:
            cmd.extend(["--cloud-watch-params-json", aws_params["cloud_watch_params_json"]])
        if "list_log_group_jsonfile" in aws_params:
            cmd.extend(["--list-log-group-jsonfile", aws_params["list_log_group_jsonfile"]])
    
    return cmd 