"""Master Key Encryption Keys (mkeks) management tools for CipherTrust Manager."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


class MkeksListParams(BaseModel):
    """Parameters for listing master KEKs."""
    all: bool = Field(False, description="List all Master KEKs (default and non-default), otherwise only default")


class MkeksGetParams(BaseModel):
    """Parameters for getting a master KEK."""
    id: str = Field(..., description="Master KEK ID")


class MkeksRotateParams(BaseModel):
    """Parameters for rotating a master KEK."""
    name: Optional[str] = Field(None, description="Custom name for the new Master KEK")


class MasterKekManagementTool(BaseTool):
    name = "master_kek_management"
    description = "Master KEK management operations (list, get, rotate)"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["list", "get", "rotate"]},
                **MkeksListParams.model_json_schema()["properties"],
                **MkeksGetParams.model_json_schema()["properties"],
                **MkeksRotateParams.model_json_schema()["properties"],
            },
            "required": ["action"],
        }

    async def execute(self, action: str, **kwargs: Any) -> Any:
        if action == "list":
            params = MkeksListParams(**kwargs)
            args = ["mkeks", "list"]
            if params.all:
                args.append("--all")
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "get":
            params = MkeksGetParams(**kwargs)
            args = ["mkeks", "get", "--id", params.id]
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "rotate":
            params = MkeksRotateParams(**kwargs)
            args = ["mkeks", "rotate"]
            if params.name:
                args.extend(["--name", params.name])
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")

MKEKS_TOOLS = [MasterKekManagementTool]
