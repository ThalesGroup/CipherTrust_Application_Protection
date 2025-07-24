"""Group management tools for CipherTrust Manager with built-in domain support."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


class GroupListParams(BaseModel):
    """Parameters for listing groups."""
    limit: int = Field(10, description="Maximum number of groups to return")
    skip: int = Field(0, description="Offset at which to start the search")
    client_filter: Optional[str] = Field(None, description="ID of the client whose groups are to be enumerated")
    connection_id: Optional[str] = Field(None, description="ID of the connection whose groups are to be enumerated")
    user_filter: Optional[str] = Field(None, description="ID of the user whose groups are to be enumerated")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to list groups from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class GroupCreateParams(BaseModel):
    """Parameters for creating a group."""
    name: str = Field(..., description="Group name")
    description: Optional[str] = Field(None, description="Description of the group")
    ids: Optional[str] = Field(None, description="Comma-separated list of user IDs that belong to the group")
    jsonfile: Optional[str] = Field(None, description="Group information passed in JSON format via a file")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to create group in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class GroupGetParams(BaseModel):
    """Parameters for getting a group."""
    name: str = Field(..., description="Group name")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to get group from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class GroupDeleteParams(BaseModel):
    """Parameters for deleting a group."""
    name: str = Field(..., description="Group name")
    force: bool = Field(False, description="When true, groupmaps within this group will be deleted")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to delete group from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class GroupAddUserParams(BaseModel):
    """Parameters for adding a user to a group."""
    name: str = Field(..., description="Group name")
    userid: str = Field(..., description="ID of user to be added to the group")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to modify group in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class GroupRemoveUserParams(BaseModel):
    """Parameters for removing a user from a group."""
    name: str = Field(..., description="Group name")
    userid: str = Field(..., description="ID of user to be removed from the group")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to modify group in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class GroupAddClientParams(BaseModel):
    """Parameters for adding a client to a group."""
    name: str = Field(..., description="Group name")
    clientid: str = Field(..., description="ID of client to be added to the group")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to modify group in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class GroupRemoveClientParams(BaseModel):
    """Parameters for removing a client from a group."""
    name: str = Field(..., description="Group name")
    clientid: str = Field(..., description="ID of client to be removed from the group")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to modify group in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class GroupManagementTool(BaseTool):
    name = "group_management"
    description = "Group management operations (list, create, get, delete, add_user, remove_user, add_client, remove_client)"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": [
                    "list", "create", "get", "delete", "add_user", "remove_user", "add_client", "remove_client"
                ]},
                # ... all possible parameters ...
            },
            "required": ["action"],
        }

    async def execute(self, **kwargs: Any) -> Any:
        action = kwargs.get("action")
        if action == "list":
            params = GroupListParams(**kwargs)
            args = ["groups", "list"]
            args.extend(["--limit", str(params.limit)])
            args.extend(["--skip", str(params.skip)])
            if params.client_filter:
                args.extend(["--clientfilter", params.client_filter])
            if params.connection_id:
                args.extend(["--connectionId", params.connection_id])
            if params.user_filter:
                args.extend(["--userfilter", params.user_filter])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "create":
            params = GroupCreateParams(**kwargs)
            args = ["groups", "create", "--name", params.name]
            if params.description:
                args.extend(["--description", params.description])
            if params.ids:
                args.extend(["--ids", params.ids])
            if params.jsonfile:
                args.extend(["--jsonfile", params.jsonfile])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "get":
            params = GroupGetParams(**kwargs)
            args = ["groups", "get", "--name", params.name]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "delete":
            params = GroupDeleteParams(**kwargs)
            args = ["groups", "delete", "--name", params.name]
            if params.force:
                args.append("--force")
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "add_user":
            params = GroupAddUserParams(**kwargs)
            args = ["groups", "adduser", "--name", params.name, "--userid", params.userid]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "remove_user":
            params = GroupRemoveUserParams(**kwargs)
            args = ["groups", "rmuser", "--name", params.name, "--userid", params.userid]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "add_client":
            params = GroupAddClientParams(**kwargs)
            args = ["groups", "addclient", "--name", params.name, "--clientid", params.clientid]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "remove_client":
            params = GroupRemoveClientParams(**kwargs)
            args = ["groups", "rmclient", "--name", params.name, "--clientid", params.clientid]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")


# Export all group tools
GROUP_TOOLS = [GroupManagementTool]
