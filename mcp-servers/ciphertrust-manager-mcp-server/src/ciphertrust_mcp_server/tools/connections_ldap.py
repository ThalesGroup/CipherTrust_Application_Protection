"""LDAP connection management tools for CipherTrust Manager with built-in domain support."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


# LDAP Connection Parameter Models
class ConnectionLDAPCreateParams(BaseModel):
    """Parameters for creating an LDAP connection."""
    name: str = Field(..., description="A friendly name for your connection")
    server_url: str = Field(..., description="LDAP URL for your server (e.g. ldap://172.16.2.2:3268)")
    root_dn: str = Field(..., description="Starting point to use when searching for users")
    bind_dn: Optional[str] = Field(None, description="Object which has permission to search under the root DN for users")
    bind_password: Optional[str] = Field(None, description="Password for the Bind DN object")
    user_id_field: str = Field(..., description="Attribute inside the user object which contains the user id")
    guid_field: Optional[str] = Field(None, description="Attribute containing globally unique user identification")
    search_filter: Optional[str] = Field(None, description="LDAP search filter to restrict allowed users")
    user_dn_field: Optional[str] = Field(None, description="Attribute containing user distinguished name")
    # Group support
    group_base_dn: Optional[str] = Field(None, description="Starting point for group searches")
    group_id_field: Optional[str] = Field(None, description="Attribute containing group identifier")
    group_member_field: Optional[str] = Field(None, description="Attribute containing group membership")
    group_search_filter: Optional[str] = Field(None, description="Search filter for listing groups")
    # Security
    insecure_skip_verify: bool = Field(False, description="Disable server certificate verification (not recommended)")
    root_ca: Optional[str] = Field(None, description="PEM encoded certificate for server trust")
    disable_auto_create: bool = Field(False, description="Disable automatic user creation on login")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to create connection in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class ConnectionLDAPListParams(BaseModel):
    """Parameters for listing LDAP connections."""
    limit: int = Field(10, description="Maximum number of connections to return")
    skip: int = Field(0, description="Offset at which to start the search")
    strategy: str = Field("ldap", description="Filter by connection strategy")
    sort: Optional[str] = Field(None, description="Sort field (prefix with - for descending)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to list connections from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class ConnectionLDAPGetParams(BaseModel):
    """Parameters for getting an LDAP connection."""
    id: str = Field(..., description="ID of the connection")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to get connection from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class ConnectionLDAPDeleteParams(BaseModel):
    """Parameters for deleting an LDAP connection."""
    id: str = Field(..., description="ID of the connection")
    force: bool = Field(False, description="Delete associated sub-domain users and groupmaps silently")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to delete connection from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class ConnectionLDAPModifyParams(BaseModel):
    """Parameters for modifying an LDAP connection."""
    id: str = Field(..., description="ID of the connection")
    server_url: Optional[str] = Field(None, description="LDAP URL for your server")
    root_dn: Optional[str] = Field(None, description="Starting point to use when searching for users")
    bind_dn: Optional[str] = Field(None, description="Object which has permission to search under the root DN")
    bind_password: Optional[str] = Field(None, description="Password for the Bind DN object")
    user_id_field: Optional[str] = Field(None, description="Attribute containing user id")
    guid_field: Optional[str] = Field(None, description="Attribute containing globally unique user identification")
    search_filter: Optional[str] = Field(None, description="LDAP search filter to restrict allowed users")
    user_dn_field: Optional[str] = Field(None, description="Attribute containing user distinguished name")
    # Group support
    group_base_dn: Optional[str] = Field(None, description="Starting point for group searches")
    group_id_field: Optional[str] = Field(None, description="Attribute containing group identifier")
    group_member_field: Optional[str] = Field(None, description="Attribute containing group membership")
    group_search_filter: Optional[str] = Field(None, description="Search filter for listing groups")
    # Security
    insecure_skip_verify: Optional[bool] = Field(None, description="Disable server certificate verification")
    root_ca: Optional[str] = Field(None, description="PEM encoded certificate for server trust")
    disable_auto_create: Optional[bool] = Field(None, description="Disable automatic user creation on login")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to modify connection in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class ConnectionLDAPTestParams(BaseModel):
    """Parameters for testing an LDAP connection."""
    test_username: str = Field(..., description="Username to use when testing connection")
    test_password: str = Field(..., description="Password to use when testing connection")
    # Connection config for direct testing
    server_url: Optional[str] = Field(None, description="LDAP URL for your server")
    root_dn: Optional[str] = Field(None, description="Starting point to use when searching for users")
    bind_dn: Optional[str] = Field(None, description="Object which has permission to search under the root DN")
    bind_password: Optional[str] = Field(None, description="Password for the Bind DN object")
    user_id_field: Optional[str] = Field(None, description="Attribute containing user id")
    search_filter: Optional[str] = Field(None, description="LDAP search filter to restrict allowed users")
    insecure_skip_verify: bool = Field(False, description="Disable server certificate verification")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain context (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class ConnectionLDAPManagementTool(BaseTool):
    """Manage LDAP connections (grouped)."""

    @property
    def name(self) -> str:
        return "connection_ldap_management"

    @property
    def description(self) -> str:
        return "Manage LDAP connections (create, list, get, delete, modify, test)"

    def get_schema(self) -> dict[str, Any]:
        return {
            "title": "ConnectionLDAPManagementTool",
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["create", "list", "get", "delete", "modify", "test"],
                    "description": "Action to perform"
                },
                # Merge all params from the old tool classes
            },
            "required": ["action"]
        }

    async def execute(self, **kwargs: Any) -> Any:
        action = kwargs.get("action")
        if action == "create":
            params = ConnectionLDAPCreateParams(**kwargs)
            args = ["connections", "create", "ldap"]
            args.extend(["--name", params.name])
            args.extend(["--server-url", params.server_url])
            args.extend(["--root-dn", params.root_dn])
            args.extend(["--user-id-field", params.user_id_field])
            if params.bind_dn:
                args.extend(["--bind-dn", params.bind_dn])
            if params.bind_password:
                args.extend(["--bind-password", params.bind_password])
            if params.guid_field:
                args.extend(["--guid-field", params.guid_field])
            if params.search_filter:
                args.extend(["--search-filter", params.search_filter])
            if params.user_dn_field:
                args.extend(["--user-dn-field", params.user_dn_field])
            if params.group_base_dn:
                args.extend(["--group-base-dn", params.group_base_dn])
            if params.group_id_field:
                args.extend(["--group-id-field", params.group_id_field])
            if params.group_member_field:
                args.extend(["--group-member-field", params.group_member_field])
            if params.group_search_filter:
                args.extend(["--group-search-filter", params.group_search_filter])
            if params.insecure_skip_verify:
                args.append("--insecure-skip-verify")
            if params.root_ca:
                args.extend(["--root-ca", params.root_ca])
            if params.disable_auto_create:
                args.append("--disable-auto-create")
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "list":
            params = ConnectionLDAPListParams(**kwargs)
            args = ["connections", "list"]
            args.extend(["--limit", str(params.limit)])
            args.extend(["--skip", str(params.skip)])
            args.extend(["--strategy", params.strategy])
            if params.sort:
                args.extend(["--sort", params.sort])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "get":
            params = ConnectionLDAPGetParams(**kwargs)
            args = ["connections", "get", "--id", params.id]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "delete":
            params = ConnectionLDAPDeleteParams(**kwargs)
            args = ["connections", "delete", "--id", params.id]
            if params.force:
                args.append("--force")
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "modify":
            params = ConnectionLDAPModifyParams(**kwargs)
            args = ["connections", "modify", "ldap", "--id", params.id]
            if params.server_url:
                args.extend(["--server-url", params.server_url])
            if params.root_dn:
                args.extend(["--root-dn", params.root_dn])
            if params.bind_dn:
                args.extend(["--bind-dn", params.bind_dn])
            if params.bind_password:
                args.extend(["--bind-password", params.bind_password])
            if params.user_id_field:
                args.extend(["--user-id-field", params.user_id_field])
            if params.guid_field:
                args.extend(["--guid-field", params.guid_field])
            if params.search_filter:
                args.extend(["--search-filter", params.search_filter])
            if params.user_dn_field:
                args.extend(["--user-dn-field", params.user_dn_field])
            if params.group_base_dn is not None:
                args.extend(["--group-base-dn", params.group_base_dn])
            if params.group_id_field is not None:
                args.extend(["--group-id-field", params.group_id_field])
            if params.group_member_field is not None:
                args.extend(["--group-member-field", params.group_member_field])
            if params.group_search_filter is not None:
                args.extend(["--group-search-filter", params.group_search_filter])
            if params.insecure_skip_verify is not None:
                if params.insecure_skip_verify:
                    args.append("--insecure-skip-verify")
                else:
                    args.append("--insecure-skip-verify=false")
            if params.root_ca is not None:
                args.extend(["--root-ca", params.root_ca])
            if params.disable_auto_create is not None:
                if params.disable_auto_create:
                    args.append("--disable-auto-create")
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "test":
            params = ConnectionLDAPTestParams(**kwargs)
            args = ["connections", "test"]
            args.extend(["--strategy", "ldap"])
            args.extend(["--test-username", params.test_username])
            args.extend(["--test-password", params.test_password])
            if params.server_url:
                args.extend(["--server-url", params.server_url])
            if params.root_dn:
                args.extend(["--root-dn", params.root_dn])
            if params.bind_dn:
                args.extend(["--bind-dn", params.bind_dn])
            if params.bind_password:
                args.extend(["--bind-password", params.bind_password])
            if params.user_id_field:
                args.extend(["--user-id-field", params.user_id_field])
            if params.search_filter:
                args.extend(["--search-filter", params.search_filter])
            if params.insecure_skip_verify:
                args.append("--insecure-skip-verify")
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")

# Export only the grouped tool
CONNECTION_LDAP_TOOLS = [ConnectionLDAPManagementTool]
