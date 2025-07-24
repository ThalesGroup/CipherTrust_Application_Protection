"""System information tools for CipherTrust Manager."""

from typing import Any
from pydantic import BaseModel, Field
from .base import BaseTool


class SystemInfoGetParams(BaseModel):
    """Parameters for system info get."""
    # No parameters needed for get
    pass


class SystemInfoSetParams(BaseModel):
    """Parameters for system info set."""
    name: str = Field(..., description="User friendly name for the system")


class SystemInformationTool(BaseTool):
    name = "system_information"
    description = "Get or set CipherTrust Manager system information. Actions: get, set."

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["get", "set"]},
                "name": {"type": "string", "description": "User friendly name for the system (for set action)", "nullable": True},
            },
            "required": ["action"],
        }

    async def execute(self, **kwargs: Any) -> Any:
        action = kwargs.get("action")
        if action == "get":
            result = self.ksctl.execute(["system", "info", "get"])
            return result.get("data", result.get("stdout", ""))
        elif action == "set":
            name = kwargs.get("name")
            if not name:
                raise ValueError("'name' is required for set action")
            result = self.ksctl.execute(["system", "info", "set", "--name", name])
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")


# Export all system tools
SYSTEM_TOOLS = [SystemInformationTool]
