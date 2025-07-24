"""CipherTrust MCP tools package with integrated domain support."""

from typing import Type

from .base import BaseTool

# Import domain management tools (administrative domain operations)
from .domains import DOMAIN_TOOLS

# Import existing tools - all now have optional domain/auth_domain parameters
from .akeyless import AKEYLESS_TOOLS     # Akeyless Gateway integration (with domain support)
from .backup import BACKUP_TOOLS         # Backup management (with domain support)
from .backupkeys import BACKUPKEY_TOOLS  # Backup key management (with domain support)
from .groupmaps import GROUPMAP_TOOLS    # Group mappings with domain support
from .groups import GROUP_TOOLS          # Updated with domain support
from .keys import KEY_TOOLS              # Updated with domain support
from .keypolicies import KEY_POLICY_TOOLS  # Key policies with domain support
from .licensing import LICENSING_TOOLS   # System-wide operations
from .metrics import METRICS_TOOLS       # Prometheus metrics (system-wide)
from .mkeks import MKEKS_TOOLS           # Master KEKs (system-wide)
from .network import NETWORK_TOOLS       # Network diagnostics (system-wide)
from .ntp import NTP_TOOLS               # NTP server management (system-wide)
from .properties import PROPERTIES_TOOLS # System properties (system-wide)
from .proxy import PROXY_TOOLS           # Proxy configurations (system-wide)
from .quorum import QUORUM_TOOLS         # Quorum management (with domain support)
from .records import RECORD_TOOLS        # Audit records and alarm configs (system-wide)
from .rotkeys import ROTKEY_TOOLS        # Root of Trust keys (system-wide)
from .scp import SCP_TOOLS               # SCP public key management (with domain support)
from .secrets import SECRET_TOOLS        # Secrets management (with domain support)
from .services import SERVICE_MGMT_TOOLS # Service management (system-wide)
from .system import SYSTEM_TOOLS         # System-wide operations
from .templates import TEMPLATE_TOOLS    # Template management (with domain support)
from .tokens import TOKEN_TOOLS          # Updated with domain support
from .users import USER_TOOLS            # Updated with domain support + password policies
from .vkeys import VKEYS_TOOLS           # Versioned keys management (with domain support)

# Import connection management tools
from .connection_management import CONNECTION_TOOLS

# Import authentication connection management tools
from .connections_ldap import CONNECTION_LDAP_TOOLS      # LDAP connection management (with domain support)
from .connections_oidc import CONNECTION_OIDC_TOOLS      # OIDC connection management (with domain support)
from .connections_users import CONNECTION_USERS_TOOLS    # Connection users management (with domain support)

# Import cryptographic operation tools
from .crypto import CRYPTO_TOOLS         # Cryptographic operations (with domain support)

# Import unified CTE management tool (replaces monolithic CTE tool)
#from .cte_management_unified import CTE_TOOLS    # Unified CTE management (with domain support)
from .cte_management import CTE_TOOLS    # Unified CTE management (with domain support)

# Import cluster management tools
from .cluster_management import CLUSTER_MANAGEMENT_TOOLS        # Cluster management tools
from .clientmgmt import CLIENTMGMT_TOOLS                        # Client management tools
from .banner_management import BANNER_MANAGEMENT_TOOLS          # Banner management tools
from .interfaces_management import INTERFACES_MANAGEMENT_TOOLS  # Interface management tools
from .ddc_management import DDC_MANAGEMENT_TOOLS                # DDC management tools
from .cckm_management import CCKM_TOOLS                         # CCKM Management tools
from .data_protection import DATA_PROTECTION_TOOLS              # Application Data Protection tools

# Collect all available tools
ALL_TOOLS: list[Type[BaseTool]] = [
    # Core functionality (all tools now support optional domain parameters where applicable)
    *SYSTEM_TOOLS,          # 2 tools - system info (system-wide)
    *SERVICE_MGMT_TOOLS,    # 3 tools - service management (system-wide)
    *TOKEN_TOOLS,           # 5 tools - JWT/refresh tokens (with domain support)
    *USER_TOOLS,            # 10 tools - user management + password policies (with domain support)
    *GROUP_TOOLS,           # 8 tools - group management (with domain support)
    *GROUPMAP_TOOLS,        # 5 tools - group mappings (with domain support)
    *KEY_TOOLS,             # 18 tools - key management (with domain support)
    *KEY_POLICY_TOOLS,      # 5 tools - key policies (with domain support)
    *SECRET_TOOLS,          # 9 tools - secrets management (with domain support)
    *SCP_TOOLS,             # 2 tools - SCP public key management (with domain support)
    *TEMPLATE_TOOLS,        # 5 tools - template management (with domain support)
    *VKEYS_TOOLS,           # 4 tools - versioned keys management (with domain support)
    *AKEYLESS_TOOLS,        # 7 tools - Akeyless Gateway integration (with domain support)
    *BACKUP_TOOLS,          # 11 tools - backup management (with domain support)
    *BACKUPKEY_TOOLS,       # 8 tools - backup key management (with domain support)
    *LICENSING_TOOLS,       # 10 tools - licensing (system-wide)
    *ROTKEY_TOOLS,          # 4 tools - root of trust keys (system-wide)
    *RECORD_TOOLS,          # 7 tools - audit records & alarm configs (system-wide)
    *METRICS_TOOLS,         # 5 tools - Prometheus metrics (system-wide)
    *MKEKS_TOOLS,           # 3 tools - Master KEKs (system-wide)
    *NETWORK_TOOLS,         # 5 tools - network diagnostics (system-wide)
    *NTP_TOOLS,             # 5 tools - NTP server management (system-wide)
    *PROPERTIES_TOOLS,      # 4 tools - system properties (system-wide)
    *PROXY_TOOLS,           # 11 tools - proxy configurations (system-wide)
    *QUORUM_TOOLS,          # 14 tools - quorum management (with domain support)

    # Domain management (administrative domain operations)
    *DOMAIN_TOOLS,          # 16 tools - domain admin, KEKs, log redirection

    # Connection management
    *CONNECTION_TOOLS,      # 11 clean connection management tools

    # Authentication connection management
    *CONNECTION_LDAP_TOOLS,    # 6 tools - LDAP connection management (with domain support)
    *CONNECTION_OIDC_TOOLS,    # 6 tools - OIDC connection management (with domain support)
    *CONNECTION_USERS_TOOLS,   # 2 tools - Connection users management (with domain support)

    # Cryptographic operations
    *CRYPTO_TOOLS,            # 7 tools - Encryption, signing, FPE operations (with domain support)

    # CTE (CipherTrust Transparent Encryption) management - UNIFIED TOOL
    *CTE_TOOLS,               # 1 unified tool - modular CTE management with domain support

    # Additional management tools
    *CLUSTER_MANAGEMENT_TOOLS,    # 9 tools - Cluster management tools
    *CLIENTMGMT_TOOLS,            # 20 tools - Client management tools
    *BANNER_MANAGEMENT_TOOLS,     # 2 tools - Banner management tools
    *INTERFACES_MANAGEMENT_TOOLS, # 7 tools - Interface management tools
    *DDC_MANAGEMENT_TOOLS,        # 10 tools - DDC management tools
    *CCKM_TOOLS,                  # 1 unified tool - modular CCKM management with domain support
    *DATA_PROTECTION_TOOLS,       # 10 tools - Data Protection tools
]

all = ["BaseTool", "ALL_TOOLS"]