"""SCP public key management tools for CipherTrust Manager with built-in domain support."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


# SCP Public Key Parameter Models
class ScpPublicKeyGetParams(BaseModel):
    """Parameters for getting SCP public key."""
    # Domain support (SCP operations may be system-wide but including for consistency)
    domain: Optional[str] = Field(None, description="Domain to get SCP public key from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class ScpPublicKeyRotateParams(BaseModel):
    """Parameters for rotating SCP public key."""
    # Domain support (SCP operations may be system-wide but including for consistency)
    domain: Optional[str] = Field(None, description="Domain to rotate SCP public key in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class ScpManagementTool(BaseTool):
    name = "scp_management"
    description = "SCP public key management operations (public_key_get, public_key_rotate)"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["public_key_get", "public_key_rotate"]},
                **ScpPublicKeyGetParams.model_json_schema()["properties"],
                **ScpPublicKeyRotateParams.model_json_schema()["properties"],
            },
            "required": ["action"],
        }

    async def execute(self, **kwargs: Any) -> Any:
        action = kwargs.get("action")
        if action == "public_key_get":
            params = ScpPublicKeyGetParams(**kwargs)
            args = ["scp", "public-key", "get"]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "public_key_rotate":
            params = ScpPublicKeyRotateParams(**kwargs)
            args = ["scp", "public-key", "rotate"]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")


# Export all SCP tools
SCP_TOOLS = [ScpManagementTool]
