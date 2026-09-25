"""Constants for Connection Management operations."""

# Common schema properties for all Connection Management operations
COMMON_SCHEMA_PROPERTIES = {
    "domain": {
        "type": "string",
        "description": "The CipherTrust Manager domain where the action, operation, or execution will be performed. This specifies the target environment for the command."
    },
    "auth_domain": {
        "type": "string", 
        "description": "The CipherTrust Manager domain where the user is created and authenticated. Unless explicitly specified, this defaults to 'root'. This is used for access control and does not affect the command's execution target."
    }
}

# Common parameters for connection operations
COMMON_CONNECTION_PARAMETERS = {
    "id": {"type": "string", "description": "Connection ID for get/delete/test operations"},
    "name": {"type": "string", "description": "Connection name"},
    "description": {"type": "string", "description": "Connection description"},
    "products": {"type": "string", "description": "Comma-separated list of products"},
    "cloudname": {"type": "string", "description": "Cloud name"},
    "category": {"type": "string", "description": "Category"},
    "meta": {"type": "string", "description": "Meta information in JSON format"},
    "labels": {"type": "string", "description": "Labels (key/value pairs)"},
    "json_file": {"type": "string", "description": "Connection information in JSON format via file (REQUIRES FILE PATH - provide path to JSON configuration file)"},
    "limit": {"type": "integer", "description": "Maximum number of results to return"},
    "skip": {"type": "integer", "description": "Number of results to skip"},
    "fields": {"type": "string", "description": "Fields to include in response"},
    "labels_query": {"type": "string", "description": "Label selector expressions for filtering"},
    "lastconnectionafter": {"type": "string", "description": "Last connection after timestamp"},
    "lastconnectionbefore": {"type": "string", "description": "Last connection before timestamp"},
    "lastconnectionok": {"type": "string", "description": "Last connection OK status"},
    "force": {"type": "boolean", "description": "Force delete in_use connections"}
}

# AWS connection parameters
AWS_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "clientid": {"type": "string", "description": "AWS access key ID"},
    "secret": {"type": "string", "description": "AWS secret access key"},
    "assumerolearn": {"type": "string", "description": "Assume role ARN"},
    "assumeroleexternalid": {"type": "string", "description": "Assume role external ID"},
    "iamroleanywhere": {"type": "string", "description": "IAM role anywhere parameters (REQUIRES FILE PATH - provide path to JSON file with IAM role anywhere parameters)"},
    "isroleanywhere": {"type": "string", "description": "Set to true for IAM Anywhere connections"}
}

# Azure connection parameters
AZURE_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "clientid": {"type": "string", "description": "Azure client ID"},
    "secret": {"type": "string", "description": "Azure client secret"},
    "tenantid": {"type": "string", "description": "Azure tenant ID"},
    "use_certificate": {"type": "string", "description": "Use certificate-based authentication"},
    "certificate": {"type": "string", "description": "Certificate for authentication"},
    "certificate_file": {"type": "string", "description": "Certificate file path (REQUIRES FILE PATH - provide path to PEM or PKCS12 certificate file)"},
    "certificate_duration": {"type": "integer", "description": "Certificate validity in days"},
    "connection_type": {"type": "string", "description": "Azure stack connection type (AAD or ADFS)"},
    "active_dir_endpoint": {"type": "string", "description": "Active directory endpoint for Azure stack"},
    "management_url": {"type": "string", "description": "Management URL for Azure stack"},
    "res_manager_url": {"type": "string", "description": "Resource manager URL for Azure stack"},
    "key_vault_dns_suffix": {"type": "string", "description": "Key vault DNS suffix for Azure stack"},
    "vault_res_url": {"type": "string", "description": "Vault resource URL for Azure stack"},
    "server_cert_file": {"type": "string", "description": "Server certificate file path (REQUIRES FILE PATH - provide path to server certificate file)"}
}

# GCP connection parameters
GCP_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "key_file": {"type": "string", "description": "GCP service account key file path (REQUIRES FILE PATH - provide path to .json key file)"}
}

# OCI connection parameters
OCI_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "tenancy_ocid": {"type": "string", "description": "OCI tenancy OCID"},
    "user_ocid": {"type": "string", "description": "OCI user OCID"},
    "fingerprint": {"type": "string", "description": "OCI fingerprint (supports both colon-separated format like '00:30:31:52:64:84:f0:7f:cb:d0:55:29:93:b7:e5:54' and continuous format like '003031526484f07fcbd0552993b7e554')"},
    "oci_region": {"type": "string", "description": "OCI region"},
    "conn_creds": {"type": "string", "description": "OCI connection credentials file path (REQUIRES FILE PATH - provide path to JSON file with key_file content and optional pass_phrase). This is the primary method for OCI connections."},
    "key_file": {"type": "string", "description": "OCI private key input (can be file path or pasted PEM content). The tool will automatically create a temporary conn_creds JSON file. Alternative to conn_creds for direct key specification."},
    "pass_phrase": {"type": "string", "description": "Pass phrase for the OCI private key (optional, only used when key_file is specified)"}
}

# Salesforce connection parameters
SALESFORCE_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "clientid": {"type": "string", "description": "Salesforce client ID"},
    "secret": {"type": "string", "description": "Salesforce client secret"},
    "username": {"type": "string", "description": "Salesforce username"},
    "password": {"type": "string", "description": "Salesforce password"},
    "security_token": {"type": "string", "description": "Salesforce security token"},
    "certificate_file": {"type": "string", "description": "Certificate file path (REQUIRES FILE PATH - provide path to PEM or PKCS12 certificate file)"},
    "tls_client_cert_with_private_key_file": {"type": "string", "description": "TLS client certificate file path (REQUIRES FILE PATH - provide path to TLS client PEM certificate file)"}
}

# Akeyless connection parameters
AKEYLESS_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "clientid": {"type": "string", "description": "Akeyless access ID"},
    "secret": {"type": "string", "description": "Akeyless access key"},
    "api_url": {"type": "string", "description": "Akeyless API URL"}
}

# Hadoop connection parameters
HADOOP_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "namenode_url": {"type": "string", "description": "Hadoop namenode URL"},
    "username": {"type": "string", "description": "Hadoop username"},
    "password": {"type": "string", "description": "Hadoop password"},
    "kerberos_principal": {"type": "string", "description": "Kerberos principal"},
    "keytab_file": {"type": "string", "description": "Keytab file path (REQUIRES FILE PATH - provide path to keytab file)"},
    "nodes_json_file": {"type": "string", "description": "Nodes JSON file path (REQUIRES FILE PATH - provide path to JSON file with server nodes list)"}
}

# Luna HSM connection parameters
LUNA_HSM_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "server_url": {"type": "string", "description": "Luna HSM server URL"},
    "partition_name": {"type": "string", "description": "Luna HSM partition name"},
    "partition_password": {"type": "string", "description": "Luna HSM partition password"},
    "certificate_file": {"type": "string", "description": "Luna HSM certificate file path (REQUIRES FILE PATH - provide path to certificate file)"},
    "partitions_json_file": {"type": "string", "description": "Partitions JSON file path (REQUIRES FILE PATH - provide path to JSON file with partitions list)"}
}

# SMB connection parameters
SMB_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "server": {"type": "string", "description": "SMB server address"},
    "share": {"type": "string", "description": "SMB share name"},
    "username": {"type": "string", "description": "SMB username"},
    "password": {"type": "string", "description": "SMB password"},
    "domain": {"type": "string", "description": "SMB domain"}
}

# DSM connection parameters
DSM_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "server_url": {"type": "string", "description": "DSM server URL"},
    "username": {"type": "string", "description": "DSM username"},
    "password": {"type": "string", "description": "DSM password"},
    "certificate_file": {"type": "string", "description": "DSM certificate file path (REQUIRES FILE PATH - provide path to certificate file)"},
    "nodes_json_file": {"type": "string", "description": "Nodes JSON file path (REQUIRES FILE PATH - provide path to JSON file with server nodes list)"}
}

# SCP/SFTP connection parameters
SCP_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "host": {"type": "string", "description": "SCP/SFTP host"},
    "port": {"type": "integer", "description": "SCP/SFTP port"},
    "username": {"type": "string", "description": "SCP/SFTP username"},
    "password": {"type": "string", "description": "SCP/SFTP password"},
    "private_key_file": {"type": "string", "description": "Private key file path (REQUIRES FILE PATH - provide path to private key file)"},
    "passphrase": {"type": "string", "description": "Private key passphrase"}
}

# SAP Data Custodian connection parameters
SAP_DC_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "clientid": {"type": "string", "description": "SAP DC client ID"},
    "secret": {"type": "string", "description": "SAP DC client secret"},
    "tenant_id": {"type": "string", "description": "SAP DC tenant ID"},
    "endpoint_url": {"type": "string", "description": "SAP DC endpoint URL"}
}

# Log Forwarder connection parameters
LOG_FORWARDER_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "type": {"type": "string", "description": "Log forwarder type (elasticsearch, loki, syslog)"},
    "endpoint_url": {"type": "string", "description": "Log forwarder endpoint URL"},
    "username": {"type": "string", "description": "Log forwarder username"},
    "password": {"type": "string", "description": "Log forwarder password"},
    "certificate_file": {"type": "string", "description": "Log forwarder certificate file path (REQUIRES FILE PATH - provide path to certificate file)"}
}

# Elasticsearch Log Forwarder parameters
ELASTICSEARCH_LOG_FORWARDER_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "endpoint_url": {"type": "string", "description": "Elasticsearch endpoint URL"},
    "username": {"type": "string", "description": "Elasticsearch username"},
    "password": {"type": "string", "description": "Elasticsearch password"},
    "certificate_file": {"type": "string", "description": "Elasticsearch certificate file path (REQUIRES FILE PATH - provide path to certificate file)"},
    "index_name": {"type": "string", "description": "Elasticsearch index name"},
    "ssl_verify": {"type": "boolean", "description": "Verify SSL certificate"}
}

# Loki Log Forwarder parameters
LOKI_LOG_FORWARDER_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "endpoint_url": {"type": "string", "description": "Loki endpoint URL"},
    "username": {"type": "string", "description": "Loki username"},
    "password": {"type": "string", "description": "Loki password"},
    "certificate_file": {"type": "string", "description": "Loki certificate file path (REQUIRES FILE PATH - provide path to certificate file)"},
    "tenant_id": {"type": "string", "description": "Loki tenant ID"}
}

# Syslog Log Forwarder parameters
SYSLOG_LOG_FORWARDER_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "endpoint_url": {"type": "string", "description": "Syslog endpoint URL"},
    "username": {"type": "string", "description": "Syslog username"},
    "password": {"type": "string", "description": "Syslog password"},
    "certificate_file": {"type": "string", "description": "Syslog certificate file path (REQUIRES FILE PATH - provide path to certificate file)"},
    "facility": {"type": "string", "description": "Syslog facility"},
    "priority": {"type": "string", "description": "Syslog priority"}
}

# Luna HSM Server parameters
LUNA_HSM_SERVER_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "server_url": {"type": "string", "description": "Luna HSM server URL"},
    "certificate_file": {"type": "string", "description": "Luna HSM server certificate file path (REQUIRES FILE PATH - provide path to certificate file)"},
    "server_name": {"type": "string", "description": "Luna HSM server name"}
}

# Luna HSM STC Partition parameters
LUNA_HSM_STC_PARTITION_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "server_id": {"type": "string", "description": "Luna HSM server ID"},
    "partition_name": {"type": "string", "description": "STC partition name"},
    "partition_password": {"type": "string", "description": "STC partition password"},
    "certificate_file": {"type": "string", "description": "STC partition certificate file path (REQUIRES FILE PATH - provide path to certificate file)"},
    "partition_identity": {"type": "string", "description": "Partition identity file path (REQUIRES FILE PATH - provide path to partition identity file)"}
}

# Hadoop Node parameters
HADOOP_NODE_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "connection_id": {"type": "string", "description": "Hadoop connection ID"},
    "node_url": {"type": "string", "description": "Hadoop node URL"},
    "node_type": {"type": "string", "description": "Hadoop node type (namenode, datanode, etc.)"},
    "username": {"type": "string", "description": "Hadoop node username"},
    "password": {"type": "string", "description": "Hadoop node password"}
}

# External CM Node parameters
EXTERNAL_CM_NODE_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "connection_id": {"type": "string", "description": "External CM connection ID"},
    "node_url": {"type": "string", "description": "External CM node URL"},
    "node_name": {"type": "string", "description": "External CM node name"},
    "username": {"type": "string", "description": "External CM node username"},
    "password": {"type": "string", "description": "External CM node password"}
}

# External CM Trusted CA parameters
EXTERNAL_CM_TRUSTED_CA_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "connection_id": {"type": "string", "description": "External CM connection ID"},
    "ca_certificate": {"type": "string", "description": "Trusted CA certificate"},
    "ca_certificate_file": {"type": "string", "description": "Trusted CA certificate file path (REQUIRES FILE PATH - provide path to trusted CA certificate file)"}
}

# Connections CSR parameters
CONNECTIONS_CSR_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "common_name": {"type": "string", "description": "Common name for the certificate"},
    "country": {"type": "string", "description": "Country code"},
    "state": {"type": "string", "description": "State or province"},
    "locality": {"type": "string", "description": "City or locality"},
    "organization": {"type": "string", "description": "Organization name"},
    "organizational_unit": {"type": "string", "description": "Organizational unit"},
    "email": {"type": "string", "description": "Email address"},
    "key_size": {"type": "integer", "description": "Key size in bits"},
    "output_file": {"type": "string", "description": "Output file path for CSR (REQUIRES FILE PATH - provide path where CSR file should be saved)"}
}

# Confidential Computing connection parameters
CONFIDENTIAL_COMPUTING_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "clientid": {"type": "string", "description": "Confidential computing client ID"},
    "secret": {"type": "string", "description": "Confidential computing client secret"},
    "endpoint_url": {"type": "string", "description": "Confidential computing endpoint URL"}
}

# External CM connection parameters
EXTERNAL_CM_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "server_url": {"type": "string", "description": "External CM server URL"},
    "username": {"type": "string", "description": "External CM username"},
    "password": {"type": "string", "description": "External CM password"},
    "certificate_file": {"type": "string", "description": "External CM certificate file path (REQUIRES FILE PATH - provide path to certificate file)"},
    "nodes_json_file": {"type": "string", "description": "Nodes JSON file path (REQUIRES FILE PATH - provide path to JSON file with server nodes list)"}
}

# LDAP connection parameters
LDAP_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "server_url": {"type": "string", "description": "LDAP server URL"},
    "bind_dn": {"type": "string", "description": "LDAP bind DN"},
    "bind_password": {"type": "string", "description": "LDAP bind password"},
    "search_base": {"type": "string", "description": "LDAP search base"},
    "certificate_file": {"type": "string", "description": "LDAP certificate file path (REQUIRES FILE PATH - provide path to certificate file)"},
    "root_ca_files": {"type": "string", "description": "Root CA files path (REQUIRES FILE PATH - provide semicolon-separated list of PEM certificate files)"}
}

# OIDC connection parameters
OIDC_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "clientid": {"type": "string", "description": "OIDC client ID"},
    "secret": {"type": "string", "description": "OIDC client secret"},
    "issuer_url": {"type": "string", "description": "OIDC issuer URL"},
    "redirect_uri": {"type": "string", "description": "OIDC redirect URI"}
}

# CM connection parameters
CM_PARAMETERS = {
    **COMMON_CONNECTION_PARAMETERS,
    "server_url": {"type": "string", "description": "CM server URL"},
    "username": {"type": "string", "description": "CM username"},
    "password": {"type": "string", "description": "CM password"},
    "certificate_file": {"type": "string", "description": "CM certificate file path (REQUIRES FILE PATH - provide path to certificate file)"},
    "client_cert_file": {"type": "string", "description": "Client certificate file path (REQUIRES FILE PATH - provide path to client certificate file)"}
}

# Operation mappings for each connection type
CONNECTION_OPERATIONS = {
    "list": ["list"],
    "delete": ["delete"],
    "aws": ["create", "list", "get", "delete", "modify", "test"],
    "azure": ["create", "list", "get", "delete", "modify", "test"],
    "gcp": ["create", "list", "get", "delete", "modify", "test"],
    "oci": ["create", "list", "get", "delete", "modify", "test"],
    "salesforce": ["create", "list", "get", "delete", "modify", "test"],
    "akeyless": ["create", "list", "get", "delete", "modify", "test"],
    "hadoop": ["create", "list", "get", "delete", "modify", "test"],
    "luna_hsm": ["create", "list", "get", "delete", "modify", "test"],
    "smb": ["create", "list", "get", "delete", "modify", "test"],
    "dsm": ["create", "list", "get", "delete", "modify", "test"],
    "scp": ["create", "list", "get", "delete", "modify", "test"],
    "sap_dc": ["create", "list", "get", "delete", "modify", "test"],
    "log_forwarder": ["create", "list", "get", "delete", "modify", "test"],
    "confidential_computing": ["create", "list", "get", "delete", "modify", "test"],
    "external_cm": ["create", "list", "get", "delete", "modify", "test"],
    "ldap": ["create", "list", "get", "delete", "modify", "test"],
    "oidc": ["create", "list", "get", "delete", "modify", "test"],
    "cm": ["create", "list", "get", "delete", "modify", "test"],
    # New specialized operations
    "elasticsearch_log_forwarder": ["create", "list", "get", "delete", "modify", "test"],
    "loki_log_forwarder": ["create", "list", "get", "delete", "modify", "test"],
    "syslog_log_forwarder": ["create", "list", "get", "delete", "modify", "test"],
    "luna_hsm_server": ["create", "list", "get", "delete", "modify"],
    "luna_hsm_stc_partition": ["create", "list", "get", "delete"],
    "hadoop_node": ["add", "list", "get", "delete", "modify"],
    "external_cm_node": ["add", "list", "get", "delete", "modify"],
    "external_cm_trusted_ca": ["add", "list", "get", "delete"],
    "connections_csr": ["create"]
} 