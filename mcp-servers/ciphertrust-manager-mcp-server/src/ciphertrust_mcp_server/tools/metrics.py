"""Metrics management tools for CipherTrust Manager (Prometheus integration)."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


class MetricsPrometheusStatusParams(BaseModel):
    """Parameters for getting Prometheus metrics status."""
    # No parameters needed for status
    pass


class MetricsPrometheusEnableParams(BaseModel):
    """Parameters for enabling Prometheus metrics."""
    # No parameters needed for enable
    pass


class MetricsPrometheusDisableParams(BaseModel):
    """Parameters for disabling Prometheus metrics."""
    # No parameters needed for disable
    pass


class MetricsPrometheusGetParams(BaseModel):
    """Parameters for getting Prometheus metrics."""
    api_token: str = Field(..., description="API token used for scraping metrics")
    file: Optional[str] = Field(None, description="File to write metrics to (stdout if not specified)")


class MetricsPrometheusRenewTokenParams(BaseModel):
    """Parameters for renewing Prometheus API token."""
    # No parameters needed for token renewal
    pass


class MetricsPrometheusStatusTool(BaseTool):
    """Get Prometheus metrics collection status."""

    @property
    def name(self) -> str:
        return "ct_metrics_prometheus_status"

    @property
    def description(self) -> str:
        return "Get the status of Prometheus metrics collection and API token"

    def get_schema(self) -> dict[str, Any]:
        return MetricsPrometheusStatusParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute metrics prometheus status command."""
        result = self.ksctl.execute(["metrics", "prometheus", "status"])
        return result.get("data", result.get("stdout", ""))


class MetricsPrometheusEnableTool(BaseTool):
    """Enable Prometheus metrics collection."""

    @property
    def name(self) -> str:
        return "ct_metrics_prometheus_enable"

    @property
    def description(self) -> str:
        return "Enable Prometheus metrics collection and get API token for scraping"

    def get_schema(self) -> dict[str, Any]:
        return MetricsPrometheusEnableParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute metrics prometheus enable command."""
        result = self.ksctl.execute(["metrics", "prometheus", "enable"])
        return result.get("data", result.get("stdout", ""))


class MetricsPrometheusDisableTool(BaseTool):
    """Disable Prometheus metrics collection."""

    @property
    def name(self) -> str:
        return "ct_metrics_prometheus_disable"

    @property
    def description(self) -> str:
        return "Disable Prometheus metrics collection"

    def get_schema(self) -> dict[str, Any]:
        return MetricsPrometheusDisableParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute metrics prometheus disable command."""
        result = self.ksctl.execute(["metrics", "prometheus", "disable"])
        return result.get("data", result.get("stdout", ""))


class MetricsPrometheusGetTool(BaseTool):
    """Get collected Prometheus metrics."""

    @property
    def name(self) -> str:
        return "ct_metrics_prometheus_get"

    @property
    def description(self) -> str:
        return "Retrieve the Prometheus metrics that have been collected"

    def get_schema(self) -> dict[str, Any]:
        return MetricsPrometheusGetParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute metrics prometheus get command."""
        params = MetricsPrometheusGetParams(**kwargs)
        
        args = ["metrics", "prometheus", "get"]
        args.extend(["--api-token", params.api_token])
        
        if params.file:
            args.extend(["--file", params.file])
        
        result = self.ksctl.execute(args)
        return result.get("data", result.get("stdout", ""))


class MetricsPrometheusRenewTokenTool(BaseTool):
    """Renew Prometheus API token."""

    @property
    def name(self) -> str:
        return "ct_metrics_prometheus_renew_token"

    @property
    def description(self) -> str:
        return "Renew the API token used for Prometheus metrics collection"

    def get_schema(self) -> dict[str, Any]:
        return MetricsPrometheusRenewTokenParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute metrics prometheus renew-token command."""
        result = self.ksctl.execute(["metrics", "prometheus", "renew-token"])
        return result.get("data", result.get("stdout", ""))


class MetricsManagementTool(BaseTool):
    """Manage Prometheus metrics operations (grouped)."""

    @property
    def name(self) -> str:
        return "metrics_management"

    @property
    def description(self) -> str:
        return "Manage Prometheus metrics operations (status, enable, disable, get, renew_token)"

    def get_schema(self) -> dict[str, Any]:
        return {
            "title": "MetricsManagementTool",
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "status", "enable", "disable", "get", "renew_token"
                    ],
                    "description": "Action to perform"
                },
                "api_token": {"type": "string", "description": "API token used for scraping metrics"},
                "file": {"type": "string", "description": "File to write metrics to (stdout if not specified)"}
            },
            "required": ["action"]
        }

    async def execute(self, **kwargs: Any) -> Any:
        action = kwargs.get("action")
        if action == "status":
            result = self.ksctl.execute(["metrics", "prometheus", "status"])
            return result.get("data", result.get("stdout", ""))
        elif action == "enable":
            result = self.ksctl.execute(["metrics", "prometheus", "enable"])
            return result.get("data", result.get("stdout", ""))
        elif action == "disable":
            result = self.ksctl.execute(["metrics", "prometheus", "disable"])
            return result.get("data", result.get("stdout", ""))
        elif action == "get":
            api_token = kwargs["api_token"]
            args = ["metrics", "prometheus", "get", "--api-token", api_token]
            if kwargs.get("file"):
                args.extend(["--file", kwargs["file"]])
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "renew_token":
            result = self.ksctl.execute(["metrics", "prometheus", "renew-token"])
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")


# Export only the grouped tool
METRICS_TOOLS = [MetricsManagementTool]
