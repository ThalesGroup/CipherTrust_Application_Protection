"""Resource set operations for CTE management."""

from typing import Any
from .base import CTESubTool

class ResourceSetOperations(CTESubTool):
    """Handles all resource set operations for CTE management."""
    
    def get_operations(self) -> list[str]:
        """Return list of all resource set operations."""
        return [
            "resource_set_create", "resource_set_list", "resource_set_get", "resource_set_delete", "resource_set_modify",
            "resource_set_add_resources", "resource_set_delete_resource", "resource_set_update_resource",
            "resource_set_list_resources", "resource_set_list_policies"
        ]
    
    def get_schema_properties(self) -> dict[str, Any]:
        """Return schema properties specific to resource set operations."""
        return {
            "resource_set_identifier": {
                "type": "string",
                "description": "Resource set identifier (name, ID, or URI)"
            },
            "resource_set_name": {
                "type": "string",
                "description": "Resource set name for filtering"
            },
            "resource_json": {
                "type": "string", 
                "description": "Resource set configuration in JSON format"
            },
            "resource_json_file": {
                "type": "string",
                "description": "Path to JSON file containing resource set configuration"
            },
            "resource_index": {
                "type": "string",
                "description": "Index of resource in resource set"
            },
            "resource_index_list": {
                "type": "string",
                "description": "Comma-separated list of resource indices"
            }
        }
    
    def get_action_requirements(self) -> dict[str, Any]:
        """Return action requirements for resource set operations."""
        return {
            "resource_set_create": {
                "required": [],
                "optional": ["resource_json", "resource_json_file", "domain", "auth_domain"],
                "example": {
                    "action": "resource_set_create",
                    "resource_json": "{\"name\": \"RSet01\", \"description\": \"Sensitive data directories\", \"resources\": [{\"directory\": \"/data/sensitive\", \"file\": \"*\", \"include_subfolders\": true, \"hdfs\": false}]}"
                },
                "json_structure": {
                    "name": "string",
                    "description": "string",
                    "resources": [
                        {
                            "directory": "string",
                            "file": "string (filename or * for all)",
                            "include_subfolders": "boolean",
                            "hdfs": "boolean"
                        }
                    ]
                }
            },
            "resource_set_list": {
                "required": [],
                "optional": ["limit", "skip", "resource_set_name", "domain", "auth_domain"],
                "example": {
                    "action": "resource_set_list",
                    "limit": 20
                }
            },
            "resource_set_get": {
                "required": ["resource_set_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "resource_set_get",
                    "resource_set_identifier": "RSet01"
                }
            },
            "resource_set_delete": {
                "required": ["resource_set_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "resource_set_delete",
                    "resource_set_identifier": "RSet01"
                }
            },
            "resource_set_modify": {
                "required": ["resource_set_identifier"],
                "optional": ["resource_json", "resource_json_file", "domain", "auth_domain"],
                "example": {
                    "action": "resource_set_modify",
                    "resource_set_identifier": "RSet01",
                    "resource_json": "{\"description\": \"Updated resource set description\"}"
                }
            },
            "resource_set_add_resources": {
                "required": ["resource_set_identifier", "resource_json_file"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "resource_set_add_resources",
                    "resource_set_identifier": "RSet01",
                    "resource_json_file": "/path/to/resources.json"
                }
            },
            "resource_set_delete_resource": {
                "required": ["resource_set_identifier", "resource_index_list"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "resource_set_delete_resource",
                    "resource_set_identifier": "RSet01",
                    "resource_index_list": "0,1,2"
                }
            },
            "resource_set_update_resource": {
                "required": ["resource_set_identifier", "resource_index", "resource_json_file"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "resource_set_update_resource",
                    "resource_set_identifier": "RSet01",
                    "resource_index": "0",
                    "resource_json_file": "/path/to/updated_resource.json"
                }
            },
            "resource_set_list_resources": {
                "required": ["resource_set_identifier"],
                "optional": ["limit", "skip", "search", "domain", "auth_domain"],
                "example": {
                    "action": "resource_set_list_resources",
                    "resource_set_identifier": "RSet01"
                }
            },
            "resource_set_list_policies": {
                "required": ["resource_set_identifier"],
                "optional": ["limit", "skip", "domain", "auth_domain"],
                "example": {
                    "action": "resource_set_list_policies",
                    "resource_set_identifier": "RSet01"
                }
            }
        }
    
    async def execute_operation(self, action: str, **kwargs: Any) -> Any:
        """Execute the specified resource set operation."""
        method_name = f"_{action}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(**kwargs)
        else:
            return {"error": f"Unknown resource set action: {action}"}
    
    def _resource_set_create(self, **kwargs):
        """Create a CTE resource set."""
        args = ["cte", "resource-sets", "create"]
        
        if kwargs.get("resource_json"):
            args.extend(["--resource-json", kwargs["resource_json"]])
        elif kwargs.get("resource_json_file"):
            args.extend(["--resource-json-file", kwargs["resource_json_file"]])
        else:
            return {"error": "Either resource_json or resource_json_file must be specified"}
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _resource_set_list(self, **kwargs):
        """List CTE resource sets."""
        args = ["cte", "resource-sets", "list"]
        args.extend(["--limit", str(kwargs.get("limit", 10))])
        args.extend(["--skip", str(kwargs.get("skip", 0))])
        
        if kwargs.get("resource_set_name"):
            args.extend(["--resource-set-name", kwargs["resource_set_name"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _resource_set_get(self, **kwargs):
        """Get a CTE resource set."""
        args = ["cte", "resource-sets", "get"]
        args.extend(["--resource-set-identifier", kwargs["resource_set_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _resource_set_delete(self, **kwargs):
        """Delete a CTE resource set."""
        args = ["cte", "resource-sets", "delete"]
        args.extend(["--resource-set-identifier", kwargs["resource_set_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _resource_set_modify(self, **kwargs):
        """Modify a CTE resource set."""
        args = ["cte", "resource-sets", "modify"]
        args.extend(["--resource-set-identifier", kwargs["resource_set_identifier"]])
        
        if kwargs.get("resource_json"):
            args.extend(["--resource-json", kwargs["resource_json"]])
        elif kwargs.get("resource_json_file"):
            args.extend(["--resource-json-file", kwargs["resource_json_file"]])
        else:
            return {"error": "Either resource_json or resource_json_file must be specified"}
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _resource_set_add_resources(self, **kwargs):
        """Add resources to a CTE resource set."""
        args = ["cte", "resource-sets", "add-resources"]
        args.extend(["--resource-set-identifier", kwargs["resource_set_identifier"]])
        args.extend(["--resource-json-file", kwargs["resource_json_file"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _resource_set_delete_resource(self, **kwargs):
        """Delete a resource from a CTE resource set."""
        args = ["cte", "resource-sets", "delete-resource"]
        args.extend(["--resource-set-identifier", kwargs["resource_set_identifier"]])
        args.extend(["--resource-index-list", kwargs["resource_index_list"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _resource_set_update_resource(self, **kwargs):
        """Update a resource in a CTE resource set."""
        args = ["cte", "resource-sets", "update-resource"]
        args.extend(["--resource-set-identifier", kwargs["resource_set_identifier"]])
        args.extend(["--resource-index", kwargs["resource_index"]])
        args.extend(["--resource-json-file", kwargs["resource_json_file"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _resource_set_list_resources(self, **kwargs):
        """List resources in a CTE resource set."""
        args = ["cte", "resource-sets", "list-resources"]
        args.extend(["--resource-set-identifier", kwargs["resource_set_identifier"]])
        args.extend(["--limit", str(kwargs.get("limit", 10))])
        args.extend(["--skip", str(kwargs.get("skip", 0))])
        
        if kwargs.get("search"):
            args.extend(["--search", kwargs["search"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _resource_set_list_policies(self, **kwargs):
        """List policies associated with a CTE resource set."""
        args = ["cte", "resource-sets", "list-policies"]
        args.extend(["--resource-set-identifier", kwargs["resource_set_identifier"]])
        args.extend(["--limit", str(kwargs.get("limit", 10))])
        args.extend(["--skip", str(kwargs.get("skip", 0))])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))