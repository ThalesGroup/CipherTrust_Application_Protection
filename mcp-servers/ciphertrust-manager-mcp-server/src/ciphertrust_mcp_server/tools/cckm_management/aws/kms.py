"""AWS KMS operations for CCKM."""
from typing import Any, Dict

def get_kms_operations() -> Dict[str, Any]:
    """Return schema and action requirements for AWS KMS operations."""
    return {
        "schema_properties": {
            "aws_kms_params": {
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "ID of the AWS account"},
                    "regions": {"type": "array", "items": {"type": "string"}, "description": "List of AWS regions"},
                    "name": {"type": "string", "description": "Unique name for the KMS"},
                    "connection_identifier": {"type": "string", "description": "Name or ID of the connection"},
                    "assume_role_arn": {"type": "string", "description": "ARN of the Assume Role"},
                    "assume_role_ext_id": {"type": "string", "description": "External ID of the Assume Role"},
                    "id": {"type": "string", "description": "KMS ID"},
                    "acls": {"type": "string", "description": "ACLs in JSON format"},
                    "limit": {"type": "integer", "description": "Maximum number of results to return"},
                    "skip": {"type": "integer", "description": "Number of results to skip"},
                    "kms": {"type": "string", "description": "KMS name or ID for filtering"},
                    "aws_kmsadd_jsonfile": {"type": "string", "description": "AWS KMS add parameters in JSON file"},
                    "applyacls_jsonfile": {"type": "string", "description": "Apply ACLs parameters in JSON file"}
                }
            }
        },
        "action_requirements": {
            "kms_list": {"required": [], "optional": ["limit", "skip", "account_id", "id", "kms"]},
            "kms_get": {"required": ["id"], "optional": []},
            "kms_add": {
                "required": ["account_id", "regions", "name", "connection_identifier"],
                "optional": ["assume_role_arn", "assume_role_ext_id", "aws_kmsadd_jsonfile"]
            },
            "kms_update": {
                "required": ["id"],
                "optional": ["regions", "connection_identifier", "assume_role_arn", "assume_role_ext_id"]
            },
            "kms_delete": {"required": ["id"], "optional": []},
            "kms_archive": {"required": ["id"], "optional": []},
            "kms_recover": {"required": ["id"], "optional": []},
            "kms_get_account": {"required": [], "optional": ["connection_identifier", "assume_role_arn", "assume_role_ext_id"]},
            "kms_get_all_regions": {"required": [], "optional": ["connection_identifier"]},
            "kms_update_acls": {"required": ["id"], "optional": ["acls", "applyacls_jsonfile"]},
        }
    }

def build_kms_command(action: str, aws_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given AWS KMS operation."""
    cmd = ["cckm", "aws", "kms"]
    
    # Extract the base operation name (remove 'kms_' prefix)
    base_action = action.replace("kms_", "")
    
    # Simple actions that only need --id parameter
    simple_actions = ["delete", "archive", "recover", "get"]
    
    if base_action in simple_actions:
        cmd.extend([base_action, "--id", aws_params["id"]])
        return cmd
    
    if base_action == "list":
        cmd.append("list")
        if "limit" in aws_params:
            cmd.extend(["--limit", str(aws_params["limit"])])
        if "skip" in aws_params:
            cmd.extend(["--skip", str(aws_params["skip"])])
        if "account_id" in aws_params:
            cmd.extend(["--account-id", aws_params["account_id"]])
        if "id" in aws_params:
            cmd.extend(["--id", aws_params["id"]])
        if "kms" in aws_params:
            cmd.extend(["--kms", aws_params["kms"]])
            
    elif base_action == "add":
        cmd.append("add")
        cmd.extend(["--account-id", aws_params["account_id"]])
        cmd.extend(["--regions", ",".join(aws_params["regions"])])
        cmd.extend(["--name", aws_params["name"]])
        cmd.extend(["--connection-identifier", aws_params["connection_identifier"]])
        
        if "assume_role_arn" in aws_params:
            cmd.extend(["--assume-role-arn", aws_params["assume_role_arn"]])
        if "assume_role_ext_id" in aws_params:
            cmd.extend(["--assume-role-ext-id", aws_params["assume_role_ext_id"]])
        if "aws_kmsadd_jsonfile" in aws_params:
            cmd.extend(["--aws-kmsadd-jsonfile", aws_params["aws_kmsadd_jsonfile"]])
            
    elif base_action == "update":
        cmd.append("update")
        cmd.extend(["--id", aws_params["id"]])
        
        if "regions" in aws_params:
            cmd.extend(["--regions", ",".join(aws_params["regions"])])
        if "connection_identifier" in aws_params:
            cmd.extend(["--connection-identifier", aws_params["connection_identifier"]])
        if "assume_role_arn" in aws_params:
            cmd.extend(["--assume-role-arn", aws_params["assume_role_arn"]])
        if "assume_role_ext_id" in aws_params:
            cmd.extend(["--assume-role-ext-id", aws_params["assume_role_ext_id"]])
            
    elif base_action == "get_account":
        cmd.append("get-account")
        
        if "connection_identifier" in aws_params:
            cmd.extend(["--connection-identifier", aws_params["connection_identifier"]])
        if "assume_role_arn" in aws_params:
            cmd.extend(["--assume-role-arn", aws_params["assume_role_arn"]])
        if "assume_role_ext_id" in aws_params:
            cmd.extend(["--assume-role-ext-id", aws_params["assume_role_ext_id"]])
            
    elif base_action == "get_all_regions":
        cmd.append("get-all-regions")
        
        if "connection_identifier" in aws_params:
            cmd.extend(["--connection-identifier", aws_params["connection_identifier"]])
            
    elif base_action == "update_acls":
        cmd.append("update-acls")
        cmd.extend(["--id", aws_params["id"]])
        
        if "acls" in aws_params:
            cmd.extend(["--acls", aws_params["acls"]])
        if "applyacls_jsonfile" in aws_params:
            cmd.extend(["--applyacls-jsonfile", aws_params["applyacls_jsonfile"]])
    else:
        raise ValueError(f"Unsupported KMS action: {action}")
        
    return cmd
