"""Licensing management tools for CipherTrust Manager."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


# Licensed Features Parameter Models
class LicensingFeaturesListParams(BaseModel):
    """Parameters for listing licensed features."""
    bind_type: Optional[str] = Field(None, description="Bind type filter (cluster or instance)")


# License Management Parameter Models
class LicensingLicensesAddParams(BaseModel):
    """Parameters for adding a license."""
    license: str = Field(..., description="License code that is locked to this CipherTrust Manager instance")
    bind_type: Optional[str] = Field(None, description="Bind type (cluster or instance)")


class LicensingLicensesDeleteParams(BaseModel):
    """Parameters for deleting a license."""
    id: str = Field(..., description="ID of the license to delete")


class LicensingLicensesGetParams(BaseModel):
    """Parameters for getting a license."""
    id: str = Field(..., description="ID of the license to retrieve")


class LicensingLicensesListParams(BaseModel):
    """Parameters for listing licenses."""
    bind_type: Optional[str] = Field(None, description="Bind type filter (cluster or instance)")


# Lock Data Parameter Models  
class LicensingLockDataParams(BaseModel):
    """Parameters for getting license lock data."""
    # No parameters needed for lockdata
    pass


# Trials Parameter Models
class LicensingTrialsActivateParams(BaseModel):
    """Parameters for activating a trial."""
    id: str = Field(..., description="ID or name of the trial to activate")


class LicensingTrialsDeactivateParams(BaseModel):
    """Parameters for deactivating a trial."""
    id: str = Field(..., description="ID or name of the trial to deactivate")


class LicensingTrialsGetParams(BaseModel):
    """Parameters for getting a trial."""
    id: str = Field(..., description="ID or name of the trial to retrieve")


class LicensingTrialsListParams(BaseModel):
    """Parameters for listing trials."""
    # No parameters needed for trials list
    pass


# Tool Implementations - Licensed Features
class LicensingFeaturesListTool(BaseTool):
    """List licensed features."""

    @property
    def name(self) -> str:
        return "ct_licensing_features_list"

    @property
    def description(self) -> str:
        return "List information about all licensed features with optional bind-type filtering"

    def get_schema(self) -> dict[str, Any]:
        return LicensingFeaturesListParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute licensing features list command."""
        params = LicensingFeaturesListParams(**kwargs)
        
        args = ["licensing", "features", "list"]
        if params.bind_type:
            args.extend(["--bind-type", params.bind_type])
        
        result = self.ksctl.execute(args)
        return result.get("data", result.get("stdout", ""))


# License Management Tools
class LicensingLicensesAddTool(BaseTool):
    """Install a license code."""

    @property
    def name(self) -> str:
        return "ct_licensing_licenses_add"

    @property
    def description(self) -> str:
        return "Install a license code locked to this CipherTrust Manager instance or cluster"

    def get_schema(self) -> dict[str, Any]:
        return LicensingLicensesAddParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute licensing licenses add command."""
        params = LicensingLicensesAddParams(**kwargs)
        
        args = ["licensing", "licenses", "add", "--license", params.license]
        if params.bind_type:
            args.extend(["--bind-type", params.bind_type])
        
        result = self.ksctl.execute(args)
        return result.get("data", result.get("stdout", ""))


class LicensingLicensesDeleteTool(BaseTool):
    """Delete a license."""

    @property
    def name(self) -> str:
        return "ct_licensing_licenses_delete"

    @property
    def description(self) -> str:
        return "Delete a license by ID"

    def get_schema(self) -> dict[str, Any]:
        return LicensingLicensesDeleteParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute licensing licenses delete command."""
        params = LicensingLicensesDeleteParams(**kwargs)
        
        result = self.ksctl.execute([
            "licensing", "licenses", "delete",
            "--id", params.id
        ])
        return result.get("data", result.get("stdout", ""))


class LicensingLicensesGetTool(BaseTool):
    """Get information about a specific license."""

    @property
    def name(self) -> str:
        return "ct_licensing_licenses_get"

    @property
    def description(self) -> str:
        return "Get detailed information about a specific license by ID"

    def get_schema(self) -> dict[str, Any]:
        return LicensingLicensesGetParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute licensing licenses get command."""
        params = LicensingLicensesGetParams(**kwargs)
        
        result = self.ksctl.execute([
            "licensing", "licenses", "get",
            "--id", params.id
        ])
        return result.get("data", result.get("stdout", ""))


class LicensingLicensesListTool(BaseTool):
    """List all installed licenses."""

    @property
    def name(self) -> str:
        return "ct_licensing_licenses_list"

    @property
    def description(self) -> str:
        return "List information about all installed licenses with optional bind-type filtering"

    def get_schema(self) -> dict[str, Any]:
        return LicensingLicensesListParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute licensing licenses list command."""
        params = LicensingLicensesListParams(**kwargs)
        
        args = ["licensing", "licenses", "list"]
        if params.bind_type:
            args.extend(["--bind-type", params.bind_type])
        
        result = self.ksctl.execute(args)
        return result.get("data", result.get("stdout", ""))


# Lock Data Tool
class LicensingLockDataTool(BaseTool):
    """Get license lock data."""

    @property
    def name(self) -> str:
        return "ct_licensing_lockdata"

    @property
    def description(self) -> str:
        return "Get license lock data for use with Thales Virtual CipherTrust Manager License portal"

    def get_schema(self) -> dict[str, Any]:
        return LicensingLockDataParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute licensing lockdata command."""
        result = self.ksctl.execute(["licensing", "lockdata"])
        return result.get("data", result.get("stdout", ""))


# Trials Management Tools
class LicensingTrialsActivateTool(BaseTool):
    """Activate a feature trial."""

    @property
    def name(self) -> str:
        return "ct_licensing_trials_activate"

    @property
    def description(self) -> str:
        return "Activate a feature trial by name or ID"

    def get_schema(self) -> dict[str, Any]:
        return LicensingTrialsActivateParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute licensing trials activate command."""
        params = LicensingTrialsActivateParams(**kwargs)
        
        result = self.ksctl.execute([
            "licensing", "trials", "activate",
            "--id", params.id
        ])
        return result.get("data", result.get("stdout", ""))


class LicensingTrialsDeactivateTool(BaseTool):
    """Deactivate a feature trial."""

    @property
    def name(self) -> str:
        return "ct_licensing_trials_deactivate"

    @property
    def description(self) -> str:
        return "Deactivate a feature trial by name or ID"

    def get_schema(self) -> dict[str, Any]:
        return LicensingTrialsDeactivateParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute licensing trials deactivate command."""
        params = LicensingTrialsDeactivateParams(**kwargs)
        
        result = self.ksctl.execute([
            "licensing", "trials", "deactivate",
            "--id", params.id
        ])
        return result.get("data", result.get("stdout", ""))


class LicensingTrialsGetTool(BaseTool):
    """Get information about a specific trial."""

    @property
    def name(self) -> str:
        return "ct_licensing_trials_get"

    @property
    def description(self) -> str:
        return "Get detailed information about a specific trial by name or ID"

    def get_schema(self) -> dict[str, Any]:
        return LicensingTrialsGetParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute licensing trials get command."""
        params = LicensingTrialsGetParams(**kwargs)
        
        result = self.ksctl.execute([
            "licensing", "trials", "get",
            "--id", params.id
        ])
        return result.get("data", result.get("stdout", ""))


class LicensingTrialsListTool(BaseTool):
    """List available feature trials."""

    @property
    def name(self) -> str:
        return "ct_licensing_trials_list"

    @property
    def description(self) -> str:
        return "List all available feature trials"

    def get_schema(self) -> dict[str, Any]:
        return LicensingTrialsListParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute licensing trials list command."""
        result = self.ksctl.execute(["licensing", "trials", "list"])
        return result.get("data", result.get("stdout", ""))


# Export all licensing tools
LICENSING_TOOLS = [
    # Licensed Features
    LicensingFeaturesListTool,
    
    # License Management
    LicensingLicensesAddTool,
    LicensingLicensesDeleteTool,
    LicensingLicensesGetTool,
    LicensingLicensesListTool,
    
    # Lock Data
    LicensingLockDataTool,
    
    # Trials Management
    LicensingTrialsActivateTool,
    LicensingTrialsDeactivateTool,
    LicensingTrialsGetTool,
    LicensingTrialsListTool,
]

class LicensingManagementTool(BaseTool):
    name = "licensing_management"
    description = "Licensing management operations (features_list, licenses_add, licenses_delete, licenses_get, licenses_list, lockdata, trials_activate, trials_deactivate, trials_get, trials_list)"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": [
                    "features_list", "licenses_add", "licenses_delete", "licenses_get", "licenses_list", "lockdata", "trials_activate", "trials_deactivate", "trials_get", "trials_list"
                ]},
                **LicensingFeaturesListParams.model_json_schema()["properties"],
                **LicensingLicensesAddParams.model_json_schema()["properties"],
                **LicensingLicensesDeleteParams.model_json_schema()["properties"],
                **LicensingLicensesGetParams.model_json_schema()["properties"],
                **LicensingLicensesListParams.model_json_schema()["properties"],
                **LicensingLockDataParams.model_json_schema()["properties"],
                **LicensingTrialsActivateParams.model_json_schema()["properties"],
                **LicensingTrialsDeactivateParams.model_json_schema()["properties"],
                **LicensingTrialsGetParams.model_json_schema()["properties"],
                **LicensingTrialsListParams.model_json_schema()["properties"],
            },
            "required": ["action"],
        }

    async def execute(self, action: str, **kwargs: Any) -> Any:
        if action == "features_list":
            params = LicensingFeaturesListParams(**kwargs)
            args = ["licensing", "features", "list"]
            if params.bind_type:
                args.extend(["--bind-type", params.bind_type])
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "licenses_add":
            params = LicensingLicensesAddParams(**kwargs)
            args = ["licensing", "licenses", "add", "--license", params.license]
            if params.bind_type:
                args.extend(["--bind-type", params.bind_type])
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "licenses_delete":
            params = LicensingLicensesDeleteParams(**kwargs)
            result = self.ksctl.execute([
                "licensing", "licenses", "delete",
                "--id", params.id
            ])
            return result.get("data", result.get("stdout", ""))
        elif action == "licenses_get":
            params = LicensingLicensesGetParams(**kwargs)
            result = self.ksctl.execute([
                "licensing", "licenses", "get",
                "--id", params.id
            ])
            return result.get("data", result.get("stdout", ""))
        elif action == "licenses_list":
            params = LicensingLicensesListParams(**kwargs)
            args = ["licensing", "licenses", "list"]
            if params.bind_type:
                args.extend(["--bind-type", params.bind_type])
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "lockdata":
            result = self.ksctl.execute(["licensing", "lockdata"])
            return result.get("data", result.get("stdout", ""))
        elif action == "trials_activate":
            params = LicensingTrialsActivateParams(**kwargs)
            result = self.ksctl.execute([
                "licensing", "trials", "activate",
                "--id", params.id
            ])
            return result.get("data", result.get("stdout", ""))
        elif action == "trials_deactivate":
            params = LicensingTrialsDeactivateParams(**kwargs)
            result = self.ksctl.execute([
                "licensing", "trials", "deactivate",
                "--id", params.id
            ])
            return result.get("data", result.get("stdout", ""))
        elif action == "trials_get":
            params = LicensingTrialsGetParams(**kwargs)
            result = self.ksctl.execute([
                "licensing", "trials", "get",
                "--id", params.id
            ])
            return result.get("data", result.get("stdout", ""))
        elif action == "trials_list":
            result = self.ksctl.execute(["licensing", "trials", "list"])
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")

LICENSING_TOOLS = [LicensingManagementTool]
