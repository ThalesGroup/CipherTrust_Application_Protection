"""OIDC connection management tools for CipherTrust Manager with built-in domain support."""

from typing import Any, Optional, List

from pydantic import BaseModel, Field

from .base import BaseTool


# OIDC Connection Parameter Models
class ConnectionOIDCCreateParams(BaseModel):
    """Parameters for creating an OIDC connection."""
    name: str = Field(..., description="A friendly name for your connection")
    client_id: str = Field(..., description="Client ID from the external identity provider")
    redirect_uris: List[str] = Field(..., description="Allowed URIs to redirect after authentication")
    discovery_uri: str = Field(..., description="URI of issuer's well-known configuration")
    flow_type: str = Field("implicit", description="Flow type (implicit or authorization_code)")
    client_secret: Optional[str] = Field(None, description="Client secret for authorization_code connections")
    groups_claim: str = Field("groups", description="Claim field name for group membership")
    token_endpoint: Optional[str] = Field(None, description="Token endpoint (use discovery_uri instead)")
    authorization_uri: Optional[str] = Field(None, description="Authorization URI (use discovery_uri instead)")
    jwks: Optional[str] = Field(None, description="Array of JWKS public keys (use discovery_uri instead)")
    disable_auto_create: bool = Field(False, description="Disable automatic user creation on login")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to create connection in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class ConnectionOIDCListParams(BaseModel):
    """Parameters for listing OIDC connections."""
    limit: int = Field(10, description="Maximum number of connections to return")
    skip: int = Field(0, description="Offset at which to start the search")
    strategy: str = Field("oidc", description="Filter by connection strategy")
    sort: Optional[str] = Field(None, description="Sort field (prefix with - for descending)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to list connections from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class ConnectionOIDCGetParams(BaseModel):
    """Parameters for getting an OIDC connection."""
    id: str = Field(..., description="ID of the connection")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to get connection from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class ConnectionOIDCDeleteParams(BaseModel):
    """Parameters for deleting an OIDC connection."""
    id: str = Field(..., description="ID of the connection")
    force: bool = Field(False, description="Delete associated sub-domain users and groupmaps silently")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to delete connection from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class ConnectionOIDCModifyParams(BaseModel):
    """Parameters for modifying an OIDC connection."""
    id: str = Field(..., description="ID of the connection")
    name: Optional[str] = Field(None, description="A friendly name for your connection")
    client_id: Optional[str] = Field(None, description="Client ID from the external identity provider")
    redirect_uris: Optional[List[str]] = Field(None, description="Allowed URIs to redirect after authentication")
    discovery_uri: Optional[str] = Field(None, description="URI of issuer's well-known configuration")
    flow_type: Optional[str] = Field(None, description="Flow type (implicit or authorization_code)")
    client_secret: Optional[str] = Field(None, description="Client secret for authorization_code connections")
    groups_claim: Optional[str] = Field(None, description="Claim field name for group membership")
    token_endpoint: Optional[str] = Field(None, description="Token endpoint")
    authorization_uri: Optional[str] = Field(None, description="Authorization URI")
    jwks: Optional[str] = Field(None, description="Array of JWKS public keys")
    disable_auto_create: Optional[bool] = Field(None, description="Disable automatic user creation on login")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to modify connection in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class ConnectionOIDCRefreshParams(BaseModel):
    """Parameters for refreshing an OIDC connection."""
    id: str = Field(..., description="ID of the connection")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to refresh connection in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class ConnectionOIDCManagementTool(BaseTool):
    """Manage OIDC connections (grouped)."""

    @property
    def name(self) -> str:
        return "connection_oidc_management"

    @property
    def description(self) -> str:
        return "Manage OIDC connections (create, list, get, delete, modify, refresh)"

    def get_schema(self) -> dict[str, Any]:
        return {
            "title": "ConnectionOIDCManagementTool",
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["create", "list", "get", "delete", "modify", "refresh"],
                    "description": "Action to perform"
                },
                # Merge all params from the old tool classes
            },
            "required": ["action"]
        }

    async def execute(self, **kwargs: Any) -> Any:
        action = kwargs.get("action")
        if action == "create":
            params = ConnectionOIDCCreateParams(**kwargs)
            args = ["connections", "create", "oidc"]
            args.extend(["--name", params.name])
            args.extend(["--client-id", params.client_id])
            args.extend(["--discovery-uri", params.discovery_uri])
            for uri in params.redirect_uris:
                args.extend(["--redirect-uris", uri])
            if params.flow_type != "implicit":
                args.extend(["--flow-type", params.flow_type])
            if params.client_secret:
                args.extend(["--client-secret", params.client_secret])
            if params.groups_claim != "groups":
                args.extend(["--groups-claim", params.groups_claim])
            if params.token_endpoint:
                args.extend(["--token-endpoint", params.token_endpoint])
            if params.authorization_uri:
                args.extend(["--authorization-uri", params.authorization_uri])
            if params.jwks:
                args.extend(["--jwks", params.jwks])
            if params.disable_auto_create:
                args.append("--disable-auto-create")
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "list":
            params = ConnectionOIDCListParams(**kwargs)
            args = ["connections", "list"]
            args.extend(["--limit", str(params.limit)])
            args.extend(["--skip", str(params.skip)])
            args.extend(["--strategy", params.strategy])
            if params.sort:
                args.extend(["--sort", params.sort])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "get":
            params = ConnectionOIDCGetParams(**kwargs)
            args = ["connections", "get", "--id", params.id]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "delete":
            params = ConnectionOIDCDeleteParams(**kwargs)
            args = ["connections", "delete", "--id", params.id]
            if params.force:
                args.append("--force")
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "modify":
            params = ConnectionOIDCModifyParams(**kwargs)
            args = ["connections", "modify", "oidc", "--id", params.id]
            if params.name:
                args.extend(["--name", params.name])
            if params.client_id:
                args.extend(["--client-id", params.client_id])
            if params.redirect_uris:
                for uri in params.redirect_uris:
                    args.extend(["--redirect-uris", uri])
            if params.discovery_uri:
                args.extend(["--discovery-uri", params.discovery_uri])
            if params.flow_type:
                args.extend(["--flow-type", params.flow_type])
            if params.client_secret:
                args.extend(["--client-secret", params.client_secret])
            if params.groups_claim:
                args.extend(["--groups-claim", params.groups_claim])
            if params.token_endpoint:
                args.extend(["--token-endpoint", params.token_endpoint])
            if params.authorization_uri:
                args.extend(["--authorization-uri", params.authorization_uri])
            if params.jwks:
                args.extend(["--jwks", params.jwks])
            if params.disable_auto_create is not None:
                if params.disable_auto_create:
                    args.append("--disable-auto-create")
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "refresh":
            params = ConnectionOIDCRefreshParams(**kwargs)
            args = ["connections", "refresh", "--id", params.id]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")

# Export only the grouped tool
CONNECTION_OIDC_TOOLS = [ConnectionOIDCManagementTool]
