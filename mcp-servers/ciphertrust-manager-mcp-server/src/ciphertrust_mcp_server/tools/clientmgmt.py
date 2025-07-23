from typing import Optional, Any
from pydantic import BaseModel, Field, ValidationError
from .base import BaseTool

# --- CLIENTS SUBCOMMANDS ---
class ClientListParams(BaseModel):
    ca_id: Optional[str] = Field(None, description="ID of the trusted Certificate Authority.")
    client_id: Optional[str] = Field(None, description="An identifier of registered CipherTrust Manager client.")
    client_meta_data: Optional[str] = Field(None, description="Filter the results by client_metadata fields.")
    client_mgmt_profile_id: Optional[str] = Field(None, description="ID of the Client Management Profile.")
    client_name: Optional[str] = Field(None, description="A friendly name of client to be registered.")
    limit: Optional[int] = Field(None, description="The maximum number of resources to return.")
    sha256_fingerprint: Optional[str] = Field(None, description="The SHA256 fingerprint of the client certificate.")
    skip: Optional[int] = Field(None, description="The index of the first resource to return.")
    state: Optional[str] = Field(None, description="The state of the client.")
    domain: Optional[str] = Field(None, description="The CipherTrust Manager Domain that the command will operate in.")
    auth_domain: Optional[str] = Field(None, description="The CipherTrust Manager domain where the user is authenticated.")

class ClientGetParams(BaseModel):
    client_id: str = Field(..., description="The unique identifier (ID) of the registered CipherTrust Manager client.")
    domain: Optional[str] = Field(None, description="The CipherTrust Manager Domain that the command will operate in.")
    auth_domain: Optional[str] = Field(None, description="The CipherTrust Manager domain where the user is authenticated.")

class ClientRegisterParams(BaseModel):
    reg_token: str = Field(..., description="The registration token for the client.")
    csr: Optional[str] = Field(None, description="CSR of the node.")
    cert_file: Optional[str] = Field(None, description="File containing certificate issued by a CA known to CipherTrust Manager.")
    client_type: Optional[str] = Field(None, description="CipherTrust Manager client type.")
    client_name: Optional[str] = Field(None, description="A friendly name of client to be registered.")
    cn: Optional[str] = Field(None, description="Common Name.")
    csrfile: Optional[str] = Field(None, description="File containing CSR of registering CipherTrust Manager client.")
    dns: Optional[str] = Field(None, description="DNS of the client.")
    do_not_modify_subject_dn: Optional[bool] = Field(None, description="Do not modify the subject DN.")
    email: Optional[str] = Field(None, description="Email of the client.")
    enc_alg: Optional[str] = Field(None, description="Encryption algorithm.")
    ips: Optional[str] = Field(None, description="IP addresses of the client.")
    names: Optional[str] = Field(None, description="Names of the client.")
    pass_: Optional[str] = Field(None, description="Password for the private key.")
    private_key_file: Optional[str] = Field(None, description="Private key file.")
    size: Optional[int] = Field(None, description="Size of the key.")
    subject_dn_field_to_modify: Optional[str] = Field(None, description="Subject DN field to modify.")
    domain: Optional[str] = Field(None, description="The CipherTrust Manager Domain that the command will operate in.")
    auth_domain: Optional[str] = Field(None, description="The CipherTrust Manager domain where the user is authenticated.")

class ClientDeleteParams(BaseModel):
    client_id: str = Field(..., description="The unique identifier (ID) of the client to delete.")
    nowarning: Optional[bool] = Field(None, description="Don't show warning messages.")
    domain: Optional[str] = Field(None, description="The CipherTrust Manager Domain that the command will operate in.")
    auth_domain: Optional[str] = Field(None, description="The CipherTrust Manager domain where the user is authenticated.")

class ClientRenewParams(BaseModel):
    client_id: str = Field(..., description="The unique identifier (ID) of the client to renew.")
    alg: Optional[str] = Field(None, description="Algorithm for the new certificate.")
    ca_id: Optional[str] = Field(None, description="ID of the trusted Certificate Authority.")
    cert_duration: Optional[int] = Field(None, description="Duration in days for which the CipherTrust Manager client certificate is valid.")
    clientcsr: Optional[str] = Field(None, description="CSR of the client.")
    cn: Optional[str] = Field(None, description="Common Name.")
    dns: Optional[str] = Field(None, description="DNS of the client.")
    do_not_modify_subject_dn: Optional[bool] = Field(None, description="Do not modify the subject DN.")
    email: Optional[str] = Field(None, description="Email of the client.")
    enc_alg: Optional[str] = Field(None, description="Encryption algorithm.")
    ext_cert: Optional[str] = Field(None, description="External certificate.")
    ips: Optional[str] = Field(None, description="IP addresses of the client.")
    names: Optional[str] = Field(None, description="Names of the client.")
    pass_: Optional[str] = Field(None, description="Password for the private key.")
    private_key_bytes: Optional[str] = Field(None, description="Private key in bytes.")
    private_key_file: Optional[str] = Field(None, description="Private key file.")
    size: Optional[int] = Field(None, description="Size of the key.")
    subject_dn_field_to_modify: Optional[str] = Field(None, description="Subject DN field to modify.")
    domain: Optional[str] = Field(None, description="The CipherTrust Manager Domain that the command will operate in.")
    auth_domain: Optional[str] = Field(None, description="The CipherTrust Manager domain where the user is authenticated.")

class ClientRevokeParams(BaseModel):
    client_id: str = Field(..., description="The unique identifier (ID) of the client to revoke.")
    revoke_reason: Optional[str] = Field(None, description="Reason for revocation.")
    domain: Optional[str] = Field(None, description="The CipherTrust Manager Domain that the command will operate in.")
    auth_domain: Optional[str] = Field(None, description="The CipherTrust Manager domain where the user is authenticated.")

class ClientSelfParams(BaseModel):
    domain: Optional[str] = Field(None, description="The CipherTrust Manager Domain that the command will operate in.")
    auth_domain: Optional[str] = Field(None, description="The CipherTrust Manager domain where the user is authenticated.")

# --- PROFILES SUBCOMMANDS ---
class ProfileCreateParams(BaseModel):
    name: str = Field(..., description="Name of the client management profile.")
    ca_id: Optional[str] = Field(None, description="ID of the trusted Certificate Authority.")
    cert_duration: Optional[int] = Field(None, description="Duration in days for which the client certificate is valid.")
    csr_params_jsonfile: Optional[str] = Field(None, description="JSON file containing the CSR parameters.")
    csr_parameters: Optional[str] = Field(None, description="CSR parameters as a JSON string.")
    groups: Optional[str] = Field(None, description="Comma-separated list of groups to associate with the profile.")
    domain: Optional[str] = Field(None, description="The CipherTrust Manager Domain that the command will operate in.")
    auth_domain: Optional[str] = Field(None, description="The CipherTrust Manager domain where the user is authenticated.")

class ProfileDeleteParams(BaseModel):
    profile_id: str = Field(..., description="The unique identifier (ID) of the profile to delete.")
    domain: Optional[str] = Field(None, description="The CipherTrust Manager Domain that the command will operate in.")
    auth_domain: Optional[str] = Field(None, description="The CipherTrust Manager domain where the user is authenticated.")

class ProfileGetParams(BaseModel):
    profile_id: str = Field(..., description="The unique identifier (ID) of the client profile.")
    domain: Optional[str] = Field(None, description="The CipherTrust Manager Domain that the command will operate in.")
    auth_domain: Optional[str] = Field(None, description="The CipherTrust Manager domain where the user is authenticated.")

class ProfileListParams(BaseModel):
    domain: Optional[str] = Field(None, description="The CipherTrust Manager Domain that the command will operate in.")
    auth_domain: Optional[str] = Field(None, description="The CipherTrust Manager domain where the user is authenticated.")

class ProfileUpdateParams(BaseModel):
    profile_id: str = Field(..., description="The unique identifier (ID) of the profile to update.")
    name: Optional[str] = Field(None, description="New name for the client management profile.")
    ca_id: Optional[str] = Field(None, description="New ID of the trusted Certificate Authority.")
    cert_duration: Optional[int] = Field(None, description="New duration in days for which the client certificate is valid.")
    csr_params_jsonfile: Optional[str] = Field(None, description="New JSON file containing the CSR parameters.")
    csr_parameters: Optional[str] = Field(None, description="New CSR parameters as a JSON string.")
    groups: Optional[str] = Field(None, description="New comma-separated list of groups to associate with the profile.")
    domain: Optional[str] = Field(None, description="The CipherTrust Manager Domain that the command will operate in.")
    auth_domain: Optional[str] = Field(None, description="The CipherTrust Manager domain where the user is authenticated.")

# --- REGISTRATION TOKENS SUBCOMMANDS ---
class RegistrationTokenCreateParams(BaseModel):
    ca_id: Optional[str] = Field(None, description="ID of the trusted Certificate Authority.")
    cert_duration: Optional[int] = Field(None, description="Duration in days for which the client certificate is valid.")
    client_mgmt_profile_id: Optional[str] = Field(None, description="ID of the Client Management Profile.")
    label: Optional[str] = Field(None, description="Label for the registration token.")
    life_time: Optional[str] = Field(None, description="Lifetime of the registration token.")
    max_clients: Optional[int] = Field(None, description="Maximum number of clients that can use this token.")
    name_prefix: Optional[str] = Field(None, description="Prefix for the name of the clients registered with this token.")
    domain: Optional[str] = Field(None, description="The CipherTrust Manager Domain that the command will operate in.")
    auth_domain: Optional[str] = Field(None, description="The CipherTrust Manager domain where the user is authenticated.")

class RegistrationTokenDeleteParams(BaseModel):
    token_id: str = Field(..., description="The unique identifier (ID) of the registration token to delete.")
    domain: Optional[str] = Field(None, description="The CipherTrust Manager Domain that the command will operate in.")
    auth_domain: Optional[str] = Field(None, description="The CipherTrust Manager domain where the user is authenticated.")

class RegistrationTokenGetParams(BaseModel):
    token_id: str = Field(..., description="The unique identifier (ID) for the registration token. This is required to get a specific token.")
    domain: Optional[str] = Field(None, description="The CipherTrust Manager Domain that the command will operate in.")
    auth_domain: Optional[str] = Field(None, description="The CipherTrust Manager domain where the user is authenticated.")

class RegistrationTokenListParams(BaseModel):
    ca_id: Optional[str] = Field(None, description="ID of the trusted Certificate Authority.")
    client_mgmt_profile_id: Optional[str] = Field(None, description="ID of the Client Management Profile.")
    label: Optional[str] = Field(None, description="Label for the registration token.")
    max_clients: Optional[int] = Field(None, description="Maximum number of clients that can use this token.")
    name_prefix: Optional[str] = Field(None, description="Prefix for the name of the clients registered with this token.")
    domain: Optional[str] = Field(None, description="The CipherTrust Manager Domain that the command will operate in.")
    auth_domain: Optional[str] = Field(None, description="The CipherTrust Manager domain where the user is authenticated.")

class RegistrationTokenUpdateParams(BaseModel):
    token_id: str = Field(..., description="The unique identifier (ID) of the registration token to update.")
    ca_id: Optional[str] = Field(None, description="New ID of the trusted Certificate Authority.")
    cert_duration: Optional[int] = Field(None, description="New duration in days for which the client certificate is valid.")
    client_mgmt_profile_id: Optional[str] = Field(None, description="New ID of the Client Management Profile.")
    label: Optional[str] = Field(None, description="New label for the registration token.")
    life_time: Optional[str] = Field(None, description="New lifetime of the registration token.")
    max_clients: Optional[int] = Field(None, description="New maximum number of clients that can use this token.")
    name_prefix: Optional[str] = Field(None, description="New prefix for the name of the clients registered with this token.")
    domain: Optional[str] = Field(None, description="The CipherTrust Manager Domain that the command will operate in.")
    auth_domain: Optional[str] = Field(None, description="The CipherTrust Manager domain where the user is authenticated.")

class RegistrationTokenWebcertFingerprintParams(BaseModel):
    domain: Optional[str] = Field(None, description="The CipherTrust Manager Domain that the command will operate in.")
    auth_domain: Optional[str] = Field(None, description="The CipherTrust Manager domain where the user is authenticated.")

class ClientMgmtTool(BaseTool):
    name = "clientmgmt"
    description = (
        "Manages CipherTrust Manager client operations. This tool wraps `ksctl clientmgmt` commands.\n\n"
        "Supported Operations:\n"
        "Clients: `clients_list`, `clients_get`, `clients_register`, `clients_delete`, `clients_renew`, `clients_revoke`, `clients_self`\n"
        "Profiles: `profiles_create`, `profiles_delete`, `profiles_get`, `profiles_list`, `profiles_update`\n"
        "Registration Tokens: `registration_tokens_create`, `registration_tokens_delete`, `registration_tokens_get`, `registration_tokens_list`, `registration_tokens_update`, `registration_tokens_webcert_fingerprint`"
    )

    def get_schema(self):
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "clients_list", "clients_get", "clients_register", "clients_delete", "clients_renew", "clients_revoke", "clients_self",
                        "profiles_create", "profiles_delete", "profiles_get", "profiles_list", "profiles_update",
                        "registration_tokens_create", "registration_tokens_delete", "registration_tokens_get", "registration_tokens_list", "registration_tokens_update", "registration_tokens_webcert_fingerprint"
                    ],
                    "description": (
                        "The specific action to perform. Actions are grouped by functionality:\n"
                        "- `clients_*`: Manage client registrations.\n"
                        "- `profiles_*`: Manage client profiles.\n"
                        "- `registration_tokens_*`: Manage client registration tokens."
                    )
                },
                "params": {
                    "type": "object",
                    "description": "A dictionary of parameters for the specified action. The required parameters depend on the selected action."
                }
            },
            "required": ["action"]
        }

    async def execute(self, **kwargs: Any) -> Any:
        """Execute the client management tool with the given parameters."""
        action = kwargs.get("action")
        params = kwargs.get("params", {})
        
        if not action:
            raise ValueError("Action is required")

        try:
            if action == "clients_list":
                p = ClientListParams(**params)
                cmd = ["clientmgmt", "clients", "list"]
                if p.ca_id: cmd += ["--ca-id", p.ca_id]
                if p.client_id: cmd += ["--client-id", p.client_id]
                if p.client_meta_data: cmd += ["--client-meta-data", p.client_meta_data]
                if p.client_mgmt_profile_id: cmd += ["--client-mgmt-profile-id", p.client_mgmt_profile_id]
                if p.client_name: cmd += ["--client-name", p.client_name]
                if p.limit is not None: cmd += ["--limit", str(p.limit)]
                if p.sha256_fingerprint: cmd += ["--sha256-fingerprint", p.sha256_fingerprint]
                if p.skip is not None: cmd += ["--skip", str(p.skip)]
                if p.state: cmd += ["--state", p.state]
                self.add_domain_auth_params(cmd, params)
                return self.ksctl.execute(cmd)
            elif action == "clients_get":
                p = ClientGetParams(**params)
                cmd = ["clientmgmt", "clients", "get", "--client-id", p.client_id]
                self.add_domain_auth_params(cmd, params)
                return self.ksctl.execute(cmd)
            elif action == "clients_register":
                p = ClientRegisterParams(**params)
                cmd = ["clientmgmt", "clients", "register", "--reg-token", p.reg_token]
                if p.csr: cmd += ["--csr", p.csr]
                if p.cert_file: cmd += ["--cert-file", p.cert_file]
                if p.client_type: cmd += ["--client-type", p.client_type]
                if p.client_name: cmd += ["--client-name", p.client_name]
                if p.cn: cmd += ["--cn", p.cn]
                if p.csrfile: cmd += ["--csrfile", p.csrfile]
                if p.dns: cmd += ["--dns", p.dns]
                if p.do_not_modify_subject_dn: cmd += ["--do-not-modify-subject-dn"]
                if p.email: cmd += ["--email", p.email]
                if p.enc_alg: cmd += ["--enc-alg", p.enc_alg]
                if p.ips: cmd += ["--ips", p.ips]
                if p.names: cmd += ["--names", p.names]
                if p.pass_: cmd += ["--pass", p.pass_]
                if p.private_key_file: cmd += ["--private-key-file", p.private_key_file]
                if p.size is not None: cmd += ["--size", str(p.size)]
                if p.subject_dn_field_to_modify: cmd += ["--subject-dn-field-to-modify", p.subject_dn_field_to_modify]
                self.add_domain_auth_params(cmd, params)
                return self.ksctl.execute(cmd)
            elif action == "clients_delete":
                p = ClientDeleteParams(**params)
                cmd = ["clientmgmt", "clients", "delete", "--client-id", p.client_id]
                if p.nowarning: cmd += ["--nowarning"]
                self.add_domain_auth_params(cmd, params)
                return self.ksctl.execute(cmd)
            elif action == "clients_renew":
                p = ClientRenewParams(**params)
                cmd = ["clientmgmt", "clients", "renew", "--client-id", p.client_id]
                if p.alg: cmd += ["--alg", p.alg]
                if p.ca_id: cmd += ["--ca-id", p.ca_id]
                if p.cert_duration is not None: cmd += ["--cert-duration", str(p.cert_duration)]
                if p.clientcsr: cmd += ["--clientcsr", p.clientcsr]
                if p.cn: cmd += ["--cn", p.cn]
                if p.dns: cmd += ["--dns", p.dns]
                if p.do_not_modify_subject_dn: cmd += ["--do-not-modify-subject-dn"]
                if p.email: cmd += ["--email", p.email]
                if p.enc_alg: cmd += ["--enc-alg", p.enc_alg]
                if p.ext_cert: cmd += ["--ext-cert", p.ext_cert]
                if p.ips: cmd += ["--ips", p.ips]
                if p.names: cmd += ["--names", p.names]
                if p.pass_: cmd += ["--pass", p.pass_]
                if p.private_key_bytes: cmd += ["--private-key-bytes", p.private_key_bytes]
                if p.private_key_file: cmd += ["--private-key-file", p.private_key_file]
                if p.size is not None: cmd += ["--size", str(p.size)]
                if p.subject_dn_field_to_modify: cmd += ["--subject-dn-field-to-modify", p.subject_dn_field_to_modify]
                self.add_domain_auth_params(cmd, params)
                return self.ksctl.execute(cmd)
            elif action == "clients_revoke":
                p = ClientRevokeParams(**params)
                cmd = ["clientmgmt", "clients", "revoke", "--client-id", p.client_id]
                if p.revoke_reason: cmd += ["--revoke-reason", p.revoke_reason]
                self.add_domain_auth_params(cmd, params)
                return self.ksctl.execute(cmd)
            elif action == "clients_self":
                cmd = ["clientmgmt", "clients", "self"]
                self.add_domain_auth_params(cmd, params)
                return self.ksctl.execute(cmd)
            # --- PROFILES ---
            elif action == "profiles_create":
                p = ProfileCreateParams(**params)
                cmd = ["clientmgmt", "profiles", "create", "--name", p.name]
                if p.ca_id: cmd += ["--ca-id", p.ca_id]
                if p.cert_duration is not None: cmd += ["--cert-duration", str(p.cert_duration)]
                if p.csr_params_jsonfile: cmd += ["--csr-params-jsonfile", p.csr_params_jsonfile]
                if p.csr_parameters: cmd += ["--csr-parameters", p.csr_parameters]
                if p.groups: cmd += ["--groups", p.groups]
                self.add_domain_auth_params(cmd, params)
                return self.ksctl.execute(cmd)
            elif action == "profiles_delete":
                p = ProfileDeleteParams(**params)
                cmd = ["clientmgmt", "profiles", "delete", "--profile-id", p.profile_id]
                self.add_domain_auth_params(cmd, params)
                return self.ksctl.execute(cmd)
            elif action == "profiles_get":
                p = ProfileGetParams(**params)
                cmd = ["clientmgmt", "profiles", "get", "--profile-id", p.profile_id]
                self.add_domain_auth_params(cmd, params)
                return self.ksctl.execute(cmd)
            elif action == "profiles_list":
                cmd = ["clientmgmt", "profiles", "list"]
                self.add_domain_auth_params(cmd, params)
                return self.ksctl.execute(cmd)
            elif action == "profiles_update":
                p = ProfileUpdateParams(**params)
                cmd = ["clientmgmt", "profiles", "update", "--profile-id", p.profile_id]
                if p.ca_id: cmd += ["--ca-id", p.ca_id]
                if p.cert_duration is not None: cmd += ["--cert-duration", str(p.cert_duration)]
                if p.csr_params_jsonfile: cmd += ["--csr-params-jsonfile", p.csr_params_jsonfile]
                if p.csr_parameters: cmd += ["--csr-parameters", p.csr_parameters]
                if p.groups: cmd += ["--groups", p.groups]
                if p.name: cmd += ["--name", p.name]
                self.add_domain_auth_params(cmd, params)
                return self.ksctl.execute(cmd)
            # --- REGISTRATION TOKENS ---
            elif action == "registration_tokens_create":
                p = RegistrationTokenCreateParams(**params)
                cmd = ["clientmgmt", "tokens", "create"]
                if p.ca_id: cmd += ["--ca-id", p.ca_id]
                if p.cert_duration is not None: cmd += ["--cert-duration", str(p.cert_duration)]
                if p.client_mgmt_profile_id: cmd += ["--client-mgmt-profile-id", p.client_mgmt_profile_id]
                if p.label: cmd += ["--label", p.label]
                if p.life_time: cmd += ["--life-time", p.life_time]
                if p.max_clients is not None: cmd += ["--max-clients", str(p.max_clients)]
                if p.name_prefix: cmd += ["--name-prefix", p.name_prefix]
                self.add_domain_auth_params(cmd, params)
                return self.ksctl.execute(cmd)
            elif action == "registration_tokens_delete":
                p = RegistrationTokenDeleteParams(**params)
                cmd = ["clientmgmt", "tokens", "delete", "--token-id", p.token_id]
                self.add_domain_auth_params(cmd, params)
                return self.ksctl.execute(cmd)
            elif action == "registration_tokens_get":
                p = RegistrationTokenGetParams(**params)
                cmd = ["clientmgmt", "tokens", "get", "--token-id", p.token_id]
                self.add_domain_auth_params(cmd, params)
                return self.ksctl.execute(cmd)
            elif action == "registration_tokens_list":
                p = RegistrationTokenListParams(**params)
                cmd = ["clientmgmt", "tokens", "list"]
                self.add_domain_auth_params(cmd, params)
                return self.ksctl.execute(cmd)
            elif action == "registration_tokens_update":
                p = RegistrationTokenUpdateParams(**params)
                cmd = ["clientmgmt", "tokens", "update", "--token-id", p.token_id]
                if p.ca_id: cmd += ["--ca-id", p.ca_id]
                if p.cert_duration is not None: cmd += ["--cert-duration", str(p.cert_duration)]
                if p.client_mgmt_profile_id: cmd += ["--client-mgmt-profile-id", p.client_mgmt_profile_id]
                if p.label: cmd += ["--label", p.label]
                if p.life_time: cmd += ["--life-time", p.life_time]
                if p.max_clients is not None: cmd += ["--max-clients", str(p.max_clients)]
                if p.name_prefix: cmd += ["--name-prefix", p.name_prefix]
                self.add_domain_auth_params(cmd, params)
                return self.ksctl.execute(cmd)
            elif action == "registration_tokens_webcert_fingerprint":
                p = RegistrationTokenWebcertFingerprintParams(**params)
                cmd = ["clientmgmt", "tokens", "webcert-fingerprint"]
                self.add_domain_auth_params(cmd, params)
                return self.ksctl.execute(cmd)
            else:
                raise ValueError(f"Unknown action: {action}")
        except ValidationError as e:
            # Reformat Pydantic's error for clarity.
            error_details = []
            for error in e.errors():
                loc = " -> ".join(map(str, error["loc"]))
                error_details.append(f"Parameter '{loc}': {error['msg']}")
            return {"error": f"Invalid parameters for action '{action}'. Please check your inputs.", "details": error_details}

CLIENTMGMT_TOOLS = [ClientMgmtTool] 