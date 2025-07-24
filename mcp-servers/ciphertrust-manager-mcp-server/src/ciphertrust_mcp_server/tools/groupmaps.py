"""Group mapping management tools for CipherTrust Manager with built-in domain support."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


class GroupMapListParams(BaseModel):
    """Parameters for listing group mappings."""
    limit: int = Field(10, description="Maximum number of group mappings to return")
    skip: int = Field(0, description="Offset at which to start the search")
    connection_name: Optional[str] = Field(None, description="Filter by connection name")
    connection_group: Optional[str] = Field(None, description="Filter by connection group name (supports wildcards)")
    ks_group: Optional[str] = Field(None, description="Filter by CipherTrust Manager group name")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to list group mappings from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class GroupMapCreateParams(BaseModel):
    """Parameters for creating a group mapping."""
    connection_name: str = Field(..., description="Connection name (LDAP or zone connection)")
    connection_group: str = Field(..., description="Connection group name")
    ks_group: str = Field(..., description="CipherTrust Manager group name")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to create group mapping in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class GroupMapGetParams(BaseModel):
    """Parameters for getting a group mapping."""
    id: str = Field(..., description="Group map ID")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to get group mapping from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class GroupMapDeleteParams(BaseModel):
    """Parameters for deleting a group mapping."""
    id: str = Field(..., description="Group map ID")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to delete group mapping from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class GroupMapModifyParams(BaseModel):
    """Parameters for modifying a group mapping."""
    id: str = Field(..., description="Group map ID")
    ks_group: str = Field(..., description="New CipherTrust Manager group name")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to modify group mapping in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class GroupMapManagementTool(BaseTool):
    name = "groupmap_management"
    description = "Group mapping management operations (list, create, get, delete, modify)"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["list", "create", "get", "delete", "modify"]},
                **GroupMapListParams.model_json_schema()["properties"],
                **GroupMapCreateParams.model_json_schema()["properties"],
                **GroupMapGetParams.model_json_schema()["properties"],
                **GroupMapDeleteParams.model_json_schema()["properties"],
                **GroupMapModifyParams.model_json_schema()["properties"],
            },
            "required": ["action"],
        }

    async def execute(self, action: str, **kwargs: Any) -> Any:
        if action == "list":
            params = GroupMapListParams(**kwargs)
            args = ["groupmaps", "list"]
            args.extend(["--limit", str(params.limit)])
            args.extend(["--skip", str(params.skip)])
            if params.connection_name:
                args.extend(["--connection-name", params.connection_name])
            if params.connection_group:
                args.extend(["--connection-group", params.connection_group])
            if params.ks_group:
                args.extend(["--ks-group", params.ks_group])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "create":
            params = GroupMapCreateParams(**kwargs)
            args = ["groupmaps", "create"]
            args.extend(["--connection-name", params.connection_name])
            args.extend(["--connection-group", params.connection_group])
            args.extend(["--ks-group", params.ks_group])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "get":
            params = GroupMapGetParams(**kwargs)
            args = ["groupmaps", "get", "--id", params.id]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "delete":
            params = GroupMapDeleteParams(**kwargs)
            args = ["groupmaps", "delete", "--id", params.id]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "modify":
            params = GroupMapModifyParams(**kwargs)
            args = ["groupmaps", "modify"]
            args.extend(["--id", params.id])
            args.extend(["--ks-group", params.ks_group])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")

GROUPMAP_TOOLS = [GroupMapManagementTool]
