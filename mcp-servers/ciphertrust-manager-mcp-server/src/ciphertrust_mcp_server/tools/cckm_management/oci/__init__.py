"""OCI CCKM operations module."""

from .keys import get_key_operations, build_key_command
from .vaults import get_vault_operations, build_vault_command
from .compartments import get_compartment_operations, build_compartment_command
from .external_vaults import get_external_vault_operations, build_external_vault_command
from .issuers import get_issuer_operations, build_issuer_command
from .regions import get_region_operations, build_region_command
from .tenancy import get_tenancy_operations, build_tenancy_command
from .reports import get_reports_operations, build_reports_command
from .smart_id_resolver import OCISmartIDResolver

__all__ = [
    "get_key_operations", "build_key_command",
    "get_vault_operations", "build_vault_command", 
    "get_compartment_operations", "build_compartment_command",
    "OCISmartIDResolver"
] 