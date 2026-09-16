"""Backup key management tools for CipherTrust Manager with built-in domain support."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


# Backup Key Parameter Models
class BackupKeyCreateParams(BaseModel):
    """Parameters for creating a backup key."""
    scope: str = Field("system", description="Scope of the backup key (system or domain)")
    default: bool = Field(False, description="Set this backup key as default")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to create backup key in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


class BackupKeyListParams(BaseModel):
    """Parameters for listing backup keys."""
    limit: int = Field(10, description="Maximum number of backup keys to return")
    skip: int = Field(0, description="Offset at which to start the search")
    scope: str = Field("system", description="Scope of the backup key (system or domain)")
    default: bool = Field(False, description="Return only the default backup key")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to list backup keys from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


class BackupKeyGetParams(BaseModel):
    """Parameters for getting backup key information."""
    id: str = Field(..., description="Backup key ID")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to get backup key from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


class BackupKeyDeleteParams(BaseModel):
    """Parameters for deleting a backup key."""
    id: str = Field(..., description="Backup key ID")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to delete backup key from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


class BackupKeyDefaultParams(BaseModel):
    """Parameters for setting default backup key."""
    id: str = Field(..., description="Backup key ID to set as default")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to set default in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root'if not specified.")


class BackupKeyDownloadParams(BaseModel):
    """Parameters for downloading a backup key."""
    id: str = Field(..., description="Backup key ID")
    bkpassword: Optional[str] = Field(None, description="Backup key password (prompted securely if omitted)")
    file: Optional[str] = Field(None, description="File name to write downloaded backup key to")
    hint: Optional[str] = Field(None, description="Password hint for the backup key")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to download backup key from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


class BackupKeyUploadParams(BaseModel):
    """Parameters for uploading a backup key."""
    bkpassword: Optional[str] = Field(None, description="Backup key password (prompted securely if omitted)")
    file: Optional[str] = Field(None, description="File name to read backup key from")
    scope: str = Field("system", description="Scope of the backup key (scope is auto-detected, this flag is ignored)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to upload backup key to (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


class BackupKeyInspectParams(BaseModel):
    """Parameters for inspecting a backup key."""
    file: str = Field(..., description="Backup key file name to inspect")
    bkpassword: Optional[str] = Field(None, description="Backup key password to test (optional)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain context (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


class BackupKeyManagementTool(BaseTool):
    name = "backupkey_management"
    description = "Backup key management operations (create, list, get, delete, default, download, upload, inspect)"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": [
                    "create", "list", "get", "delete", "default", "download", "upload", "inspect"
                ]},
                **BackupKeyCreateParams.model_json_schema()["properties"],
                **BackupKeyListParams.model_json_schema()["properties"],
                **BackupKeyGetParams.model_json_schema()["properties"],
                **BackupKeyDeleteParams.model_json_schema()["properties"],
                **BackupKeyDefaultParams.model_json_schema()["properties"],
                **BackupKeyDownloadParams.model_json_schema()["properties"],
                **BackupKeyUploadParams.model_json_schema()["properties"],
                **BackupKeyInspectParams.model_json_schema()["properties"],
            },
            "required": ["action"],
        }

    async def execute(self, **kwargs: Any) -> Any:
        action = kwargs.get("action")
        if action == "create":
            params = BackupKeyCreateParams(**kwargs)
            args = ["backupkeys", "create"]
            if params.scope != "system":
                args.extend(["--scope", params.scope])
            if params.default:
                args.append("--default")
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "list":
            params = BackupKeyListParams(**kwargs)
            args = ["backupkeys", "list"]
            args.extend(["--limit", str(params.limit)])
            args.extend(["--skip", str(params.skip)])
            if params.scope != "system":
                args.extend(["--scope", params.scope])
            if params.default:
                args.append("--default")
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "get":
            params = BackupKeyGetParams(**kwargs)
            args = ["backupkeys", "get", "--id", params.id]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "delete":
            params = BackupKeyDeleteParams(**kwargs)
            args = ["backupkeys", "delete", "--id", params.id]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "default":
            params = BackupKeyDefaultParams(**kwargs)
            args = ["backupkeys", "default", "--id", params.id]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "download":
            params = BackupKeyDownloadParams(**kwargs)
            args = ["backupkeys", "download", "--id", params.id]
            if params.bkpassword:
                args.extend(["--bkpassword", params.bkpassword])
            if params.file:
                args.extend(["--file", params.file])
            if params.hint:
                args.extend(["--hint", params.hint])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "upload":
            params = BackupKeyUploadParams(**kwargs)
            args = ["backupkeys", "upload"]
            if params.bkpassword:
                args.extend(["--bkpassword", params.bkpassword])
            if params.file:
                args.extend(["--file", params.file])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "inspect":
            params = BackupKeyInspectParams(**kwargs)
            args = ["backupkeys", "inspect", "--file", params.file]
            if params.bkpassword:
                args.extend(["--bkpassword", params.bkpassword])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")

BACKUPKEY_TOOLS = [BackupKeyManagementTool]
