"""Azure common operations for CCKM (subscriptions, reports, bulkjob)."""

from typing import Any, Dict


def get_subscription_operations() -> Dict[str, Any]:
    """Return schema and action requirements for Azure subscription operations."""
    return {
        "schema_properties": {
            "azure_subscriptions_params": {
                "type": "object",
                "properties": {
                    "subscription_id": {"type": "string", "description": "Azure subscription ID"},
                    "subscription_name": {"type": "string", "description": "Azure subscription name"},
                    "tenant_id": {"type": "string", "description": "Azure tenant ID"},
                    "state": {"type": "string", "description": "Subscription state"},
                    "limit": {"type": "integer", "description": "Maximum number of results"},
                    "skip": {"type": "integer", "description": "Number of results to skip"},
                    "id": {"type": "string", "description": "Subscription ID"}
                }
            }
        },
        "action_requirements": {
            "subscriptions_list": {"required": [], "optional": ["limit", "skip"]},
            "subscriptions_get": {"required": ["id"], "optional": []},
            "subscriptions_get_subscriptions": {"required": [], "optional": []},
        }
    }


def get_report_operations() -> Dict[str, Any]:
    """Return schema and action requirements for Azure report operations."""
    return {
        "schema_properties": {
            "azure_reports_params": {
                "type": "object",
                "properties": {
                    "report_type": {"type": "string", "description": "Report type"},
                    "report_format": {"type": "string", "description": "Report format"},
                    "filters": {"type": "object", "description": "Report filters"},
                    "job_id": {"type": "string", "description": "Report job ID"},
                    "file_path": {"type": "string", "description": "File path for download"},
                    "id": {"type": "string", "description": "Report ID"},
                    "limit": {"type": "integer", "description": "Maximum number of results"},
                    "skip": {"type": "integer", "description": "Number of results to skip"}
                }
            }
        },
        "action_requirements": {
            "reports_list": {"required": [], "optional": ["limit", "skip"]},
            "reports_get": {"required": ["id"], "optional": []},
            "reports_generate": {"required": ["report_type"], "optional": ["report_format", "filters"]},
            "reports_download": {"required": ["id"], "optional": ["file_path"]},
            "reports_delete": {"required": ["id"], "optional": []},
            "reports_get_report": {"required": ["id"], "optional": []},
        }
    }


def get_bulkjob_operations() -> Dict[str, Any]:
    """Return schema and action requirements for Azure bulkjob operations."""
    return {
        "schema_properties": {
            "azure_bulkjob_params": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "string", "description": "Bulk job ID"},
                    "id": {"type": "string", "description": "Job ID"},
                    "bulkjob_operation": {"type": "string", "description": "Bulk job operation (e.g., delete-key-backups)"},
                    "operation": {"type": "string", "description": "Bulk operation type"},
                    "parameters": {"type": "object", "description": "Bulk job parameters"},
                    "status": {"type": "string", "description": "Job status"},
                    "backups": {"type": "string", "description": "Comma-separated backup IDs"},
                    "created_after": {"type": "string", "description": "Filter by created after date"},
                    "created_before": {"type": "string", "description": "Filter by created before date"},
                    "limit": {"type": "integer", "description": "Maximum number of results"},
                    "skip": {"type": "integer", "description": "Number of results to skip"}
                }
            }
        },
        "action_requirements": {
            "bulkjob_list": {"required": [], "optional": ["limit", "skip"]},
            "bulkjob_get": {"required": ["id"], "optional": []},
            "bulkjob_create": {"required": ["bulkjob_operation"], "optional": ["backups", "created_after", "created_before"]},
            "bulkjob_cancel": {"required": ["id"], "optional": []},
            "bulkjob_delete": {"required": ["id"], "optional": []},
        }
    }


def build_common_command(action: str, azure_params: Dict[str, Any]) -> list:
    """Build commands for subscriptions, reports, and bulkjob operations."""
    if action.startswith("subscriptions_"):
        cmd = ["cckm", "azure", "subscriptions"]
        base_action = action.replace("subscriptions_", "")
        
        if base_action == "list":
            cmd.append("list")
            if "limit" in azure_params:
                cmd.extend(["--limit", str(azure_params["limit"])])
            if "skip" in azure_params:
                cmd.extend(["--skip", str(azure_params["skip"])])
        elif base_action == "get":
            cmd.extend(["get", "--id", azure_params["id"]])
        elif base_action == "get_subscriptions":
            cmd.append("get-subscriptions")
            
    elif action.startswith("reports_"):
        cmd = ["cckm", "azure", "reports"]
        base_action = action.replace("reports_", "")
        
        if base_action == "list":
            cmd.append("list")
            if "limit" in azure_params:
                cmd.extend(["--limit", str(azure_params["limit"])])
            if "skip" in azure_params:
                cmd.extend(["--skip", str(azure_params["skip"])])
        elif base_action == "get":
            cmd.extend(["get", "--id", azure_params["id"]])
        elif base_action == "generate":
            cmd.extend(["generate", "--report-type", azure_params["report_type"]])
            if "report_format" in azure_params:
                cmd.extend(["--report-format", azure_params["report_format"]])
        elif base_action == "download":
            cmd.extend(["download", "--id", azure_params["id"]])
            if "file_path" in azure_params:
                cmd.extend(["--file-path", azure_params["file_path"]])
        elif base_action == "delete":
            cmd.extend(["delete", "--id", azure_params["id"]])
        elif base_action == "get_report":
            cmd.extend(["get-report", "--id", azure_params["id"]])
            
    elif action.startswith("bulkjob_"):
        cmd = ["cckm", "azure", "bulkjob"]
        base_action = action.replace("bulkjob_", "")
        
        if base_action == "list":
            cmd.append("list")
            if "limit" in azure_params:
                cmd.extend(["--limit", str(azure_params["limit"])])
            if "skip" in azure_params:
                cmd.extend(["--skip", str(azure_params["skip"])])
        elif base_action == "get":
            cmd.extend(["get", "--id", azure_params["id"]])
        elif base_action == "create":
            cmd.extend(["create", "--bulkjob-operation", azure_params["bulkjob_operation"]])
            if "backups" in azure_params:
                cmd.extend(["--backups", azure_params["backups"]])
            if "created_after" in azure_params:
                cmd.extend(["--created-after", azure_params["created_after"]])
            if "created_before" in azure_params:
                cmd.extend(["--created-before", azure_params["created_before"]])
        elif base_action == "cancel":
            cmd.extend(["cancel", "--id", azure_params["id"]])
        elif base_action == "delete":
            cmd.extend(["delete", "--id", azure_params["id"]])
    else:
        raise ValueError(f"Unsupported Azure common action: {action}")
    
    return cmd 