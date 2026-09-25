"""AWS Reports operations for CCKM."""
from typing import Any, Dict

def get_reports_operations() -> Dict[str, Any]:
    """Return schema and action requirements for AWS reports operations."""
    return {
        "schema_properties": {
            "aws_reports_params": {
                "type": "object",
                "properties": {
                    # Report generation parameters
                    "report_type": {
                        "type": "string", 
                        "description": "Type of report to be generated. Available options: service-report, key-report, reconciliation-report, key-aging. Default: key-report"
                    },
                    "name": {
                        "type": "string", 
                        "description": "Unique name for the report resource"
                    },
                    "start_time": {
                        "type": "string", 
                        "description": "Start time for report generation in ISO format (e.g., 2020-08-05T09:20:48Z). If not provided with end_time, generates last 24-hour report"
                    },
                    "end_time": {
                        "type": "string", 
                        "description": "End time for report generation in ISO format (e.g., 2020-08-06T09:20:48Z). If not provided with start_time, generates last 24-hour report"
                    },
                    
                    # JSON file parameters
                    "create_report_jobs_jsonfile": {
                        "type": "string", 
                        "description": "JSON file containing complete report job parameters. Overrides individual parameters if provided"
                    },
                    "cloud_watch_params_jsonfile": {
                        "type": "string", 
                        "description": "JSON file containing CloudWatch parameters for report generation"
                    },
                    
                    # Report management parameters
                    "id": {
                        "type": "string", 
                        "description": "Report job ID for get, download, or delete operations"
                    },
                    
                    # List and filtering parameters
                    "limit": {
                        "type": "integer", 
                        "description": "Maximum number of resources to return. Default: 10"
                    },
                    "skip": {
                        "type": "integer", 
                        "description": "Number of results to skip for pagination. Default: 0"
                    },
                    "sort": {
                        "type": "string", 
                        "description": "Sort parameter for ordering results"
                    },
                    "overall_status": {
                        "type": "string", 
                        "description": "Filter results by overall status"
                    },
                    "report_name": {
                        "type": "string", 
                        "description": "Filter list results by report name"
                    },
                    
                    # get-reports specific filters
                    "key_arn": {
                        "type": "string", 
                        "description": "Filter resources by key ARN"
                    },
                    "region": {
                        "type": "string", 
                        "description": "Filter resources by AWS region"
                    },
                    "aws_account_id": {
                        "type": "string", 
                        "description": "Filter resources by AWS account ID"
                    },
                    "cloud_name": {
                        "type": "string", 
                        "description": "Filter resources by cloud name"
                    }
                }
            }
        },
        "action_requirements": {
            "reports_list": {
                "required": [], 
                "optional": ["id", "limit", "skip", "overall_status", "report_name", "report_type", "sort"]
            },
            "reports_get": {
                "required": ["id"], 
                "optional": []
            },
            "reports_get_report": {
                "required": [], 
                "optional": ["id", "key_arn", "region", "aws_account_id", "cloud_name", "limit", "skip", "sort"]
            },
            "reports_generate": {
                "required": [], 
                "optional": ["report_type", "name", "start_time", "end_time", "create_report_jobs_jsonfile", "cloud_watch_params_jsonfile"]
            },
            "reports_download": {
                "required": ["id"], 
                "optional": []
            },
            "reports_delete": {
                "required": ["id"], 
                "optional": []
            },
            "reports_get_reports": {
                "required": [], 
                "optional": ["id", "key_arn", "region", "aws_account_id", "cloud_name", "limit", "skip", "sort"]
            }
        }
    }

def build_reports_command(action: str, aws_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given AWS reports operation."""
    cmd = ["cckm", "aws", "reports"]
    
    # Extract the base operation name (remove 'reports_' prefix)
    base_action = action.replace("reports_", "")
    
    # Simple actions that only need --id parameter
    simple_actions = ["get", "download", "delete"]
    
    if base_action in simple_actions:
        cmd.extend([base_action, "--id", aws_params["id"]])
        return cmd
    
    if base_action == "list":
        cmd.append("list")
        # Add all possible list filters
        if "id" in aws_params:
            cmd.extend(["--id", aws_params["id"]])
        if "limit" in aws_params:
            cmd.extend(["--limit", str(aws_params["limit"])])
        if "skip" in aws_params:
            cmd.extend(["--skip", str(aws_params["skip"])])
        if "overall_status" in aws_params:
            cmd.extend(["--overall-status", aws_params["overall_status"]])
        if "report_name" in aws_params:
            cmd.extend(["--report-name", aws_params["report_name"]])
        if "report_type" in aws_params:
            cmd.extend(["--report-type", aws_params["report_type"]])
        if "sort" in aws_params:
            cmd.extend(["--sort", aws_params["sort"]])
            
    elif base_action == "generate":
        cmd.append("generate-report")
        
        # Handle JSON file parameter first (overrides individual parameters)
        if "create_report_jobs_jsonfile" in aws_params:
            cmd.extend(["--create-report-jobs-jsonfile", aws_params["create_report_jobs_jsonfile"]])
        else:
            # Individual parameters
            if "report_type" in aws_params:
                cmd.extend(["--report-type", aws_params["report_type"]])
            if "name" in aws_params:
                cmd.extend(["--name", aws_params["name"]])
            if "start_time" in aws_params:
                cmd.extend(["--start-time", aws_params["start_time"]])
            if "end_time" in aws_params:
                cmd.extend(["--end-time", aws_params["end_time"]])
            if "cloud_watch_params_jsonfile" in aws_params:
                cmd.extend(["--cloud-watch-params-jsonfile", aws_params["cloud_watch_params_jsonfile"]])
            
    elif base_action == "get_reports":
        cmd.append("get-reports")
        # Add all possible get-reports filters
        if "id" in aws_params:
            cmd.extend(["--id", aws_params["id"]])
        if "key_arn" in aws_params:
            cmd.extend(["--key-arn", aws_params["key_arn"]])
        if "region" in aws_params:
            cmd.extend(["--region", aws_params["region"]])
        if "aws_account_id" in aws_params:
            cmd.extend(["--aws-account-id", aws_params["aws_account_id"]])
        if "cloud_name" in aws_params:
            cmd.extend(["--cloud-name", aws_params["cloud_name"]])
        if "limit" in aws_params:
            cmd.extend(["--limit", str(aws_params["limit"])])
        if "skip" in aws_params:
            cmd.extend(["--skip", str(aws_params["skip"])])
        if "sort" in aws_params:
            cmd.extend(["--sort", aws_params["sort"]])
    elif base_action == "get_report":
        cmd.append("get-report")
        # Add all possible get-report filters (same as get-reports)
        if "id" in aws_params:
            cmd.extend(["--id", aws_params["id"]])
        if "key_arn" in aws_params:
            cmd.extend(["--key-arn", aws_params["key_arn"]])
        if "region" in aws_params:
            cmd.extend(["--region", aws_params["region"]])
        if "aws_account_id" in aws_params:
            cmd.extend(["--aws-account-id", aws_params["aws_account_id"]])
        if "cloud_name" in aws_params:
            cmd.extend(["--cloud-name", aws_params["cloud_name"]])
        if "limit" in aws_params:
            cmd.extend(["--limit", str(aws_params["limit"])])
        if "skip" in aws_params:
            cmd.extend(["--skip", str(aws_params["skip"])])
        if "sort" in aws_params:
            cmd.extend(["--sort", aws_params["sort"]])
    else:
        raise ValueError(f"Unsupported reports action: {action}")
        
    return cmd
