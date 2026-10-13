"""
Thales CDSP CSM MCP Server - Base Authentication Method Class

This module provides the base class for all authentication method types
with common functionality and parameters.
"""

import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from ...core.client import ThalesCDSPCSMClient

logger = logging.getLogger(__name__)


class BaseAuthMethod(ABC):
    """Base class for authentication method implementations."""
    
    def __init__(self, client: ThalesCDSPCSMClient):
        self.client = client
    
    @abstractmethod
    async def create(self, **kwargs) -> Dict[str, Any]:
        """Create a new authentication method of this type."""
        pass
    
    @abstractmethod
    async def update(self, **kwargs) -> Dict[str, Any]:
        """Update an existing authentication method of this type."""
        pass
    
    def _prepare_common_data(self, **kwargs) -> Dict[str, Any]:
        """Prepare common data fields for authentication methods."""
        common_fields = [
            'access_expires', 'audit_logs_claims', 'bound_ips', 'delete_protection',
            'description', 'expiration_event_in', 'force_sub_claims', 'gw_bound_ips',
            'json', 'jwt_ttl', 'product_type', 'accessibility', 'tags'
        ]
        
        data = {}
        for field in common_fields:
            if field in kwargs and kwargs[field] is not None:
                # Convert field names to API format
                api_field = field.replace('_', '-')
                data[api_field] = kwargs[field]
        
        return data
    
    def _remove_none_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove None values from data to avoid API errors."""
        return {k: v for k, v in data.items() if v is not None} 