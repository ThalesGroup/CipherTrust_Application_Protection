"""AWS connection operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import AWS_PARAMETERS, CONNECTION_OPERATIONS


class AWSOperations(ConnectionOperations):
    """AWS connection operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported AWS operations."""
        return CONNECTION_OPERATIONS["aws"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for AWS operations."""
        return {
            "aws_params": {
                "type": "object",
                "properties": AWS_PARAMETERS,
                "description": "AWS-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for AWS."""
        return {
            "create": {
                "required": ["name"],
                "optional": ["clientid", "secret", "assumerolearn", "assumeroleexternalid", "iamroleanywhere", "isroleanywhere", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "list": {
                "required": [],
                "optional": ["isroleanywhere", "name", "cloudname", "category", "products", "limit", "skip", "fields", "labels_query", "lastconnectionafter", "lastconnectionbefore", "lastconnectionok", "domain", "auth_domain"]
            },
            "get": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "delete": {
                "required": ["id"],
                "optional": ["force", "domain", "auth_domain"]
            },
            "modify": {
                "required": ["id"],
                "optional": ["name", "clientid", "secret", "assumerolearn", "assumeroleexternalid", "iamroleanywhere", "isroleanywhere", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "test": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute AWS connection operation."""
        aws_params = params.get("aws_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "aws", action]
        
        # Add action-specific parameters
        if action == "create":
            if aws_params.get("name"):
                cmd.extend(["--name", aws_params["name"]])
            if aws_params.get("clientid"):
                cmd.extend(["--clientid", aws_params["clientid"]])
            if aws_params.get("secret"):
                cmd.extend(["--secret", aws_params["secret"]])
            if aws_params.get("assumerolearn"):
                cmd.extend(["--assumerolearn", aws_params["assumerolearn"]])
            if aws_params.get("assumeroleexternalid"):
                cmd.extend(["--assumeroleexternalid", aws_params["assumeroleexternalid"]])
            if aws_params.get("iamroleanywhere"):
                cmd.extend(["--iamroleanywhere", aws_params["iamroleanywhere"]])
            if aws_params.get("isroleanywhere"):
                cmd.extend(["--isroleanywhere", aws_params["isroleanywhere"]])
            if aws_params.get("products"):
                cmd.extend(["--products", aws_params["products"]])
            if aws_params.get("description"):
                cmd.extend(["--description", aws_params["description"]])
            if aws_params.get("meta"):
                cmd.extend(["--meta", aws_params["meta"]])
            if aws_params.get("labels"):
                cmd.extend(["--labels", aws_params["labels"]])
            if aws_params.get("json_file"):
                cmd.extend(["--json-file", aws_params["json_file"]])
                
        elif action == "list":
            if aws_params.get("isroleanywhere"):
                cmd.extend(["--isroleanywhere", aws_params["isroleanywhere"]])
            if aws_params.get("name"):
                cmd.extend(["--name", aws_params["name"]])
            if aws_params.get("cloudname"):
                cmd.extend(["--cloudname", aws_params["cloudname"]])
            if aws_params.get("category"):
                cmd.extend(["--category", aws_params["category"]])
            if aws_params.get("products"):
                cmd.extend(["--products", aws_params["products"]])
            if aws_params.get("limit"):
                cmd.extend(["--limit", str(aws_params["limit"])])
            if aws_params.get("skip"):
                cmd.extend(["--skip", str(aws_params["skip"])])
            if aws_params.get("fields"):
                cmd.extend(["--fields", aws_params["fields"]])
            if aws_params.get("labels_query"):
                cmd.extend(["--labels-query", aws_params["labels_query"]])
            if aws_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", aws_params["lastconnectionafter"]])
            if aws_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", aws_params["lastconnectionbefore"]])
            if aws_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", aws_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", aws_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", aws_params["id"]])
            if aws_params.get("force"):
                cmd.append("--force")
                
        elif action == "modify":
            cmd.extend(["--id", aws_params["id"]])
            if aws_params.get("name"):
                cmd.extend(["--name", aws_params["name"]])
            if aws_params.get("clientid"):
                cmd.extend(["--clientid", aws_params["clientid"]])
            if aws_params.get("secret"):
                cmd.extend(["--secret", aws_params["secret"]])
            if aws_params.get("assumerolearn"):
                cmd.extend(["--assumerolearn", aws_params["assumerolearn"]])
            if aws_params.get("assumeroleexternalid"):
                cmd.extend(["--assumeroleexternalid", aws_params["assumeroleexternalid"]])
            if aws_params.get("iamroleanywhere"):
                cmd.extend(["--iamroleanywhere", aws_params["iamroleanywhere"]])
            if aws_params.get("isroleanywhere"):
                cmd.extend(["--isroleanywhere", aws_params["isroleanywhere"]])
            if aws_params.get("products"):
                cmd.extend(["--products", aws_params["products"]])
            if aws_params.get("description"):
                cmd.extend(["--description", aws_params["description"]])
            if aws_params.get("meta"):
                cmd.extend(["--meta", aws_params["meta"]])
            if aws_params.get("labels"):
                cmd.extend(["--labels", aws_params["labels"]])
            if aws_params.get("json_file"):
                cmd.extend(["--json-file", aws_params["json_file"]])
                
        elif action == "test":
            cmd.extend(["--id", aws_params["id"]])
            
        else:
            raise ValueError(f"Unsupported AWS action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 