"""Backup management tools for CipherTrust Manager with built-in domain support."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


# Core Backup Parameter Models
class BackupCreateParams(BaseModel):
    """Parameters for creating a backup."""
    scope: str = Field("system", description="Scope of the backup (system or domain)")
    tied_to_hsm: bool = Field(False, description="Backup can only be restored on instances using same HSM partition (system scope only)")
    keyid: Optional[str] = Field(None, description="Backup key ID for encryption/decryption")
    description: Optional[str] = Field(None, description="User defined description for the backup")
    filters: Optional[str] = Field(None, description="JSON filters for domain-scoped backups to specify resources to include")
    filters_jsonfile: Optional[str] = Field(None, description="JSON file containing filters for domain-scoped backups")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to create backup in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class BackupListParams(BaseModel):
    """Parameters for listing backups."""
    limit: int = Field(10, description="Maximum number of backups to return")
    skip: int = Field(0, description="Offset at which to start the search")
    scope: str = Field("system", description="Scope of the backup (system or domain)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to list backups from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class BackupGetParams(BaseModel):
    """Parameters for getting backup information."""
    id: str = Field(..., description="Backup ID")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to get backup from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class BackupDeleteParams(BaseModel):
    """Parameters for deleting a backup."""
    id: str = Field(..., description="Backup ID")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to delete backup from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class BackupRestoreParams(BaseModel):
    """Parameters for restoring a backup."""
    id: str = Field(..., description="Backup ID")
    force: bool = Field(False, description="Skip version check prior to restore")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to restore backup in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class BackupStatusParams(BaseModel):
    """Parameters for getting backup status."""
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to get status from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class BackupDownloadParams(BaseModel):
    """Parameters for downloading a backup."""
    id: str = Field(..., description="Backup ID")
    file: Optional[str] = Field(None, description="File name to write downloaded backup to")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to download backup from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class BackupUploadParams(BaseModel):
    """Parameters for uploading a backup."""
    file: Optional[str] = Field(None, description="File name to read backup from")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to upload backup to (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class BackupInspectParams(BaseModel):
    """Parameters for inspecting a backup."""
    file: str = Field(..., description="Backup file name to inspect")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain context (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class BackupScpParams(BaseModel):
    """Parameters for SCP backup transfer."""
    id: str = Field(..., description="Backup ID")
    conn: str = Field(..., description="Name or ID of the SCP connection")
    host: str = Field(..., description="Server hostname")
    port: int = Field(..., description="Port on SCP host to connect")
    username: str = Field(..., description="Username for SCP host access")
    auth_method: str = Field(..., description="Authentication type (key or password)")
    path_to: str = Field(..., description="Destination path for SCP transfer")
    public_key: str = Field(..., description="Public key for host verification")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain context (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class BackupScpStatusParams(BaseModel):
    """Parameters for getting SCP backup status."""
    id: str = Field(..., description="Backup ID")
    scpid: str = Field(..., description="SCP ID")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain context (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class BackupManagementTool(BaseTool):
    name = "backup_management"
    description = "Backup management operations (create, list, get, delete, restore, status, download, upload, inspect, scp, scp_status)"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": [
                    "create", "list", "get", "delete", "restore", "status", "download", "upload", "inspect", "scp", "scp_status"
                ]},
                **BackupCreateParams.model_json_schema()["properties"],
                **BackupListParams.model_json_schema()["properties"],
                **BackupGetParams.model_json_schema()["properties"],
                **BackupDeleteParams.model_json_schema()["properties"],
                **BackupRestoreParams.model_json_schema()["properties"],
                **BackupStatusParams.model_json_schema()["properties"],
                **BackupDownloadParams.model_json_schema()["properties"],
                **BackupUploadParams.model_json_schema()["properties"],
                **BackupInspectParams.model_json_schema()["properties"],
                **BackupScpParams.model_json_schema()["properties"],
                **BackupScpStatusParams.model_json_schema()["properties"],
            },
            "required": ["action"],
        }

    async def execute(self, **kwargs: Any) -> Any:
        action = kwargs.get("action")
        if action == "create":
            params = BackupCreateParams(**kwargs)
            args = ["backup", "create"]
            if params.scope != "system":
                args.extend(["--scope", params.scope])
            if params.tied_to_hsm:
                args.append("--tied-to-hsm")
            if params.keyid:
                args.extend(["--keyid", params.keyid])
            if params.description:
                args.extend(["--description", params.description])
            if params.filters:
                args.extend(["--filters", params.filters])
            if params.filters_jsonfile:
                args.extend(["--filters-jsonfile", params.filters_jsonfile])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "list":
            params = BackupListParams(**kwargs)
            args = ["backup", "list"]
            args.extend(["--limit", str(params.limit)])
            args.extend(["--skip", str(params.skip)])
            if params.scope != "system":
                args.extend(["--scope", params.scope])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "get":
            params = BackupGetParams(**kwargs)
            args = ["backup", "get", "--id", params.id]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "delete":
            params = BackupDeleteParams(**kwargs)
            args = ["backup", "delete", "--id", params.id]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "restore":
            params = BackupRestoreParams(**kwargs)
            args = ["backup", "restore", "--id", params.id]
            if params.force:
                args.append("--force")
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "status":
            params = BackupStatusParams(**kwargs)
            args = ["backup", "status"]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "download":
            params = BackupDownloadParams(**kwargs)
            args = ["backup", "download", "--id", params.id]
            if params.file:
                args.extend(["--file", params.file])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "upload":
            params = BackupUploadParams(**kwargs)
            args = ["backup", "upload"]
            if params.file:
                args.extend(["--file", params.file])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "inspect":
            params = BackupInspectParams(**kwargs)
            args = ["backup", "inspect", "--file", params.file]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "scp":
            params = BackupScpParams(**kwargs)
            args = ["backup", "scp"]
            args.extend(["--id", params.id])
            args.extend(["--conn", params.conn])
            args.extend(["--host", params.host])
            args.extend(["--port", str(params.port)])
            args.extend(["--username", params.username])
            args.extend(["--auth-method", params.auth_method])
            args.extend(["--path-to", params.path_to])
            args.extend(["--public-key", params.public_key])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "scp_status":
            params = BackupScpStatusParams(**kwargs)
            args = ["backup", "scp", "status"]
            args.extend(["--id", params.id])
            args.extend(["--scpid", params.scpid])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")

BACKUP_TOOLS = [BackupManagementTool]
