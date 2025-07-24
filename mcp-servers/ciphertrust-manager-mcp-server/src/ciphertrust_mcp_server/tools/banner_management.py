from typing import Optional
from pydantic import BaseModel
from .base import BaseTool

class BannerGetParams(BaseModel):
    name: str  # 'pre-auth' or 'post-auth'

class BannerUpdateParams(BaseModel):
    name: str  # 'pre-auth' or 'post-auth'
    message: Optional[str] = None
    file: Optional[str] = None

class BannerManagementTool(BaseTool):
    name = "banner_management"
    description = "Manage login banners (pre-auth and post-auth) for CipherTrust Manager."

    def get_schema(self):
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["get", "update"]},
                "name": {"type": "string", "enum": ["pre-auth", "post-auth"]},
                "message": {"type": "string", "nullable": True},
                "file": {"type": "string", "nullable": True},
            },
            "required": ["action", "name"],
        }

    async def execute(self, **kwargs):
        action = kwargs.get("action")
        if action == "get":
            params = BannerGetParams(**kwargs)
            cmd = ["banners", "get", "--name", params.name]
            return self.execute_command(cmd)
        elif action == "update":
            params = BannerUpdateParams(**kwargs)
            cmd = ["banners", "update", "--name", params.name]
            if params.message:
                cmd += ["--message", params.message]
            if params.file:
                cmd += ["--file", params.file]
            return self.execute_command(cmd)
        else:
            return f"Unknown action: {action}"

BANNER_MANAGEMENT_TOOLS = [BannerManagementTool] 