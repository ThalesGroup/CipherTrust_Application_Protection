"""User management tools for CipherTrust Manager with built-in domain support."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


# Password Policy Parameter Models
class UserPwdPolicyCreateParams(BaseModel):
    """Parameters for creating a password policy."""
    policy_name: str = Field(..., description="Password policy name")
    failed_logins_lockout_thresholds: Optional[str] = Field(None, description="List of lockout durations in minutes (e.g., '[0,5,30]')")
    history: Optional[int] = Field(None, description="Number of past passwords saved (how frequently old passwords can be reused)")
    lifetime: Optional[int] = Field(None, description="Maximum lifetime of the user password (0 is ignored)")
    maxlength: Optional[int] = Field(None, description="Maximum length of the password")
    mindig: Optional[int] = Field(None, description="Minimum number of digits required")
    minlength: Optional[int] = Field(None, description="Minimum length of the password")
    minlower: Optional[int] = Field(None, description="Minimum number of lower case letters")
    minother: Optional[int] = Field(None, description="Minimum number of other characters")
    minupper: Optional[int] = Field(None, description="Minimum number of upper case letters")
    pwdchngdays: Optional[int] = Field(None, description="Maximum lifetime of the password in days")
    pwdexpirynotificationdays: Optional[int] = Field(14, description="Days before expiry when notifications are sent (0-30, default 14)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to create policy in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to 'root' if not specified)")


class UserPwdPolicyListParams(BaseModel):
    """Parameters for listing password policies."""
    limit: int = Field(10, description="Maximum number of policies to return")
    skip: int = Field(0, description="Offset at which to start the search")
    policy_name: Optional[str] = Field(None, description="Filter by password policy name")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to list policies from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to 'root' if not specified)")


class UserPwdPolicyGetParams(BaseModel):
    """Parameters for getting a password policy."""
    policy_name: Optional[str] = Field(None, description="Password policy name (if not specified, applied policy is fetched)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to get policy from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to 'root' if not specified)")


class UserPwdPolicyDeleteParams(BaseModel):
    """Parameters for deleting a password policy."""
    policy_name: str = Field(..., description="Password policy name to delete")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to delete policy from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to 'root' if not specified)")


class UserPwdPolicyUpdateParams(BaseModel):
    """Parameters for updating a password policy."""
    policy_name: Optional[str] = Field(None, description="Password policy name (if not specified, global policy is updated)")
    failed_logins_lockout_thresholds: Optional[str] = Field(None, description="List of lockout durations in minutes (e.g., '[0,5,30]')")
    history: Optional[int] = Field(None, description="Number of past passwords saved")
    lifetime: Optional[int] = Field(None, description="Maximum lifetime of the user password")
    maxlength: Optional[int] = Field(None, description="Maximum length of the password")
    mindig: Optional[int] = Field(None, description="Minimum number of digits required")
    minlength: Optional[int] = Field(None, description="Minimum length of the password")
    minlower: Optional[int] = Field(None, description="Minimum number of lower case letters")
    minother: Optional[int] = Field(None, description="Minimum number of other characters")
    minupper: Optional[int] = Field(None, description="Minimum number of upper case letters")
    pwdchngdays: Optional[int] = Field(None, description="Maximum lifetime of the password in days")
    pwdexpirynotificationdays: Optional[int] = Field(None, description="Days before expiry when notifications are sent (0-30)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to update policy in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to 'root' if not specified)")


# User Management Parameter Models
class UserCreateParams(BaseModel):
    """Parameters for user creation."""
    username: str = Field(..., description="Username to create")
    password: str = Field(..., description="User password")
    email: Optional[str] = Field(None, description="User email address")
    friendly_name: Optional[str] = Field(None, description="User's display name")
    userconnection: str = Field("local_account", description="Connection name (local_account or LDAP connection name)")
    enable_cert_auth: Optional[bool] = Field(None, description="Enable certificate-based authentication")
    password_change: Optional[bool] = Field(None, description="Require password change on next login")
    expires_at: Optional[str] = Field(None, description="Local account expiration date")
    allowed_auth_methods: Optional[str] = Field(None, description="Comma-separated list of allowed auth methods")
    allowed_client_types: Optional[str] = Field(None, description="Comma-separated list of allowed client types")
    prevent_ui_login: Optional[bool] = Field(None, description="Disable user login from Web UI")
    is_domain_user: Optional[bool] = Field(None, description="Create user in non-root domain")
    dn: Optional[str] = Field(None, description="DN value for LDAP users")
    # Domain support (optional - defaults to global settings if not provided)
    domain: Optional[str] = Field(None, description="Domain to create user in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to 'root' if not specified)")


class UserListParams(BaseModel):
    """Parameters for listing users."""
    limit: int = Field(10, description="Maximum number of users to return")
    skip: int = Field(0, description="Offset at which to start the search")
    username: Optional[str] = Field(None, description="Filter by username")
    email: Optional[str] = Field(None, description="Filter by email")
    group: Optional[str] = Field(None, description="Filter by group name")
    groups: Optional[str] = Field(None, description="Filter by multiple groups (comma-separated)")
    return_groups: bool = Field(False, description="Return list of groups for each user")
    sort: Optional[str] = Field(None, description="Sort field (prefix with - for descending)")
    # Domain support (optional - defaults to global settings if not provided)
    domain: Optional[str] = Field(None, description="Domain to list users from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to 'root' if not specified)")


class UserGetParams(BaseModel):
    """Parameters for getting a user."""
    id: str = Field(..., description="User ID (or 'self' for current user)")
    # Domain support (optional - defaults to global settings if not provided)
    domain: Optional[str] = Field(None, description="Domain to get user from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to 'root' if not specified)")


class UserDeleteParams(BaseModel):
    """Parameters for deleting a user."""
    id: str = Field(..., description="User ID")
    # Domain support (optional - defaults to global settings if not provided)
    domain: Optional[str] = Field(None, description="Domain to delete user from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to 'root' if not specified)")


class UserModifyParams(BaseModel):
    """Parameters for modifying a user."""
    id: str = Field(..., description="User ID (or 'self' for current user)")
    username: Optional[str] = Field(None, description="New username")
    email: Optional[str] = Field(None, description="New email address")
    password: Optional[str] = Field(None, description="New password")
    friendly_name: Optional[str] = Field(None, description="New display name")
    enable_cert_auth: Optional[bool] = Field(None, description="Enable/disable certificate authentication")
    password_change: Optional[bool] = Field(None, description="Require password change on next login")
    expires_at: Optional[str] = Field(None, description="Account expiration date")
    allowed_auth_methods: Optional[str] = Field(None, description="Allowed authentication methods")
    allowed_client_types: Optional[str] = Field(None, description="Allowed client types")
    prevent_ui_login: Optional[bool] = Field(None, description="Disable Web UI login")
    unlock: bool = Field(False, description="Unlock the user account")
    dn: Optional[str] = Field(None, description="DN value for LDAP users")
    # Domain support (optional - defaults to global settings if not provided)
    domain: Optional[str] = Field(None, description="Domain to modify user in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to 'root' if not specified)")


class UserManagementTool(BaseTool):
    name = "user_management"
    description = (
        "User management operations (create, delete, list, update, get)"
    )

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["create", "list", "get", "delete", "modify"],
                    "description": "The user action to perform"
                },
                **UserCreateParams.model_json_schema()["properties"],
                **UserListParams.model_json_schema()["properties"],
                **UserGetParams.model_json_schema()["properties"],
                **UserDeleteParams.model_json_schema()["properties"],
                **UserModifyParams.model_json_schema()["properties"],
            },
            "required": ["action"],
        }

    async def execute(self, action: str, **kwargs: Any) -> Any:
        if action == "create":
            return self.create_user(**kwargs)
        elif action == "list":
            return self.list_users(**kwargs)
        elif action == "get":
            return self.get_user(**kwargs)
        elif action == "delete":
            return self.delete_user(**kwargs)
        elif action == "modify":
            return self.modify_user(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")

    def create_user(self, **kwargs):
        params = UserCreateParams(**kwargs)
        args = ["users", "create"]
        args.extend(["--username", params.username])
        args.extend(["--pword", params.password])
        if params.email:
            args.extend(["--email", params.email])
        if params.friendly_name:
            args.extend(["--friendly-name", params.friendly_name])
        if params.userconnection != "local_account":
            args.extend(["--userconnection", params.userconnection])
        if params.enable_cert_auth is not None:
            args.extend(["--enable-cert-auth", "yes" if params.enable_cert_auth else "no"])
        if params.password_change is not None:
            args.extend(["--password-change", "yes" if params.password_change else "no"])
        if params.expires_at:
            args.extend(["--expires-at", params.expires_at])
        if params.allowed_auth_methods:
            args.extend(["--allowed-auth-methods", params.allowed_auth_methods])
        if params.allowed_client_types:
            args.extend(["--allowed-client-types", params.allowed_client_types])
        if params.prevent_ui_login is not None:
            args.extend(["--prevent-ui-login", "yes" if params.prevent_ui_login else "no"])
        if params.is_domain_user is not None:
            args.extend(["--is-domain-user", "yes" if params.is_domain_user else "no"])
        if params.dn:
            args.extend(["--dn", params.dn])
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))

    def list_users(self, **kwargs):
        params = UserListParams(**kwargs)
        args = ["users", "list"]
        args.extend(["--limit", str(params.limit)])
        args.extend(["--skip", str(params.skip)])
        if params.username:
            args.extend(["--username", params.username])
        if params.email:
            args.extend(["--email", params.email])
        if params.group:
            args.extend(["--group", params.group])
        if params.groups:
            args.extend(["--groups", params.groups])
        if params.return_groups:
            args.append("--return-groups")
        if params.sort:
            args.extend(["--sort", params.sort])
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))

    def get_user(self, **kwargs):
        params = UserGetParams(**kwargs)
        args = ["users", "get", "--id", params.id]
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))

    def delete_user(self, **kwargs):
        params = UserDeleteParams(**kwargs)
        args = ["users", "delete", "--id", params.id]
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))

    def modify_user(self, **kwargs):
        params = UserModifyParams(**kwargs)
        args = ["users", "modify", "--id", params.id]
        if params.username:
            args.extend(["--username", params.username])
        if params.email:
            args.extend(["--email", params.email])
        if params.password:
            args.extend(["--pword", params.password])
        if params.friendly_name:
            args.extend(["--friendly-name", params.friendly_name])
        if params.enable_cert_auth is not None:
            args.extend(["--enable-cert-auth", "yes" if params.enable_cert_auth else "no"])
        if params.password_change is not None:
            args.extend(["--password-change", "yes" if params.password_change else "no"])
        if params.expires_at:
            args.extend(["--expires-at", params.expires_at])
        if params.allowed_auth_methods:
            args.extend(["--allowed-auth-methods", params.allowed_auth_methods])
        if params.allowed_client_types:
            args.extend(["--allowed-client-types", params.allowed_client_types])
        if params.prevent_ui_login is not None:
            args.extend(["--prevent-ui-login", "yes" if params.prevent_ui_login else "no"])
        if params.unlock:
            args.append("--unlock")
        if params.dn:
            args.extend(["--dn", params.dn])
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))

class PasswordPolicyManagementTool(BaseTool):
    name = "password_policy_management"
    description = (
        "Password policy management operations (pwdpolicy_create, pwdpolicy_list, pwdpolicy_get, pwdpolicy_delete, pwdpolicy_update)"
    )

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "pwdpolicy_create", "pwdpolicy_list", "pwdpolicy_get", "pwdpolicy_delete", "pwdpolicy_update"
                    ],
                    "description": "The password policy action to perform"
                },
                **UserPwdPolicyCreateParams.model_json_schema()["properties"],
                **UserPwdPolicyListParams.model_json_schema()["properties"],
                **UserPwdPolicyGetParams.model_json_schema()["properties"],
                **UserPwdPolicyDeleteParams.model_json_schema()["properties"],
                **UserPwdPolicyUpdateParams.model_json_schema()["properties"],
            },
            "required": ["action"],
        }

    async def execute(self, action: str, **kwargs: Any) -> Any:
        if action == "pwdpolicy_create":
            return self.pwdpolicy_create(**kwargs)
        elif action == "pwdpolicy_list":
            return self.pwdpolicy_list(**kwargs)
        elif action == "pwdpolicy_get":
            return self.pwdpolicy_get(**kwargs)
        elif action == "pwdpolicy_delete":
            return self.pwdpolicy_delete(**kwargs)
        elif action == "pwdpolicy_update":
            return self.pwdpolicy_update(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")

    def pwdpolicy_create(self, **kwargs):
        params = UserPwdPolicyCreateParams(**kwargs)
        args = ["users", "pwdpolicy", "create", "--policy-name", params.policy_name]
        if params.failed_logins_lockout_thresholds:
            args.extend(["--failed-logins-lockout-thresholds", params.failed_logins_lockout_thresholds])
        if params.history is not None:
            args.extend(["--history", str(params.history)])
        if params.lifetime is not None:
            args.extend(["--lifetime", str(params.lifetime)])
        if params.maxlength is not None:
            args.extend(["--maxlength", str(params.maxlength)])
        if params.mindig is not None:
            args.extend(["--mindig", str(params.mindig)])
        if params.minlength is not None:
            args.extend(["--minlength", str(params.minlength)])
        if params.minlower is not None:
            args.extend(["--minlower", str(params.minlower)])
        if params.minother is not None:
            args.extend(["--minother", str(params.minother)])
        if params.minupper is not None:
            args.extend(["--minupper", str(params.minupper)])
        if params.pwdchngdays is not None:
            args.extend(["--pwdchngdays", str(params.pwdchngdays)])
        if params.pwdexpirynotificationdays is not None:
            args.extend(["--pwdexpirynotificationdays", str(params.pwdexpirynotificationdays)])
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))

    def pwdpolicy_list(self, **kwargs):
        params = UserPwdPolicyListParams(**kwargs)
        args = ["users", "pwdpolicy", "list"]
        args.extend(["--limit", str(params.limit)])
        args.extend(["--skip", str(params.skip)])
        if params.policy_name:
            args.extend(["--policy-name", params.policy_name])
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))

    def pwdpolicy_get(self, **kwargs):
        params = UserPwdPolicyGetParams(**kwargs)
        args = ["users", "pwdpolicy", "get"]
        if params.policy_name:
            args.extend(["--policy-name", params.policy_name])
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))

    def pwdpolicy_delete(self, **kwargs):
        params = UserPwdPolicyDeleteParams(**kwargs)
        args = ["users", "pwdpolicy", "delete", "--policy-name", params.policy_name]
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))

    def pwdpolicy_update(self, **kwargs):
        params = UserPwdPolicyUpdateParams(**kwargs)
        args = ["users", "pwdpolicy", "update"]
        if params.policy_name:
            args.extend(["--policy-name", params.policy_name])
        if params.failed_logins_lockout_thresholds:
            args.extend(["--failed-logins-lockout-thresholds", params.failed_logins_lockout_thresholds])
        if params.history is not None:
            args.extend(["--history", str(params.history)])
        if params.lifetime is not None:
            args.extend(["--lifetime", str(params.lifetime)])
        if params.maxlength is not None:
            args.extend(["--maxlength", str(params.maxlength)])
        if params.mindig is not None:
            args.extend(["--mindig", str(params.mindig)])
        if params.minlength is not None:
            args.extend(["--minlength", str(params.minlength)])
        if params.minlower is not None:
            args.extend(["--minlower", str(params.minlower)])
        if params.minother is not None:
            args.extend(["--minother", str(params.minother)])
        if params.minupper is not None:
            args.extend(["--minupper", str(params.minupper)])
        if params.pwdchngdays is not None:
            args.extend(["--pwdchngdays", str(params.pwdchngdays)])
        if params.pwdexpirynotificationdays is not None:
            args.extend(["--pwdexpirynotificationdays", str(params.pwdexpirynotificationdays)])
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))

# Export the grouped user tools
USER_TOOLS = [UserManagementTool, PasswordPolicyManagementTool]
