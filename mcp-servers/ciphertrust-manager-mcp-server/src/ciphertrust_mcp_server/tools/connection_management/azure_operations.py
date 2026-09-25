"""Azure connection operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import AZURE_PARAMETERS, CONNECTION_OPERATIONS


class AzureOperations(ConnectionOperations):
    """Azure connection operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported Azure operations."""
        return CONNECTION_OPERATIONS["azure"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for Azure operations."""
        return {
            "azure_params": {
                "type": "object",
                "properties": AZURE_PARAMETERS,
                "description": "Azure-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for Azure."""
        return {
            "create": {
                "required": ["name"],
                "optional": ["clientid", "secret", "tenantid", "use_certificate", "certificate", "certificate_file", "certificate_duration", "connection_type", "active_dir_endpoint", "management_url", "res_manager_url", "key_vault_dns_suffix", "vault_res_url", "server_cert_file", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "list": {
                "required": [],
                "optional": ["name", "cloudname", "category", "products", "limit", "skip", "fields", "labels_query", "lastconnectionafter", "lastconnectionbefore", "lastconnectionok", "domain", "auth_domain"]
            },
            "get": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "delete": {
                "required": ["id"],
                "optional": ["force", "domain", "auth_domain"]
            },
            "modify": {
                "required": ["id"],
                "optional": ["name", "clientid", "secret", "tenantid", "use_certificate", "certificate", "certificate_file", "certificate_duration", "connection_type", "active_dir_endpoint", "management_url", "res_manager_url", "key_vault_dns_suffix", "vault_res_url", "server_cert_file", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "test": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute Azure connection operation."""
        azure_params = params.get("azure_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "azure", action]
        
        # Add action-specific parameters
        if action == "create":
            if azure_params.get("name"):
                cmd.extend(["--name", azure_params["name"]])
            if azure_params.get("clientid"):
                cmd.extend(["--clientid", azure_params["clientid"]])
            if azure_params.get("secret"):
                cmd.extend(["--secret", azure_params["secret"]])
            if azure_params.get("tenantid"):
                cmd.extend(["--tenantid", azure_params["tenantid"]])
            if azure_params.get("use_certificate"):
                cmd.extend(["--use-certificate", azure_params["use_certificate"]])
            if azure_params.get("certificate"):
                cmd.extend(["--certificate", azure_params["certificate"]])
            if azure_params.get("certificate_file"):
                cmd.extend(["--certificate-file", azure_params["certificate_file"]])
            if azure_params.get("certificate_duration"):
                cmd.extend(["--certificate-duration", str(azure_params["certificate_duration"])])
            if azure_params.get("connection_type"):
                cmd.extend(["--connection-type", azure_params["connection_type"]])
            if azure_params.get("active_dir_endpoint"):
                cmd.extend(["--active-dir-endpoint", azure_params["active_dir_endpoint"]])
            if azure_params.get("management_url"):
                cmd.extend(["--management-url", azure_params["management_url"]])
            if azure_params.get("res_manager_url"):
                cmd.extend(["--res-manager-url", azure_params["res_manager_url"]])
            if azure_params.get("key_vault_dns_suffix"):
                cmd.extend(["--key-vault-dns-suffix", azure_params["key_vault_dns_suffix"]])
            if azure_params.get("vault_res_url"):
                cmd.extend(["--vault-res-url", azure_params["vault_res_url"]])
            if azure_params.get("server_cert_file"):
                cmd.extend(["--server-cert-file", azure_params["server_cert_file"]])
            if azure_params.get("products"):
                cmd.extend(["--products", azure_params["products"]])
            if azure_params.get("description"):
                cmd.extend(["--description", azure_params["description"]])
            if azure_params.get("meta"):
                cmd.extend(["--meta", azure_params["meta"]])
            if azure_params.get("labels"):
                cmd.extend(["--labels", azure_params["labels"]])
            if azure_params.get("json_file"):
                cmd.extend(["--json-file", azure_params["json_file"]])
                
        elif action == "list":
            if azure_params.get("name"):
                cmd.extend(["--name", azure_params["name"]])
            if azure_params.get("cloudname"):
                cmd.extend(["--cloudname", azure_params["cloudname"]])
            if azure_params.get("category"):
                cmd.extend(["--category", azure_params["category"]])
            if azure_params.get("products"):
                cmd.extend(["--products", azure_params["products"]])
            if azure_params.get("limit"):
                cmd.extend(["--limit", str(azure_params["limit"])])
            if azure_params.get("skip"):
                cmd.extend(["--skip", str(azure_params["skip"])])
            if azure_params.get("fields"):
                cmd.extend(["--fields", azure_params["fields"]])
            if azure_params.get("labels_query"):
                cmd.extend(["--labels-query", azure_params["labels_query"]])
            if azure_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", azure_params["lastconnectionafter"]])
            if azure_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", azure_params["lastconnectionbefore"]])
            if azure_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", azure_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", azure_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", azure_params["id"]])
            if azure_params.get("force"):
                cmd.append("--force")
                
        elif action == "modify":
            cmd.extend(["--id", azure_params["id"]])
            if azure_params.get("name"):
                cmd.extend(["--name", azure_params["name"]])
            if azure_params.get("clientid"):
                cmd.extend(["--clientid", azure_params["clientid"]])
            if azure_params.get("secret"):
                cmd.extend(["--secret", azure_params["secret"]])
            if azure_params.get("tenantid"):
                cmd.extend(["--tenantid", azure_params["tenantid"]])
            if azure_params.get("use_certificate"):
                cmd.extend(["--use-certificate", azure_params["use_certificate"]])
            if azure_params.get("certificate"):
                cmd.extend(["--certificate", azure_params["certificate"]])
            if azure_params.get("certificate_file"):
                cmd.extend(["--certificate-file", azure_params["certificate_file"]])
            if azure_params.get("certificate_duration"):
                cmd.extend(["--certificate-duration", str(azure_params["certificate_duration"])])
            if azure_params.get("connection_type"):
                cmd.extend(["--connection-type", azure_params["connection_type"]])
            if azure_params.get("active_dir_endpoint"):
                cmd.extend(["--active-dir-endpoint", azure_params["active_dir_endpoint"]])
            if azure_params.get("management_url"):
                cmd.extend(["--management-url", azure_params["management_url"]])
            if azure_params.get("res_manager_url"):
                cmd.extend(["--res-manager-url", azure_params["res_manager_url"]])
            if azure_params.get("key_vault_dns_suffix"):
                cmd.extend(["--key-vault-dns-suffix", azure_params["key_vault_dns_suffix"]])
            if azure_params.get("vault_res_url"):
                cmd.extend(["--vault-res-url", azure_params["vault_res_url"]])
            if azure_params.get("server_cert_file"):
                cmd.extend(["--server-cert-file", azure_params["server_cert_file"]])
            if azure_params.get("products"):
                cmd.extend(["--products", azure_params["products"]])
            if azure_params.get("description"):
                cmd.extend(["--description", azure_params["description"]])
            if azure_params.get("meta"):
                cmd.extend(["--meta", azure_params["meta"]])
            if azure_params.get("labels"):
                cmd.extend(["--labels", azure_params["labels"]])
            if azure_params.get("json_file"):
                cmd.extend(["--json-file", azure_params["json_file"]])
                
        elif action == "test":
            cmd.extend(["--id", azure_params["id"]])
            
        else:
            raise ValueError(f"Unsupported Azure action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 