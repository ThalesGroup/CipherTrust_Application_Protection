"""Process set operations for CTE management."""

from typing import Any
from .base import CTESubTool

class ProcessSetOperations(CTESubTool):
    """Handles all process set operations for CTE management."""
    
    def get_operations(self) -> list[str]:
        """Return list of all process set operations."""
        return [
            "process_set_create", "process_set_list", "process_set_get", "process_set_delete", "process_set_modify",
            "process_set_add_processes", "process_set_delete_process", "process_set_update_process",
            "process_set_list_processes", "process_set_list_policies"
        ]
    
    def get_schema_properties(self) -> dict[str, Any]:
        """Return schema properties specific to process set operations."""
        return {
            "process_set_identifier": {
                "type": "string", 
                "description": "Process set identifier (name, ID, or URI)"
            },
            "process_set_name": {
                "type": "string",
                "description": "Process set name for filtering"
            },
            "process_json": {
                "type": "string",
                "description": "Process set configuration in JSON format"
            },
            "process_json_file": {
                "type": "string",
                "description": "Path to JSON file containing process set configuration"
            },
            "process_index": {
                "type": "string",
                "description": "Index of process in process set"
            },
            "process_index_list": {
                "type": "string",
                "description": "Comma-separated list of process indices"
            }
        }
    
    def get_action_requirements(self) -> dict[str, Any]:
        """Return action requirements for process set operations."""
        return {
            "process_set_create": {
                "required": [],
                "optional": ["process_json", "process_json_file", "domain", "auth_domain"],
                "example": {
                    "action": "process_set_create",
                    "process_json": "{\"name\": \"PSet01\", \"description\": \"Trusted application processes\", \"processes\": [{\"signature\": \"AppSignatureSet\", \"directory\": \"/usr/bin\", \"file\": \"app.exe\"}]}"
                },
                "json_structure": {
                    "name": "string",
                    "description": "string",
                    "processes": [
                        {
                            "signature": "string (signature set name)",
                            "directory": "string",
                            "file": "string (filename or * for all)"
                        }
                    ]
                }
            },
            "process_set_list": {
                "required": [],
                "optional": ["limit", "skip", "process_set_name", "domain", "auth_domain"],
                "example": {
                    "action": "process_set_list",
                    "limit": 20
                }
            },
            "process_set_get": {
                "required": ["process_set_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "process_set_get",
                    "process_set_identifier": "PSet01"
                }
            },
            "process_set_delete": {
                "required": ["process_set_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "process_set_delete",
                    "process_set_identifier": "PSet01"
                }
            },
            "process_set_modify": {
                "required": ["process_set_identifier"],
                "optional": ["process_json", "process_json_file", "domain", "auth_domain"],
                "example": {
                    "action": "process_set_modify",
                    "process_set_identifier": "PSet01",
                    "process_json": "{\"description\": \"Updated process set description\"}"
                }
            },
            "process_set_add_processes": {
                "required": ["process_set_identifier", "process_json_file"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "process_set_add_processes",
                    "process_set_identifier": "PSet01",
                    "process_json_file": "/path/to/processes.json"
                }
            },
            "process_set_delete_process": {
                "required": ["process_set_identifier", "process_index_list"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "process_set_delete_process",
                    "process_set_identifier": "PSet01",
                    "process_index_list": "0,1,2"
                }
            },
            "process_set_update_process": {
                "required": ["process_set_identifier", "process_index", "process_json_file"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "process_set_update_process",
                    "process_set_identifier": "PSet01",
                    "process_index": "0",
                    "process_json_file": "/path/to/updated_process.json"
                }
            },
            "process_set_list_processes": {
                "required": ["process_set_identifier"],
                "optional": ["limit", "skip", "search", "domain", "auth_domain"],
                "example": {
                    "action": "process_set_list_processes",
                    "process_set_identifier": "PSet01"
                }
            },
            "process_set_list_policies": {
                "required": ["process_set_identifier"],
                "optional": ["limit", "skip", "domain", "auth_domain"],
                "example": {
                    "action": "process_set_list_policies",
                    "process_set_identifier": "PSet01"
                }
            }
        }
    
    async def execute_operation(self, action: str, **kwargs: Any) -> Any:
        """Execute the specified process set operation."""
        method_name = f"_{action}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(**kwargs)
        else:
            return {"error": f"Unknown process set action: {action}"}
    
    def _process_set_create(self, **kwargs):
        """Create a CTE process set."""
        args = ["cte", "process-sets", "create"]
        
        if kwargs.get("process_json"):
            args.extend(["--process-json", kwargs["process_json"]])
        elif kwargs.get("process_json_file"):
            args.extend(["--process-json-file", kwargs["process_json_file"]])
        else:
            return {"error": "Either process_json or process_json_file must be specified"}
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _process_set_list(self, **kwargs):
        """List CTE process sets."""
        args = ["cte", "process-sets", "list"]
        args.extend(["--limit", str(kwargs.get("limit", 10))])
        args.extend(["--skip", str(kwargs.get("skip", 0))])
        
        if kwargs.get("process_set_name"):
            args.extend(["--process-set-name", kwargs["process_set_name"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _process_set_get(self, **kwargs):
        """Get a CTE process set."""
        args = ["cte", "process-sets", "get"]
        args.extend(["--process-set-identifier", kwargs["process_set_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _process_set_delete(self, **kwargs):
        """Delete a CTE process set."""
        args = ["cte", "process-sets", "delete"]
        args.extend(["--process-set-identifier", kwargs["process_set_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _process_set_modify(self, **kwargs):
        """Modify a CTE process set."""
        args = ["cte", "process-sets", "modify"]
        args.extend(["--process-set-identifier", kwargs["process_set_identifier"]])
        
        if kwargs.get("process_json"):
            args.extend(["--process-json", kwargs["process_json"]])
        elif kwargs.get("process_json_file"):
            args.extend(["--process-json-file", kwargs["process_json_file"]])
        else:
            return {"error": "Either process_json or process_json_file must be specified"}
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _process_set_add_processes(self, **kwargs):
        """Add processes to a CTE process set."""
        args = ["cte", "process-sets", "add-processes"]
        args.extend(["--process-set-identifier", kwargs["process_set_identifier"]])
        args.extend(["--process-json-file", kwargs["process_json_file"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _process_set_delete_process(self, **kwargs):
        """Delete a process from a CTE process set."""
        args = ["cte", "process-sets", "delete-process"]
        args.extend(["--process-set-identifier", kwargs["process_set_identifier"]])
        args.extend(["--process-index-list", kwargs["process_index_list"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _process_set_update_process(self, **kwargs):
        """Update a process in a CTE process set."""
        args = ["cte", "process-sets", "update-process"]
        args.extend(["--process-set-identifier", kwargs["process_set_identifier"]])
        args.extend(["--process-index", kwargs["process_index"]])
        args.extend(["--process-json-file", kwargs["process_json_file"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _process_set_list_processes(self, **kwargs):
        """List processes in a CTE process set."""
        args = ["cte", "process-sets", "list-processes"]
        args.extend(["--process-set-identifier", kwargs["process_set_identifier"]])
        args.extend(["--limit", str(kwargs.get("limit", 10))])
        args.extend(["--skip", str(kwargs.get("skip", 0))])
        
        if kwargs.get("search"):
            args.extend(["--search", kwargs["search"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _process_set_list_policies(self, **kwargs):
        """List policies associated with a CTE process set."""
        args = ["cte", "process-sets", "list-policies"]
        args.extend(["--process-set-identifier", kwargs["process_set_identifier"]])
        args.extend(["--limit", str(kwargs.get("limit", 10))])
        args.extend(["--skip", str(kwargs.get("skip", 0))])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))