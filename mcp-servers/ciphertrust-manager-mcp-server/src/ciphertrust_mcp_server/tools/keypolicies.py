"""Key policy management tools for CipherTrust Manager with built-in domain support."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


class KeyPolicyListParams(BaseModel):
    """Parameters for listing key policies."""
    limit: Optional[int] = Field(None, description="Maximum number of key policies to return")
    key_policy_skip: Optional[int] = Field(None, description="Offset at which to start the search")
    id: Optional[str] = Field(None, description="Name or ID of the key policy")
    name: Optional[str] = Field(None, description="Name of the key policy")
    description: Optional[str] = Field(None, description="Description of key policy")
    labels: Optional[str] = Field(None, description="Labels on which the key policy is applied")
    permissions_contains: Optional[str] = Field(None, description="Permissions applied on key policy")
    created_after: Optional[str] = Field(None, description="Time after which the key policy is created")
    created_before: Optional[str] = Field(None, description="Time before which the key policy is created")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to list key policies from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class KeyPolicyCreateParams(BaseModel):
    """Parameters for creating a key policy."""
    name: str = Field(..., description="Name of the key policy")
    label_selector: str = Field(..., description="Label selector on which the key policy is applied")
    permissions: Optional[str] = Field(None, description="Permissions for users, clients and groups (JSON string)")
    permissions_jsonfile: Optional[str] = Field(None, description="File containing permissions in JSON format")
    description: Optional[str] = Field(None, description="Description of the key policy")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to create key policy in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class KeyPolicyGetParams(BaseModel):
    """Parameters for getting a key policy."""
    id: str = Field(..., description="Name or ID of the key policy")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to get key policy from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class KeyPolicyUpdateParams(BaseModel):
    """Parameters for updating a key policy."""
    id: str = Field(..., description="Name or ID of the key policy")
    description: Optional[str] = Field(None, description="New description of the key policy")
    label_selector: Optional[str] = Field(None, description="New label selector for the key policy")
    permissions: Optional[str] = Field(None, description="New permissions for users, clients and groups (JSON string)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to update key policy in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class KeyPolicyDeleteParams(BaseModel):
    """Parameters for deleting a key policy."""
    id: str = Field(..., description="Name or ID of the key policy")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to delete key policy from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class KeyPolicyManagementTool(BaseTool):
    name = "key_policy_management"
    description = "Key policy management operations (list, create, get, update, delete)"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["list", "create", "get", "update", "delete"]},
                **KeyPolicyListParams.model_json_schema()["properties"],
                **KeyPolicyCreateParams.model_json_schema()["properties"],
                **KeyPolicyGetParams.model_json_schema()["properties"],
                **KeyPolicyUpdateParams.model_json_schema()["properties"],
                **KeyPolicyDeleteParams.model_json_schema()["properties"],
            },
            "required": ["action"],
        }

    async def execute(self, action: str, **kwargs: Any) -> Any:
        if action == "list":
            params = KeyPolicyListParams(**kwargs)
            args = ["key-policy", "list"]
            if params.limit is not None:
                args.extend(["--limit", str(params.limit)])
            if params.key_policy_skip is not None:
                args.extend(["--keyPolicySkip", str(params.key_policy_skip)])
            if params.id:
                args.extend(["--id", params.id])
            if params.name:
                args.extend(["--name", params.name])
            if params.description:
                args.extend(["--description", params.description])
            if params.labels:
                args.extend(["--labels", params.labels])
            if params.permissions_contains:
                args.extend(["--permissionsContains", params.permissions_contains])
            if params.created_after:
                args.extend(["--createdAfter", params.created_after])
            if params.created_before:
                args.extend(["--createdBefore", params.created_before])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "create":
            params = KeyPolicyCreateParams(**kwargs)
            if not params.permissions and not params.permissions_jsonfile:
                raise ValueError("Either permissions or permissions_jsonfile must be specified")
            args = ["key-policy", "create"]
            args.extend(["--name", params.name])
            args.extend(["--label-selector", params.label_selector])
            if params.permissions:
                args.extend(["--permissions", params.permissions])
            elif params.permissions_jsonfile:
                args.extend(["--permissions-jsonfile", params.permissions_jsonfile])
            if params.description:
                args.extend(["--description", params.description])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "get":
            params = KeyPolicyGetParams(**kwargs)
            args = ["key-policy", "get", "--id", params.id]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "update":
            params = KeyPolicyUpdateParams(**kwargs)
            args = ["key-policy", "update", "--id", params.id]
            if params.description:
                args.extend(["--description", params.description])
            if params.label_selector:
                args.extend(["--label-selector", params.label_selector])
            if params.permissions:
                args.extend(["--permissions", params.permissions])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "delete":
            params = KeyPolicyDeleteParams(**kwargs)
            args = ["key-policy", "delete", "--id", params.id]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")


# Export all key policy tools
KEY_POLICY_TOOLS = [KeyPolicyManagementTool]
