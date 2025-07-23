"""Domain management tools for CipherTrust Manager."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


# Local Domain Management (Runtime Switching)
class DomainSwitchParams(BaseModel):
    """Parameters for switching domains."""
    domain: str = Field(..., description="Domain to switch to for subsequent operations")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (optional)")


class DomainGetCurrentParams(BaseModel):
    """Parameters for getting current domain."""
    # No parameters needed
    pass


# Server Domain Management
class DomainCreateParams(BaseModel):
    """Parameters for creating a domain."""
    name: str = Field(..., description="Name of the domain")
    admins: str = Field(..., description="Comma-separated list of user IDs who will be domain administrators")
    allow_user_mgmt: bool = Field(False, description="Allow user creation and management in the domain")
    hsm_connection_id: Optional[str] = Field(None, description="ID of the HSM connection for HSM-anchored domains")
    hsm_kek_label: Optional[str] = Field(None, description="KEK label for HSM-anchored domain (random UUID if not provided)")
    parent_ca_id: Optional[str] = Field(None, description="ID or URI of the parent domain's CA for signing the new domain's CA")
    jsonfile: Optional[str] = Field(None, description="JSON file containing domain creation parameters")


class DomainListParams(BaseModel):
    """Parameters for listing domains."""
    limit: int = Field(10, description="Maximum number of domains to return")
    skip: int = Field(0, description="Offset at which to start the search")


class DomainGetParams(BaseModel):
    """Parameters for getting domain information."""
    id: str = Field(..., description="Name or ID of the domain")


class DomainUpdateParams(BaseModel):
    """Parameters for updating a domain."""
    id: str = Field(..., description="Name or ID of the domain")
    hsm_connection_id: Optional[str] = Field(None, description="ID of the HSM connection")
    hsm_kek_label: Optional[str] = Field(None, description="HSM KEK label for HSM-anchored domains")


# Domain KEK Management
class DomainKeksListParams(BaseModel):
    """Parameters for listing domain KEKs."""
    id: str = Field(..., description="Name or ID of the domain")
    limit: int = Field(10, description="Maximum number of KEKs to return")
    skip: int = Field(0, description="Offset at which to start the search")


class DomainKeksGetParams(BaseModel):
    """Parameters for getting domain KEK."""
    id: str = Field(..., description="Name or ID of the domain")
    kek_id: str = Field(..., description="ID of the domain KEK")


class DomainRotateKekParams(BaseModel):
    """Parameters for rotating domain KEK."""
    id: str = Field(..., description="Name or ID of the domain")
    hsm_connection_id: Optional[str] = Field(None, description="ID of the HSM connection")
    hsm_kek_label: Optional[str] = Field(None, description="HSM KEK label")


class DomainRetryKekRotationParams(BaseModel):
    """Parameters for retrying KEK rotation."""
    id: str = Field(..., description="Name or ID of the domain")


# Log Redirection Management
class DomainLogRedirectionParams(BaseModel):
    """Parameters for log redirection commands."""
    # No parameters needed for enable/disable/status
    pass


# Local Domain Management Tools
class DomainSwitchTool(BaseTool):
    """Switch the current operating domain."""

    @property
    def name(self) -> str:
        return "ct_domain_switch"

    @property
    def description(self) -> str:
        return "Switch the current operating domain for subsequent operations"

    def get_schema(self) -> dict[str, Any]:
        return DomainSwitchParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Switch domain by updating settings."""
        from ..config import settings
        
        params = DomainSwitchParams(**kwargs)
        
        # Update global settings
        settings.ciphertrust_domain = params.domain
        if params.auth_domain:
            settings.ciphertrust_auth_domain = params.auth_domain
        
        return {
            "success": True,
            "message": f"Switched to domain: {params.domain}",
            "operating_domain": settings.ciphertrust_domain,
            "auth_domain": settings.ciphertrust_auth_domain
        }


class DomainGetCurrentTool(BaseTool):
    """Get the current operating domain."""

    @property
    def name(self) -> str:
        return "ct_domain_get_current"

    @property
    def description(self) -> str:
        return "Get the current operating domain and auth domain settings"

    def get_schema(self) -> dict[str, Any]:
        return DomainGetCurrentParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Get current domain settings."""
        from ..config import settings
        
        return {
            "operating_domain": settings.ciphertrust_domain,
            "auth_domain": settings.ciphertrust_auth_domain,
            "message": f"Currently operating in domain: {settings.ciphertrust_domain}"
        }


# Server Domain Management Tools
class DomainCreateTool(BaseTool):
    """Create a new domain."""

    @property
    def name(self) -> str:
        return "ct_domain_create"

    @property
    def description(self) -> str:
        return "Create a new domain in CipherTrust Manager"

    def get_schema(self) -> dict[str, Any]:
        return DomainCreateParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute domains create command."""
        params = DomainCreateParams(**kwargs)
        
        args = ["domains", "create"]
        args.extend(["--name", params.name])
        args.extend(["--admins", params.admins])
        
        if params.allow_user_mgmt:
            args.append("--allow-user-mgmt")
        if params.hsm_connection_id:
            args.extend(["--hsm-connection-id", params.hsm_connection_id])
        if params.hsm_kek_label:
            args.extend(["--hsm-kek-label", params.hsm_kek_label])
        if params.parent_ca_id:
            args.extend(["--parent-ca-id", params.parent_ca_id])
        if params.jsonfile:
            args.extend(["--jsonfile", params.jsonfile])
        
        result = self.ksctl.execute(args)
        return result.get("data", result.get("stdout", ""))


class DomainListTool(BaseTool):
    """List available domains."""

    @property
    def name(self) -> str:
        return "ct_domain_list"

    @property
    def description(self) -> str:
        return "List available domains in the CipherTrust Manager"

    def get_schema(self) -> dict[str, Any]:
        return DomainListParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute domain list command."""
        params = DomainListParams(**kwargs)
        
        args = ["domains", "list"]
        args.extend(["--limit", str(params.limit)])
        args.extend(["--skip", str(params.skip)])
        
        result = self.ksctl.execute(args)
        return result.get("data", result.get("stdout", ""))


class DomainGetTool(BaseTool):
    """Get information about a specific domain."""

    @property
    def name(self) -> str:
        return "ct_domain_get"

    @property
    def description(self) -> str:
        return "Get detailed information about a specific domain by name or ID"

    def get_schema(self) -> dict[str, Any]:
        return DomainGetParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute domain get command."""
        params = DomainGetParams(**kwargs)
        
        result = self.ksctl.execute([
            "domains", "get",
            "--id", params.id
        ])
        return result.get("data", result.get("stdout", ""))


class DomainUpdateTool(BaseTool):
    """Update a domain."""

    @property
    def name(self) -> str:
        return "ct_domain_update"

    @property
    def description(self) -> str:
        return "Update domain settings including HSM connection and KEK label"

    def get_schema(self) -> dict[str, Any]:
        return DomainUpdateParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute domain update command."""
        params = DomainUpdateParams(**kwargs)
        
        args = ["domains", "update", "--id", params.id]
        if params.hsm_connection_id:
            args.extend(["--hsm-connection-id", params.hsm_connection_id])
        if params.hsm_kek_label:
            args.extend(["--hsm-kek-label", params.hsm_kek_label])
        
        result = self.ksctl.execute(args)
        return result.get("data", result.get("stdout", ""))


# Domain KEK Management Tools
class DomainKeksListTool(BaseTool):
    """List domain protection keys."""

    @property
    def name(self) -> str:
        return "ct_domain_keks_list"

    @property
    def description(self) -> str:
        return "List domain protection keys (KEKs) for a specific domain"

    def get_schema(self) -> dict[str, Any]:
        return DomainKeksListParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute domain keks list command."""
        params = DomainKeksListParams(**kwargs)
        
        args = ["domains", "keks", "list"]
        args.extend(["--id", params.id])
        args.extend(["--limit", str(params.limit)])
        args.extend(["--skip", str(params.skip)])
        
        result = self.ksctl.execute(args)
        return result.get("data", result.get("stdout", ""))


class DomainKeksGetTool(BaseTool):
    """Get domain protection key."""

    @property
    def name(self) -> str:
        return "ct_domain_keks_get"

    @property
    def description(self) -> str:
        return "Get information about a specific domain protection key"

    def get_schema(self) -> dict[str, Any]:
        return DomainKeksGetParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute domain keks get command."""
        params = DomainKeksGetParams(**kwargs)
        
        result = self.ksctl.execute([
            "domains", "keks", "get",
            "--id", params.id,
            "--kek-id", params.kek_id
        ])
        return result.get("data", result.get("stdout", ""))


class DomainRotateKekTool(BaseTool):
    """Rotate a domain KEK."""

    @property
    def name(self) -> str:
        return "ct_domain_rotate_kek"

    @property
    def description(self) -> str:
        return "Rotate a domain KEK (applies only to HSM anchored domains)"

    def get_schema(self) -> dict[str, Any]:
        return DomainRotateKekParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute domain rotate-kek command."""
        params = DomainRotateKekParams(**kwargs)
        
        args = ["domains", "rotate-kek", "--id", params.id]
        if params.hsm_connection_id:
            args.extend(["--hsm-connection-id", params.hsm_connection_id])
        if params.hsm_kek_label:
            args.extend(["--hsm-kek-label", params.hsm_kek_label])
        
        result = self.ksctl.execute(args)
        return result.get("data", result.get("stdout", ""))


class DomainRetryKekRotationTool(BaseTool):
    """Retry rotation of a domain KEK."""

    @property
    def name(self) -> str:
        return "ct_domain_retry_kek_rotation"

    @property
    def description(self) -> str:
        return "Retry rotation of a domain KEK"

    def get_schema(self) -> dict[str, Any]:
        return DomainRetryKekRotationParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute domain retry-kek-rotation command."""
        params = DomainRetryKekRotationParams(**kwargs)
        
        result = self.ksctl.execute([
            "domains", "retry-kek-rotation",
            "--id", params.id
        ])
        return result.get("data", result.get("stdout", ""))


# Log Redirection Tools
class DomainLogForwardersRedirectionEnableTool(BaseTool):
    """Enable log-forwarders messages redirection."""

    @property
    def name(self) -> str:
        return "ct_domain_log_forwarders_redirection_enable"

    @property
    def description(self) -> str:
        return "Enable log-forwarders messages redirection to parent domain (not applicable for root domain)"

    def get_schema(self) -> dict[str, Any]:
        return DomainLogRedirectionParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute domain log-forwarders-redirection enable command."""
        result = self.ksctl.execute(["domains", "log-forwarders-redirection", "enable"])
        return result.get("data", result.get("stdout", ""))


class DomainLogForwardersRedirectionDisableTool(BaseTool):
    """Disable log-forwarders messages redirection."""

    @property
    def name(self) -> str:
        return "ct_domain_log_forwarders_redirection_disable"

    @property
    def description(self) -> str:
        return "Disable log-forwarders messages redirection to parent domain"

    def get_schema(self) -> dict[str, Any]:
        return DomainLogRedirectionParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute domain log-forwarders-redirection disable command."""
        result = self.ksctl.execute(["domains", "log-forwarders-redirection", "disable"])
        return result.get("data", result.get("stdout", ""))


class DomainLogForwardersRedirectionStatusTool(BaseTool):
    """Get log-forwarders messages redirection status."""

    @property
    def name(self) -> str:
        return "ct_domain_log_forwarders_redirection_status"

    @property
    def description(self) -> str:
        return "Get status of log-forwarders messages redirection to parent domain"

    def get_schema(self) -> dict[str, Any]:
        return DomainLogRedirectionParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute domain log-forwarders-redirection status command."""
        result = self.ksctl.execute(["domains", "log-forwarders-redirection", "status"])
        return result.get("data", result.get("stdout", ""))


class DomainSyslogRedirectionEnableTool(BaseTool):
    """Enable syslog messages redirection."""

    @property
    def name(self) -> str:
        return "ct_domain_syslog_redirection_enable"

    @property
    def description(self) -> str:
        return "Enable syslog messages redirection to parent domain (not applicable for root domain)"

    def get_schema(self) -> dict[str, Any]:
        return DomainLogRedirectionParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute domain syslog-redirection enable command."""
        result = self.ksctl.execute(["domains", "syslog-redirection", "enable"])
        return result.get("data", result.get("stdout", ""))


class DomainSyslogRedirectionDisableTool(BaseTool):
    """Disable syslog messages redirection."""

    @property
    def name(self) -> str:
        return "ct_domain_syslog_redirection_disable"

    @property
    def description(self) -> str:
        return "Disable syslog messages redirection to parent domain"

    def get_schema(self) -> dict[str, Any]:
        return DomainLogRedirectionParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute domain syslog-redirection disable command."""
        result = self.ksctl.execute(["domains", "syslog-redirection", "disable"])
        return result.get("data", result.get("stdout", ""))


class DomainSyslogRedirectionStatusTool(BaseTool):
    """Get syslog messages redirection status."""

    @property
    def name(self) -> str:
        return "ct_domain_syslog_redirection_status"

    @property
    def description(self) -> str:
        return "Get status of syslog messages redirection to parent domain"

    def get_schema(self) -> dict[str, Any]:
        return DomainLogRedirectionParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute domain syslog-redirection status command."""
        result = self.ksctl.execute(["domains", "syslog-redirection", "status"])
        return result.get("data", result.get("stdout", ""))


class DomainManagementTool(BaseTool):
    name = "domain_management"
    description = "Domain management operations (switch, get_current, create, list, get, update, keks_list, keks_get, rotate_kek, retry_kek_rotation, log_forwarders_redirection_enable, log_forwarders_redirection_disable, log_forwarders_redirection_status, syslog_redirection_enable, syslog_redirection_disable, syslog_redirection_status)"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": [
                    "switch", "get_current", "create", "list", "get", "update", "keks_list", "keks_get", "rotate_kek", "retry_kek_rotation", "log_forwarders_redirection_enable", "log_forwarders_redirection_disable", "log_forwarders_redirection_status", "syslog_redirection_enable", "syslog_redirection_disable", "syslog_redirection_status"
                ]},
                **DomainSwitchParams.model_json_schema()["properties"],
                **DomainGetCurrentParams.model_json_schema()["properties"],
                **DomainCreateParams.model_json_schema()["properties"],
                **DomainListParams.model_json_schema()["properties"],
                **DomainGetParams.model_json_schema()["properties"],
                **DomainUpdateParams.model_json_schema()["properties"],
                **DomainKeksListParams.model_json_schema()["properties"],
                **DomainKeksGetParams.model_json_schema()["properties"],
                **DomainRotateKekParams.model_json_schema()["properties"],
                **DomainRetryKekRotationParams.model_json_schema()["properties"],
                **DomainLogRedirectionParams.model_json_schema()["properties"],
            },
            "required": ["action"],
        }

    async def execute(self, action: str, **kwargs: Any) -> Any:
        from ..config import settings
        if action == "switch":
            params = DomainSwitchParams(**kwargs)
            settings.ciphertrust_domain = params.domain
            if params.auth_domain:
                settings.ciphertrust_auth_domain = params.auth_domain
            return {
                "success": True,
                "message": f"Switched to domain: {params.domain}",
                "operating_domain": settings.ciphertrust_domain,
                "auth_domain": settings.ciphertrust_auth_domain
            }
        elif action == "get_current":
            return {
                "operating_domain": settings.ciphertrust_domain,
                "auth_domain": settings.ciphertrust_auth_domain,
                "message": f"Currently operating in domain: {settings.ciphertrust_domain}"
            }
        elif action == "create":
            params = DomainCreateParams(**kwargs)
            args = ["domains", "create", "--name", params.name, "--admins", params.admins]
            if params.allow_user_mgmt:
                args.append("--allow-user-mgmt")
            if params.hsm_connection_id:
                args.extend(["--hsm-connection-id", params.hsm_connection_id])
            if params.hsm_kek_label:
                args.extend(["--hsm-kek-label", params.hsm_kek_label])
            if params.parent_ca_id:
                args.extend(["--parent-ca-id", params.parent_ca_id])
            if params.jsonfile:
                args.extend(["--jsonfile", params.jsonfile])
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "list":
            params = DomainListParams(**kwargs)
            args = ["domains", "list", "--limit", str(params.limit), "--skip", str(params.skip)]
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "get":
            params = DomainGetParams(**kwargs)
            result = self.ksctl.execute(["domains", "get", "--id", params.id])
            return result.get("data", result.get("stdout", ""))
        elif action == "update":
            params = DomainUpdateParams(**kwargs)
            args = ["domains", "update", "--id", params.id]
            if params.hsm_connection_id:
                args.extend(["--hsm-connection-id", params.hsm_connection_id])
            if params.hsm_kek_label:
                args.extend(["--hsm-kek-label", params.hsm_kek_label])
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "keks_list":
            params = DomainKeksListParams(**kwargs)
            args = ["domains", "keks", "list", "--id", params.id, "--limit", str(params.limit), "--skip", str(params.skip)]
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "keks_get":
            params = DomainKeksGetParams(**kwargs)
            result = self.ksctl.execute(["domains", "keks", "get", "--id", params.id, "--kek-id", params.kek_id])
            return result.get("data", result.get("stdout", ""))
        elif action == "rotate_kek":
            params = DomainRotateKekParams(**kwargs)
            args = ["domains", "rotate-kek", "--id", params.id]
            if params.hsm_connection_id:
                args.extend(["--hsm-connection-id", params.hsm_connection_id])
            if params.hsm_kek_label:
                args.extend(["--hsm-kek-label", params.hsm_kek_label])
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "retry_kek_rotation":
            params = DomainRetryKekRotationParams(**kwargs)
            result = self.ksctl.execute(["domains", "retry-kek-rotation", "--id", params.id])
            return result.get("data", result.get("stdout", ""))
        elif action == "log_forwarders_redirection_enable":
            result = self.ksctl.execute(["domains", "log-forwarders-redirection", "enable"])
            return result.get("data", result.get("stdout", ""))
        elif action == "log_forwarders_redirection_disable":
            result = self.ksctl.execute(["domains", "log-forwarders-redirection", "disable"])
            return result.get("data", result.get("stdout", ""))
        elif action == "log_forwarders_redirection_status":
            result = self.ksctl.execute(["domains", "log-forwarders-redirection", "status"])
            return result.get("data", result.get("stdout", ""))
        elif action == "syslog_redirection_enable":
            result = self.ksctl.execute(["domains", "syslog-redirection", "enable"])
            return result.get("data", result.get("stdout", ""))
        elif action == "syslog_redirection_disable":
            result = self.ksctl.execute(["domains", "syslog-redirection", "disable"])
            return result.get("data", result.get("stdout", ""))
        elif action == "syslog_redirection_status":
            result = self.ksctl.execute(["domains", "syslog-redirection", "status"])
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")

DOMAIN_TOOLS = [DomainManagementTool]
