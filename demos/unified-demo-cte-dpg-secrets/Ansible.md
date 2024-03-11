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

### Creating CTE ResourceSet

### Creating CTE Policy for Kubernetes type

### Create Storage Group

### Add CTE Policy to the Storage Group

### Create Registration Token
