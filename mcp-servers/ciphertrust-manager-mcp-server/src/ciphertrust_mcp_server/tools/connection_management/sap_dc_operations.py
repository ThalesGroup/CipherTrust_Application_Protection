"""SAP DC connection operations for Connection Management."""

from typing import Any, Dict, List
from .base import ConnectionOperations
from .constants import SAP_DC_PARAMETERS, CONNECTION_OPERATIONS


class SAPDCOperations(ConnectionOperations):
    """SAP DC connection operations for Connection Management."""
    
    def get_operations(self) -> List[str]:
        """Return list of supported SAP DC operations."""
        return CONNECTION_OPERATIONS["sap_dc"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for SAP DC operations."""
        return {
            "sap_dc_params": {
                "type": "object",
                "properties": SAP_DC_PARAMETERS,
                "description": "SAP DC-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for SAP DC."""
        return {
            "create": {
                "required": ["name"],
                "optional": ["clientid", "secret", "tenant_id", "endpoint_url", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
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
                "optional": ["name", "clientid", "secret", "tenant_id", "endpoint_url", "products", "description", "meta", "labels", "json_file", "domain", "auth_domain"]
            },
            "test": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute SAP DC connection operation."""
        sap_dc_params = params.get("sap_dc_params", {})
        
        # Build base command
        cmd = ["connectionmgmt", "sap-dc", action]
        
        # Add action-specific parameters
        if action == "create":
            if sap_dc_params.get("name"):
                cmd.extend(["--name", sap_dc_params["name"]])
            if sap_dc_params.get("clientid"):
                cmd.extend(["--clientid", sap_dc_params["clientid"]])
            if sap_dc_params.get("secret"):
                cmd.extend(["--secret", sap_dc_params["secret"]])
            if sap_dc_params.get("tenant_id"):
                cmd.extend(["--tenant-id", sap_dc_params["tenant_id"]])
            if sap_dc_params.get("endpoint_url"):
                cmd.extend(["--endpoint-url", sap_dc_params["endpoint_url"]])
            if sap_dc_params.get("products"):
                cmd.extend(["--products", sap_dc_params["products"]])
            if sap_dc_params.get("description"):
                cmd.extend(["--description", sap_dc_params["description"]])
            if sap_dc_params.get("meta"):
                cmd.extend(["--meta", sap_dc_params["meta"]])
            if sap_dc_params.get("labels"):
                cmd.extend(["--labels", sap_dc_params["labels"]])
            if sap_dc_params.get("json_file"):
                cmd.extend(["--json-file", sap_dc_params["json_file"]])
                
        elif action == "list":
            if sap_dc_params.get("name"):
                cmd.extend(["--name", sap_dc_params["name"]])
            if sap_dc_params.get("cloudname"):
                cmd.extend(["--cloudname", sap_dc_params["cloudname"]])
            if sap_dc_params.get("category"):
                cmd.extend(["--category", sap_dc_params["category"]])
            if sap_dc_params.get("products"):
                cmd.extend(["--products", sap_dc_params["products"]])
            if sap_dc_params.get("limit"):
                cmd.extend(["--limit", str(sap_dc_params["limit"])])
            if sap_dc_params.get("skip"):
                cmd.extend(["--skip", str(sap_dc_params["skip"])])
            if sap_dc_params.get("fields"):
                cmd.extend(["--fields", sap_dc_params["fields"]])
            if sap_dc_params.get("labels_query"):
                cmd.extend(["--labels-query", sap_dc_params["labels_query"]])
            if sap_dc_params.get("lastconnectionafter"):
                cmd.extend(["--lastconnectionafter", sap_dc_params["lastconnectionafter"]])
            if sap_dc_params.get("lastconnectionbefore"):
                cmd.extend(["--lastconnectionbefore", sap_dc_params["lastconnectionbefore"]])
            if sap_dc_params.get("lastconnectionok"):
                cmd.extend(["--lastconnectionok", sap_dc_params["lastconnectionok"]])
                
        elif action == "get":
            cmd.extend(["--id", sap_dc_params["id"]])
            
        elif action == "delete":
            cmd.extend(["--id", sap_dc_params["id"]])
            if sap_dc_params.get("force"):
                cmd.append("--force")
                
        elif action == "modify":
            cmd.extend(["--id", sap_dc_params["id"]])
            if sap_dc_params.get("name"):
                cmd.extend(["--name", sap_dc_params["name"]])
            if sap_dc_params.get("clientid"):
                cmd.extend(["--clientid", sap_dc_params["clientid"]])
            if sap_dc_params.get("secret"):
                cmd.extend(["--secret", sap_dc_params["secret"]])
            if sap_dc_params.get("tenant_id"):
                cmd.extend(["--tenant-id", sap_dc_params["tenant_id"]])
            if sap_dc_params.get("endpoint_url"):
                cmd.extend(["--endpoint-url", sap_dc_params["endpoint_url"]])
            if sap_dc_params.get("products"):
                cmd.extend(["--products", sap_dc_params["products"]])
            if sap_dc_params.get("description"):
                cmd.extend(["--description", sap_dc_params["description"]])
            if sap_dc_params.get("meta"):
                cmd.extend(["--meta", sap_dc_params["meta"]])
            if sap_dc_params.get("labels"):
                cmd.extend(["--labels", sap_dc_params["labels"]])
            if sap_dc_params.get("json_file"):
                cmd.extend(["--json-file", sap_dc_params["json_file"]])
                
        elif action == "test":
            cmd.extend(["--id", sap_dc_params["id"]])
            
        else:
            raise ValueError(f"Unsupported SAP DC action: {action}")
        
        # Execute command
        result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", "")) 