"""Policy operations for CTE management."""

from typing import Any
from .base import CTESubTool

class PolicyOperations(CTESubTool):
    """Handles all policy-related operations for CTE management."""
    
    def get_operations(self) -> list[str]:
        """Return list of all policy operations."""
        return [
            # Core policy operations
            "policy_create", "policy_list", "policy_get", "policy_delete", "policy_modify",
            # Security rule operations
            "policy_add_security_rule", "policy_delete_security_rule", "policy_get_security_rule",
            "policy_list_security_rules", "policy_modify_security_rule",
            # Key rule operations
            "policy_add_key_rule", "policy_delete_key_rule", "policy_get_key_rule",
            "policy_list_key_rules", "policy_modify_key_rule",
            # LDT rule operations
            "policy_add_ldt_rule", "policy_delete_ldt_rule", "policy_get_ldt_rule",
            "policy_list_ldt_rules", "policy_modify_ldt_rule"
        ]
    
    def get_schema_properties(self) -> dict[str, Any]:
        """Return schema properties specific to policy operations."""
        return {
            # Core policy parameters
            "cte_policy_name": {
                "type": "string",
                "description": "Name of the CTE policy (required for policy_create)"
            },
            "cte_policy_identifier": {
                "type": "string", 
                "description": "Policy identifier: name, ID, or URI (required for policy operations)"
            },
            "policy_type": {
                "type": "string",
                "enum": ["Standard", "Cloud_Object_Storage", "LDT", "IDT", "CSI"],
                "description": "Type of policy (required for policy_create)"
            },
            "never_deny": {
                "type": "boolean",
                "default": False,
                "description": "Always permit operations in policy (for policies)"
            },
            
            # Security rule parameters
            "effect": {
                "type": "string", 
                "description": "Rule effect: permit, deny, audit, applykey (comma-separated for multiple effects)"
            },
            "action_type": {
                "type": "string",
                "description": "Action type: read, write, all_ops, key_op (for security rules)"
            },
            "security_rule_identifier": {
                "type": "string",
                "description": "Security rule identifier for rule operations"
            },
            "exclude_user_set": {
                "type": "boolean",
                "default": False,
                "description": "Exclude the user set from the policy"
            },
            "exclude_process_set": {
                "type": "boolean", 
                "default": False,
                "description": "Exclude the process set from the policy"
            },
            "exclude_resource_set": {
                "type": "boolean",
                "default": False,
                "description": "Exclude the resource set from the policy"
            },
            "order_number": {
                "type": "integer",
                "description": "Order number for rule ordering"
            },
            
            # Key rule parameters
            "key_identifier": {
                "type": "string",
                "description": "Key identifier: name, id, slug, alias, uri, uuid, muid, key_id, or 'clear_key'"
            },
            "key_type": {
                "type": "string",
                "description": "Key type: name, id, slug, alias, uri, uuid, muid, or key_id"
            },
            "key_rule_identifier": {
                "type": "string",
                "description": "Key rule identifier for rule operations"
            },
            
            # LDT rule parameters
            "current_key_json_file": {
                "type": "string",
                "description": "Path to JSON file with current key parameters (required for LDT rules)"
            },
            "transform_key_json_file": {
                "type": "string", 
                "description": "Path to JSON file with transformation key parameters (required for LDT rules)"
            },
            "ldt_rule_identifier": {
                "type": "string",
                "description": "LDT rule identifier for rule operations"
            },
            "is_exclusion_rule": {
                "type": "boolean",
                "default": False,
                "description": "Whether LDT rule is exclusion rule"
            },
            
            # Rule JSON parameters
            "security_rules_json": {
                "type": "string",
                "description": "Security rules in JSON format (for policy_create)"
            },
            "security_rules_json_file": {
                "type": "string",
                "description": "Path to JSON file containing security rules (for policy_create)"
            },
            "key_rules_json": {
                "type": "string",
                "description": "Key rules in JSON format (for policy_create)"
            },
            "key_rules_json_file": {
                "type": "string",
                "description": "Path to JSON file containing key rules (for policy_create)"
            },
            "ldt_rules_json": {
                "type": "string",
                "description": "LDT rules in JSON format (for policy_create)"
            },
            "ldt_rules_json_file": {
                "type": "string",
                "description": "Path to JSON file containing LDT rules (for policy_create)"
            },
            "data_tx_rules_json": {
                "type": "string",
                "description": "Data transformation rules in JSON format (for policy_create)"
            },
            "data_tx_rules_json_file": {
                "type": "string",
                "description": "Path to JSON file containing data transformation rules (for policy_create)"
            },
            "idt_rules_json": {
                "type": "string",
                "description": "IDT rules in JSON format (for policy_create)"
            },
            "idt_rules_json_file": {
                "type": "string",
                "description": "Path to JSON file containing IDT rules (for policy_create)"
            },
            "signature_rules_json": {
                "type": "string",
                "description": "Signature rules in JSON format (for policy_create)"
            },
            "signature_rules_json_file": {
                "type": "string",
                "description": "Path to JSON file containing signature rules (for policy_create)"
            },
            "restrict_update_json": {
                "type": "string",
                "description": "Restrict update parameters in JSON format"
            },
            "restrict_update_json_file": {
                "type": "string",
                "description": "Path to JSON file containing restrict update parameters"
            },
            
            # Set identifiers used in policy rules
            "user_set_identifier": {
                "type": "string",
                "description": "User set identifier (name, ID, or URI)"
            },
            "process_set_identifier": {
                "type": "string", 
                "description": "Process set identifier (name, ID, or URI)"
            },
            "resource_set_identifier": {
                "type": "string",
                "description": "Resource set identifier (name, ID, or URI)"
            }
        }
    
    def get_action_requirements(self) -> dict[str, Any]:
        """Return action requirements for policy operations."""
        return {
            "policy_create": {
                "required": ["cte_policy_name", "policy_type"],
                "optional": ["description", "never_deny", "security_rules_json", "key_rules_json", "domain", "auth_domain"],
                "example": {
                    "action": "policy_create",
                    "cte_policy_name": "MyDataPolicy", 
                    "policy_type": "Standard",
                    "description": "Policy for sensitive data protection"
                }
            },
            "policy_list": {
                "required": [],
                "optional": ["limit", "skip", "cte_policy_name", "policy_type", "domain", "auth_domain"],
                "example": {
                    "action": "policy_list",
                    "limit": 20
                }
            },
            "policy_get": {
                "required": ["cte_policy_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "policy_get",
                    "cte_policy_identifier": "MyDataPolicy"
                }
            },
            "policy_delete": {
                "required": ["cte_policy_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "policy_delete",
                    "cte_policy_identifier": "MyDataPolicy"
                }
            },
            "policy_modify": {
                "required": ["cte_policy_identifier"],
                "optional": ["description", "never_deny", "restrict_update_json", "restrict_update_json_file", "domain", "auth_domain"],
                "example": {
                    "action": "policy_modify",
                    "cte_policy_identifier": "MyDataPolicy",
                    "description": "Updated policy description"
                }
            },
            "policy_add_security_rule": {
                "required": ["cte_policy_identifier", "effect"],
                "optional": ["action_type", "user_set_identifier", "process_set_identifier", "resource_set_identifier", 
                            "exclude_user_set", "exclude_process_set", "exclude_resource_set", "domain", "auth_domain"],
                "example": {
                    "action": "policy_add_security_rule",
                    "cte_policy_identifier": "MyDataPolicy",
                    "effect": "permit",
                    "action_type": "read",
                    "user_set_identifier": "AdminUsers"
                }
            },
            "policy_delete_security_rule": {
                "required": ["cte_policy_identifier", "security_rule_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "policy_delete_security_rule",
                    "cte_policy_identifier": "MyDataPolicy",
                    "security_rule_identifier": "rule123"
                }
            },
            "policy_get_security_rule": {
                "required": ["cte_policy_identifier", "security_rule_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "policy_get_security_rule",
                    "cte_policy_identifier": "MyDataPolicy",
                    "security_rule_identifier": "rule123"
                }
            },
            "policy_list_security_rules": {
                "required": ["cte_policy_identifier"],
                "optional": ["limit", "skip", "action_type", "domain", "auth_domain"],
                "example": {
                    "action": "policy_list_security_rules",
                    "cte_policy_identifier": "MyDataPolicy"
                }
            },
            "policy_modify_security_rule": {
                "required": ["cte_policy_identifier", "security_rule_identifier"],
                "optional": ["effect", "action_type", "order_number", "user_set_identifier", "process_set_identifier", 
                            "resource_set_identifier", "exclude_user_set", "exclude_process_set", "exclude_resource_set", 
                            "domain", "auth_domain"],
                "example": {
                    "action": "policy_modify_security_rule",
                    "cte_policy_identifier": "MyDataPolicy",
                    "security_rule_identifier": "rule123",
                    "effect": "permit,audit"
                }
            },
            "policy_add_key_rule": {
                "required": ["cte_policy_identifier", "key_identifier"],
                "optional": ["key_type", "resource_set_identifier", "domain", "auth_domain"],
                "example": {
                    "action": "policy_add_key_rule", 
                    "cte_policy_identifier": "MyDataPolicy",
                    "key_identifier": "DataEncryptionKey",
                    "key_type": "name"
                }
            },
            "policy_delete_key_rule": {
                "required": ["cte_policy_identifier", "key_rule_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "policy_delete_key_rule",
                    "cte_policy_identifier": "MyDataPolicy",
                    "key_rule_identifier": "keyrule123"
                }
            },
            "policy_get_key_rule": {
                "required": ["cte_policy_identifier", "key_rule_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "policy_get_key_rule",
                    "cte_policy_identifier": "MyDataPolicy",
                    "key_rule_identifier": "keyrule123"
                }
            },
            "policy_list_key_rules": {
                "required": ["cte_policy_identifier"],
                "optional": ["limit", "skip", "domain", "auth_domain"],
                "example": {
                    "action": "policy_list_key_rules",
                    "cte_policy_identifier": "MyDataPolicy"
                }
            },
            "policy_modify_key_rule": {
                "required": ["cte_policy_identifier", "key_rule_identifier"],
                "optional": ["key_identifier", "key_type", "order_number", "resource_set_identifier", "domain", "auth_domain"],
                "example": {
                    "action": "policy_modify_key_rule",
                    "cte_policy_identifier": "MyDataPolicy",
                    "key_rule_identifier": "keyrule123",
                    "key_identifier": "NewEncryptionKey"
                }
            },
            "policy_add_ldt_rule": {
                "required": ["cte_policy_identifier", "current_key_json_file", "transform_key_json_file"],
                "optional": ["resource_set_identifier", "is_exclusion_rule", "domain", "auth_domain"],
                "example": {
                    "action": "policy_add_ldt_rule",
                    "cte_policy_identifier": "MyLDTPolicy",
                    "current_key_json_file": "/path/to/current_key.json",
                    "transform_key_json_file": "/path/to/transform_key.json"
                }
            },
            "policy_delete_ldt_rule": {
                "required": ["cte_policy_identifier", "ldt_rule_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "policy_delete_ldt_rule",
                    "cte_policy_identifier": "MyLDTPolicy",
                    "ldt_rule_identifier": "ldtrule123"
                }
            },
            "policy_get_ldt_rule": {
                "required": ["cte_policy_identifier", "ldt_rule_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "policy_get_ldt_rule",
                    "cte_policy_identifier": "MyLDTPolicy",
                    "ldt_rule_identifier": "ldtrule123"
                }
            },
            "policy_list_ldt_rules": {
                "required": ["cte_policy_identifier"],
                "optional": ["domain", "auth_domain"],
                "example": {
                    "action": "policy_list_ldt_rules",
                    "cte_policy_identifier": "MyLDTPolicy"
                }
            },
            "policy_modify_ldt_rule": {
                "required": ["cte_policy_identifier", "ldt_rule_identifier"],
                "optional": ["current_key_json_file", "transform_key_json_file", "order_number", 
                            "resource_set_identifier", "is_exclusion_rule", "domain", "auth_domain"],
                "example": {
                    "action": "policy_modify_ldt_rule",
                    "cte_policy_identifier": "MyLDTPolicy",
                    "ldt_rule_identifier": "ldtrule123",
                    "is_exclusion_rule": True
                }
            }
        }
    
    async def execute_operation(self, action: str, **kwargs: Any) -> Any:
        """Execute the specified policy operation."""
        method_name = f"_{action}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(**kwargs)
        else:
            return {"error": f"Unknown policy action: {action}"}
    
    # Core Policy Operations
    
    def _policy_create(self, **kwargs):
        """Create a CTE policy."""
        args = ["cte", "policies", "create"]
        
        # Required parameters
        args.extend(["--cte-policy-name", kwargs["cte_policy_name"]])
        args.extend(["--policy-type", kwargs["policy_type"]])
        
        # Optional parameters
        if kwargs.get("description"):
            args.extend(["--description", kwargs["description"]])
        if kwargs.get("never_deny", False):
            args.append("--never-deny")
        
        # Rule JSON parameters
        if kwargs.get("security_rules_json"):
            args.extend(["--security-rules-json", kwargs["security_rules_json"]])
        elif kwargs.get("security_rules_json_file"):
            args.extend(["--security-rules-json-file", kwargs["security_rules_json_file"]])
            
        if kwargs.get("key_rules_json"):
            args.extend(["--key-rules-json", kwargs["key_rules_json"]])
        elif kwargs.get("key_rules_json_file"):
            args.extend(["--key-rules-json-file", kwargs["key_rules_json_file"]])
            
        if kwargs.get("data_tx_rules_json"):
            args.extend(["--data-tx-rules-json", kwargs["data_tx_rules_json"]])
        elif kwargs.get("data_tx_rules_json_file"):
            args.extend(["--data-tx-rules-json-file", kwargs["data_tx_rules_json_file"]])
            
        if kwargs.get("ldt_rules_json"):
            args.extend(["--ldt-rules-json", kwargs["ldt_rules_json"]])
        elif kwargs.get("ldt_rules_json_file"):
            args.extend(["--ldt-rules-json-file", kwargs["ldt_rules_json_file"]])
            
        if kwargs.get("idt_rules_json"):
            args.extend(["--idt-rules-json", kwargs["idt_rules_json"]])
        elif kwargs.get("idt_rules_json_file"):
            args.extend(["--idt-rules-json-file", kwargs["idt_rules_json_file"]])
            
        if kwargs.get("signature_rules_json"):
            args.extend(["--signature-rules-json", kwargs["signature_rules_json"]])
        elif kwargs.get("signature_rules_json_file"):
            args.extend(["--signature-rules-json-file", kwargs["signature_rules_json_file"]])
            
        if kwargs.get("restrict_update_json"):
            args.extend(["--restrict-update-json", kwargs["restrict_update_json"]])
        elif kwargs.get("restrict_update_json_file"):
            args.extend(["--restrict-update-json-file", kwargs["restrict_update_json_file"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _policy_list(self, **kwargs):
        """List CTE policies."""
        args = ["cte", "policies", "list"]
        args.extend(["--limit", str(kwargs.get("limit", 10))])
        args.extend(["--skip", str(kwargs.get("skip", 0))])
        
        if kwargs.get("cte_policy_name"):
            args.extend(["--cte-policy-name", kwargs["cte_policy_name"]])
        if kwargs.get("policy_type"):
            args.extend(["--policy-type", kwargs["policy_type"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _policy_get(self, **kwargs):
        """Get a specific CTE policy."""
        args = ["cte", "policies", "get"]
        args.extend(["--cte-policy-identifier", kwargs["cte_policy_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _policy_delete(self, **kwargs):
        """Delete a CTE policy."""
        args = ["cte", "policies", "delete"]
        args.extend(["--cte-policy-identifier", kwargs["cte_policy_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _policy_modify(self, **kwargs):
        """Modify a CTE policy."""
        args = ["cte", "policies", "modify"]
        args.extend(["--cte-policy-identifier", kwargs["cte_policy_identifier"]])
        
        if kwargs.get("description") is not None:
            args.extend(["--description", kwargs["description"]])
        if kwargs.get("never_deny") is not None:
            args.append("--never-deny" if kwargs["never_deny"] else "--no-never-deny")
        
        if kwargs.get("restrict_update_json"):
            args.extend(["--restrict-update-json", kwargs["restrict_update_json"]])
        elif kwargs.get("restrict_update_json_file"):
            args.extend(["--restrict-update-json-file", kwargs["restrict_update_json_file"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    # Security Rule Operations
    
    def _policy_add_security_rule(self, **kwargs):
        """Add a security rule to a policy."""
        args = ["cte", "policies", "add-security-rules"]
        args.extend(["--cte-policy-identifier", kwargs["cte_policy_identifier"]])
        args.extend(["--effect", kwargs["effect"]])
        
        if kwargs.get("action_type"):
            args.extend(["--action", kwargs["action_type"]])  # Note: CLI uses --action
        if kwargs.get("user_set_identifier"):
            args.extend(["--user-set-identifier", kwargs["user_set_identifier"]])
        if kwargs.get("process_set_identifier"):
            args.extend(["--process-set-identifier", kwargs["process_set_identifier"]])
        if kwargs.get("resource_set_identifier"):
            args.extend(["--resource-set-identifier", kwargs["resource_set_identifier"]])
        if kwargs.get("exclude_user_set"):
            args.append("--exclude-user-set")
        if kwargs.get("exclude_process_set"):
            args.append("--exclude-process-set")
        if kwargs.get("exclude_resource_set"):
            args.append("--exclude-resource-set")
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _policy_delete_security_rule(self, **kwargs):
        """Delete a security rule from a policy."""
        args = ["cte", "policies", "delete-security-rules"]
        args.extend(["--cte-policy-identifier", kwargs["cte_policy_identifier"]])
        args.extend(["--security-rule-identifier", kwargs["security_rule_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _policy_get_security_rule(self, **kwargs):
        """Get a security rule from a policy."""
        args = ["cte", "policies", "get-security-rules"]
        args.extend(["--cte-policy-identifier", kwargs["cte_policy_identifier"]])
        args.extend(["--security-rule-identifier", kwargs["security_rule_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _policy_list_security_rules(self, **kwargs):
        """List security rules in a policy."""
        args = ["cte", "policies", "list-security-rules"]
        args.extend(["--cte-policy-identifier", kwargs["cte_policy_identifier"]])
        args.extend(["--limit", str(kwargs.get("limit", 10))])
        args.extend(["--skip", str(kwargs.get("skip", 0))])
        
        if kwargs.get("action_type"):
            args.extend(["--action", kwargs["action_type"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _policy_modify_security_rule(self, **kwargs):
        """Modify a security rule in a policy."""
        args = ["cte", "policies", "modify-security-rules"]
        args.extend(["--cte-policy-identifier", kwargs["cte_policy_identifier"]])
        args.extend(["--security-rule-identifier", kwargs["security_rule_identifier"]])
        
        if kwargs.get("effect"):
            args.extend(["--effect", kwargs["effect"]])
        if kwargs.get("action_type"):
            args.extend(["--action", kwargs["action_type"]])
        if kwargs.get("order_number") is not None:
            args.extend(["--order-number", str(kwargs["order_number"])])
        if kwargs.get("user_set_identifier"):
            args.extend(["--user-set-identifier", kwargs["user_set_identifier"]])
        if kwargs.get("process_set_identifier"):
            args.extend(["--process-set-identifier", kwargs["process_set_identifier"]])
        if kwargs.get("resource_set_identifier"):
            args.extend(["--resource-set-identifier", kwargs["resource_set_identifier"]])
        if kwargs.get("exclude_user_set") is not None:
            args.append("--exclude-user-set" if kwargs["exclude_user_set"] else "--no-exclude-user-set")
        if kwargs.get("exclude_process_set") is not None:
            args.append("--exclude-process-set" if kwargs["exclude_process_set"] else "--no-exclude-process-set")
        if kwargs.get("exclude_resource_set") is not None:
            args.append("--exclude-resource-set" if kwargs["exclude_resource_set"] else "--no-exclude-resource-set")
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    # Key Rule Operations
    
    def _policy_add_key_rule(self, **kwargs):
        """Add a key rule to a policy."""
        args = ["cte", "policies", "add-key-rules"]
        args.extend(["--cte-policy-identifier", kwargs["cte_policy_identifier"]])
        args.extend(["--key-identifier", kwargs["key_identifier"]])
        
        if kwargs.get("key_type"):
            args.extend(["--key-type", kwargs["key_type"]])
        if kwargs.get("resource_set_identifier"):
            args.extend(["--resource-set-identifier", kwargs["resource_set_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _policy_delete_key_rule(self, **kwargs):
        """Delete a key rule from a policy."""
        args = ["cte", "policies", "delete-key-rules"]
        args.extend(["--cte-policy-identifier", kwargs["cte_policy_identifier"]])
        args.extend(["--key-rule-identifier", kwargs["key_rule_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _policy_get_key_rule(self, **kwargs):
        """Get a key rule from a policy."""
        args = ["cte", "policies", "get-key-rules"]
        args.extend(["--cte-policy-identifier", kwargs["cte_policy_identifier"]])
        args.extend(["--key-rule-identifier", kwargs["key_rule_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _policy_list_key_rules(self, **kwargs):
        """List key rules in a policy."""
        args = ["cte", "policies", "list-key-rules"]
        args.extend(["--cte-policy-identifier", kwargs["cte_policy_identifier"]])
        args.extend(["--limit", str(kwargs.get("limit", 10))])
        args.extend(["--skip", str(kwargs.get("skip", 0))])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _policy_modify_key_rule(self, **kwargs):
        """Modify a key rule in a policy."""
        args = ["cte", "policies", "modify-key-rules"]
        args.extend(["--cte-policy-identifier", kwargs["cte_policy_identifier"]])
        args.extend(["--key-rule-identifier", kwargs["key_rule_identifier"]])
        
        if kwargs.get("key_identifier"):
            args.extend(["--key-identifier", kwargs["key_identifier"]])
        if kwargs.get("key_type"):
            args.extend(["--key-type", kwargs["key_type"]])
        if kwargs.get("order_number") is not None:
            args.extend(["--order-number", str(kwargs["order_number"])])
        if kwargs.get("resource_set_identifier"):
            args.extend(["--resource-set-identifier", kwargs["resource_set_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    # LDT Rule Operations
    
    def _policy_add_ldt_rule(self, **kwargs):
        """Add an LDT rule to a policy."""
        args = ["cte", "policies", "add-ldt-rules"]
        args.extend(["--cte-policy-identifier", kwargs["cte_policy_identifier"]])
        args.extend(["--current-key-json-file", kwargs["current_key_json_file"]])
        args.extend(["--transform-key-json-file", kwargs["transform_key_json_file"]])
        
        if kwargs.get("resource_set_identifier"):
            args.extend(["--resource-set-identifier", kwargs["resource_set_identifier"]])
        if kwargs.get("is_exclusion_rule"):
            args.append("--is-exclusion-rule")
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _policy_delete_ldt_rule(self, **kwargs):
        """Delete an LDT rule from a policy."""
        args = ["cte", "policies", "delete-ldt-rules"]
        args.extend(["--cte-policy-identifier", kwargs["cte_policy_identifier"]])
        args.extend(["--ldt-rule-identifier", kwargs["ldt_rule_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _policy_get_ldt_rule(self, **kwargs):
        """Get an LDT rule from a policy."""
        args = ["cte", "policies", "get-ldt-rules"]
        args.extend(["--cte-policy-identifier", kwargs["cte_policy_identifier"]])
        args.extend(["--ldt-rule-identifier", kwargs["ldt_rule_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _policy_list_ldt_rules(self, **kwargs):
        """List LDT rules in a policy."""
        args = ["cte", "policies", "list-ldt-rules"]
        args.extend(["--cte-policy-identifier", kwargs["cte_policy_identifier"]])
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _policy_modify_ldt_rule(self, **kwargs):
        """Modify an LDT rule in a policy."""
        args = ["cte", "policies", "modify-ldt-rules"]
        args.extend(["--cte-policy-identifier", kwargs["cte_policy_identifier"]])
        args.extend(["--ldt-rule-identifier", kwargs["ldt_rule_identifier"]])
        
        if kwargs.get("current_key_json_file"):
            args.extend(["--current-key-json-file", kwargs["current_key_json_file"]])
        if kwargs.get("transform_key_json_file"):
            args.extend(["--transform-key-json-file", kwargs["transform_key_json_file"]])
        if kwargs.get("order_number") is not None:
            args.extend(["--order-number", str(kwargs["order_number"])])
        if kwargs.get("resource_set_identifier"):
            args.extend(["--resource-set-identifier", kwargs["resource_set_identifier"]])
        if kwargs.get("is_exclusion_rule") is not None:
            args.append("--is-exclusion-rule" if kwargs["is_exclusion_rule"] else "--no-is-exclusion-rule")
        
        result = self.execute_with_domain(args, kwargs.get("domain"), kwargs.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))