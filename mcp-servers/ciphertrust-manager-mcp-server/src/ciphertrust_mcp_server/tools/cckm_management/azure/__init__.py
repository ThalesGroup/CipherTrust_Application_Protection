"""Azure CCKM operations module."""

from .keys import get_key_operations, build_key_command
from .certificates import get_certificate_operations, build_certificate_command
from .vaults import get_vault_operations, build_vault_command
from .secrets import get_secret_operations, build_secret_command
from .common import (
    get_subscription_operations, get_report_operations, get_bulkjob_operations,
    build_common_command
)
from .smart_id_resolver import AzureSmartIDResolver

__all__ = [
    "get_key_operations", "build_key_command",
    "get_certificate_operations", "build_certificate_command", 
    "get_vault_operations", "build_vault_command",
    "get_secret_operations", "build_secret_command",
    "get_subscription_operations", "get_report_operations", "get_bulkjob_operations",
    "build_common_command",
    "AzureSmartIDResolver"
] 