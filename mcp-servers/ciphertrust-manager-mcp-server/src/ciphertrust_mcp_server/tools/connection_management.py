"""Connection Management tools for CipherTrust Manager."""

from typing import Any, Dict
import json

from .base import BaseTool


class ConnectionManagementTool(BaseTool):
    name = "connection_management"
    description = "Connection management operations (list, delete, aws_create, aws_list, aws_get, aws_delete, aws_modify, aws_test, azure_create, azure_list, azure_get, azure_delete, azure_modify, azure_test, gcp_create, gcp_list, gcp_get, gcp_delete, gcp_modify, gcp_test, oci_create, oci_list, oci_get, oci_delete, oci_modify, oci_test, salesforce_create, salesforce_list, salesforce_get, salesforce_delete, salesforce_modify, salesforce_test, akeyless_create, akeyless_list, akeyless_get, akeyless_delete, akeyless_modify, akeyless_test)"

    def get_schema(self) -> dict:
        # For brevity, merge all param schemas
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": [
                    "list", "delete",
                    "aws_create", "aws_list", "aws_get", "aws_delete", "aws_modify", "aws_test",
                    "azure_create", "azure_list", "azure_get", "azure_delete", "azure_modify", "azure_test",
                    "gcp_create", "gcp_list", "gcp_get", "gcp_delete", "gcp_modify", "gcp_test",
                    "oci_create", "oci_list", "oci_get", "oci_delete", "oci_modify", "oci_test",
                    "salesforce_create", "salesforce_list", "salesforce_get", "salesforce_delete", "salesforce_modify", "salesforce_test",
                    "akeyless_create", "akeyless_list", "akeyless_get", "akeyless_delete", "akeyless_modify", "akeyless_test"
                ]},
                # ... merge all properties from all param schemas ...
            },
            "required": ["action"],
        }
    
    async def execute(self, **kwargs: Any) -> Any:
        action = kwargs.get("action")
        
        if action == "list":
            cmd = ["connection_management", "list"]
            if kwargs.get("name"):
                cmd.extend(["--name", kwargs["name"]])
            if kwargs.get("category"):
                cmd.extend(["--category", kwargs["category"]])
            if kwargs.get("cloudname"):
                cmd.extend(["--cloudname", kwargs["cloudname"]])
            if kwargs.get("products"):
                cmd.extend(["--products", kwargs["products"]])
            cmd.extend(["--limit", str(kwargs.get("limit", 10))])
            cmd.extend(["--skip", str(kwargs.get("skip", 0))])
            return self.ksctl.execute(cmd)
        
        elif action == "delete":
            cmd = ["connection_management", "delete", "--id", kwargs["id"]]
            if kwargs.get("force", False):
                cmd.append("--force")
            return self.ksctl.execute(cmd)
        
        # Cloud provider actions
        elif action.startswith("aws_"):
            subaction = action[4:]
            cmd = ["connection_management", "aws", subaction]
            if subaction in ("create", "modify"):
                if kwargs.get("name"):
                    cmd.extend(["--name", kwargs["name"]])
                if kwargs.get("access_key"):
                    cmd.extend(["--access-key", kwargs["access_key"]])
                if kwargs.get("secret_key"):
                    cmd.extend(["--secret-key", kwargs["secret_key"]])
                if kwargs.get("region"):
                    cmd.extend(["--region", kwargs["region"]])
                if kwargs.get("session_token"):
                    cmd.extend(["--session-token", kwargs["session_token"]])
            elif subaction in ("get", "delete", "test"):
                cmd.extend(["--id", kwargs["id"]])
            return self.ksctl.execute(cmd)
        elif action.startswith("azure_"):
            subaction = action[6:]
            cmd = ["connection_management", "azure", subaction]
            if subaction in ("create", "modify"):
                if kwargs.get("name"):
                    cmd.extend(["--name", kwargs["name"]])
                if kwargs.get("client_id"):
                    cmd.extend(["--client-id", kwargs["client_id"]])
                if kwargs.get("client_secret"):
                    cmd.extend(["--client-secret", kwargs["client_secret"]])
                if kwargs.get("tenant_id"):
                    cmd.extend(["--tenant-id", kwargs["tenant_id"]])
                if kwargs.get("subscription_id"):
                    cmd.extend(["--subscription-id", kwargs["subscription_id"]])
            elif subaction in ("get", "delete", "test"):
                cmd.extend(["--id", kwargs["id"]])
            return self.ksctl.execute(cmd)
        elif action.startswith("gcp_"):
            subaction = action[4:]
            cmd = ["connection_management", "gcp", subaction]
            if subaction in ("create", "modify"):
                if kwargs.get("name"):
                    cmd.extend(["--name", kwargs["name"]])
                if kwargs.get("project_id"):
                    cmd.extend(["--project-id", kwargs["project_id"]])
                if kwargs.get("credentials_json"):
                    cmd.extend(["--credentials-json", kwargs["credentials_json"]])
            elif subaction in ("get", "delete", "test"):
                cmd.extend(["--id", kwargs["id"]])
            return self.ksctl.execute(cmd)
        elif action.startswith("oci_"):
            subaction = action[4:]
            cmd = ["connection_management", "oci", subaction]
            if subaction in ("create", "modify"):
                if kwargs.get("name"):
                    cmd.extend(["--name", kwargs["name"]])
                if kwargs.get("tenancy_ocid"):
                    cmd.extend(["--tenancy-ocid", kwargs["tenancy_ocid"]])
                if kwargs.get("user_ocid"):
                    cmd.extend(["--user-ocid", kwargs["user_ocid"]])
                if kwargs.get("fingerprint"):
                    cmd.extend(["--fingerprint", kwargs["fingerprint"]])
                if kwargs.get("private_key"):
                    cmd.extend(["--private-key", kwargs["private_key"]])
                if kwargs.get("region"):
                    cmd.extend(["--region", kwargs["region"]])
            elif subaction in ("get", "delete", "test"):
                cmd.extend(["--id", kwargs["id"]])
            return self.ksctl.execute(cmd)
        elif action.startswith("salesforce_"):
            subaction = action[11:]
            cmd = ["connection_management", "salesforce", subaction]
            if subaction in ("create", "modify"):
                if kwargs.get("name"):
                    cmd.extend(["--name", kwargs["name"]])
                if kwargs.get("client_id"):
                    cmd.extend(["--client-id", kwargs["client_id"]])
                if kwargs.get("client_secret"):
                    cmd.extend(["--client-secret", kwargs["client_secret"]])
                if kwargs.get("username"):
                    cmd.extend(["--username", kwargs["username"]])
                if kwargs.get("password"):
                    cmd.extend(["--password", kwargs["password"]])
                if kwargs.get("security_token"):
                    cmd.extend(["--security-token", kwargs["security_token"]])
            elif subaction in ("get", "delete", "test"):
                cmd.extend(["--id", kwargs["id"]])
            return self.ksctl.execute(cmd)
        elif action.startswith("akeyless_"):
            subaction = action[9:]
            cmd = ["connection_management", "akeyless", subaction]
            if subaction in ("create", "modify"):
                if kwargs.get("name"):
                    cmd.extend(["--name", kwargs["name"]])
                if kwargs.get("access_id"):
                    cmd.extend(["--access-id", kwargs["access_id"]])
                if kwargs.get("access_key"):
                    cmd.extend(["--access-key", kwargs["access_key"]])
                if kwargs.get("api_url"):
                    cmd.extend(["--api-url", kwargs["api_url"]])
            elif subaction in ("get", "delete", "test"):
                cmd.extend(["--id", kwargs["id"]])
            return self.ksctl.execute(cmd)
        else:
            raise ValueError(f"Unknown action: {action}")

CONNECTION_TOOLS = [ConnectionManagementTool]
