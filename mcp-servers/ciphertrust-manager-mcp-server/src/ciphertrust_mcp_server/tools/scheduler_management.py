"""Scheduler Management Tool for CipherTrust Manager.

This tool provides comprehensive scheduler configuration and job management capabilities,
including creating, listing, getting, deleting, and modifying scheduler configurations,
as well as managing scheduler job runs.
"""

from typing import Any, Optional, Dict
from pydantic import BaseModel, Field
from .base import BaseTool
import re


def validate_scheduler_job_type(job_type: str) -> None:
    """Validate scheduler job type."""
    valid_job_types = [
        "key-rotation", "cckm-synchronization", "backup", "cckm-key-rotation", 
        "cckm-xks-credential-rotation", "sync-crl", "user-password-expiry-notification", 
        "cckm-add-containers", "cckm-key-backup"
    ]
    if job_type not in valid_job_types:
        raise ValueError(f"Invalid job_type '{job_type}'. "
                        f"Valid values: {', '.join(valid_job_types)}")


def validate_scheduler_params(params: Dict[str, Any], job_type: str) -> None:
    """Validate parameters for scheduler operations."""
    # Validate job type
    validate_scheduler_job_type(job_type)
    
    # Validate required parameters based on job type
    if job_type == "cckm-synchronization":
        required_params = ["cloud_name"]
        missing_params = []
        
        for param in required_params:
            if param not in params or params[param] is None:
                missing_params.append(param)
        
        if missing_params:
            raise ValueError(f"Missing required parameters for cckm-synchronization: {', '.join(missing_params)}. "
                            f"Required parameters: {', '.join(required_params)}")
        
        # Validate cloud_name
        valid_clouds = ["aws", "hsm-luna", "dsm", "oci", "sfdc", "gcp", "sap", "AzureCloud"]
        if params.get("cloud_name") not in valid_clouds:
            raise ValueError(f"Invalid cloud_name '{params.get('cloud_name')}'. "
                            f"Valid values: {', '.join(valid_clouds)}")
    
    elif job_type == "cckm-add-containers":
        required_params = ["cloud_name", "connection_id"]
        missing_params = []
        
        for param in required_params:
            if param not in params or params[param] is None:
                missing_params.append(param)
        
        if missing_params:
            raise ValueError(f"Missing required parameters for cckm-add-containers: {', '.join(missing_params)}. "
                            f"Required parameters: {', '.join(required_params)}")
    
    elif job_type == "key-rotation":
        # key-rotation doesn't have specific required parameters beyond the basic ones
        pass
    
    elif job_type == "backup":
        required_params = ["backup_type"]
        missing_params = []
        
        for param in required_params:
            if param not in params or params[param] is None:
                missing_params.append(param)
        
        if missing_params:
            raise ValueError(f"Missing required parameters for backup: {', '.join(missing_params)}. "
                            f"Required parameters: {', '.join(required_params)}")
        
        # Validate backup_type
        valid_backup_types = ["database", "scp"]
        if params.get("backup_type") not in valid_backup_types:
            raise ValueError(f"Invalid backup_type '{params.get('backup_type')}'. "
                            f"Valid values: {', '.join(valid_backup_types)}")


def validate_cron_expression(cron_expr: str) -> None:
    """Validate cron expression format."""
    if not cron_expr or not isinstance(cron_expr, str):
        raise ValueError("Cron expression must be a non-empty string")
    
    # Basic cron validation (5 fields: minute hour day month weekday)
    parts = cron_expr.split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron expression '{cron_expr}'. "
                        f"Expected 5 fields (minute hour day month weekday), got {len(parts)}")
    
    # Validate each field
    for i, part in enumerate(parts):
        if not part or part == "":
            raise ValueError(f"Empty field in cron expression at position {i+1}")
        
        # Basic validation - allow common cron patterns
        if not re.match(r'^(\*|[0-9,\-*/]+)$', part):
            raise ValueError(f"Invalid cron field '{part}' at position {i+1}. "
                            f"Expected format: number, range, list, or *")


# Scheduler Config Parameter Models
class SchedulerConfigCreateParams(BaseModel):
    """Parameters for creating scheduler configurations."""
    job_type: str = Field(..., description="Type of scheduler job (key-rotation, cckm-synchronization, backup, cckm-key-rotation, cckm-xks-credential-rotation, sync-crl, user-password-expiry-notification, cckm-add-containers, cckm-key-backup)")
    name: str = Field(..., description="Name of the scheduler configuration")
    run_at: str = Field(..., description="Cron expression for when the job should run (e.g., '0 9 * * *' for daily at 9 AM)")
    description: Optional[str] = Field(None, description="Description of the scheduler configuration")
    disabled: Optional[bool] = Field(None, description="Whether to disable the job on creation")
    start_date: Optional[str] = Field(None, description="Date and time when configuration is activated (RFC3339Nano or free-form string)")
    end_date: Optional[str] = Field(None, description="Date and time when configuration is deactivated (RFC3339Nano or free-form string)")
    run_on: Optional[str] = Field(None, description="Cluster node ID or IP address on which to run the job")
    
    # Key rotation specific parameters
    key_query_json: Optional[str] = Field(None, description="JSON query for determining which keys to rotate")
    key_query_file: Optional[str] = Field(None, description="File containing JSON query for key rotation")
    metadata_json: Optional[str] = Field(None, description="JSON metadata for replaced keys")
    metadata_file: Optional[str] = Field(None, description="File containing JSON metadata for replaced keys")
    deactivate_replaced_key: Optional[int] = Field(None, description="Time in seconds after which replaced key is deactivated")
    replaced_key_state: Optional[str] = Field(None, description="State to set for replaced key (Deactivated or ProtectStop)")
    change_state_after_time: Optional[int] = Field(None, description="Time in seconds after which replaced key changes state")
    offset: Optional[int] = Field(None, description="Offset time in seconds for replacement key activation")
    
    # CCKM synchronization specific parameters
    cloud_name: Optional[str] = Field(None, description="Cloud provider (aws, hsm-luna, dsm, oci, sfdc, gcp, sap, AzureCloud)")
    kms: Optional[str] = Field(None, description="KMS resource IDs/names for AWS synchronization")
    key_vaults: Optional[str] = Field(None, description="Vault IDs/names for Azure synchronization")
    key_rings: Optional[str] = Field(None, description="Key ring IDs/names for Google synchronization")
    oci_vaults: Optional[str] = Field(None, description="OCI vault IDs for synchronization")
    organizations: Optional[str] = Field(None, description="Organization IDs for Salesforce synchronization")
    domains: Optional[str] = Field(None, description="Domain IDs for DSM synchronization")
    partitions: Optional[str] = Field(None, description="Partition IDs for HSM synchronization")
    groups: Optional[str] = Field(None, description="Group IDs for SAP synchronization")
    sync_item: Optional[str] = Field(None, description="Items to synchronize for Azure (key, secret, certificate, all)")
    synchronize_all: Optional[bool] = Field(None, description="Synchronize all keys from all vaults/KMS")
    take_cloud_key_backup: Optional[bool] = Field(None, description="Take cloud key backup during Azure synchronization")
    
    # CCKM add-containers specific parameters
    connection_id: Optional[str] = Field(None, description="Connection ID for CCKM add-containers operation")
    discover_only: Optional[bool] = Field(None, description="Whether to just discover container details or add to CCKM as well")
    enable_success_audit_event: Optional[bool] = Field(None, description="Enable or disable audit recording of successful operations")
    aws_filter: Optional[str] = Field(None, description="Filter to be applied on discovered AWS accounts before adding to CCKM")
    aws_regions: Optional[str] = Field(None, description="AWS regions to be added to CCKM (comma-separated)")
    aws_role: Optional[str] = Field(None, description="AWS role to be assumed")
    aws_role_external_id: Optional[str] = Field(None, description="AWS role external ID")
    
    # Backup specific parameters
    backup_type: Optional[str] = Field(None, description="Type of backup (database, scp)")
    backup_key: Optional[str] = Field(None, description="Backup encryption key ID")
    backup_location: Optional[str] = Field(None, description="Backup storage location")
    
    # User password expiry notification parameters
    notification_days: Optional[int] = Field(None, description="Days before password expiry to send notification")
    email_template: Optional[str] = Field(None, description="Email template for notifications")
    
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to operate in")
    auth_domain: Optional[str] = Field(None, description="Authentication domain")


class SchedulerConfigListParams(BaseModel):
    """Parameters for listing scheduler configurations."""
    limit: Optional[int] = Field(None, description="Maximum number of results to return")
    skip: Optional[int] = Field(None, description="Number of results to skip")
    id: Optional[str] = Field(None, description="ID or name of the resource")
    name: Optional[str] = Field(None, description="Name of the scheduler configuration")
    operation: Optional[str] = Field(None, description="Operation type (key_rotation, database_backup, cckm_key_rotation, cckm_xks_credential_rotation)")
    disabled: Optional[bool] = Field(None, description="Filter by disabled status")
    created_after: Optional[str] = Field(None, description="Filter by creation date (after)")
    created_before: Optional[str] = Field(None, description="Filter by creation date (before)")
    domain: Optional[str] = Field(None, description="Domain to operate in")
    auth_domain: Optional[str] = Field(None, description="Authentication domain")


class SchedulerConfigGetParams(BaseModel):
    """Parameters for getting a scheduler configuration."""
    id: str = Field(..., description="ID of the scheduler configuration to get.")
    # Domain support
    domain: Optional[str] = Field(None, description="The domain where the action/operation will be performed.")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


class SchedulerConfigDeleteParams(BaseModel):
    """Parameters for deleting a scheduler configuration."""
    id: str = Field(..., description="ID of the scheduler configuration to delete.")
    # Domain support
    domain: Optional[str] = Field(None, description="The domain where the action/operation will be performed.")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


class SchedulerConfigModifyParams(BaseModel):
    """Parameters for modifying a scheduler configuration."""
    id: str = Field(..., description="ID of the scheduler configuration")
    job_type: Optional[str] = Field(None, description="Type of scheduler job being modified")
    run_at: Optional[str] = Field(None, description="New cron expression")
    description: Optional[str] = Field(None, description="New description")
    disabled: Optional[bool] = Field(None, description="New disabled status")
    start_date: Optional[str] = Field(None, description="New start date")
    end_date: Optional[str] = Field(None, description="New end date")
    run_on: Optional[str] = Field(None, description="New cluster node")
    
    # Key rotation modification parameters
    key_query_json: Optional[str] = Field(None, description="New JSON query for key rotation")
    metadata_json: Optional[str] = Field(None, description="New JSON metadata")
    deactivate_replaced_key: Optional[int] = Field(None, description="New deactivation time")
    
    # CCKM synchronization modification parameters
    cloud_name: Optional[str] = Field(None, description="New cloud provider")
    kms: Optional[str] = Field(None, description="New KMS resources")
    key_vaults: Optional[str] = Field(None, description="New Azure key vaults")
    key_rings: Optional[str] = Field(None, description="New GCP key rings")
    oci_vaults: Optional[str] = Field(None, description="New OCI vaults")
    organizations: Optional[str] = Field(None, description="New Salesforce organizations")
    domains: Optional[str] = Field(None, description="New DSM domains")
    partitions: Optional[str] = Field(None, description="New HSM partitions")
    groups: Optional[str] = Field(None, description="New SAP groups")
    sync_item: Optional[str] = Field(None, description="New Azure sync items")
    synchronize_all: Optional[bool] = Field(None, description="Synchronize all keys from all vaults/KMS")
    connection_id: Optional[str] = Field(None, description="Connection ID for CCKM add-containers operation")
    discover_only: Optional[bool] = Field(None, description="Whether to just discover container details or add to CCKM as well")
    enable_success_audit_event: Optional[bool] = Field(None, description="Enable or disable audit recording of successful operations")
    aws_filter: Optional[str] = Field(None, description="Filter to be applied on discovered AWS accounts before adding to CCKM")
    aws_regions: Optional[str] = Field(None, description="AWS regions to be added to CCKM (comma-separated)")
    aws_role: Optional[str] = Field(None, description="AWS role to be assumed")
    aws_role_external_id: Optional[str] = Field(None, description="AWS role external ID")
    
    domain: Optional[str] = Field(None, description="Domain to operate in")
    auth_domain: Optional[str] = Field(None, description="Authentication domain")


class SchedulerConfigRunNowParams(BaseModel):
    """Parameters for running a scheduler configuration immediately."""
    id: str = Field(..., description="ID of the scheduler configuration")
    domain: Optional[str] = Field(None, description="Domain to operate in")
    auth_domain: Optional[str] = Field(None, description="Authentication domain")


class SchedulerJobListParams(BaseModel):
    """Parameters for listing scheduler jobs."""
    limit: Optional[int] = Field(None, description="Maximum number of results to return")
    skip: Optional[int] = Field(None, description="Number of results to skip")
    id: Optional[str] = Field(None, description="ID of the job run")
    name: Optional[str] = Field(None, description="Name of the scheduler configuration")
    job_config_id: Optional[str] = Field(None, description="Scheduler job config ID")
    job_status: Optional[str] = Field(None, description="Job status (scheduled, in_progress, completed, failed, aborted)")
    operation: Optional[str] = Field(None, description="Operation type")
    processing_node: Optional[str] = Field(None, description="Cluster node ID where job was run")
    created_after: Optional[str] = Field(None, description="Filter by creation date (after)")
    created_before: Optional[str] = Field(None, description="Filter by creation date (before)")
    domain: Optional[str] = Field(None, description="Domain to operate in")
    auth_domain: Optional[str] = Field(None, description="Authentication domain")


class SchedulerJobGetParams(BaseModel):
    """Parameters for getting a scheduler job."""
    id: str = Field(..., description="ID of the scheduler job to get.")
    # Domain support
    domain: Optional[str] = Field(None, description="The domain where the action/operation will be performed.")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


class SchedulerJobDeleteParams(BaseModel):
    """Parameters for deleting a scheduler job."""
    id: str = Field(..., description="ID of the job run")
    domain: Optional[str] = Field(None, description="Domain to operate in")
    auth_domain: Optional[str] = Field(None, description="Authentication domain")


class SchedulerManagementTool(BaseTool):
    """Scheduler Management Tool for CipherTrust Manager."""
    
    @property
    def name(self) -> str:
        return "scheduler_management"
    
    @property
    def description(self) -> str:
        return (
            "Comprehensive scheduler management for CipherTrust Manager. "
            "Supports creating, listing, getting, deleting, and modifying scheduler configurations, "
            "as well as managing scheduler job runs. "
            "Scheduler configurations can run various operations including: "
            "key rotation, CCKM synchronization (AWS, Azure, Google, OCI, Salesforce, SAP, HSM, DSM), "
            "database backup, SCP backup, AWS XKS credential rotation, CRL synchronization, "
            "user password expiry notifications, CCKM container addition, and CCKM key backup. "
            "Supports cron expressions for flexible scheduling (e.g., '0 9 * * *' for daily at 9 AM, "
            "'0 9 * * 1' for Mondays at 9 AM). "
            "Jobs can be configured with start/end dates, run on specific cluster nodes, "
            "and include operation-specific parameters like key queries, cloud resources, and backup settings. "
            "REQUIRED PARAMETERS: job_type, name, run_at. For cckm-synchronization: cloud_name. "
            "For cckm-add-containers: cloud_name, connection_id. For backup: backup_type."
        )
    
    def get_schema(self) -> dict[str, Any]:
        """Get the JSON schema for scheduler management parameters."""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "configs_create", "configs_list", "configs_get", "configs_delete", 
                        "configs_modify", "configs_run_now", 
                        "jobs_list", "jobs_get", "jobs_delete"
                    ],
                    "description": "The scheduler management action to perform"
                },
                **self.get_domain_auth_params(),
                
                # Scheduler config create parameters
                "job_type": {"type": "string", "description": "Type of scheduler job. REQUIRED. Valid values: key-rotation, cckm-synchronization, backup, cckm-key-rotation, cckm-xks-credential-rotation, sync-crl, user-password-expiry-notification, cckm-add-containers, cckm-key-backup"},
                "name": {"type": "string", "description": "Name of the scheduler configuration. REQUIRED"},
                "run_at": {"type": "string", "description": "Cron expression (e.g., '0 9 * * *'). REQUIRED. Format: minute hour day month weekday"},
                "description": {"type": "string", "description": "Description of the scheduler configuration"},
                "disabled": {"type": "boolean", "description": "Whether to disable the job on creation"},
                "start_date": {"type": "string", "description": "Start date/time for activation"},
                "end_date": {"type": "string", "description": "End date/time for deactivation"},
                "run_on": {"type": "string", "description": "Cluster node ID or IP address"},
                
                # Key rotation parameters
                "key_query_json": {"type": "string", "description": "JSON query for key selection"},
                "key_query_file": {"type": "string", "description": "File with JSON query"},
                "metadata_json": {"type": "string", "description": "JSON metadata for replaced keys"},
                "metadata_file": {"type": "string", "description": "File with JSON metadata"},
                "deactivate_replaced_key": {"type": "integer", "description": "Deactivation time in seconds"},
                "replaced_key_state": {"type": "string", "description": "State for replaced key"},
                "change_state_after_time": {"type": "integer", "description": "State change time in seconds"},
                "offset": {"type": "integer", "description": "Offset time for replacement key"},
                
                # CCKM synchronization parameters
                "cloud_name": {"type": "string", "description": "Cloud provider. REQUIRED for cckm-synchronization and cckm-add-containers. Valid values: aws, hsm-luna, dsm, oci, sfdc, gcp, sap, AzureCloud"},
                "kms": {"type": "string", "description": "KMS resource IDs/names"},
                "key_vaults": {"type": "string", "description": "Azure vault IDs/names"},
                "key_rings": {"type": "string", "description": "Google key ring IDs/names"},
                "oci_vaults": {"type": "string", "description": "OCI vault IDs"},
                "organizations": {"type": "string", "description": "Salesforce organization IDs"},
                "domains": {"type": "string", "description": "DSM domain IDs"},
                "partitions": {"type": "string", "description": "HSM partition IDs"},
                "groups": {"type": "string", "description": "SAP group IDs"},
                "sync_item": {"type": "string", "description": "Azure sync items"},
                "synchronize_all": {"type": "boolean", "description": "Synchronize all keys"},
                "take_cloud_key_backup": {"type": "boolean", "description": "Take cloud key backup"},
                "connection_id": {"type": "string", "description": "Connection ID for CCKM add-containers operation. REQUIRED for cckm-add-containers"},
                "discover_only": {"type": "boolean", "description": "Whether to just discover container details or add to CCKM as well"},
                "enable_success_audit_event": {"type": "boolean", "description": "Enable or disable audit recording of successful operations"},
                "aws_filter": {"type": "string", "description": "Filter to be applied on discovered AWS accounts before adding to CCKM"},
                "aws_regions": {"type": "string", "description": "AWS regions to be added to CCKM (comma-separated)"},
                "aws_role": {"type": "string", "description": "AWS role to be assumed"},
                "aws_role_external_id": {"type": "string", "description": "AWS role external ID"},
                
                # Backup parameters
                "backup_type": {"type": "string", "description": "Backup type. REQUIRED for backup job type. Valid values: database, scp"},
                "backup_key": {"type": "string", "description": "Backup encryption key"},
                "backup_location": {"type": "string", "description": "Backup location"},
                
                # Notification parameters
                "notification_days": {"type": "integer", "description": "Days before expiry"},
                "email_template": {"type": "string", "description": "Email template"},
                
                # List/filter parameters
                "limit": {"type": "integer", "description": "Maximum results to return"},
                "skip": {"type": "integer", "description": "Results to skip"},
                "id": {"type": "string", "description": "Resource ID"},
                "operation": {"type": "string", "description": "Operation type filter"},
                "job_config_id": {"type": "string", "description": "Job config ID"},
                "job_status": {"type": "string", "description": "Job status filter"},
                "processing_node": {"type": "string", "description": "Processing node filter"},
                "created_after": {"type": "string", "description": "Created after timestamp"},
                "created_before": {"type": "string", "description": "Created before timestamp"}
            },
            "required": ["action"],
            "additionalProperties": False
        }
    
    async def execute(self, action: str, **kwargs: Any) -> Any:
        """Execute scheduler management operation."""
        try:
            if action == "configs_create":
                return await self._create_config(SchedulerConfigCreateParams(**kwargs))
            elif action == "configs_list":
                return await self._list_configs(SchedulerConfigListParams(**kwargs))
            elif action == "configs_get":
                return await self._get_config(SchedulerConfigGetParams(**kwargs))
            elif action == "configs_delete":
                return await self._delete_config(SchedulerConfigDeleteParams(**kwargs))
            elif action == "configs_modify":
                return await self._modify_config(SchedulerConfigModifyParams(**kwargs))
            elif action == "configs_run_now":
                return await self._run_config_now(SchedulerConfigRunNowParams(**kwargs))
            elif action == "jobs_list":
                return await self._list_jobs(SchedulerJobListParams(**kwargs))
            elif action == "jobs_get":
                return await self._get_job(SchedulerJobGetParams(**kwargs))
            elif action == "jobs_delete":
                return await self._delete_job(SchedulerJobDeleteParams(**kwargs))
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            return {"error": f"Failed to execute {action}: {str(e)}"}
    
    async def _create_config(self, params: SchedulerConfigCreateParams) -> Any:
        """Create a scheduler configuration."""
        # Validate parameters before creating the command
        try:
            validate_cron_expression(params.run_at)
            validate_scheduler_params(params.dict(), params.job_type)
        except ValueError as e:
            return {"error": f"Scheduler validation failed: {str(e)}"}
        
        cmd = ["scheduler", "configs", "create", params.job_type]
        
        # Required parameters
        cmd.extend(["--name", params.name])
        cmd.extend(["--run-at", params.run_at])
        
        # Common optional parameters
        if params.description:
            cmd.extend(["--description", params.description])
        if params.disabled is not None:
            if params.disabled:
                cmd.append("--disabled")
            else:
                cmd.append("--disabled=false")
        if params.start_date:
            cmd.extend(["--start-date", params.start_date])
        if params.end_date:
            cmd.extend(["--end-date", params.end_date])
        if params.run_on:
            cmd.extend(["--run-on", params.run_on])
        
        # Job type specific parameters
        if params.job_type == "key-rotation":
            if params.key_query_json:
                cmd.extend(["--key-query-json", params.key_query_json])
            if params.key_query_file:
                cmd.extend(["--key-query-file", params.key_query_file])
            if params.metadata_json:
                cmd.extend(["--metadata-json", params.metadata_json])
            if params.metadata_file:
                cmd.extend(["--metadata-file", params.metadata_file])
            if params.deactivate_replaced_key is not None:
                cmd.extend(["--deactivate-replaced-key", str(params.deactivate_replaced_key)])
            if params.replaced_key_state:
                cmd.extend(["--replaced-key-state", params.replaced_key_state])
            if params.change_state_after_time is not None:
                cmd.extend(["--change-state-after-time", str(params.change_state_after_time)])
            if params.offset is not None:
                cmd.extend(["--offset", str(params.offset)])
        
        elif params.job_type == "cckm-synchronization":
            if params.cloud_name:
                cmd.extend(["--cloud_name", params.cloud_name])
            if params.kms:
                cmd.extend(["--kms", params.kms])
            if params.key_vaults:
                cmd.extend(["--key_vaults", params.key_vaults])
            if params.key_rings:
                cmd.extend(["--key_rings", params.key_rings])
            if params.oci_vaults:
                cmd.extend(["--oci_vaults", params.oci_vaults])
            if params.organizations:
                cmd.extend(["--organizations", params.organizations])
            if params.domains:
                cmd.extend(["--domains", params.domains])
            if params.partitions:
                cmd.extend(["--partitions", params.partitions])
            if params.groups:
                cmd.extend(["--groups", params.groups])
            if params.sync_item:
                cmd.extend(["--sync_item", params.sync_item])
            if params.synchronize_all is not None:
                cmd.append("--synchronize_all" if params.synchronize_all else "--synchronize_all=false")
            if params.take_cloud_key_backup is not None:
                cmd.append("--take-cloud-key-backup" if params.take_cloud_key_backup else "--take-cloud-key-backup=false")
        
        elif params.job_type == "cckm-add-containers":
            if params.cloud_name:
                cmd.extend(["--cloud_name", params.cloud_name])
            if params.connection_id:
                cmd.extend(["--conn", params.connection_id])
            if params.discover_only is not None:
                cmd.append("--discover-only" if params.discover_only else "--discover-only=false")
            if params.enable_success_audit_event is not None:
                cmd.append("--enable-success-audit-event" if params.enable_success_audit_event else "--enable-success-audit-event=false")
            if params.aws_filter:
                cmd.extend(["--aws-filter", params.aws_filter])
            if params.aws_regions:
                cmd.extend(["--aws-regions", params.aws_regions])
            if params.aws_role:
                cmd.extend(["--aws-role", params.aws_role])
            if params.aws_role_external_id:
                cmd.extend(["--aws-role-external-id", params.aws_role_external_id])
        
        elif params.job_type == "backup":
            if params.backup_type:
                cmd.extend(["--backup-type", params.backup_type])
            if params.backup_key:
                cmd.extend(["--backup-key", params.backup_key])
            if params.backup_location:
                cmd.extend(["--backup-location", params.backup_location])
        
        elif params.job_type == "user-password-expiry-notification":
            if params.notification_days is not None:
                cmd.extend(["--notification-days", str(params.notification_days)])
            if params.email_template:
                cmd.extend(["--email-template", params.email_template])
        
        result = self.execute_with_domain(cmd, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))
    
    async def _list_configs(self, params: SchedulerConfigListParams) -> Any:
        """List scheduler configurations."""
        cmd = ["scheduler", "configs", "list"]
        
        if params.limit is not None:
            cmd.extend(["--limit", str(params.limit)])
        if params.skip is not None:
            cmd.extend(["--skip", str(params.skip)])
        if params.id:
            cmd.extend(["--id", params.id])
        if params.name:
            cmd.extend(["--name", params.name])
        if params.operation:
            cmd.extend(["--operation", params.operation])
        if params.disabled is not None:
            cmd.append("--disabled" if params.disabled else "--disabled=false")
        if params.created_after:
            cmd.extend(["--created-after", params.created_after])
        if params.created_before:
            cmd.extend(["--created-before", params.created_before])
        
        result = self.execute_with_domain(cmd, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))
    
    async def _get_config(self, params: SchedulerConfigGetParams) -> Any:
        """Get a scheduler configuration."""
        cmd = ["scheduler", "configs", "get", "--id", params.id]
        
        result = self.execute_with_domain(cmd, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))
    
    async def _delete_config(self, params: SchedulerConfigDeleteParams) -> Any:
        """Delete a scheduler configuration."""
        cmd = ["scheduler", "configs", "delete", "--id", params.id]
        
        result = self.execute_with_domain(cmd, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))
    
    async def _modify_config(self, params: SchedulerConfigModifyParams) -> Any:
        """Modify a scheduler configuration."""
        # Get job_type if not provided
        job_type = params.job_type
        if not job_type:
            # Get current config to extract job_type
            get_params = SchedulerConfigGetParams(id=params.id, domain=params.domain, auth_domain=params.auth_domain)
            current_config = await self._get_config(get_params)
            if isinstance(current_config, dict):
                job_type = current_config.get("operation", "").replace("_", "-")
            if not job_type:
                raise ValueError("Could not determine job type for scheduler configuration")
        
        cmd = ["scheduler", "configs", "modify", job_type, "--id", params.id]
        
        # Common modifiable parameters
        if params.run_at:
            cmd.extend(["--run-at", params.run_at])
        if params.description:
            cmd.extend(["--description", params.description])
        if params.disabled is not None:
            cmd.append("--disabled" if params.disabled else "--disabled=false")
        if params.start_date:
            cmd.extend(["--start-date", params.start_date])
        if params.end_date:
            cmd.extend(["--end-date", params.end_date])
        if params.run_on:
            cmd.extend(["--run-on", params.run_on])
        
        # Job type specific parameters
        if job_type == "key-rotation":
            if params.key_query_json:
                cmd.extend(["--key-query-json", params.key_query_json])
            if params.metadata_json:
                cmd.extend(["--metadata-json", params.metadata_json])
            if params.deactivate_replaced_key is not None:
                cmd.extend(["--deactivate-replaced-key", str(params.deactivate_replaced_key)])
        
        elif job_type == "cckm-synchronization":
            # Note: Based on help output, --cloud_name is NOT available in modify, only in create
            if params.kms:
                cmd.extend(["--kms", params.kms])
            if params.key_vaults:
                cmd.extend(["--key_vaults", params.key_vaults])
            if params.key_rings:
                cmd.extend(["--key_rings", params.key_rings])
            if params.oci_vaults:
                cmd.extend(["--oci_vaults", params.oci_vaults])
            if params.organizations:
                cmd.extend(["--organizations", params.organizations])
            if params.domains:
                cmd.extend(["--domains", params.domains])
            if params.partitions:
                cmd.extend(["--partitions", params.partitions])
            if params.groups:
                cmd.extend(["--groups", params.groups])
            if params.sync_item:
                cmd.extend(["--sync_item", params.sync_item])
            if params.synchronize_all is not None:
                cmd.append("--synchronize_all" if params.synchronize_all else "--synchronize_all=false")
        
        elif job_type == "cckm-add-containers":
            if params.connection_id:
                cmd.extend(["--conn", params.connection_id])
            if params.discover_only is not None:
                cmd.append("--discover-only" if params.discover_only else "--discover-only=false")
            if params.enable_success_audit_event is not None:
                cmd.append("--enable-success-audit-event" if params.enable_success_audit_event else "--enable-success-audit-event=false")
            if params.aws_filter:
                cmd.extend(["--aws-filter", params.aws_filter])
            if params.aws_regions:
                cmd.extend(["--aws-regions", params.aws_regions])
            if params.aws_role:
                cmd.extend(["--aws-role", params.aws_role])
            if params.aws_role_external_id:
                cmd.extend(["--aws-role-external-id", params.aws_role_external_id])
        
        result = self.execute_with_domain(cmd, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))
    
    async def _run_config_now(self, params: SchedulerConfigRunNowParams) -> Any:
        """Run a scheduler configuration immediately."""
        cmd = ["scheduler", "configs", "run-now", "--id", params.id]
        
        result = self.execute_with_domain(cmd, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))
    
    async def _list_jobs(self, params: SchedulerJobListParams) -> Any:
        """List scheduler jobs."""
        cmd = ["scheduler", "jobs", "list"]
        
        if params.limit is not None:
            cmd.extend(["--limit", str(params.limit)])
        if params.skip is not None:
            cmd.extend(["--skip", str(params.skip)])
        if params.id:
            cmd.extend(["--id", params.id])
        if params.name:
            cmd.extend(["--name", params.name])
        if params.job_config_id:
            cmd.extend(["--job-config-id", params.job_config_id])
        if params.job_status:
            cmd.extend(["--job-status", params.job_status])
        if params.operation:
            cmd.extend(["--operation", params.operation])
        if params.processing_node:
            cmd.extend(["--processing-node", params.processing_node])
        if params.created_after:
            cmd.extend(["--created-after", params.created_after])
        if params.created_before:
            cmd.extend(["--created-before", params.created_before])
        
        result = self.execute_with_domain(cmd, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))
    
    async def _get_job(self, params: SchedulerJobGetParams) -> Any:
        """Get a scheduler job."""
        cmd = ["scheduler", "jobs", "get", "--id", params.id]
        
        result = self.execute_with_domain(cmd, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))
    
    async def _delete_job(self, params: SchedulerJobDeleteParams) -> Any:
        """Delete a scheduler job."""
        cmd = ["scheduler", "jobs", "delete", "--id", params.id]
        
        result = self.execute_with_domain(cmd, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


# Export tools
SCHEDULER_TOOLS = [SchedulerManagementTool] 