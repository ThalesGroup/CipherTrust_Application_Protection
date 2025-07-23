"""Proxy configuration management tools for CipherTrust Manager."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


# Proxy Configuration Parameter Models
class ProxyListParams(BaseModel):
    """Parameters for listing proxy configurations."""
    # No parameters needed for list
    pass


class ProxyAddParams(BaseModel):
    """Parameters for adding proxy configuration."""
    http_proxy: Optional[str] = Field(None, description="HTTP proxy URL")
    https_proxy: Optional[str] = Field(None, description="HTTPS proxy URL")
    no_proxy: Optional[str] = Field(None, description="Comma-separated list of no-proxy exceptions")
    ca_cert_file: Optional[str] = Field(None, description="Path to CA certificate file to be trusted")


class ProxyUpdateParams(BaseModel):
    """Parameters for updating proxy configuration."""
    http_proxy: Optional[str] = Field(None, description="HTTP proxy URL")
    https_proxy: Optional[str] = Field(None, description="HTTPS proxy URL")
    no_proxy: Optional[str] = Field(None, description="Comma-separated list of no-proxy exceptions")
    ca_cert_file: Optional[str] = Field(None, description="Path to CA certificate file to be trusted")


class ProxyDeleteParams(BaseModel):
    """Parameters for deleting proxy configuration."""
    # No parameters needed for delete
    pass


class ProxyTestParams(BaseModel):
    """Parameters for testing proxy configuration."""
    http_proxy: Optional[str] = Field(None, description="HTTP proxy URL to test")
    https_proxy: Optional[str] = Field(None, description="HTTPS proxy URL to test")
    test_url: Optional[str] = Field(None, description="HTTPS URL to test (default: https://www.thalesdocs.com)")
    ca_cert_file: Optional[str] = Field(None, description="Path to CA certificate file to be trusted")


# Proxy Protocol Allow Proxies Parameter Models
class ProxyProtocolAllowProxiesListParams(BaseModel):
    """Parameters for listing proxy protocol allow proxies."""
    limit: int = Field(10, description="Maximum number of configurations to return")
    skip: int = Field(0, description="Offset at which to start the search")


class ProxyProtocolAllowProxiesAddParams(BaseModel):
    """Parameters for adding proxy protocol allow proxies."""
    ip_address: str = Field(..., description="IP address or CIDR block for proxy configuration")
    description: Optional[str] = Field(None, description="Description for proxy configuration")


class ProxyProtocolAllowProxiesGetParams(BaseModel):
    """Parameters for getting proxy protocol allow proxies."""
    id: str = Field(..., description="Proxy protocol allow proxy ID")


class ProxyProtocolAllowProxiesUpdateParams(BaseModel):
    """Parameters for updating proxy protocol allow proxies."""
    id: str = Field(..., description="Proxy protocol allow proxy ID")
    description: Optional[str] = Field(None, description="Description for proxy configuration")


class ProxyProtocolAllowProxiesDeleteParams(BaseModel):
    """Parameters for deleting proxy protocol allow proxies."""
    id: str = Field(..., description="Proxy protocol allow proxy ID")


class ProxyProtocolAllowProxiesResetParams(BaseModel):
    """Parameters for resetting proxy protocol allow proxies."""
    # No parameters needed for reset
    pass


class ProxyManagementTool(BaseTool):
    name = "proxy_management"
    description = "Proxy and proxy protocol allow proxies management operations (list, add, update, delete, test, protocol_allow_list, protocol_allow_add, protocol_allow_get, protocol_allow_update, protocol_allow_delete, protocol_allow_reset)"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": [
                    "list", "add", "update", "delete", "test",
                    "protocol_allow_list", "protocol_allow_add", "protocol_allow_get", "protocol_allow_update", "protocol_allow_delete", "protocol_allow_reset"
                ]},
                **ProxyListParams.model_json_schema()["properties"],
                **ProxyAddParams.model_json_schema()["properties"],
                **ProxyUpdateParams.model_json_schema()["properties"],
                **ProxyDeleteParams.model_json_schema()["properties"],
                **ProxyTestParams.model_json_schema()["properties"],
                **ProxyProtocolAllowProxiesListParams.model_json_schema()["properties"],
                **ProxyProtocolAllowProxiesAddParams.model_json_schema()["properties"],
                **ProxyProtocolAllowProxiesGetParams.model_json_schema()["properties"],
                **ProxyProtocolAllowProxiesUpdateParams.model_json_schema()["properties"],
                **ProxyProtocolAllowProxiesDeleteParams.model_json_schema()["properties"],
                **ProxyProtocolAllowProxiesResetParams.model_json_schema()["properties"],
            },
            "required": ["action"],
        }

    async def execute(self, action: str, **kwargs: Any) -> Any:
        if action == "list":
            result = self.ksctl.execute(["proxy", "list"])
            return result.get("data", result.get("stdout", ""))
        elif action == "add":
            params = ProxyAddParams(**kwargs)
            args = ["proxy", "add"]
            if params.http_proxy:
                args.extend(["--http-proxy", params.http_proxy])
            if params.https_proxy:
                args.extend(["--https-proxy", params.https_proxy])
            if params.no_proxy:
                args.extend(["--no-proxy", params.no_proxy])
            if params.ca_cert_file:
                args.extend(["--ca-cert-file", params.ca_cert_file])
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "update":
            params = ProxyUpdateParams(**kwargs)
            args = ["proxy", "update"]
            if params.http_proxy:
                args.extend(["--http-proxy", params.http_proxy])
            if params.https_proxy:
                args.extend(["--https-proxy", params.https_proxy])
            if params.no_proxy:
                args.extend(["--no-proxy", params.no_proxy])
            if params.ca_cert_file:
                args.extend(["--ca-cert-file", params.ca_cert_file])
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "delete":
            result = self.ksctl.execute(["proxy", "delete"])
            return result.get("data", result.get("stdout", ""))
        elif action == "test":
            params = ProxyTestParams(**kwargs)
            args = ["proxy", "test"]
            if params.http_proxy:
                args.extend(["--http-proxy", params.http_proxy])
            if params.https_proxy:
                args.extend(["--https-proxy", params.https_proxy])
            if params.test_url:
                args.extend(["--test-url", params.test_url])
            if params.ca_cert_file:
                args.extend(["--ca-cert-file", params.ca_cert_file])
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "protocol_allow_list":
            params = ProxyProtocolAllowProxiesListParams(**kwargs)
            args = ["proxyprotocolallowproxies", "list", "--limit", str(params.limit), "--skip", str(params.skip)]
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "protocol_allow_add":
            params = ProxyProtocolAllowProxiesAddParams(**kwargs)
            args = ["proxyprotocolallowproxies", "add", "--ip-address", params.ip_address]
            if params.description:
                args.extend(["--description", params.description])
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "protocol_allow_get":
            params = ProxyProtocolAllowProxiesGetParams(**kwargs)
            args = ["proxyprotocolallowproxies", "get", "--id", params.id]
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "protocol_allow_update":
            params = ProxyProtocolAllowProxiesUpdateParams(**kwargs)
            args = ["proxyprotocolallowproxies", "update", "--id", params.id]
            if params.description:
                args.extend(["--description", params.description])
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "protocol_allow_delete":
            params = ProxyProtocolAllowProxiesDeleteParams(**kwargs)
            args = ["proxyprotocolallowproxies", "delete", "--id", params.id]
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "protocol_allow_reset":
            result = self.ksctl.execute(["proxyprotocolallowproxies", "reset"])
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")

PROXY_TOOLS = [ProxyManagementTool]
