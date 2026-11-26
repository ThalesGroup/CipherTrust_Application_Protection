"""
Thales CDSP CSM (CipherTrust Secrets Management) MCP Server

A Model Context Protocol (MCP) server for managing secrets in Thales CSM (CipherTrust Secrets Management) Akeyless Vault
"""

from .server import ThalesCDSPCSMMCPServer
from .core import ThalesCDSPCSMConfig, ThalesCDSPCSMClient

__version__ = "1.0.0"
__author__ = "Thales CDSP Team"
__mcp_protocol_version_latest__ = "2025-06-18"
__mcp_protocol_version_backward__ = "2025-03-26"
__mcp_protocol_version__ = __mcp_protocol_version_latest__  # Default to latest
__all__ = ["ThalesCDSPCSMMCPServer", "ThalesCDSPCSMConfig", "ThalesCDSPCSMClient"] 