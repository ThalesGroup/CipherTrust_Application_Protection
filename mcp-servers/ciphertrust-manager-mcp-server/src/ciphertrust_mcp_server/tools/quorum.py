"""Quorum management tools for CipherTrust Manager with built-in domain support.

This module provides tools for managing quorums, quorum policies, and quorum profiles in CipherTrust Manager.
It supports operations like activating, approving, denying, and revoking quorums, as well as managing quorum
policies and profiles. All operations support domain-specific execution.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


# Quorum Management Parameter Models
class QuorumListParams(BaseModel):
    """Parameters for listing quorums.
    
    Supports filtering by operation, requester ID, state, and URI. Includes pagination
    controls and sorting options. All operations support domain-specific execution.
    """
    limit: int = Field(10, description="Maximum number of quorum structures to return")
    skip: int = Field(0, description="Offset at which to start the search")
    sort: Optional[str] = Field(None, description="Sort by name, createdAt, or updatedAt (prefix with '-' for descending)")
    operation: Optional[str] = Field(None, description="Filter by quorum operation")
    req_id: Optional[str] = Field(None, description="Filter by requester ID (owner of the quorum)")
    state: Optional[str] = Field(None, description="Filter by quorum state")
    uri: Optional[str] = Field(None, description="Filter by resource URI")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to list quorums from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


class QuorumGetParams(BaseModel):
    """Parameters for getting a quorum.
    
    Retrieves detailed information about a specific quorum by its ID.
    Supports domain-specific execution.
    """
    id: str = Field(..., description="Quorum ID")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to get quorum from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


class QuorumActivateParams(BaseModel):
    """Parameters for activating a quorum.
    
    Activates a quorum with an optional reason. Supports domain-specific execution.
    """
    id: str = Field(..., description="Quorum ID")
    quorum_reason: Optional[str] = Field(None, description="Reason to activate the quorum")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to activate quorum in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


class QuorumApproveParams(BaseModel):
    """Parameters for approving a quorum.
    
    Approves a quorum with an optional note. Supports domain-specific execution.
    """
    id: str = Field(..., description="Quorum ID")
    note: Optional[str] = Field(None, description="Additional note for approval")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to approve quorum in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


class QuorumDenyParams(BaseModel):
    """Parameters for denying a quorum.
    
    Denies a quorum with an optional note. Supports domain-specific execution.
    """
    id: str = Field(..., description="Quorum ID")
    note: Optional[str] = Field(None, description="Additional note for denial")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to deny quorum in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


class QuorumRevokeParams(BaseModel):
    """Parameters for revoking a quorum vote.
    
    Revokes a previously cast vote on a quorum. Supports domain-specific execution.
    """
    id: str = Field(..., description="Quorum ID")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to revoke quorum vote in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


class QuorumDeleteParams(BaseModel):
    """Parameters for deleting a quorum.
    
    Deletes a quorum by its ID. Supports domain-specific execution.
    """
    id: str = Field(..., description="Quorum ID")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to delete quorum from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


class QuorumGetResourcesListParams(BaseModel):
    """Parameters for getting quorum resources list.
    
    Retrieves a list of resource URIs associated with a quorum. Supports domain-specific execution.
    """
    id: str = Field(..., description="Quorum ID")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to get resources from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


# Quorum Policy Parameter Models
class QuorumPolicyActivateParams(BaseModel):
    """Parameters for activating quorum policy.
    
    Activates quorum policy for specified actions. Each action must be activated individually.
    Supports domain-specific execution.
    """
    actions: str = Field(..., description="Comma-separated list of actions/operations to enable quorum for")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to activate policy in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


class QuorumPolicyDeactivateParams(BaseModel):
    """Parameters for deactivating quorum policy.
    
    Deactivates quorum policy for specified actions. Supports domain-specific execution.
    """
    actions: str = Field(..., description="Comma-separated list of actions/operations to disable quorum for")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to deactivate policy in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


class QuorumPolicyStatusParams(BaseModel):
    """Parameters for getting quorum policy status.
    
    Retrieves the status of quorum policies with filtering and pagination options.
    Supports domain-specific execution.
    """
    limit: int = Field(10, description="Maximum number of policies to return")
    skip: int = Field(0, description="Offset at which to start the search")
    sort: Optional[str] = Field(None, description="Sort by name, createdAt, or updatedAt (prefix with '-' for descending)")
    operation: Optional[str] = Field(None, description="Filter by quorum operation")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to get policy status from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


# Quorum Profiles Parameter Models
class QuorumProfilesListParams(BaseModel):
    """Parameters for listing quorum profiles.
    
    Lists quorum profiles with filtering and pagination options. Supports domain-specific execution.
    """
    limit: int = Field(10, description="Maximum number of profiles to return")
    skip: int = Field(0, description="Offset at which to start the search")
    sort: Optional[str] = Field(None, description="Sort by name, createdAt, or updatedAt (prefix with '-' for descending)")
    profile_name: Optional[str] = Field(None, description="Filter by quorum profile name")
    category: Optional[str] = Field(None, description="Filter by quorum profile category")
    label: Optional[str] = Field(None, description="Filter by quorum profile label")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to list profiles from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


class QuorumProfilesGetParams(BaseModel):
    """Parameters for getting a quorum profile.
    
    Retrieves details of a specific quorum profile by its ID. Supports domain-specific execution.
    """
    profile_id: str = Field(..., description="Quorum Profile ID")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to get profile from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


class QuorumProfilesUpdateParams(BaseModel):
    """Parameters for updating a quorum profile.
    
    Updates settings of a quorum profile including approvals needed and voter groups.
    Supports domain-specific execution.
    """
    profile_id: str = Field(..., description="Quorum Profile ID")
    approvals: Optional[int] = Field(None, description="Number of approvals needed for quorum")
    voter_groups: Optional[str] = Field(None, description="Comma-separated list of voter groups allowed to approve")
    excluded_groups: Optional[str] = Field(None, description="Comma-separated list of groups excluded from quorum")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to update profile in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="The domain where the user is created. Defaults to 'root' if not specified.")


# Quorum Management Tools
class QuorumManagementTool(BaseTool):
    """Manage quorums, quorum policies, and quorum profiles in CipherTrust Manager.
    
    This tool provides comprehensive quorum management capabilities including:
    - Basic quorum operations (list, get, activate, approve, deny, revoke, delete)
    - Resource management (get resources list)
    - Policy management (activate, deactivate, status)
    - Profile management (list, get, update)
    
    All operations support domain-specific execution and include proper error handling
    and response formatting.
    """

    @property
    def name(self) -> str:
        return "quorum_management"

    @property
    def description(self) -> str:
        return "Quorum management operations (list, get, activate, approve, deny, revoke, delete, get_resources_list, policy_activate, policy_deactivate, policy_status, profiles_list, profiles_get, profiles_update)"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": [
                    "list", "get", "activate", "approve", "deny", "revoke", "delete", "get_resources_list",
                    "policy_activate", "policy_deactivate", "policy_status",
                    "profiles_list", "profiles_get", "profiles_update"
                ]},
                **QuorumListParams.model_json_schema()["properties"],
                **QuorumGetParams.model_json_schema()["properties"],
                **QuorumActivateParams.model_json_schema()["properties"],
                **QuorumApproveParams.model_json_schema()["properties"],
                **QuorumDenyParams.model_json_schema()["properties"],
                **QuorumRevokeParams.model_json_schema()["properties"],
                **QuorumDeleteParams.model_json_schema()["properties"],
                **QuorumGetResourcesListParams.model_json_schema()["properties"],
                **QuorumPolicyActivateParams.model_json_schema()["properties"],
                **QuorumPolicyDeactivateParams.model_json_schema()["properties"],
                **QuorumPolicyStatusParams.model_json_schema()["properties"],
                **QuorumProfilesListParams.model_json_schema()["properties"],
                **QuorumProfilesGetParams.model_json_schema()["properties"],
                **QuorumProfilesUpdateParams.model_json_schema()["properties"],
            },
            "required": ["action"],
        }

    async def execute(self, action: str, **kwargs: Any) -> Any:
        if action == "list":
            params = QuorumListParams(**kwargs)
            args = ["quorum", "list", "--limit", str(params.limit), "--skip", str(params.skip)]
            if params.sort:
                args.extend(["--sort", params.sort])
            if params.operation:
                args.extend(["--operation", params.operation])
            if params.req_id:
                args.extend(["--req-id", params.req_id])
            if params.state:
                args.extend(["--state", params.state])
            if params.uri:
                args.extend(["--uri", params.uri])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "get":
            params = QuorumGetParams(**kwargs)
            args = ["quorum", "get", "--id", params.id]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "activate":
            params = QuorumActivateParams(**kwargs)
            args = ["quorum", "activate", "--id", params.id]
            if params.quorum_reason:
                args.extend(["--quorum-reason", params.quorum_reason])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "approve":
            params = QuorumApproveParams(**kwargs)
            args = ["quorum", "approve", "--id", params.id]
            if params.note:
                args.extend(["--note", params.note])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "deny":
            params = QuorumDenyParams(**kwargs)
            args = ["quorum", "deny", "--id", params.id]
            if params.note:
                args.extend(["--note", params.note])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "revoke":
            params = QuorumRevokeParams(**kwargs)
            args = ["quorum", "revoke", "--id", params.id]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "delete":
            params = QuorumDeleteParams(**kwargs)
            args = ["quorum", "delete", "--id", params.id]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "get_resources_list":
            params = QuorumGetResourcesListParams(**kwargs)
            args = ["quorum", "get-resources-list", "--id", params.id]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "policy_activate":
            params = QuorumPolicyActivateParams(**kwargs)
            args = ["quorum-policy", "activate", "--actions", params.actions]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "policy_deactivate":
            params = QuorumPolicyDeactivateParams(**kwargs)
            args = ["quorum-policy", "deactivate", "--actions", params.actions]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "policy_status":
            params = QuorumPolicyStatusParams(**kwargs)
            args = ["quorum-policy", "status", "--limit", str(params.limit), "--skip", str(params.skip)]
            if params.sort:
                args.extend(["--sort", params.sort])
            if params.operation:
                args.extend(["--operation", params.operation])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "profiles_list":
            params = QuorumProfilesListParams(**kwargs)
            args = ["quorum-profiles", "list", "--limit", str(params.limit), "--skip", str(params.skip)]
            if params.sort:
                args.extend(["--sort", params.sort])
            if params.profile_name:
                args.extend(["--profile-name", params.profile_name])
            if params.category:
                args.extend(["--category", params.category])
            if params.label:
                args.extend(["--label", params.label])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "profiles_get":
            params = QuorumProfilesGetParams(**kwargs)
            args = ["quorum-profiles", "get", "--profile-id", params.profile_id]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "profiles_update":
            params = QuorumProfilesUpdateParams(**kwargs)
            args = ["quorum-profiles", "update", "--profile-id", params.profile_id]
            if params.approvals is not None:
                args.extend(["--approvals", str(params.approvals)])
            if params.voter_groups:
                args.extend(["--voter-groups", params.voter_groups])
            if params.excluded_groups:
                args.extend(["--excluded-groups", params.excluded_groups])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")

QUORUM_TOOLS = [QuorumManagementTool]
