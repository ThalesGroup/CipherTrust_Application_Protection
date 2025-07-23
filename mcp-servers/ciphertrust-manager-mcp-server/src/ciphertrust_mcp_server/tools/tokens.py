"""Token management tools for CipherTrust Manager with built-in domain support."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


class TokenCreateParams(BaseModel):
    """Parameters for token creation."""
    issue_rt: bool = Field(False, description="Generate/renew a refresh token along with access token")
    labels: Optional[str] = Field(None, description="Comma separated labels for tagging the refresh token")
    refresh_token: Optional[str] = Field(None, description="Refresh token to be refreshed/revoked")
    rt_life: Optional[int] = Field(None, description="Lifetime for refresh token in minutes")
    rt_unused_life: Optional[int] = Field(None, description="Revoke refresh token if not used within specified time in minutes")
    user: Optional[str] = Field(None, description="CipherTrust Manager username (if not using env/config)")
    password: Optional[str] = Field(None, description="CipherTrust Manager password (if not using env/config)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to create token in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class TokenListParams(BaseModel):
    """Parameters for listing tokens."""
    expired: bool = Field(False, description="Include expired refresh tokens")
    labels: Optional[str] = Field(None, description="Comma separated labels for filtering tokens")
    limit: int = Field(10, description="Maximum number of tokens to return")
    skip: int = Field(0, description="Offset at which to start the search")
    revoked: bool = Field(False, description="Include revoked refresh tokens")
    user_id: Optional[str] = Field(None, description="ID of the user whose tokens to list")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to list tokens from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class TokenGetParams(BaseModel):
    """Parameters for getting a token."""
    id: str = Field(..., description="Token ID")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to get token from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class TokenDeleteParams(BaseModel):
    """Parameters for deleting a token."""
    id: str = Field(..., description="Token ID")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to delete token from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class TokenRevokeParams(BaseModel):
    """Parameters for revoking a token."""
    client_id: str = Field(..., description="ID linking client to the refresh token")
    refresh_token: str = Field(..., description="Refresh token to be revoked")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to revoke token in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class TokenManagementTool(BaseTool):
    name = "token_management"
    description = "Token management operations (create, list, get, delete, revoke)"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["create", "list", "get", "delete", "revoke"]},
                **TokenCreateParams.model_json_schema()["properties"],
                **TokenListParams.model_json_schema()["properties"],
                **TokenGetParams.model_json_schema()["properties"],
                **TokenDeleteParams.model_json_schema()["properties"],
                **TokenRevokeParams.model_json_schema()["properties"],
            },
            "required": ["action"],
        }

    async def execute(self, **kwargs: Any) -> Any:
        action = kwargs.get("action")
        if action == "create":
            params = TokenCreateParams(**kwargs)
            args = ["tokens", "create"]
            if params.issue_rt:
                args.extend(["--issue-rt"])
            if params.labels:
                args.extend(["--labels", params.labels])
            if params.refresh_token:
                args.extend(["--refresh-token", params.refresh_token])
            if params.rt_life:
                args.extend(["--rt-life", str(params.rt_life)])
            if params.rt_unused_life:
                args.extend(["--rt-unused-life", str(params.rt_unused_life)])
            if params.user:
                args.extend(["--user", params.user])
            if params.password:
                args.extend(["--password", params.password])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "list":
            params = TokenListParams(**kwargs)
            args = ["tokens", "list"]
            if params.expired:
                args.append("--expired")
            if params.labels:
                args.extend(["--labels", params.labels])
            args.extend(["--limit", str(params.limit)])
            args.extend(["--skip", str(params.skip)])
            if params.revoked:
                args.append("--revoked")
            if params.user_id:
                args.extend(["--user-id", params.user_id])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "get":
            params = TokenGetParams(**kwargs)
            args = ["tokens", "get", "--id", params.id]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "delete":
            params = TokenDeleteParams(**kwargs)
            args = ["tokens", "delete", "--id", params.id]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "revoke":
            params = TokenRevokeParams(**kwargs)
            args = [
                "tokens", "revoke",
                "--client-id", params.client_id,
                "--refresh-token", params.refresh_token
            ]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")

TOKEN_TOOLS = [TokenManagementTool]
