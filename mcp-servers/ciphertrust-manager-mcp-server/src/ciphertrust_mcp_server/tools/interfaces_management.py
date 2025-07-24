from typing import Optional
from pydantic import BaseModel
from .base import BaseTool

class InterfacesListParams(BaseModel):
    limit: Optional[int] = None
    skip: Optional[int] = None

class InterfacesGetParams(BaseModel):
    name: str

class InterfacesCreateParams(BaseModel):
    type: str
    port: int
    name: Optional[str] = None
    network_interface: Optional[str] = None
    mode: Optional[str] = None
    max_tls_version: Optional[str] = None
    tlsversion: Optional[str] = None
    default_connection: Optional[str] = None
    autoregistration: Optional[str] = None
    cert_user_field: Optional[str] = None
    allow_unregistered: Optional[str] = None
    auto_gen_ca_id: Optional[str] = None
    auto_gen_days_before_exp: Optional[int] = None
    kmip_enable_hard_delete: Optional[str] = None
    mask_system_groups: Optional[str] = None
    custom_uid_size: Optional[int] = None
    custom_uid_v2: Optional[str] = None
    trusted_external_cas: Optional[str] = None
    trusted_local_cas: Optional[str] = None
    ifaceRegToken: Optional[str] = None

class InterfacesDeleteParams(BaseModel):
    name: str

class InterfacesEnableParams(BaseModel):
    name: str

class InterfacesDisableParams(BaseModel):
    name: str

class InterfacesModifyParams(BaseModel):
    name: str
    port: Optional[int] = None
    mode: Optional[str] = None
    max_tls_version: Optional[str] = None
    tlsversion: Optional[str] = None
    default_connection: Optional[str] = None
    autoregistration: Optional[str] = None
    cert_user_field: Optional[str] = None
    allow_unregistered: Optional[str] = None
    auto_gen_ca_id: Optional[str] = None
    auto_gen_days_before_exp: Optional[int] = None
    kmip_enable_hard_delete: Optional[str] = None
    mask_system_groups: Optional[str] = None
    custom_uid_size: Optional[int] = None
    custom_uid_v2: Optional[str] = None
    trusted_external_cas: Optional[str] = None
    trusted_local_cas: Optional[str] = None
    ifaceRegToken: Optional[str] = None

class InterfacesManagementTool(BaseTool):
    name = "interfaces_management"
    description = "Manage CipherTrust Manager interfaces (web, kmip, ssh, nae, etc.)."

    def get_schema(self):
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": [
                    "list", "get", "create", "delete", "enable", "disable", "modify"
                ]},
                "name": {"type": "string", "nullable": True},
                "type": {"type": "string", "nullable": True},
                "port": {"type": "integer", "nullable": True},
                "network_interface": {"type": "string", "nullable": True},
                "mode": {"type": "string", "nullable": True},
                "max_tls_version": {"type": "string", "nullable": True},
                "tlsversion": {"type": "string", "nullable": True},
                "default_connection": {"type": "string", "nullable": True},
                "autoregistration": {"type": "string", "nullable": True},
                "cert_user_field": {"type": "string", "nullable": True},
                "allow_unregistered": {"type": "string", "nullable": True},
                "auto_gen_ca_id": {"type": "string", "nullable": True},
                "auto_gen_days_before_exp": {"type": "integer", "nullable": True},
                "kmip_enable_hard_delete": {"type": "string", "nullable": True},
                "mask_system_groups": {"type": "string", "nullable": True},
                "custom_uid_size": {"type": "integer", "nullable": True},
                "custom_uid_v2": {"type": "string", "nullable": True},
                "trusted_external_cas": {"type": "string", "nullable": True},
                "trusted_local_cas": {"type": "string", "nullable": True},
                "ifaceRegToken": {"type": "string", "nullable": True},
            },
            "required": ["action"],
        }

    async def execute(self, **kwargs):
        action = kwargs.get("action")
        if action == "list":
            params = InterfacesListParams(**kwargs)
            cmd = ["interfaces", "list"]
            if params.limit is not None:
                cmd += ["--limit", str(params.limit)]
            if params.skip is not None:
                cmd += ["--skip", str(params.skip)]
            return self.execute_command(cmd)
        elif action == "get":
            params = InterfacesGetParams(**kwargs)
            cmd = ["interfaces", "get", "--name", params.name]
            return self.execute_command(cmd)
        elif action == "create":
            params = InterfacesCreateParams(**kwargs)
            cmd = ["interfaces", "create", "--type", params.type, "--port", str(params.port)]
            if params.name:
                cmd += ["--name", params.name]
            if params.network_interface:
                cmd += ["--network-interface", params.network_interface]
            if params.mode:
                cmd += ["--mode", params.mode]
            if params.max_tls_version:
                cmd += ["--max-tls-version", params.max_tls_version]
            if params.tlsversion:
                cmd += ["--tlsversion", params.tlsversion]
            if params.default_connection:
                cmd += ["--default-connection", params.default_connection]
            if params.autoregistration:
                cmd += ["--autoregistration", params.autoregistration]
            if params.cert_user_field:
                cmd += ["--cert-user-field", params.cert_user_field]
            if params.allow_unregistered:
                cmd += ["--allow-unregistered", params.allow_unregistered]
            if params.auto_gen_ca_id:
                cmd += ["--auto-gen-ca-id", params.auto_gen_ca_id]
            if params.auto_gen_days_before_exp is not None:
                cmd += ["--auto-gen-days-before-exp", str(params.auto_gen_days_before_exp)]
            if params.kmip_enable_hard_delete:
                cmd += ["--kmip-enable-hard-delete", params.kmip_enable_hard_delete]
            if params.mask_system_groups:
                cmd += ["--mask-system-groups", params.mask_system_groups]
            if params.custom_uid_size is not None:
                cmd += ["--custom-uid-size", str(params.custom_uid_size)]
            if params.custom_uid_v2:
                cmd += ["--custom-uid-v2", params.custom_uid_v2]
            if params.trusted_external_cas:
                cmd += ["--trusted-external-cas", params.trusted_external_cas]
            if params.trusted_local_cas:
                cmd += ["--trusted-local-cas", params.trusted_local_cas]
            if params.ifaceRegToken:
                cmd += ["--ifaceRegToken", params.ifaceRegToken]
            return self.execute_command(cmd)
        elif action == "delete":
            params = InterfacesDeleteParams(**kwargs)
            cmd = ["interfaces", "delete", "--name", params.name]
            return self.execute_command(cmd)
        elif action == "enable":
            params = InterfacesEnableParams(**kwargs)
            cmd = ["interfaces", "enable", "--name", params.name]
            return self.execute_command(cmd)
        elif action == "disable":
            params = InterfacesDisableParams(**kwargs)
            cmd = ["interfaces", "disable", "--name", params.name]
            return self.execute_command(cmd)
        elif action == "modify":
            params = InterfacesModifyParams(**kwargs)
            cmd = ["interfaces", "modify", "--name", params.name]
            if params.port is not None:
                cmd += ["--port", str(params.port)]
            if params.mode:
                cmd += ["--mode", params.mode]
            if params.max_tls_version:
                cmd += ["--max-tls-version", params.max_tls_version]
            if params.tlsversion:
                cmd += ["--tlsversion", params.tlsversion]
            if params.default_connection:
                cmd += ["--default-connection", params.default_connection]
            if params.autoregistration:
                cmd += ["--autoregistration", params.autoregistration]
            if params.cert_user_field:
                cmd += ["--cert-user-field", params.cert_user_field]
            if params.allow_unregistered:
                cmd += ["--allow-unregistered", params.allow_unregistered]
            if params.auto_gen_ca_id:
                cmd += ["--auto-gen-ca-id", params.auto_gen_ca_id]
            if params.auto_gen_days_before_exp is not None:
                cmd += ["--auto-gen-days-before-exp", str(params.auto_gen_days_before_exp)]
            if params.kmip_enable_hard_delete:
                cmd += ["--kmip-enable-hard-delete", params.kmip_enable_hard_delete]
            if params.mask_system_groups:
                cmd += ["--mask-system-groups", params.mask_system_groups]
            if params.custom_uid_size is not None:
                cmd += ["--custom-uid-size", str(params.custom_uid_size)]
            if params.custom_uid_v2:
                cmd += ["--custom-uid-v2", params.custom_uid_v2]
            if params.trusted_external_cas:
                cmd += ["--trusted-external-cas", params.trusted_external_cas]
            if params.trusted_local_cas:
                cmd += ["--trusted-local-cas", params.trusted_local_cas]
            if params.ifaceRegToken:
                cmd += ["--ifaceRegToken", params.ifaceRegToken]
            return self.execute_command(cmd)
        else:
            return f"Unknown action: {action}"

INTERFACES_MANAGEMENT_TOOLS = [InterfacesManagementTool] 