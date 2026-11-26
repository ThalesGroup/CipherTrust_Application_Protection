"""CipherTrust MCP tools package."""

from typing import Type

from .base import BaseTool

# Import domain management tools
from .domains import DOMAIN_TOOLS

# Import core tools
from .akeyless import AKEYLESS_TOOLS
from .backup import BACKUP_TOOLS
from .backupkeys import BACKUPKEY_TOOLS
from .groupmaps import GROUPMAP_TOOLS
from .groups import GROUP_TOOLS
from .keys import KEY_TOOLS
from .keypolicies import KEY_POLICY_TOOLS
from .licensing import LICENSING_TOOLS
from .metrics import METRICS_TOOLS
from .mkeks import MKEKS_TOOLS
from .network import NETWORK_TOOLS
from .ntp import NTP_TOOLS
from .properties import PROPERTIES_TOOLS
from .proxy import PROXY_TOOLS
from .quorum import QUORUM_TOOLS
from .records import RECORD_TOOLS
from .rotkeys import ROTKEY_TOOLS
from .scp import SCP_TOOLS
from .secrets import SECRET_TOOLS
from .services import SERVICE_MGMT_TOOLS
from .system import SYSTEM_TOOLS
from .templates import TEMPLATE_TOOLS
from .tokens import TOKEN_TOOLS
from .users import USER_TOOLS
from .vkeys import VKEYS_TOOLS

# Import connection management tools
from .connection_management import CONNECTION_TOOLS

# Import authentication connection management tools
from .connections_ldap import CONNECTION_LDAP_TOOLS
from .connections_oidc import CONNECTION_OIDC_TOOLS
from .connections_users import CONNECTION_USERS_TOOLS

# Import cryptographic operation tools
from .crypto import CRYPTO_TOOLS

# Import unified CTE management tool
from .cte_management import CTE_TOOLS

# Import scheduler management tools
from .scheduler_management import SCHEDULER_TOOLS

# Import cluster management tools
from .cluster_management import CLUSTER_MANAGEMENT_TOOLS
from .clientmgmt import CLIENTMGMT_TOOLS
from .banner_management import BANNER_MANAGEMENT_TOOLS
from .interfaces_management import INTERFACES_MANAGEMENT_TOOLS
from .ddc_management import DDC_MANAGEMENT_TOOLS
from .cckm_management import CCKM_TOOLS
from .data_protection import DATA_PROTECTION_TOOLS

# Collect all available tools
ALL_TOOLS_UNSORTED: list[Type[BaseTool]] = [
    # Core functionality
    *SYSTEM_TOOLS,          # System information management
    *SERVICE_MGMT_TOOLS,    # Service management
    *TOKEN_TOOLS,           # JWT/refresh tokens
    *USER_TOOLS,            # User management
    *GROUP_TOOLS,           # Group management
    *GROUPMAP_TOOLS,        # Group mappings
    *KEY_TOOLS,             # Key management
    *KEY_POLICY_TOOLS,      # Key policies
    *SECRET_TOOLS,          # Secrets management
    *SCP_TOOLS,             # SCP public key management
    *TEMPLATE_TOOLS,        # Template management
    *VKEYS_TOOLS,           # Versioned keys management
    *AKEYLESS_TOOLS,        # Akeyless Gateway integration
    *BACKUP_TOOLS,          # Backup management
    *BACKUPKEY_TOOLS,       # Backup key management
    *LICENSING_TOOLS,       # Licensing
    *ROTKEY_TOOLS,          # Root of Trust keys
    *RECORD_TOOLS,          # Audit records & alarm configs
    *METRICS_TOOLS,         # Prometheus metrics
    *MKEKS_TOOLS,           # Master KEKs
    *NETWORK_TOOLS,         # Network diagnostics
    *NTP_TOOLS,             # NTP server management
    *PROPERTIES_TOOLS,      # System properties
    *PROXY_TOOLS,           # Proxy configurations
    *QUORUM_TOOLS,          # Quorum management

    # Domain management
    *DOMAIN_TOOLS,          # Domain admin, KEKs, log redirection

    # Connection management
    *CONNECTION_TOOLS,      # Unified connection management

    # Authentication connection management
    *CONNECTION_LDAP_TOOLS,    # LDAP connection management
    *CONNECTION_OIDC_TOOLS,    # OIDC connection management
    *CONNECTION_USERS_TOOLS,   # Connection users management

    # Cryptographic operations
    *CRYPTO_TOOLS,            # Encryption, signing, FPE operations

    # CTE (CipherTrust Transparent Encryption) management
    *CTE_TOOLS,               # Unified modular CTE management

    # Scheduler management
    *SCHEDULER_TOOLS,         # Scheduler configuration and job management

    # Additional management tools
    *CLUSTER_MANAGEMENT_TOOLS,    # Cluster management
    *CLIENTMGMT_TOOLS,            # Client management
    *BANNER_MANAGEMENT_TOOLS,     # Banner management
    *INTERFACES_MANAGEMENT_TOOLS, # Interface management
    *DDC_MANAGEMENT_TOOLS,        # DDC management
    *CCKM_TOOLS,                  # Unified modular CCKM management
    *DATA_PROTECTION_TOOLS,       # Data Protection
]

# Instantiate and sort tools alphabetically by name
ALL_TOOLS: list[Type[BaseTool]] = sorted(ALL_TOOLS_UNSORTED, key=lambda tool_class: tool_class().name)

all = ["BaseTool", "ALL_TOOLS"]