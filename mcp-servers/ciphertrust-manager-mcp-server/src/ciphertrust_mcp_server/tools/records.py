"""Audit records management tools for CipherTrust Manager."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


# Records Parameter Models
class RecordListParams(BaseModel):
    """Parameters for listing audit records."""
    limit: int = Field(10, description="Maximum number of records to return")
    skip: int = Field(0, description="Offset at which to start the search")
    created_after: Optional[str] = Field(None, description="Return records created at or after this time (e.g., '1 hour ago', RFC3339)")
    created_before: Optional[str] = Field(None, description="Return records created before or at this time")
    client_ip: Optional[str] = Field(None, description="Filter by client IP address")
    message: Optional[str] = Field(None, description="Filter by message content")
    service: Optional[str] = Field(None, description="Filter by service name")
    severity: Optional[str] = Field(None, description="Filter by severity (info, warning, debug, error)")
    source: Optional[str] = Field(None, description="Filter by source")
    success: Optional[str] = Field(None, description="Filter by success value ('true' or 'false')")


class RecordGetParams(BaseModel):
    """Parameters for getting a specific record."""
    id: str = Field(..., description="ID of the audit record")


# Alarm Config Parameter Models
class AlarmConfigListParams(BaseModel):
    """Parameters for listing alarm configs."""
    limit: int = Field(10, description="Maximum number of alarm configs to return")
    skip: int = Field(0, description="Offset at which to start the search")
    name: Optional[str] = Field(None, description="Filter by alarm name")


class AlarmConfigCreateParams(BaseModel):
    """Parameters for creating an alarm config."""
    name: str = Field(..., description="Name of alarm when triggered (e.g., 'Weak RSA Key')")
    description: str = Field(..., description="Description of alarm when triggered")
    severity: str = Field(..., description="Severity of alarm (critical, error, warning, info)")
    condition: Optional[str] = Field(None, description="Rego query condition (semicolon-separated subconditions)")
    conditionfile: Optional[str] = Field(None, description="File containing Rego query condition")
    threshold: int = Field(0, description="Number of matching records within interval to trigger alarm")
    interval: int = Field(0, description="Time interval in seconds for threshold evaluation")


class AlarmConfigGetParams(BaseModel):
    """Parameters for getting an alarm config."""
    id: str = Field(..., description="ID of the alarm config")


class AlarmConfigUpdateParams(BaseModel):
    """Parameters for updating an alarm config."""
    id: str = Field(..., description="ID of the alarm config")
    name: Optional[str] = Field(None, description="New name for the alarm")
    description: Optional[str] = Field(None, description="New description")
    severity: Optional[str] = Field(None, description="New severity level")
    condition: Optional[str] = Field(None, description="New Rego query condition")
    conditionfile: Optional[str] = Field(None, description="File with new Rego query condition")
    threshold: Optional[int] = Field(None, description="New threshold value")
    interval: Optional[int] = Field(None, description="New interval in seconds")


class AlarmConfigDeleteParams(BaseModel):
    """Parameters for deleting an alarm config."""
    id: str = Field(..., description="ID of the alarm config")


class RecordManagementTool(BaseTool):
    name = "record_management"
    description = "Audit record and alarm config management operations (record_list, record_get, alarm_config_list, alarm_config_create, alarm_config_get, alarm_config_update, alarm_config_delete)"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": [
                    "record_list", "record_get", "alarm_config_list", "alarm_config_create", "alarm_config_get", "alarm_config_update", "alarm_config_delete"
                ]},
                **RecordListParams.model_json_schema()["properties"],
                **RecordGetParams.model_json_schema()["properties"],
                **AlarmConfigListParams.model_json_schema()["properties"],
                **AlarmConfigCreateParams.model_json_schema()["properties"],
                **AlarmConfigGetParams.model_json_schema()["properties"],
                **AlarmConfigUpdateParams.model_json_schema()["properties"],
                **AlarmConfigDeleteParams.model_json_schema()["properties"],
            },
            "required": ["action"],
        }

    async def execute(self, **kwargs: Any) -> Any:
        action = kwargs.get("action")
        if action == "record_list":
            params = RecordListParams(**kwargs)
            args = ["records", "list"]
            args.extend(["--limit", str(params.limit)])
            args.extend(["--skip", str(params.skip)])
            if params.created_after:
                args.extend(["--created-after", params.created_after])
            if params.created_before:
                args.extend(["--created-before", params.created_before])
            if params.client_ip:
                args.extend(["--client-ip", params.client_ip])
            if params.message:
                args.extend(["--message", params.message])
            if params.service:
                args.extend(["--service", params.service])
            if params.severity:
                args.extend(["--severity", params.severity])
            if params.source:
                args.extend(["--source", params.source])
            if params.success:
                args.extend(["--success", params.success])
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "record_get":
            params = RecordGetParams(**kwargs)
            args = ["records", "get", "--id", params.id]
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "alarm_config_list":
            params = AlarmConfigListParams(**kwargs)
            args = ["records", "alarm-configs", "list"]
            args.extend(["--limit", str(params.limit)])
            args.extend(["--skip", str(params.skip)])
            if params.name:
                args.extend(["--name", params.name])
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "alarm_config_create":
            params = AlarmConfigCreateParams(**kwargs)
            if not params.condition and not params.conditionfile:
                raise ValueError("Either condition or conditionfile must be specified")
            args = ["records", "alarm-configs", "create"]
            args.extend(["--name", params.name])
            args.extend(["--description", params.description])
            args.extend(["--severity", params.severity])
            args.extend(["--threshold", str(params.threshold)])
            args.extend(["--interval", str(params.interval)])
            if params.condition:
                args.extend(["--condition", params.condition])
            elif params.conditionfile:
                args.extend(["--conditionfile", params.conditionfile])
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "alarm_config_get":
            params = AlarmConfigGetParams(**kwargs)
            args = ["records", "alarm-configs", "get", "--id", params.id]
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "alarm_config_update":
            params = AlarmConfigUpdateParams(**kwargs)
            args = ["records", "alarm-configs", "update", "--id", params.id]
            if params.name:
                args.extend(["--name", params.name])
            if params.description:
                args.extend(["--description", params.description])
            if params.severity:
                args.extend(["--severity", params.severity])
            if params.threshold is not None:
                args.extend(["--threshold", str(params.threshold)])
            if params.interval is not None:
                args.extend(["--interval", str(params.interval)])
            if params.condition:
                args.extend(["--condition", params.condition])
            elif params.conditionfile:
                args.extend(["--conditionfile", params.conditionfile])
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        elif action == "alarm_config_delete":
            params = AlarmConfigDeleteParams(**kwargs)
            args = ["records", "alarm-configs", "delete", "--id", params.id]
            result = self.ksctl.execute(args)
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")

RECORD_TOOLS = [RecordManagementTool]
