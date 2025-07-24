"""User set operations for CTE management."""

from typing import Any
from .base import CTESubTool

class UserSetOperations(CTESubTool):
    """Handles all user set operations for CTE management."""
    
    def get_operations(self) -> list[str]:
        """Return list of all user set operations."""
        return [
            "user_set_create", "user_set_list", "user_set_get", "user_set_delete", "user_set_modify",
            "user_set_add_users", "user_set_delete_user", "user_set_update_user",
            "user_set_list_users", "user_set_list_policies"
        ]
    
    def get_schema_properties(self) -> dict[str, Any]:
        """Return schema properties specific to user set operations."""
        return {
            "user_set_identifier": {
                "type": "string",
                "description": "User set identifier (name, ID, or URI)"
            },
            "user_set_name": {
                "type": "string",
                "description": "User set name for filtering"
            },
            "user_json": {
                "type": "string",
                "description": "User set configuration in JSON format"
            },
            "user_json_file": {
                "type": "string",
                "description": "Path to JSON file containing user set configuration"
            },
            "user_index": {
                "type": "string",
                "description": "Index of user in user set"
            },
            "user_index_list": {
                "type": "string",
                "description": "Comma-separated list of user indices"
            }
        }
    
    def get_action_requirements(self) -> dict[str, Any]:
        """Return action requirements for user set operations."""
        return {
            "user_set_create": {
                "required": [],
                "optional": ["user_json", "user_json_file", "domain", "auth_domain"],
                "example": {
                    "action": "user_set_create",
                    "user_json": "{\"name\": \"USet01\", \"description\": \"User set for Administrator in thales.com domain\", \"users\": [{\"uname\": \"Administrator\", \"os_domain\": \"thales.com\"}]}"
                },
                "json_structure": {
                    "name": "string",
                    "description": "string",
                    "users": [
                        {
                            "uname": "string",
                            "uid": "integer (optional)",
                            "gname": "string (optional)",
                            "gid": "integer (optional)",
                            "os_domain": "string (optional, for Windows domain users)"
                        }
                    ]
                }
            },
            "user_set_list": {
                "required": [],
                "optional": ["limit", "skip", "user_set_name", "domain", "auth_domain"],
                "example": {
                    "action": "user_set_list",
                    "limit": 20
                }
            },
            "user_set_get": {
                "required": ["user_set_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "user_set_get",
                    "user_set_identifier": "USet01"
                }
            },
            "user_set_delete": {
                "required": ["user_set_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "user_set_delete",
                    "user_set_identifier": "USet01"
                }
            },
            "user_set_modify": {
                "required": ["user_set_identifier"],
                "optional": ["user_json", "user_json_file", "domain", "auth_domain"],
                "example": {
                    "action": "user_set_modify",
                    "user_set_identifier": "USet01",
                    "user_json": "{\"description\": \"Updated user set description\"}"
                }
            },
            "user_set_add_users": {
                "required": ["user_set_identifier", "user_json_file"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "user_set_add_users",
                    "user_set_identifier": "USet01",
                    "user_json_file": "/path/to/users.json"
                }
            },
            "user_set_delete_user": {
                "required": ["user_set_identifier", "user_index_list"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "user_set_delete_user",
                    "user_set_identifier": "USet01",
                    "user_index_list": "0,1,2"
                }
            },
            "user_set_update_user": {
                "required": ["user_set_identifier", "user_index", "user_json_file"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "user_set_update_user",
                    "user_set_identifier": "USet01",
                    "user_index": "0",
                    "user_json_file": "/path/to/updated_user.json"
                }
            },
            "user_set_list_users": {
                "required": ["user_set_identifier"],
                "optional": ["limit", "skip", "search", "domain", "auth_domain"],
                "example": {
                    "action": "user_set_list_users",
                    "user_set_identifier": "USet01"
                }
            },
            "user_set_list_policies": {
                "required": ["user_set_identifier"],
                "optional": ["limit", "skip", "domain", "auth_domain"],
                "example": {
                    "action": "user_set_list_policies",
                    "user_set_identifier": "USet01"
                }
            }
        }
    
    async def execute_operation(self, action: str, **kwargs: Any) -> Any:
        """Execute the specified user set operation."""
        method_name = f"_{action}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(**kwargs)
        else:
            return {"error": f"Unknown user set action: {action}"}
    
    def _user_set_create(self, **kwargs):
        """Create a CTE user set."""
        args = ["cte", "user-sets", "create"]
        
        if kwargs.get("user_json"):
            args.extend(["--user-json", kwargs["user_json"]])
        elif kwargs.get("user_json_file"):
            args.extend(["--user-json-file", kwargs["user_json_file"]])
        else:
            return {"error": "Either user_json or user_json_file must be specified"}
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _user_set_list(self, **kwargs):
        """List CTE user sets."""
        args = ["cte", "user-sets", "list"]
        args.extend(["--limit", str(kwargs.get("limit", 10))])
        args.extend(["--skip", str(kwargs.get("skip", 0))])
        
        if kwargs.get("user_set_name"):
            args.extend(["--user-set-name", kwargs["user_set_name"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _user_set_get(self, **kwargs):
        """Get a CTE user set."""
        args = ["cte", "user-sets", "get"]
        args.extend(["--user-set-identifier", kwargs["user_set_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _user_set_delete(self, **kwargs):
        """Delete a CTE user set."""
        args = ["cte", "user-sets", "delete"]
        args.extend(["--user-set-identifier", kwargs["user_set_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _user_set_modify(self, **kwargs):
        """Modify a CTE user set."""
        args = ["cte", "user-sets", "modify"]
        args.extend(["--user-set-identifier", kwargs["user_set_identifier"]])
        
        if kwargs.get("user_json"):
            args.extend(["--user-json", kwargs["user_json"]])
        elif kwargs.get("user_json_file"):
            args.extend(["--user-json-file", kwargs["user_json_file"]])
        else:
            return {"error": "Either user_json or user_json_file must be specified"}
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _user_set_add_users(self, **kwargs):
        """Add users to a CTE user set."""
        args = ["cte", "user-sets", "add-users"]
        args.extend(["--user-set-identifier", kwargs["user_set_identifier"]])
        args.extend(["--user-json-file", kwargs["user_json_file"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _user_set_delete_user(self, **kwargs):
        """Delete a user from a CTE user set."""
        args = ["cte", "user-sets", "delete-user"]
        args.extend(["--user-set-identifier", kwargs["user_set_identifier"]])
        args.extend(["--user-index-list", kwargs["user_index_list"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _user_set_update_user(self, **kwargs):
        """Update a user in a CTE user set."""
        args = ["cte", "user-sets", "update-user"]
        args.extend(["--user-set-identifier", kwargs["user_set_identifier"]])
        args.extend(["--user-index", kwargs["user_index"]])
        args.extend(["--user-json-file", kwargs["user_json_file"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _user_set_list_users(self, **kwargs):
        """List users in a CTE user set."""
        args = ["cte", "user-sets", "list-users"]
        args.extend(["--user-set-identifier", kwargs["user_set_identifier"]])
        args.extend(["--limit", str(kwargs.get("limit", 10))])
        args.extend(["--skip", str(kwargs.get("skip", 0))])
        
        if kwargs.get("search"):
            args.extend(["--search", kwargs["search"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _user_set_list_policies(self, **kwargs):
        """List policies associated with a CTE user set."""
        args = ["cte", "user-sets", "list-policies"]
        args.extend(["--user-set-identifier", kwargs["user_set_identifier"]])
        args.extend(["--limit", str(kwargs.get("limit", 10))])
        args.extend(["--skip", str(kwargs.get("skip", 0))])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))