"""Client group operations for CTE management."""

from typing import Any
from .base import CTESubTool

class ClientGroupOperations(CTESubTool):
    """Handles all client group operations for CTE management."""
    
    def get_operations(self) -> list[str]:
        """Return list of all client group operations."""
        return [
            "client_group_create", "client_group_list", "client_group_get", 
            "client_group_delete", "client_group_modify"
        ]
    
    def get_schema_properties(self) -> dict[str, Any]:
        """Return schema properties specific to client group operations."""
        return {
            "client_group_name": {
                "type": "string",
                "description": "Name of CTE client group"
            },
            "client_group_identifier": {
                "type": "string",
                "description": "Client group identifier"
            },
            "client_group_description": {
                "type": "string",
                "description": "Description for CTE client group"
            },
            "client_group_password": {
                "type": "string",
                "description": "Password for CTE client group"
            },
            "cluster_type": {
                "type": "string",
                "enum": ["NON-CLUSTER", "HDFS"],
                "default": "NON-CLUSTER",
                "description": "Cluster type"
            }
        }
    
    def get_action_requirements(self) -> dict[str, Any]:
        """Return action requirements for client group operations."""
        return {
            "client_group_create": {
                "required": ["client_group_name"],
                "optional": ["cluster_type", "client_group_description", "client_group_password", 
                            "password_creation_method", "comm_enabled", "cte_profile_identifier", 
                            "domain", "auth_domain"],
                "example": {
                    "action": "client_group_create",
                    "client_group_name": "WebServerGroup",
                    "cluster_type": "NON-CLUSTER",
                    "client_group_description": "Web server client group"
                }
            },
            "client_group_list": {
                "required": [],
                "optional": ["limit", "skip", "client_group_name", "cluster_type", "domain", "auth_domain"],
                "example": {
                    "action": "client_group_list",
                    "limit": 20
                }
            },
            "client_group_get": {
                "required": ["client_group_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "client_group_get",
                    "client_group_identifier": "WebServerGroup"
                }
            },
            "client_group_delete": {
                "required": ["client_group_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "client_group_delete",
                    "client_group_identifier": "WebServerGroup"
                }
            },
            "client_group_modify": {
                "required": ["client_group_identifier"],
                "optional": ["client_group_description", "client_group_password", "password_creation_method", 
                            "comm_enabled", "cte_client_locked", "system_locked", "cte_profile_identifier", 
                            "domain", "auth_domain"],
                "example": {
                    "action": "client_group_modify",
                    "client_group_identifier": "WebServerGroup",
                    "client_group_description": "Updated description"
                }
            }
        }
    
    async def execute_operation(self, action: str, **kwargs: Any) -> Any:
        """Execute the specified client group operation."""
        method_name = f"_{action}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(**kwargs)
        else:
            return {"error": f"Unknown client group action: {action}"}
    
    def _client_group_create(self, **kwargs):
        """Create a CTE client group."""
        args = ["cte", "client-groups", "create"]
        args.extend(["--client-group-name", kwargs["client_group_name"]])
        args.extend(["--cluster-type", kwargs.get("cluster_type", "NON-CLUSTER")])

        if kwargs.get("client_group_description"):
            args.extend(["--client-group-description", kwargs["client_group_description"]])
        if kwargs.get("client_group_password"):
            args.extend(["--client-group-password", kwargs["client_group_password"]])
        if kwargs.get("password_creation_method", "GENERATE") != "GENERATE":
            args.extend(["--password-creation-method", kwargs["password_creation_method"]])
        if kwargs.get("comm_enabled"):
            args.append("--comm-enabled")
        if kwargs.get("cte_profile_identifier"):
            args.extend(["--cte-profile-identifier", kwargs["cte_profile_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _client_group_list(self, **kwargs):
        """List CTE client groups."""
        args = ["cte", "client-groups", "list"]
        args.extend(["--limit", str(kwargs.get("limit", 10))])
        args.extend(["--skip", str(kwargs.get("skip", 0))])
        
        if kwargs.get("client_group_name"):
            args.extend(["--client-group-name", kwargs["client_group_name"]])
        if kwargs.get("cluster_type"):
            args.extend(["--cluster-type", kwargs["cluster_type"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _client_group_get(self, **kwargs):
        """Get a CTE client group."""
        args = ["cte", "client-groups", "get"]
        args.extend(["--client-group-identifier", kwargs["client_group_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _client_group_delete(self, **kwargs):
        """Delete a CTE client group."""
        args = ["cte", "client-groups", "delete"]
        args.extend(["--client-group-identifier", kwargs["client_group_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _client_group_modify(self, **kwargs):
        """Modify a CTE client group."""
        args = ["cte", "client-groups", "modify"]
        args.extend(["--client-group-identifier", kwargs["client_group_identifier"]])
        
        if kwargs.get("client_group_description") is not None:
            args.extend(["--client-group-description", kwargs["client_group_description"]])
        if kwargs.get("client_group_password"):
            args.extend(["--client-group-password", kwargs["client_group_password"]])
        if kwargs.get("password_creation_method"):
            args.extend(["--password-creation-method", kwargs["password_creation_method"]])
        if kwargs.get("comm_enabled") is not None:
            args.append("--comm-enabled" if kwargs["comm_enabled"] else "--no-comm-enabled")
        if kwargs.get("cte_client_locked") is not None:
            args.append("--cte-client-locked" if kwargs["cte_client_locked"] else "--no-cte-client-locked")
        if kwargs.get("system_locked") is not None:
            args.append("--system-locked" if kwargs["system_locked"] else "--no-system-locked")
        if kwargs.get("cte_profile_identifier"):
            args.extend(["--cte-profile-identifier", kwargs["cte_profile_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))