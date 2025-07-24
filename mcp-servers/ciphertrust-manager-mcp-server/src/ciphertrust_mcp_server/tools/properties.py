"""System properties management tools for CipherTrust Manager."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


class PropertiesListParams(BaseModel):
    """Parameters for listing system properties."""
    limit: int = Field(10, description="Maximum number of properties to return")
    skip: int = Field(0, description="Offset at which to start the search")


class PropertiesGetParams(BaseModel):
    """Parameters for getting a system property."""
    name: str = Field(..., description="Name of the system configuration property")


class PropertiesModifyParams(BaseModel):
    """Parameters for modifying a system property."""
    name: str = Field(..., description="Name of the system configuration property")
    value: str = Field(..., description="Value to be set for the system configuration property")


class PropertiesResetParams(BaseModel):
    """Parameters for resetting a system property."""
    name: str = Field(..., description="Name of the system configuration property to reset")


class SystemPropertiesManagementTool(BaseTool):
    name = "system_properties_management"
    description = "System properties management operations (list, get, modify, reset)"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["list", "get", "modify", "reset"]},
                **PropertiesListParams.model_json_schema()["properties"],
                **PropertiesGetParams.model_json_schema()["properties"],
                **PropertiesModifyParams.model_json_schema()["properties"],
                **PropertiesResetParams.model_json_schema()["properties"],
            },
            "required": ["action"],
        }

    async def execute(self, action: str, **kwargs: Any) -> Any:
        if action == "list":
            params = PropertiesListParams(**kwargs)
            args = ["properties", "list"]
            args.extend(["--limit", str(params.limit)])
            args.extend(["--skip", str(params.skip)])
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "get":
            params = PropertiesGetParams(**kwargs)
            args = ["properties", "get", "--name", params.name]
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "modify":
            params = PropertiesModifyParams(**kwargs)
            args = ["properties", "modify"]
            args.extend(["--name", params.name])
            args.extend(["--value", params.value])
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "reset":
            params = PropertiesResetParams(**kwargs)
            args = ["properties", "reset", "--name", params.name]
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")

PROPERTIES_TOOLS = [SystemPropertiesManagementTool]
