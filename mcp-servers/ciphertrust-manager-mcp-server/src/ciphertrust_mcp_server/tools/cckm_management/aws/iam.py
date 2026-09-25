"""AWS IAM operations for CCKM."""
from typing import Any, Dict

def get_iam_operations() -> Dict[str, Any]:
    """Return schema and action requirements for AWS IAM operations."""
    return {
        "action_requirements": {
            "iam-get-iam-roles": {"required": ["kms"], "optional": ["path_prefix", "max_items", "marker"]},
            "iam-get-iam-users": {"required": ["kms"], "optional": ["path_prefix", "max_items", "marker"]}
        }
    }

def build_iam_command(action: str, aws_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given AWS IAM operation."""
    cmd = ["cckm", "aws", "iam"]
    if action == "iam-get-iam-roles":
        cmd.extend(["get-iam-roles", "--kms", aws_params["kms"]])
        if aws_params.get("path_prefix"):
            cmd.extend(["--path-prefix", aws_params["path_prefix"]])
        if aws_params.get("max_items"):
            cmd.extend(["--max-items", str(aws_params["max_items"])])
        if aws_params.get("marker"):
            cmd.extend(["--marker", aws_params["marker"]])
    elif action == "iam-get-iam-users":
        cmd.extend(["get-iam-users", "--kms", aws_params["kms"]])
        if aws_params.get("path_prefix"):
            cmd.extend(["--path-prefix", aws_params["path_prefix"]])
        if aws_params.get("max_items"):
            cmd.extend(["--max-items", str(aws_params["max_items"])])
        if aws_params.get("marker"):
            cmd.extend(["--marker", aws_params["marker"]])
    return cmd
