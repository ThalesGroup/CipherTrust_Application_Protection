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
