# Install Thales CipherTrust Ansible Collection first

```
ansible-galaxy collection install thalesgroup.ciphertrust
```

# Useful tasks
## For CipherTrust Transparent Encryption (Kubernetes)
### Creating Key
Creates an AES 256 bytes key with encrypt/decrypt as key usage and suitable for a CTE client
```
- name: "Create Key"
  thalesgroup.ciphertrust.vault_keys2_save:
    op_type: create
    name: cte_key
    algorithm: aes
    size: 256
    undeletable: false
    unexportable: false
    usageMask: 76
    meta:
      ownerId: admin
      permissions:
        DecryptWithKey:
          - "CTE Clients"
        EncryptWithKey:
          - "CTE Clients"
        ExportKey:
          - "CTE Clients"
        MACVerifyWithKey:
          - "CTE Clients"
        MACWithKey:
          - "CTE Clients"
        ReadKey:
          - "CTE Clients"
        SignVerifyWithKey:
          - "CTE Clients"
        SignWithKey:
          - "CTE Clients"
        UseKey:
          - "CTE Clients"
      cte:
        persistent_on_client: true
        encryption_mode: CBC_CS1
        cte_versioned: false
    xts: true
    localNode:
      server_ip: "{{ cm_ip }}"
      server_private_ip: "{{ cm_private_ip }}"
      server_port: 5432
      user: "{{ cm_username }}"
      password: "{{ cm_password }}"
      verify: False
      auth_domain_path:
    register: key
```

### Creating CTE ResourceSet
Create a ResourceSet for the CTE Guard Point that would protect all files in /data/cte 
```
- name: "Create CTE ResourceSet"
  thalesgroup.ciphertrust.cte_resource_set:
    op_type: create
    name: rs_name
    type: Directory
    description: "Created via Ansible"
    resources:
      - directory: "/data/cte"
        file: "*"
        include_subfolders: true
        hdfs: false
    localNode:
      server_ip: "{{ cm_ip }}"
      server_private_ip: "{{ cm_private_ip }}"
      server_port: 5432
      user: "{{ cm_username }}"
      password: "{{ cm_password }}"
      verify: False
      auth_domain_path:
  register: _result_create_rs
```

### Creating CTE Policy for Kubernetes type
Creates CTE policy using the key and resourceSet created above
```
- name: "Create CTE CSI Policy"
  thalesgroup.ciphertrust.cte_policy_save:
    op_type: create
    localNode:
      server_ip: "{{ cm_ip }}"
      server_private_ip: "{{ cm_private_ip }}"
      server_port: 5432
      user: "{{ cm_username }}"
      password: "{{ cm_password }}"
      verify: False
      auth_domain_path:
    name: policyName
    description: "Created via Ansible"
    never_deny: false
    policy_type: CSI
    metadata:
      restrict_update: false
    security_rules:
      - action: key_op
        effect: "permit,applykey"
        partial_match: true
      - resource_set_id: "{{ _result_create_rs['response']['id'] }}"
        exclude_resource_set: false
        partial_match: true
        action: all_ops
        effect: "permit,audit,applykey"
    key_rules:
      - key_id: "{{ key['response']['id'] }}"
        resource_set_id: "{{ _result_create_rs['response']['id'] }}"
    data_transform_rules:
      - key_id: "{{ key['response']['id'] }}"
        resource_set_id: "{{ _result_create_rs['response']['id'] }}"
  register: _result_create_csi_policy
```

### Create Storage Group
Create Storage Group on CipherTrust Manager for given namespace. This is the namespace where the pods leveraging CTE for kubernetes will be created
```
- name: "Create CSI Storage Group"
  thalesgroup.ciphertrust.cte_csi_storage_group:
    op_type: create
    name: sgName
    k8s_namespace: namespace
    k8s_storage_class: scName
    client_profile: DefaultClientProfile
    localNode:
      server_ip: "{{ cm_ip }}"
      server_private_ip: "{{ cm_private_ip }}"
      server_port: 5432
      user: "{{ cm_username }}"
      password: "{{ cm_password }}"
      verify: False
      auth_domain_path:
  register: _result_create_csi_sg
```

### Add CTE Policy to the Storage Group
Adds above CTE policy to above storage group
```
- name: "Add CTE Policy to the CSI Storage Group"
  thalesgroup.ciphertrust.cte_csi_storage_group:
    op_type: add_guard_point
    id: "{{ _result_create_csi_sg['response']['id'] }}"
    policy_list: 
      - "{{ _result_create_csi_policy['response']['id'] }}"
    localNode:
      server_ip: "{{ cm_ip }}"
      server_private_ip: "{{ cm_private_ip }}"
      server_port: 5432
      user: "{{ cm_username }}"
      password: "{{ cm_password }}"
      verify: False
      auth_domain_path:
  register: _result_create_csi_sg
```

### Create Registration Token
Create a registration token that we will eventually put in our kubernetes configuration files for the Storage Class and Persistent Volume Claim
```
- name: "Create Registration Token"
  thalesgroup.ciphertrust.cm_regtoken:
    op_type: create
    ca_id: "{{ ca_id }}"
    label:
      ClientProfile: DefaultClientProfile
    name_prefix: ansible_client
    localNode:
      server_ip: "{{ cm_ip }}"
      server_private_ip: "{{ cm_private_ip }}"
      server_port: 5432
      user: "{{ cm_username }}"
      password: "{{ cm_password }}"
      verify: False
      auth_domain_path:
  register: _result_create_reg_token
```

## For Data Protection Gateway
### Creating Key for DPG
Creates an AES 256 bytes key with encrypt/decrypt, FPE encrypt/decrypt as key usage and suitable for a DPG client
```
- name: "Create Key"
  thalesgroup.ciphertrust.vault_keys2_save:
    op_type: create
    name: dpgKey
    algorithm: aes
    size: 256
    usageMask: 3145740
    unexportable: false
    undeletable: false
    meta:
      ownerId: admin
      versionedKey: true
    localNode:
      server_ip: "{{ cm_ip }}"
      server_private_ip: "{{ cm_private_ip }}"
      server_port: 5432
      user: "{{ cm_username }}"
      password: "{{ cm_password }}"
      verify: False
      auth_domain_path:
  ignore_errors: true
```

### Creating Interface
Creates an NAE interface with port as 9006, TLS with cert auth and password optional, and associated with Certificate Authority as ca_id
```
- name: "Create Interface"
  thalesgroup.ciphertrust.interface_save:
    localNode:
      server_ip: "{{ cm_ip }}"
      server_private_ip: "{{ cm_private_ip }}"
      server_port: 5432
      user: "{{ cm_username }}"
      password: "{{ cm_password }}"
      verify: False
      auth_domain_path:
    op_type: create
    port: 9006
    auto_gen_ca_id: "{{ ca_id }}"
    auto_registration: true
    allow_unregistered: true
    cert_user_field: CN
    interface_type: nae
    mode: tls-cert-pw-opt
    network_interface: all
    trusted_cas:
      local:
        - "{{ ca_id }}"
  ignore_errors: true
```

### Creating UserSet for masked reveal
Creates a userset named masked with username operator in it. We will later use this to assign corresponding access policy
```
- name: "User Set for masked info"
  thalesgroup.ciphertrust.dpg_user_set_save:
    localNode:
      server_ip: "{{ cm_ip }}"
      server_private_ip: "{{ cm_private_ip }}"
      server_port: 5432
      user: "{{ cm_username }}"
      password: "{{ cm_password }}"
      verify: False
      auth_domain_path:
    op_type: "create"
    name: masked
    users:
      - operator
  register: user_set_masked
```

### Creating UserSet for plaintext reveal
Creates a userset named plain with username owner in it. We will later use this to assign corresponding access policy
```
- name: "User Set for plaintext"
  thalesgroup.ciphertrust.dpg_user_set_save:
    localNode:
      server_ip: "{{ cm_ip }}"
      server_private_ip: "{{ cm_private_ip }}"
      server_port: 5432
      user: "{{ cm_username }}"
      password: "{{ cm_password }}"
      verify: False
      auth_domain_path:
    op_type: "create"
    name: plain
    users:
      - owner
  register: user_set_plain
```

### Creating Access Policy
Creates Access Policy with default CipherText, Plaintext for plain UserSet, Masked for masked UserSet
```
# Get the Masking Format ID first
- name: "Get dynamic masket format ID"
  thalesgroup.ciphertrust.cm_resource_get_id_from_name:
    localNode:
      server_ip: "{{ cm_ip }}"
      server_private_ip: "{{ cm_private_ip }}"
      server_port: 5432
      user: "{{ cm_username }}"
      password: "{{ cm_password }}"
      verify: False
      auth_domain_path:
    query_param: "name"
    query_param_value: "SHOW_LAST_FOUR"
    resource_type: "masking-formats"
  register: masking_format_dynamic
  ignore_errors: true

# Now Create the Access Policy
- name: "Create Access Policy"
  thalesgroup.ciphertrust.dpg_access_policy_save:
    localNode:
      server_ip: "{{ cm_ip }}"
      server_private_ip: "{{ cm_private_ip }}"
      server_port: 5432
      user: "{{ cm_username }}"
      password: "{{ cm_password }}"
      verify: False
      auth_domain_path:
    op_type: "create"
    name: accessPolicy
    default_reveal_type: "Ciphertext"
    user_set_policy:
      - reveal_type: Plaintext
        user_set_id: "{{ user_set_plain['response']['id'] }}"
      - reveal_type: "Masked Value"
        user_set_id: "{{ user_set_masked['response']['id'] }}"
        masking_format_id: "{{ masking_format_dynamic['response']['id'] }}"
  register: access_policy
```

### Creating Protection Policy
Create CharSet and the Protection Policy using CharSet, Masking Format and Key created above
```
# First get the masking format ID from name
- name: "Get static masket format ID"
  thalesgroup.ciphertrust.cm_resource_get_id_from_name:
    localNode:
      server_ip: "{{ cm_ip }}"
      server_private_ip: "{{ cm_private_ip }}"
      server_port: 5432
      user: "{{ cm_username }}"
      password: "{{ cm_password }}"
      verify: False
      auth_domain_path:
    query_param: "name"
    query_param_value: "LAST_FOUR"
    resource_type: "masking-formats"
  register: masking_format_static
  ignore_errors: true

# Create DPG CharSet next
- name: "Create Character Set"
  thalesgroup.ciphertrust.dpg_character_set_save:
    localNode:
      server_ip: "{{ cm_ip }}"
      server_private_ip: "{{ cm_private_ip }}"
      server_port: 5432
      user: "{{ cm_username }}"
      password: "{{ cm_password }}"
      verify: False
      auth_domain_path:
    op_type: create
    name: charSet
    range:
      - 0030-0039
      - 0041-005A
      - 0061-007A
    encoding: UTF-8
  register: charset

# Now create the protection policy
- name: "Create Protection Policy"
  thalesgroup.ciphertrust.dpg_protection_policy_save:
    localNode:
      server_ip: "{{ cm_ip }}"
      server_private_ip: "{{ cm_private_ip }}"
      server_port: 5432
      user: "{{ cm_username }}"
      password: "{{ cm_password }}"
      verify: False
      auth_domain_path:
    op_type: create
    access_policy_name: protectionPolicy
    masking_format_id: "{{ masking_format_static['response']['id'] }}"
    name: protectionPolicy
    key: dpgKey
    tweak: "1628462495815733"
    tweak_algorithm: "SHA1"
    algorithm: "FPE/AES/UNICODE"
    character_set_id: "{{ charset['response']['id'] }}"
  register: protection_policy
```

### Creating DPG Policy
This is where we will map our REST API endpoints with the DPG policy.
We are protecting the API endpoints -
* /api/payment-info (GET/POST)
  * Fields
    * cc
    * cvv
    * zip
* /api/health-info/add (POST)
  * healthCardNum
  * zip
* /api/health-info (GET)
  * healthCardNum
  * zip
```
- name: "Create DPG Policy"
  thalesgroup.ciphertrust.dpg_policy_save:
    localNode:
      server_ip: "{{ cm_ip }}"
      server_private_ip: "{{ cm_private_ip }}"
      server_port: 5432
      user: "{{ cm_username }}"
      password: "{{ cm_password }}"
      verify: False
      auth_domain_path:
    op_type: create
    name: dpgPolicy
    proxy_config:
      - api_url: "/api/payment-info"
        json_request_post_tokens:
          - name: "cc"
            operation: "protect"
            protection_policy: protectionPolicy
          - name: "cvv"
            operation: "protect"
            protection_policy: protectionPolicy
          - name: "zip"
            operation: "protect"
            protection_policy: protectionPolicy
        json_response_get_tokens:
          - name: "data.[*].cc"
            operation: "reveal"
            protection_policy: protectionPolicy
            access_policy: accessPolicy
          - name: "data.[*].cvv"
            operation: "reveal"
            protection_policy: protectionPolicy
            access_policy: accessPolicy
          - name: "data.[*].zip"
            operation: "reveal"
            protection_policy: protectionPolicy
            access_policy: accessPolicy
      - api_url: "/api/health-info/add"
        json_request_post_tokens:
          - name: "healthCardNum"
            operation: "protect"
            protection_policy: protectionPolicy
          - name: "zip"
            operation: "protect"
            protection_policy: protectionPolicy
      - api_url: "/api/health-info"
        json_response_get_tokens:
          - name: "data.[*].healthCardNum"
            operation: "reveal"
            protection_policy: protectionPolicy
            access_policy: accessPolicy
          - name: "data.[*].zip"
            operation: "reveal"
            protection_policy: protectionPolicy
            access_policy: accessPolicy
  register: policy
```

### Creating DPG Client Profile
Finally create DPG client with above policy and resources
```
- name: "Create DPG Client Profile"
  thalesgroup.ciphertrust.dpg_client_profile_save:
    name: dpgProfile
    op_type: create
    app_connector_type: DPG
    lifetime: 30d
    cert_duration: 730
    max_clients: 200
    ca_id: "{{ ca_id }}"
    nae_iface_port: 9006
    csr_parameters:
      csr_cn: admin
    policy_id: "{{ policy['response']['id'] }}"    
    configurations:
      auth_method_used:
        scheme_name: Basic
      tls_to_appserver:
        tls_skip_verify: true
        tls_enabled: false
    localNode:
      server_ip: "{{ cm_ip }}"
      server_private_ip: "{{ cm_private_ip }}"
      server_port: 5432
      user: "{{ cm_username }}"
      password: "{{ cm_password }}"
      verify: False
      auth_domain_path:
  register: profile
```
