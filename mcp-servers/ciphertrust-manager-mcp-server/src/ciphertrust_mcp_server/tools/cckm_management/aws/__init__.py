"""AWS CCKM operations module."""

from .keys import get_key_operations, build_key_command
from .kms import get_kms_operations, build_kms_command
from .iam import get_iam_operations, build_iam_command
from .reports import get_reports_operations, build_reports_command
from .bulkjob import get_bulkjob_operations, build_bulkjob_command
from .custom_key_stores import get_custom_key_stores_operations, build_custom_key_stores_command
from .logs import get_logs_operations, build_logs_command
from .smart_id_resolver import SmartIDResolver, create_smart_resolver

__all__ = [
    "get_key_operations", "build_key_command",
    "get_kms_operations", "build_kms_command",
    "get_iam_operations", "build_iam_command", 
    "get_reports_operations", "build_reports_command",
    "get_bulkjob_operations", "build_bulkjob_command",
    "get_custom_key_stores_operations", "build_custom_key_stores_command",
    "get_logs_operations", "build_logs_command",
    "SmartIDResolver", "create_smart_resolver"
]
