"""Main Connection Management Tool."""

from typing import Any, Dict, List
from ..base import BaseTool
from .constants import COMMON_SCHEMA_PROPERTIES, CONNECTION_OPERATIONS
from .aws_operations import AWSOperations
from .azure_operations import AzureOperations
from .gcp_operations import GCPOperations
from .oci_operations import OCIOperations
from .salesforce_operations import SalesforceOperations
from .akeyless_operations import AkeylessOperations
from .hadoop_operations import HadoopOperations
from .luna_hsm_operations import LunaHSMOperations
from .smb_operations import SMBOperations
from .scp_operations import SCPOperations
from .sap_dc_operations import SAPDCOperations
from .log_forwarder_operations import LogForwarderOperations
from .confidential_computing_operations import ConfidentialComputingOperations
from .external_cm_operations import ExternalCMOperations
from .ldap_operations import LDAPOperations
from .oidc_operations import OIDCOperations
from .cm_operations import CMOperations
from .elasticsearch_log_forwarder_operations import ElasticsearchLogForwarderOperations
from .loki_log_forwarder_operations import LokiLogForwarderOperations
from .syslog_log_forwarder_operations import SyslogLogForwarderOperations
from .luna_hsm_server_operations import LunaHSMServerOperations
from .luna_hsm_stc_partition_operations import LunaHSMSTCPartitionOperations
from .hadoop_node_operations import HadoopNodeOperations
from .external_cm_node_operations import ExternalCMNodeOperations
from .external_cm_trusted_ca_operations import ExternalCMTrustedCAOperations
from .connections_csr_operations import ConnectionsCSROperations


class ConnectionManagementTool(BaseTool):
    """Unified Connection Management Tool that delegates to specialized cloud provider operations.
    
    This tool provides a single interface for all connection management operations while internally
    organizing functionality by cloud provider for better maintainability.
    """
    
    def __init__(self):
        super().__init__()
        # Initialize all cloud provider operations
        self.cloud_operations = {
            'aws': AWSOperations(self.execute_with_domain),
            'azure': AzureOperations(self.execute_with_domain),
            'gcp': GCPOperations(self.execute_with_domain),
            'oci': OCIOperations(self.execute_with_domain),
            'salesforce': SalesforceOperations(self.execute_with_domain),
            'akeyless': AkeylessOperations(self.execute_with_domain),
            'hadoop': HadoopOperations(self.execute_with_domain),
            'luna_hsm': LunaHSMOperations(self.execute_with_domain),
            'smb': SMBOperations(self.execute_with_domain),
            'scp': SCPOperations(self.execute_with_domain),
            'sap_dc': SAPDCOperations(self.execute_with_domain),
            'log_forwarder': LogForwarderOperations(self.execute_with_domain),
            'confidential_computing': ConfidentialComputingOperations(self.execute_with_domain),
            'external_cm': ExternalCMOperations(self.execute_with_domain),
            'ldap': LDAPOperations(self.execute_with_domain),
            'oidc': OIDCOperations(self.execute_with_domain),
            'cm': CMOperations(self.execute_with_domain),
            # New specialized operations
            'elasticsearch_log_forwarder': ElasticsearchLogForwarderOperations(self.execute_with_domain),
            'loki_log_forwarder': LokiLogForwarderOperations(self.execute_with_domain),
            'syslog_log_forwarder': SyslogLogForwarderOperations(self.execute_with_domain),
            'luna_hsm_server': LunaHSMServerOperations(self.execute_with_domain),
            'luna_hsm_stc_partition': LunaHSMSTCPartitionOperations(self.execute_with_domain),
            'hadoop_node': HadoopNodeOperations(self.execute_with_domain),
            'external_cm_node': ExternalCMNodeOperations(self.execute_with_domain),
            'external_cm_trusted_ca': ExternalCMTrustedCAOperations(self.execute_with_domain),
            'connections_csr': ConnectionsCSROperations(self.execute_with_domain),
        }
        
        # Build operation mapping
        self.operation_mapping = {}
        for cloud_provider, operations in self.cloud_operations.items():
            for operation in operations.get_operations():
                self.operation_mapping[f"{cloud_provider}_{operation}"] = (cloud_provider, operation)
        
        # Add general operations
        self.operation_mapping["list"] = ("general", "list")
        self.operation_mapping["delete"] = ("general", "delete")
    
    @property
    def name(self) -> str:
        return "connection_management"
    
    @property
    def description(self) -> str:
        return (
            "Connection Management operations for managing connections across various cloud providers and services. "
            "Supports AWS, Azure, GCP, OCI, Salesforce, Akeyless, Hadoop, Luna HSM, SMB, SCP, SAP Data Custodian, "
            "Log Forwarder (Elasticsearch, Loki, Syslog), Confidential Computing, External CM, LDAP, OIDC, and CM connections. "
            "Also supports specialized operations for Luna HSM servers and STC partitions, Hadoop nodes, External CM nodes and trusted CAs, "
            "and CSR generation. Each cloud provider has specific operations and parameters - see action_requirements in schema for details. "
            "IMPORTANT: Some connections require file paths for certificates, keys, or configuration files. "
            "File-requiring parameters include: GCP (key_file), AWS (iamroleanywhere), Azure (certificate_file, server_cert_file), "
            "Salesforce (certificate_file, tls_client_cert_with_private_key_file), Luna HSM (certificate_file, partitions_json_file), "
            "Hadoop (keytab_file, nodes_json_file), SCP (private_key_file), "
            "External CM (certificate_file, nodes_json_file), LDAP (certificate_file, root_ca_files), CM (certificate_file, client_cert_file), "
            "and all log forwarders (certificate_file). These parameters are clearly marked with 'REQUIRES FILE PATH' in their descriptions."
        )
    
    def get_schema(self) -> dict[str, Any]:
        """Build complete schema from all cloud providers"""
        # Collect all operations
        all_operations = []
        for cloud_provider, operations in self.cloud_operations.items():
            for operation in operations.get_operations():
                all_operations.append(f"{cloud_provider}_{operation}")
        
        # Add general operations
        all_operations.extend(["list", "delete"])
        
        # Start with common properties
        properties = {
            "action": {
                "type": "string",
                "enum": sorted(all_operations),
                "description": "The connection management operation to perform. Format: {cloud_provider}_{operation} (e.g., aws_list, azure_create) or general operations (list, delete)"
            },
            **COMMON_SCHEMA_PROPERTIES
        }
        
        # Add properties from each cloud provider
        for cloud_provider, operations in self.cloud_operations.items():
            properties.update(operations.get_schema_properties())
        
        # Collect action requirements from all cloud providers
        action_requirements = {}
        for cloud_provider, operations in self.cloud_operations.items():
            cloud_requirements = operations.get_action_requirements()
            for operation, requirements in cloud_requirements.items():
                action_requirements[f"{cloud_provider}_{operation}"] = requirements
        
        # Add general operation requirements
        action_requirements["list"] = {
            "required": [],
            "optional": ["name", "cloudname", "category", "products", "limit", "skip", "fields", "labels_query", "lastconnectionafter", "lastconnectionbefore", "lastconnectionok", "domain", "auth_domain"]
        }
        action_requirements["delete"] = {
            "required": ["id"],
            "optional": ["force", "domain", "auth_domain"]
        }
        
        return {
            "type": "object",
            "properties": properties,
            "required": ["action"],
            "additionalProperties": False,
            "action_requirements": action_requirements
        }
    
    async def execute(self, action: str, **kwargs: Any) -> Any:
        """Execute connection management operation by delegating to appropriate cloud provider."""
        # Parse action to get cloud provider and operation
        if action not in self.operation_mapping:
            return {"error": f"Unknown action: {action}. Available actions: {list(self.operation_mapping.keys())}"}
        
        cloud_provider, operation = self.operation_mapping[action]
        
        # Handle general operations
        if cloud_provider == "general":
            if operation == "list":
                return await self._execute_general_list(kwargs)
            elif operation == "delete":
                return await self._execute_general_delete(kwargs)
            else:
                return {"error": f"Unknown general operation: {operation}"}
        
        # Get the appropriate cloud operations handler
        if cloud_provider not in self.cloud_operations:
            return {"error": f"Cloud provider {cloud_provider} not implemented yet"}
        
        cloud_ops = self.cloud_operations[cloud_provider]
        
        # Validate action-specific requirements
        if not self._validate_action_params(action, kwargs):
            schema = self.get_schema()
            requirements = schema.get("action_requirements", {}).get(action, {})
            required_params = requirements.get("required", [])
            return {"error": f"Missing required parameters for {action}: {required_params}"}
        
        # Execute the operation
        try:
            return await cloud_ops.execute_operation(operation, kwargs)
        except Exception as e:
            return {"error": f"Failed to execute {action}: {str(e)}"}
    
    async def _execute_general_list(self, params: Dict[str, Any]) -> Any:
        """Execute general list operation."""
        cmd = ["connectionmgmt", "list"]
        
        if params.get("name"):
            cmd.extend(["--name", params["name"]])
        if params.get("cloudname"):
            cmd.extend(["--cloudname", params["cloudname"]])
        if params.get("category"):
            cmd.extend(["--category", params["category"]])
        if params.get("products"):
            cmd.extend(["--products", params["products"]])
        if params.get("limit"):
            cmd.extend(["--limit", str(params["limit"])])
        if params.get("skip"):
            cmd.extend(["--skip", str(params["skip"])])
        if params.get("fields"):
            cmd.extend(["--fields", params["fields"]])
        if params.get("labels_query"):
            cmd.extend(["--labels-query", params["labels_query"]])
        if params.get("lastconnectionafter"):
            cmd.extend(["--lastconnectionafter", params["lastconnectionafter"]])
        if params.get("lastconnectionbefore"):
            cmd.extend(["--lastconnectionbefore", params["lastconnectionbefore"]])
        if params.get("lastconnectionok"):
            cmd.extend(["--lastconnectionok", params["lastconnectionok"]])
        
        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    async def _execute_general_delete(self, params: Dict[str, Any]) -> Any:
        """Execute general delete operation."""
        cmd = ["connectionmgmt", "delete", "--id", params["id"]]
        
        if params.get("force"):
            cmd.append("--force")
        
        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))
    
    def _validate_action_params(self, action: str, params: dict) -> bool:
        """Validate that required parameters are present for the action."""
        schema = self.get_schema()
        requirements = schema.get("action_requirements", {}).get(action, {})
        required_params = requirements.get("required", [])
        
        # Get cloud provider and params
        cloud_provider = action.split("_")[0]
        cloud_params_key = f"{cloud_provider}_params"
        cloud_params = params.get(cloud_params_key, {})
        
        # Special handling for JSON file approach
        if cloud_params.get("json_file"):
            # When json_file is provided, only validate that json_file exists
            # Individual parameters are not required as they can be in the JSON file
            return True
        
        # Check if all required parameters are present
        for param in required_params:
            # Check in the main params and in cloud-specific params
            if param not in params and param not in cloud_params:
                return False
        
        return True 