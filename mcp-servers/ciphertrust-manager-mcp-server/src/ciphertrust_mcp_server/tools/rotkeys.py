"""Root of Trust (RoT) key management tools for CipherTrust Manager."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


class RotKeyListParams(BaseModel):
    """Parameters for listing RoT keys."""
    limit: int = Field(10, description="Maximum number of RoT keys to return")
    skip: int = Field(0, description="Offset at which to start the search")


class RotKeyGetParams(BaseModel):
    """Parameters for getting a RoT key."""
    id: str = Field(..., description="Root of trust key ID or name")


class RotKeyRotateParams(BaseModel):
    """Parameters for rotating a RoT key."""
    id: Optional[str] = Field(None, description="ID/name of existing key to rotate to (creates new if not specified)")


class RotKeyDeleteParams(BaseModel):
    """Parameters for deleting a RoT key."""
    id: str = Field(..., description="Root of trust key ID or name")
    force: bool = Field(False, description="Force deletion of the root of trust key")


class RotKeyManagementTool(BaseTool):
    name = "rotkey_management"
    description = "Root of Trust key management operations (list, get, rotate, delete)"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["list", "get", "rotate", "delete"]},
                **RotKeyListParams.model_json_schema()["properties"],
                **RotKeyGetParams.model_json_schema()["properties"],
                **RotKeyRotateParams.model_json_schema()["properties"],
                **RotKeyDeleteParams.model_json_schema()["properties"],
            },
            "required": ["action"],
        }

    async def execute(self, action: str, **kwargs: Any) -> Any:
        if action == "list":
            params = RotKeyListParams(**kwargs)
            args = ["rot-keys", "list", "--limit", str(params.limit), "--skip", str(params.skip)]
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "get":
            params = RotKeyGetParams(**kwargs)
            args = ["rot-keys", "get", "--id", params.id]
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "rotate":
            params = RotKeyRotateParams(**kwargs)
            args = ["rot-keys", "rotate"]
            if params.id:
                args.extend(["--id", params.id])
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "delete":
            params = RotKeyDeleteParams(**kwargs)
            args = ["rot-keys", "delete", "--id", params.id]
            if params.force:
                args.append("--force")
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")

ROTKEY_TOOLS = [RotKeyManagementTool]
