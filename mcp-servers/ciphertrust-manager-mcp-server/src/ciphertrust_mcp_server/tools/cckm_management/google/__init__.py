"""Google Cloud CCKM operations modules."""

from .keys import get_key_operations, build_key_command
from .keyrings import get_keyring_operations, build_keyring_command
from .projects import get_project_operations, build_project_command
from .locations import get_location_operations, build_location_command
from .reports import get_reports_operations, build_reports_command
from .smart_id_resolver import create_google_smart_resolver

__all__ = [
    "get_key_operations", "build_key_command",
    "get_keyring_operations", "build_keyring_command", 
    "get_project_operations", "build_project_command",
    "get_location_operations", "build_location_command",
    "get_reports_operations", "build_reports_command",
    "create_google_smart_resolver"
] 