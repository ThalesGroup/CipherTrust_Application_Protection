"""Connection users management tools for CipherTrust Manager with built-in domain support."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


# Connection Users Parameter Models
class ConnectionUsersListParams(BaseModel):
    """Parameters for listing users belonging to a connection."""
    id: str = Field(..., description="ID of the connection")
    limit: int = Field(10, description="Maximum number of users to return")
    skip: int = Field(0, description="Offset at which to start the search")
    username: Optional[str] = Field(None, description="Filter by username")
    useremail: Optional[str] = Field(None, description="Filter by user email")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to list users from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class ConnectionUsersGetParams(BaseModel):
    """Parameters for getting a user belonging to a connection."""
    id: str = Field(..., description="ID of the connection")
    user_id: Optional[str] = Field(None, description="ID of the user (optional for token owner)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to get user from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


# Connection Users Management Tools
class ConnectionUsersManagementTool(BaseTool):
    """Manage connection users (grouped)."""

    @property
    def name(self) -> str:
        return "connection_users_management"

    @property
    def description(self) -> str:
        return "Manage users belonging to a connection (list, get)"

    def get_schema(self) -> dict[str, Any]:
        return {
            "title": "ConnectionUsersManagementTool",
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "get"],
                    "description": "Action to perform"
                },
                # Merge all params from the old tool classes
            },
            "required": ["action"]
        }

    async def execute(self, **kwargs: Any) -> Any:
        action = kwargs.get("action")
        if action == "list":
            params = ConnectionUsersListParams(**kwargs)
            args = ["connections", "users", "list"]
            args.extend(["--id", params.id])
            args.extend(["--limit", str(params.limit)])
            args.extend(["--skip", str(params.skip)])
            if params.username:
                args.extend(["--username", params.username])
            if params.useremail:
                args.extend(["--useremail", params.useremail])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "get":
            params = ConnectionUsersGetParams(**kwargs)
            args = ["connections", "users", "get"]
            args.extend(["--id", params.id])
            if params.user_id:
                args.extend(["--user-id", params.user_id])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")


# Export only the grouped tool
CONNECTION_USERS_TOOLS = [ConnectionUsersManagementTool]
