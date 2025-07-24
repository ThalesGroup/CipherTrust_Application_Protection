"""Client operations for CTE management."""

from typing import Any
from .base import CTESubTool

class ClientOperations(CTESubTool):
    """Handles all client and guardpoint operations for CTE management."""
    
    def get_operations(self) -> list[str]:
        """Return list of all client operations."""
        return [
            "client_create", "client_list", "client_get", "client_delete", "client_modify",
            "client_create_guardpoint", "client_list_guardpoints", "client_get_guardpoint",
            "client_modify_guardpoint", "client_unguard_guardpoint"
        ]
    
    def get_schema_properties(self) -> dict[str, Any]:
        """Return schema properties specific to client operations."""
        return {
            # Client parameters
            "cte_client_name": {
                "type": "string",
                "description": "Name for the CTE client (required for client_create)"
            },
            "cte_client_identifier": {
                "type": "string",
                "description": "Client identifier: name, ID, or URI (required for client operations)"
            },
            "client_password": {
                "type": "string",
                "description": "Client password (optional, will be generated if not provided)"
            },
            "password_creation_method": {
                "type": "string",
                "enum": ["GENERATE", "MANUAL"],
                "default": "GENERATE",
                "description": "Method to create password"
            },
            "comm_enabled": {
                "type": "boolean",
                "default": False,
                "description": "Enable communication for the client"
            },
            "reg_allowed": {
                "type": "boolean", 
                "default": False,
                "description": "Allow client registration"
            },
            "cte_client_type": {
                "type": "string",
                "enum": ["FS", "CSI", "CTE-U"],
                "description": "Type of CTE client"
            },
            "cte_profile_identifier": {
                "type": "string",
                "description": "CTE profile identifier to assign to client"
            },
            "cte_client_locked": {
                "type": "boolean",
                "description": "Lock status of CTE client"
            },
            "system_locked": {
                "type": "boolean",
                "description": "System lock status"
            },
            "host_name": {
                "type": "string",
                "description": "Hostname of CTE client"
            },
            "client_mfa_enabled": {
                "type": "boolean",
                "description": "Enable MFA at client level"
            },
            
            # Guardpoint parameters
            "guard_path_list": {
                "type": "string",
                "description": "Comma-separated list of paths to guard (required for client_create_guardpoint)"
            },
            "guard_point_type": {
                "type": "string",
                "description": "Guardpoint type: directory_auto, directory_manual, etc. (required for client_create_guardpoint)"
            },
            "guard_point_identifier": {
                "type": "string",
                "description": "Guardpoint identifier for guardpoint operations"
            },
            "guard_enabled": {
                "type": "boolean",
                "default": True,
                "description": "Whether guard is enabled"
            },
            "auto_mount_enabled": {
                "type": "boolean",
                "default": False,
                "description": "Enable automount"
            },
            "cifs_enabled": {
                "type": "boolean",
                "default": False,
                "description": "Enable CIFS"
            },
            "early_access": {
                "type": "boolean",
                "default": False,
                "description": "Early access (secure start) on Windows clients"
            },
            "preserve_sparse_regions": {
                "type": "boolean",
                "default": True,
                "description": "Preserve sparse file regions (LDT clients)"
            },
            "mfa_enabled": {
                "type": "boolean",
                "default": False,
                "description": "Enable MFA at guard point level"
            },
            "intelligent_protection": {
                "type": "boolean",
                "default": False,
                "description": "Enable intelligent protection"
            },
            "is_idt_capable_device": {
                "type": "boolean", 
                "default": False,
                "description": "Whether device is IDT capable"
            }
        }
    
    def get_action_requirements(self) -> dict[str, Any]:
        """Return action requirements for client operations."""
        return {
            "client_create": {
                "required": ["cte_client_name"],
                "optional": ["client_password", "password_creation_method", "comm_enabled", "reg_allowed", 
                            "cte_client_type", "cte_profile_identifier", "description", "domain", "auth_domain"],
                "example": {
                    "action": "client_create",
                    "cte_client_name": "WebServer01",
                    "comm_enabled": True,
                    "reg_allowed": True
                }
            },
            "client_list": {
                "required": [],
                "optional": ["limit", "skip", "cte_client_name", "cte_client_type", "domain", "auth_domain"],
                "example": {
                    "action": "client_list",
                    "limit": 20
                }
            },
            "client_get": {
                "required": ["cte_client_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "client_get",
                    "cte_client_identifier": "WebServer01"
                }
            },
            "client_delete": {
                "required": ["cte_client_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "client_delete",
                    "cte_client_identifier": "WebServer01"
                }
            },
            "client_modify": {
                "required": ["cte_client_identifier"],
                "optional": ["client_password", "password_creation_method", "comm_enabled", "reg_allowed", 
                            "cte_client_locked", "system_locked", "cte_profile_identifier", "host_name", 
                            "client_mfa_enabled", "domain", "auth_domain"],
                "example": {
                    "action": "client_modify",
                    "cte_client_identifier": "WebServer01",
                    "comm_enabled": False
                }
            },
            "client_create_guardpoint": {
                "required": ["cte_client_identifier", "guard_path_list", "guard_point_type"],
                "optional": ["cte_policy_identifier", "guard_enabled", "auto_mount_enabled", "cifs_enabled", 
                            "early_access", "preserve_sparse_regions", "mfa_enabled", "intelligent_protection", 
                            "is_idt_capable_device", "domain", "auth_domain"],
                "example": {
                    "action": "client_create_guardpoint",
                    "cte_client_identifier": "WebServer01", 
                    "guard_path_list": "/data/sensitive,/logs/audit",
                    "guard_point_type": "directory_auto",
                    "cte_policy_identifier": "MyDataPolicy"
                }
            },
            "client_list_guardpoints": {
                "required": ["cte_client_identifier"],
                "optional": ["limit", "skip", "cte_policy_identifier", "sort", "domain", "auth_domain"],
                "example": {
                    "action": "client_list_guardpoints",
                    "cte_client_identifier": "WebServer01"
                }
            },
            "client_get_guardpoint": {
                "required": ["cte_client_identifier", "guard_point_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "client_get_guardpoint",
                    "cte_client_identifier": "WebServer01",
                    "guard_point_identifier": "gp123"
                }
            },
            "client_modify_guardpoint": {
                "required": ["cte_client_identifier", "guard_point_identifier"],
                "optional": ["guard_enabled", "mfa_enabled", "domain", "auth_domain"],
                "example": {
                    "action": "client_modify_guardpoint",
                    "cte_client_identifier": "WebServer01",
                    "guard_point_identifier": "gp123",
                    "guard_enabled": False
                }
            },
            "client_unguard_guardpoint": {
                "required": ["cte_client_identifier", "guard_point_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "client_unguard_guardpoint",
                    "cte_client_identifier": "WebServer01",
                    "guard_point_identifier": "gp123"
                }
            }
        }
    
    async def execute_operation(self, action: str, **kwargs: Any) -> Any:
        """Execute the specified client operation."""
        method_name = f"_{action}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(**kwargs)
        else:
            return {"error": f"Unknown client action: {action}"}
    
    # Client Operations
    
    def _client_create(self, **kwargs):
        """Create a CTE client."""
        args = ["cte", "clients", "create"]
        args.extend(["--cte-client-name", kwargs["cte_client_name"]])
        
        if kwargs.get("client_password"):
            args.extend(["--client-password", kwargs["client_password"]])
        if kwargs.get("password_creation_method", "GENERATE") != "GENERATE":
            args.extend(["--password-creation-method", kwargs["password_creation_method"]])
        if kwargs.get("comm_enabled"):
            args.append("--comm-enabled")
        if kwargs.get("reg_allowed"):
            args.append("--reg-allowed")
        if kwargs.get("cte_client_type"):
            args.extend(["--cte-client-type", kwargs["cte_client_type"]])
        if kwargs.get("cte_profile_identifier"):
            args.extend(["--cte-profile-identifier", kwargs["cte_profile_identifier"]])
        if kwargs.get("description"):
            args.extend(["--description", kwargs["description"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _client_list(self, **kwargs):
        """List CTE clients."""
        args = ["cte", "clients", "list"]
        args.extend(["--limit", str(kwargs.get("limit", 10))])
        args.extend(["--skip", str(kwargs.get("skip", 0))])
        
        if kwargs.get("cte_client_name"):
            args.extend(["--cte-client-name", kwargs["cte_client_name"]])
        if kwargs.get("cte_client_type"):
            args.extend(["--cte-client-type", kwargs["cte_client_type"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _client_get(self, **kwargs):
        """Get a CTE client."""
        args = ["cte", "clients", "get"]
        args.extend(["--cte-client-identifier", kwargs["cte_client_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _client_delete(self, **kwargs):
        """Delete a CTE client."""
        args = ["cte", "clients", "delete"]
        args.extend(["--cte-client-identifier", kwargs["cte_client_identifier"]])
        args.append("--del-client")
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _client_modify(self, **kwargs):
        """Modify a CTE client."""
        args = ["cte", "clients", "modify"]
        args.extend(["--cte-client-identifier", kwargs["cte_client_identifier"]])
        
        if kwargs.get("client_password"):
            args.extend(["--client-password", kwargs["client_password"]])
        if kwargs.get("password_creation_method"):
            args.extend(["--password-creation-method", kwargs["password_creation_method"]])
        if kwargs.get("comm_enabled") is not None:
            args.append("--comm-enabled" if kwargs["comm_enabled"] else "--no-comm-enabled")
        if kwargs.get("reg_allowed") is not None:
            args.append("--reg-allowed" if kwargs["reg_allowed"] else "--no-reg-allowed")
        if kwargs.get("cte_client_locked") is not None:
            args.append("--cte-client-locked" if kwargs["cte_client_locked"] else "--no-cte-client-locked")
        if kwargs.get("system_locked") is not None:
            args.append("--system-locked" if kwargs["system_locked"] else "--no-system-locked")
        if kwargs.get("cte_profile_identifier"):
            args.extend(["--cte-profile-identifier", kwargs["cte_profile_identifier"]])
        if kwargs.get("host_name"):
            args.extend(["--host-name", kwargs["host_name"]])
        if kwargs.get("client_mfa_enabled") is not None:
            args.append("--client-mfa-enabled" if kwargs["client_mfa_enabled"] else "--no-client-mfa-enabled")
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    # Guardpoint Operations
    
    def _client_create_guardpoint(self, **kwargs):
        """Create a guardpoint on a CTE client."""
        args = ["cte", "clients", "create-guardpoints"]
        args.extend(["--cte-client-identifier", kwargs["cte_client_identifier"]])
        args.extend(["--guard-path-list", kwargs["guard_path_list"]])
        args.extend(["--guard-point-type", kwargs["guard_point_type"]])
        
        if kwargs.get("cte_policy_identifier"):
            args.extend(["--cte-policy-identifier", kwargs["cte_policy_identifier"]])
        if not kwargs.get("guard_enabled", True):
            args.append("--no-guard-enabled")
        if kwargs.get("auto_mount_enabled"):
            args.append("--auto-mount-enabled")
        if kwargs.get("cifs_enabled"):
            args.append("--cifs-enabled")
        if kwargs.get("early_access"):
            args.append("--early-access")
        if not kwargs.get("preserve_sparse_regions", True):
            args.append("--no-preserve-sparse-regions")
        if kwargs.get("mfa_enabled"):
            args.append("--mfa-enabled")
        if kwargs.get("intelligent_protection"):
            args.append("--intelligent-protection")
        if kwargs.get("is_idt_capable_device"):
            args.append("--is-idt-capable-device")
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _client_list_guardpoints(self, **kwargs):
        """List guardpoints on a CTE client."""
        args = ["cte", "clients", "list-guardpoints"]
        args.extend(["--cte-client-identifier", kwargs["cte_client_identifier"]])
        args.extend(["--limit", str(kwargs.get("limit", 10))])
        args.extend(["--skip", str(kwargs.get("skip", 0))])
        
        if kwargs.get("cte_policy_identifier"):
            args.extend(["--cte-policy-identifier", kwargs["cte_policy_identifier"]])
        if kwargs.get("sort"):
            args.extend(["--sort", kwargs["sort"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _client_get_guardpoint(self, **kwargs):
        """Get a guardpoint on a CTE client."""
        args = ["cte", "clients", "get-guardpoints"]
        args.extend(["--cte-client-identifier", kwargs["cte_client_identifier"]])
        args.extend(["--guard-point-identifier", kwargs["guard_point_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _client_modify_guardpoint(self, **kwargs):
        """Modify a guardpoint on a CTE client."""
        args = ["cte", "clients", "modify-guardpoints"]
        args.extend(["--cte-client-identifier", kwargs["cte_client_identifier"]])
        args.extend(["--guard-point-identifier", kwargs["guard_point_identifier"]])
        
        if kwargs.get("guard_enabled") is not None:
            args.append("--guard-enabled" if kwargs["guard_enabled"] else "--no-guard-enabled")
        if kwargs.get("mfa_enabled") is not None:
            args.append("--mfa-enabled" if kwargs["mfa_enabled"] else "--no-mfa-enabled")
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _client_unguard_guardpoint(self, **kwargs):
        """Unguard a guardpoint from a CTE client."""
        args = ["cte", "clients", "unguard-guardpoints"]
        args.extend(["--cte-client-identifier", kwargs["cte_client_identifier"]])
        args.extend(["--guard-point-identifier", kwargs["guard_point_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))