"""Network Time Protocol (NTP) management tools for CipherTrust Manager."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


class NtpStatusParams(BaseModel):
    """Parameters for getting NTP status."""
    # No parameters needed for status
    pass


class NtpServersListParams(BaseModel):
    """Parameters for listing NTP servers."""
    # No parameters needed for list
    pass


class NtpServersAddParams(BaseModel):
    """Parameters for adding an NTP server."""
    host: str = Field(..., description="NTP server host or IP address")
    key: Optional[str] = Field(None, description="Encryption key for authenticated NTP server")


class NtpServersGetParams(BaseModel):
    """Parameters for getting NTP server info."""
    host: str = Field(..., description="NTP server host or IP address")


class NtpServersDeleteParams(BaseModel):
    """Parameters for deleting an NTP server."""
    host: str = Field(..., description="NTP server host or IP address")


class NtpManagementTool(BaseTool):
    name = "ntp_management"
    description = "NTP management operations (status, servers_list, servers_add, servers_get, servers_delete)"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["status", "servers_list", "servers_add", "servers_get", "servers_delete"]},
                **NtpStatusParams.model_json_schema()["properties"],
                **NtpServersListParams.model_json_schema()["properties"],
                **NtpServersAddParams.model_json_schema()["properties"],
                **NtpServersGetParams.model_json_schema()["properties"],
                **NtpServersDeleteParams.model_json_schema()["properties"],
            },
            "required": ["action"],
        }

    async def execute(self, action: str, **kwargs: Any) -> Any:
        if action == "status":
            result = self.ksctl.execute(["ntp", "status"])
            return result.get("data", result.get("stdout", ""))
        elif action == "servers_list":
            result = self.ksctl.execute(["ntp", "servers", "list"])
            return result.get("data", result.get("stdout", ""))
        elif action == "servers_add":
            params = NtpServersAddParams(**kwargs)
            args = ["ntp", "servers", "add", "--host", params.host]
            if params.key:
                args.extend(["--key", params.key])
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "servers_get":
            params = NtpServersGetParams(**kwargs)
            args = ["ntp", "servers", "get", "--host", params.host]
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "servers_delete":
            params = NtpServersDeleteParams(**kwargs)
            args = ["ntp", "servers", "delete", "--host", params.host]
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")

NTP_TOOLS = [NtpManagementTool]
