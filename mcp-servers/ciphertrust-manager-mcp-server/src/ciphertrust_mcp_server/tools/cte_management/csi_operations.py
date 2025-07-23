"""CSI operations for CTE management."""

from typing import Any
from .base import CTESubTool

class CSIOperations(CTESubTool):
    """Handles all CSI storage group operations for CTE management."""
    
    def get_operations(self) -> list[str]:
        """Return list of all CSI operations."""
        return [
            "csi_storage_group_create", "csi_storage_group_list", "csi_storage_group_get", 
            "csi_storage_group_delete", "csi_storage_group_modify"
        ]
    
    def get_schema_properties(self) -> dict[str, Any]:
        """Return schema properties specific to CSI operations."""
        return {
            "storage_group_name": {
                "type": "string",
                "description": "Name of CSI storage group"
            },
            "storage_group_identifier": {
                "type": "string",
                "description": "CSI storage group identifier"
            },
            "storage_class_name": {
                "type": "string",
                "description": "Name of storage class"
            },
            "namespace_name": {
                "type": "string",
                "description": "Name of namespace"
            },
            "ctecsi_description": {
                "type": "string",
                "description": "Description for CTE CSI resources"
            },
            "ctecsi_profile": {
                "type": "string",
                "description": "Client profile for CTE CSI resources"
            }
        }
    
    def get_action_requirements(self) -> dict[str, Any]:
        """Return action requirements for CSI operations."""
        return {
            "csi_storage_group_create": {
                "required": ["storage_group_name", "storage_class_name", "namespace_name"],
                "optional": ["ctecsi_description", "ctecsi_profile", "domain", "auth_domain"],
                "example": {
                    "action": "csi_storage_group_create",
                    "storage_group_name": "MyStorageGroup",
                    "storage_class_name": "cte-storage-class",
                    "namespace_name": "default"
                }
            },
            "csi_storage_group_list": {
                "required": [],
                "optional": ["limit", "skip", "storage_group_name", "storage_class_name", 
                            "namespace_name", "sort", "domain", "auth_domain"],
                "example": {
                    "action": "csi_storage_group_list",
                    "limit": 20
                }
            },
            "csi_storage_group_get": {
                "required": ["storage_group_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "csi_storage_group_get",
                    "storage_group_identifier": "MyStorageGroup"
                }
            },
            "csi_storage_group_delete": {
                "required": ["storage_group_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "csi_storage_group_delete",
                    "storage_group_identifier": "MyStorageGroup"
                }
            },
            "csi_storage_group_modify": {
                "required": ["storage_group_identifier"],
                "optional": ["ctecsi_description", "ctecsi_profile", "domain", "auth_domain"],
                "example": {
                    "action": "csi_storage_group_modify",
                    "storage_group_identifier": "MyStorageGroup",
                    "ctecsi_description": "Updated description"
                }
            }
        }
    
    async def execute_operation(self, action: str, **kwargs: Any) -> Any:
        """Execute the specified CSI operation."""
        method_name = f"_{action}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(**kwargs)
        else:
            return {"error": f"Unknown CSI action: {action}"}
    
    def _csi_storage_group_create(self, **kwargs):
        """Create a CSI StorageGroup."""
        args = ["cte", "csi", "k8s-storage-group", "create"]
        args.extend(["--storage-group-name", kwargs["storage_group_name"]])
        args.extend(["--storage-class-name", kwargs["storage_class_name"]])
        args.extend(["--namespace-name", kwargs["namespace_name"]])
        
        if kwargs.get("ctecsi_description"):
            args.extend(["--ctecsi-description", kwargs["ctecsi_description"]])
        if kwargs.get("ctecsi_profile"):
            args.extend(["--ctecsi-profile", kwargs["ctecsi_profile"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _csi_storage_group_list(self, **kwargs):
        """List CSI StorageGroups."""
        args = ["cte", "csi", "k8s-storage-group", "list"]
        args.extend(["--limit", str(kwargs.get("limit", 10))])
        args.extend(["--skip", str(kwargs.get("skip", 0))])
        
        if kwargs.get("storage_group_name"):
            args.extend(["--storage-group-name", kwargs["storage_group_name"]])
        if kwargs.get("storage_class_name"):
            args.extend(["--storage-class-name", kwargs["storage_class_name"]])
        if kwargs.get("namespace_name"):
            args.extend(["--namespace-name", kwargs["namespace_name"]])
        if kwargs.get("sort"):
            args.extend(["--sort", kwargs["sort"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _csi_storage_group_get(self, **kwargs):
        """Get a CSI StorageGroup."""
        args = ["cte", "csi", "k8s-storage-group", "get"]
        args.extend(["--storage-group-identifier", kwargs["storage_group_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _csi_storage_group_delete(self, **kwargs):
        """Delete a CSI StorageGroup."""
        args = ["cte", "csi", "k8s-storage-group", "delete"]
        args.extend(["--storage-group-identifier", kwargs["storage_group_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _csi_storage_group_modify(self, **kwargs):
        """Modify a CSI StorageGroup."""
        args = ["cte", "csi", "k8s-storage-group", "modify"]
        args.extend(["--storage-group-identifier", kwargs["storage_group_identifier"]])
        
        if kwargs.get("ctecsi_description") is not None:
            args.extend(["--ctecsi-description", kwargs["ctecsi_description"]])
        if kwargs.get("ctecsi_profile"):
            args.extend(["--ctecsi-profile", kwargs["ctecsi_profile"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))