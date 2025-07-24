"""Services management tools for CipherTrust Manager."""

from typing import Any, Optional

from pydantic import BaseModel, Field, ValidationError

from .base import BaseTool


class ServiceStatusParams(BaseModel):
    """Parameters for getting service status."""
    service_names: Optional[str] = Field(None, description="Comma-separated list of service names to get status for (e.g., 'nae-kmip,web'). If omitted, returns status for all services.")
    overall_status: bool = Field(False, description="If true, returns only the overall status of all services.")


class ServiceRestartParams(BaseModel):
    """Parameters for restarting services."""
    service_names: str = Field(..., description="Comma-separated list of service names to restart (e.g., 'nae-kmip,web').")
    yes: bool = Field(True, description="Automatically respond yes to all prompts.")
    delay: int = Field(5, description="Delay in seconds before restart.")


class ServiceResetParams(BaseModel):
    """Parameters for resetting services."""
    delay: int = Field(5, description="Delay in seconds before reset.")
    yes: bool = Field(False, description="Confirm the reset operation. This must be set to true to proceed, as it will WIPE ALL DATA.")


class ServiceManagementTool(BaseTool):
    name = "service_management"
    description = "Manage CipherTrust Manager services. Allows getting status, restarting, and resetting services."

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string", 
                    "enum": ["status", "restart", "reset"],
                    "description": "The service management action to perform."
                },
                "params": {
                    "type": "object",
                    "description": "Parameters for the chosen action."
                }
            },
            "required": ["action"],
        }

    def execute(self, **kwargs: Any) -> Any:
        action = kwargs.get("action")
        params = kwargs.get("params", {})
        
        if not action:
            raise ValueError("Action is required")

        try:
            if action == "status":
                p = ServiceStatusParams(**params)
                args = ["services", "status"]
                if p.overall_status:
                    args.append("--overall-status")
                elif p.service_names:
                    args.extend(["--service-names", p.service_names])
                result = self.ksctl.execute(args)
                return result.get("data", result.get("stdout", ""))

            elif action == "restart":
                p = ServiceRestartParams(**params)
                args = ["services", "restart", "--service-names", p.service_names]
                if p.yes:
                    args.append("--yes")
                args.extend(["--delay", str(p.delay)])
                result = self.ksctl.execute(args)
                return result.get("data", result.get("stdout", ""))

            elif action == "reset":
                p = ServiceResetParams(**params)
                if not p.yes:
                    return {"error": "Resetting services is a destructive operation that will WIPE ALL DATA. You must confirm this by setting the 'yes' parameter to true."}
                
                warning = (
                    "WARNING: This operation will perform a full reset of CipherTrust Manager "
                    "and WIPE ALL DATA. This action cannot be undone."
                )
                args = ["services", "reset"]
                if p.yes:
                    args.append("--yes")
                args.extend(["--delay", str(p.delay)])
                result = self.ksctl.execute(args)
                if isinstance(result, dict):
                    result["warning"] = warning
                return result
            else:
                raise ValueError(f"Unknown action: {action}")
        except ValidationError as e:
            error_details = []
            for error in e.errors():
                loc = " -> ".join(map(str, error["loc"]))
                error_details.append(f"Parameter '{loc}': {error['msg']}")
            return {"error": f"Invalid parameters for action '{action}'. Please check your inputs.", "details": error_details}


SERVICE_MGMT_TOOLS = [ServiceManagementTool]
