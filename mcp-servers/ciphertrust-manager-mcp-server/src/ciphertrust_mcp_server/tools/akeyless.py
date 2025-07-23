"""Akeyless Gateway management tools for CipherTrust Manager with built-in domain support."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


# Akeyless Config Parameter Models
class AkeylessConfigGetParams(BaseModel):
    """Parameters for getting Akeyless configuration."""
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to get config from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class AkeylessConfigModifyParams(BaseModel):
    """Parameters for modifying Akeyless configuration."""
    gateway_connection_id: Optional[str] = Field(None, description="ID, name or URI of connection associated with the Akeyless gateway")
    sso_access_id: Optional[str] = Field(None, description="The akeyless key ID to be used for Akeyless SSO")
    akeyless_signup_url: Optional[str] = Field(None, description="URL of the akeyless infrastructure for signup (defaults to https://vault.akeyless.io)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to modify config in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class AkeylessConfigStatusParams(BaseModel):
    """Parameters for getting Akeyless configuration status."""
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to get status from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


# Akeyless Customer Fragment Parameter Models
class AkeylessCustomerFragmentCreateParams(BaseModel):
    """Parameters for creating an Akeyless customer fragment."""
    name: str = Field(..., description="Name of customer fragment")
    desc: Optional[str] = Field(None, description="Description for customer fragment")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to create fragment in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class AkeylessCustomerFragmentDeleteParams(BaseModel):
    """Parameters for deleting an Akeyless customer fragment."""
    id: Optional[str] = Field(None, description="Customer fragment ID")
    name: Optional[str] = Field(None, description="Name of customer fragment")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to delete fragment from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class AkeylessCustomerFragmentListParams(BaseModel):
    """Parameters for listing Akeyless customer fragments."""
    id: Optional[str] = Field(None, description="Filter by customer fragment ID")
    name: Optional[str] = Field(None, description="Filter by customer fragment name")
    limit: int = Field(10, description="Maximum number of customer fragments to return")
    skip: int = Field(0, description="Index of the first customer fragment to return")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to list fragments from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


# Akeyless Token Parameter Models
class AkeylessTokenCreateParams(BaseModel):
    """Parameters for creating an Akeyless token."""
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to create token in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


# Akeyless Config Management Tools
class AkeylessConfigGetTool(BaseTool):
    """Get Akeyless configuration."""

    @property
    def name(self) -> str:
        return "ct_akeyless_config_get"

    @property
    def description(self) -> str:
        return "Get the Akeyless configuration for a CipherTrust Manager instance"

    def get_schema(self) -> dict[str, Any]:
        return AkeylessConfigGetParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute akeyless config get command."""
        params = AkeylessConfigGetParams(**kwargs)
        
        args = ["akeyless", "config", "get"]
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


class AkeylessConfigModifyTool(BaseTool):
    """Modify Akeyless configuration."""

    @property
    def name(self) -> str:
        return "ct_akeyless_config_modify"

    @property
    def description(self) -> str:
        return "Modify the Akeyless configuration for a CipherTrust Manager instance"

    def get_schema(self) -> dict[str, Any]:
        return AkeylessConfigModifyParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute akeyless config modify command."""
        params = AkeylessConfigModifyParams(**kwargs)
        
        args = ["akeyless", "config", "modify"]
        
        if params.gateway_connection_id:
            args.extend(["--gateway-connection-id", params.gateway_connection_id])
        if params.sso_access_id:
            args.extend(["--sso-access-id", params.sso_access_id])
        if params.akeyless_signup_url:
            args.extend(["--akeyless-signup-url", params.akeyless_signup_url])
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


class AkeylessConfigStatusTool(BaseTool):
    """Get Akeyless configuration status."""

    @property
    def name(self) -> str:
        return "ct_akeyless_config_status"

    @property
    def description(self) -> str:
        return "Get the Akeyless configuration status for a CipherTrust Manager instance"

    def get_schema(self) -> dict[str, Any]:
        return AkeylessConfigStatusParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute akeyless config status command."""
        params = AkeylessConfigStatusParams(**kwargs)
        
        args = ["akeyless", "config", "status"]
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


# Akeyless Customer Fragment Management Tools
class AkeylessCustomerFragmentCreateTool(BaseTool):
    """Create an Akeyless customer fragment."""

    @property
    def name(self) -> str:
        return "ct_akeyless_customer_fragment_create"

    @property
    def description(self) -> str:
        return "Create a customer fragment (AES key used to protect akeyless secrets)"

    def get_schema(self) -> dict[str, Any]:
        return AkeylessCustomerFragmentCreateParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute akeyless customer-fragment create command."""
        params = AkeylessCustomerFragmentCreateParams(**kwargs)
        
        args = ["akeyless", "customer-fragment", "create", "--name", params.name]
        
        if params.desc:
            args.extend(["--desc", params.desc])
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


class AkeylessCustomerFragmentDeleteTool(BaseTool):
    """Delete an Akeyless customer fragment."""

    @property
    def name(self) -> str:
        return "ct_akeyless_customer_fragment_delete"

    @property
    def description(self) -> str:
        return "Delete a customer fragment by ID or name"

    def get_schema(self) -> dict[str, Any]:
        return AkeylessCustomerFragmentDeleteParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute akeyless customer-fragment delete command."""
        params = AkeylessCustomerFragmentDeleteParams(**kwargs)
        
        if not params.id and not params.name:
            raise ValueError("Either id or name must be specified")
        
        args = ["akeyless", "customer-fragment", "delete"]
        
        if params.id:
            args.extend(["--id", params.id])
        elif params.name:
            args.extend(["--name", params.name])
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


class AkeylessCustomerFragmentListTool(BaseTool):
    """List Akeyless customer fragments."""

    @property
    def name(self) -> str:
        return "ct_akeyless_customer_fragment_list"

    @property
    def description(self) -> str:
        return "Retrieve customer fragments with optional filtering by ID or name"

    def get_schema(self) -> dict[str, Any]:
        return AkeylessCustomerFragmentListParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute akeyless customer-fragment list command."""
        params = AkeylessCustomerFragmentListParams(**kwargs)
        
        args = ["akeyless", "customer-fragment", "list"]
        args.extend(["--limit", str(params.limit)])
        args.extend(["--skip", str(params.skip)])
        
        if params.id:
            args.extend(["--id", params.id])
        if params.name:
            args.extend(["--name", params.name])
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


# Akeyless Token Management Tools
class AkeylessTokenCreateTool(BaseTool):
    """Create an Akeyless token."""

    @property
    def name(self) -> str:
        return "ct_akeyless_token_create"

    @property
    def description(self) -> str:
        return "Create a JWT token that is recognized by the akeyless server using SSO credentials"

    def get_schema(self) -> dict[str, Any]:
        return AkeylessTokenCreateParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute akeyless tokens create command."""
        params = AkeylessTokenCreateParams(**kwargs)
        
        args = ["akeyless", "tokens", "create"]
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


class AkeylessManagementTool(BaseTool):
    name = "akeyless_management"
    description = "Akeyless management operations (config_get, config_modify, config_status, customer_fragment_create, customer_fragment_delete, customer_fragment_list, token_create)"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": [
                    "config_get", "config_modify", "config_status", "customer_fragment_create", "customer_fragment_delete", "customer_fragment_list", "token_create"
                ]},
                **AkeylessConfigGetParams.model_json_schema()["properties"],
                **AkeylessConfigModifyParams.model_json_schema()["properties"],
                **AkeylessConfigStatusParams.model_json_schema()["properties"],
                **AkeylessCustomerFragmentCreateParams.model_json_schema()["properties"],
                **AkeylessCustomerFragmentDeleteParams.model_json_schema()["properties"],
                **AkeylessCustomerFragmentListParams.model_json_schema()["properties"],
                **AkeylessTokenCreateParams.model_json_schema()["properties"],
            },
            "required": ["action"],
        }

    async def execute(self, action: str, **kwargs: Any) -> Any:
        if action == "config_get":
            params = AkeylessConfigGetParams(**kwargs)
            args = ["akeyless", "config", "get"]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "config_modify":
            params = AkeylessConfigModifyParams(**kwargs)
            args = ["akeyless", "config", "modify"]
            if params.gateway_connection_id:
                args.extend(["--gateway-connection-id", params.gateway_connection_id])
            if params.sso_access_id:
                args.extend(["--sso-access-id", params.sso_access_id])
            if params.akeyless_signup_url:
                args.extend(["--akeyless-signup-url", params.akeyless_signup_url])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "config_status":
            params = AkeylessConfigStatusParams(**kwargs)
            args = ["akeyless", "config", "status"]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "customer_fragment_create":
            params = AkeylessCustomerFragmentCreateParams(**kwargs)
            args = ["akeyless", "customer-fragment", "create", "--name", params.name]
            if params.desc:
                args.extend(["--desc", params.desc])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "customer_fragment_delete":
            params = AkeylessCustomerFragmentDeleteParams(**kwargs)
            if not params.id and not params.name:
                raise ValueError("Either id or name must be specified")
            args = ["akeyless", "customer-fragment", "delete"]
            if params.id:
                args.extend(["--id", params.id])
            elif params.name:
                args.extend(["--name", params.name])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "customer_fragment_list":
            params = AkeylessCustomerFragmentListParams(**kwargs)
            args = ["akeyless", "customer-fragment", "list", "--limit", str(params.limit), "--skip", str(params.skip)]
            if params.id:
                args.extend(["--id", params.id])
            if params.name:
                args.extend(["--name", params.name])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "token_create":
            params = AkeylessTokenCreateParams(**kwargs)
            args = ["akeyless", "tokens", "create"]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")

AKEYLESS_TOOLS = [AkeylessManagementTool]
