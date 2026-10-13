"""
Thales CDSP CSM MCP Server - Tools Package

This package contains all the MCP tools for interacting with Thales CSM Akeyless Vault.
"""

from .base import ThalesCDSPCSMTools, BaseThalesCDSPCSMTool

# Consolidated tools from their new domain-specific directories
from .secrets.manage_secrets import ManageSecretsTools
from .dfc_keys.manage_dfc_keys import ManageDFCKeysTools
from .auth_methods.auth_methods_manager import AuthMethodsManager
from .customer_fragments.manage_customer_fragments import ManageCustomerFragmentsTools
from .guidelines.security_guidelines import SecurityGuidelinesTools
from .rotation.manage_rotation import ManageRotationTools
from .roles.manage_roles import ManageRolesTools
from .targets.manage_targets import ManageTargetsTools
from .monitoring.manage_analytics import ManageAnalyticsTools
from .administration.manage_account import ManageAccountTools
from .api_reference import GetAPIReferenceTools


__all__ = [
    # Base classes
    "ThalesCDSPCSMTools",
    "BaseThalesCDSPCSMTool",
    
    # Consolidated tools
    "ManageSecretsTools",
    "ManageDFCKeysTools",
    "AuthMethodsManager",
    "ManageCustomerFragmentsTools",
    "SecurityGuidelinesTools",
    "ManageRotationTools",
    "ManageRolesTools",
    "ManageTargetsTools",
    "ManageAnalyticsTools",
    "ManageAccountTools",
    "GetAPIReferenceTools",

] 