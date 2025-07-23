"""Constants and examples for CTE management"""

JSON_EXAMPLES = {
    "user_set": {
        "description": "User set structure for defining users and groups",
        "example": {
            "name": "AdminUsers",
            "description": "Administrative users set",
            "users": [
                {
                    "uname": "admin",
                    "uid": 1000,
                    "gname": "admingroup",
                    "gid": 1000,
                    "os_domain": "CORPORATE"  # For Windows domain users
                },
                {
                    "uname": "user1",
                    "uid": 1001,
                    "gname": "users",
                    "gid": 100
                }
            ]
        }
    },
    "process_set": {
        "description": "Process set structure for defining allowed processes",
        "example": {
            "name": "TrustedProcesses",
            "description": "Trusted application processes",
            "processes": [
                {
                    "signature": "AppSignatureSet",
                    "directory": "/usr/bin",
                    "file": "app.exe"
                },
                {
                    "signature": "SystemSignatureSet",
                    "directory": "/bin",
                    "file": "*"  # All files in directory
                }
            ]
        }
    },
    "resource_set": {
        "description": "Resource set structure for defining protected resources",
        "example": {
            "name": "SensitiveData",
            "description": "Sensitive data directories",
            "resources": [
                {
                    "directory": "/data/sensitive",
                    "file": "*",
                    "include_subfolders": True,
                    "hdfs": False
                },
                {
                    "directory": "/data/reports",
                    "file": "*.pdf",
                    "include_subfolders": False,
                    "hdfs": False
                }
            ]
        }
    },
    "security_rules": {
        "description": "Security rules for policy",
        "example": [
            {
                "effect": "permit,audit",  # Multiple effects comma-separated
                "action": "read",
                "partial_match": False,
                "user_set_id": "AdminUsers",
                "process_set_id": "TrustedProcesses",
                "resource_set_id": "SensitiveData",
                "exclude_user_set": False,
                "exclude_process_set": False,
                "exclude_resource_set": False
            }
        ]
    },
    "key_rules": {
        "description": "Key rules for encryption/decryption",
        "example": [
            {
                "key_id": "DataEncryptionKey",
                "key_type": "name",
                "resource_set_id": "SensitiveData"
            }
        ]
    },
    "ldt_rules": {
        "description": "LDT (Live Data Transformation) rules",
        "example": [
            {
                "resource_set_id": "DataToTransform",
                "current_key": {
                    "key_id": "clear_key",
                    "key_type": "name",
                    "key_usage": "ONLINE"
                },
                "transformation_key": {
                    "key_id": "NewEncryptionKey",
                    "key_type": "name",
                    "key_usage": "ONLINE"
                }
            }
        ]
    },
    "cache_settings": {
        "description": "Cache configuration for CTE profile",
        "example": {
            "max_files": 1000,
            "max_space": 500000  # in KB
        }
    },
    "logger_settings": {
        "description": "Logger configuration (applies to all logger types)",
        "example": {
            "duplicates": "SUPPRESS",  # ALLOW or SUPPRESS
            "threshold": "INFO",  # DEBUG, INFO, WARN, ERROR, FATAL
            "file_enabled": True,
            "syslog_enabled": False,
            "upload_enabled": True
        }
    },
    "syslog_settings": {
        "description": "Syslog configuration for CTE profile",
        "example": {
            "local": False,
            "servers": [
                {
                    "message_format": "RFC5424",  # CEF, LEEF, RFC5424, PLAIN
                    "name": "syslog.company.com",
                    "protocol": "TCP"  # TCP or UDP
                }
            ],
            "syslog_threshold": "WARN"
        }
    }
}

# Common schema properties used across multiple sub-tools
COMMON_SCHEMA_PROPERTIES = {
    "domain": {
        "type": "string", 
        "description": "Domain context (optional, defaults to current domain)"
    },
    "auth_domain": {
        "type": "string",
        "description": "Authentication domain (optional, defaults to current auth domain)" 
    },
    "limit": {
        "type": "integer",
        "default": 10,
        "description": "Maximum results to return (for list operations)"
    },
    "skip": {
        "type": "integer", 
        "default": 0,
        "description": "Number of results to skip (for pagination)"
    },
    "description": {
        "type": "string",
        "description": "Description for the resource being created/modified"
    },
    "search": {
        "type": "string",
        "description": "Search filter for list operations"
    },
    "sort": {
        "type": "string",
        "description": "Sort field (prefix with - for descending)"
    }
}
