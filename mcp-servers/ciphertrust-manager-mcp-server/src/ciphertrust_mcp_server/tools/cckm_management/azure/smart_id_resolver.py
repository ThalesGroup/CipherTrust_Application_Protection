"""Smart ID resolver for Azure operations."""

import json
import re
from typing import Any, Dict, Optional, Union


class AzureSmartIDResolver:
    """Smart ID resolver for Azure resources (keys, certificates, vaults, secrets)."""
    
    def __init__(self, operations):
        self.operations = operations
        # Cache for subscription context to improve resolution
        self._subscription_cache = {}
    
    def set_subscription_context(self, subscription_id: str, connection_identifier: str):
        """Set subscription context for better resolution."""
        self._subscription_cache[subscription_id] = {
            "connection_identifier": connection_identifier,
            "last_used": True
        }
    
    def get_subscription_context(self, subscription_id: str = None) -> Dict[str, Any]:
        """Get subscription context for resolution."""
        if subscription_id and subscription_id in self._subscription_cache:
            return self._subscription_cache[subscription_id]
        
        # Return the most recently used context if no specific subscription
        for sub_id, context in self._subscription_cache.items():
            if context.get("last_used"):
                return {"subscription_id": sub_id, **context}
        
        return {}
    
    def is_uuid(self, identifier: str) -> bool:
        """Check if the identifier is a UUID."""
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, identifier.lower()))
    
    def is_azure_resource_id(self, identifier: str) -> bool:
        """Check if the identifier is an Azure resource ID."""
        # Azure resource IDs follow pattern: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.KeyVault/vaults/{vault}/[keys|certificates|secrets]/{name}
        azure_id_pattern = r'^/subscriptions/[^/]+/resourceGroups/[^/]+/providers/Microsoft\.KeyVault/vaults/[^/]+/(keys|certificates|secrets)/[^/]+$'
        return bool(re.match(azure_id_pattern, identifier))
    
    def normalize_vault_name(self, vault_identifier: str, subscription_id: str = None) -> str:
        """Normalize vault name to handle CCKM's naming convention."""
        # CCKM stores vaults as "vault-name::subscription-id"
        if "::" in vault_identifier:
            return vault_identifier
        
        # If we have subscription context, try to construct the full name
        if subscription_id:
            return f"{vault_identifier}::{subscription_id}"
        
        # Try to get from cache
        context = self.get_subscription_context()
        if context.get("subscription_id"):
            return f"{vault_identifier}::{context['subscription_id']}"
        
        return vault_identifier
    
    async def resolve_key_id(self, key_identifier: str, azure_params: Dict[str, Any], cloud_provider: str = "azure") -> str:
        """Resolve key identifier to UUID."""
        # If already a UUID, return as is
        if self.is_uuid(key_identifier):
            return key_identifier
        
        # If it's an Azure resource ID, return as is (Azure accepts these)
        if self.is_azure_resource_id(key_identifier):
            return key_identifier
        
        # Try multiple search strategies
        search_strategies = [
            {"key_name": key_identifier},  # Search by exact name
            {}  # Get all keys and search through them
        ]
        
        for strategy in search_strategies:
            # Prepare the list parameters for key search
            list_params = {
                "cloud_provider": cloud_provider,
                "azure_keys_params": strategy.copy()
            }
            
            # Call the list operation
            try:
                result = await self.operations.execute_operation("keys_list", list_params)
                
                # Parse the result
                if isinstance(result, str):
                    result_data = json.loads(result)
                else:
                    result_data = result
                
                # Look for matching keys
                keys = result_data.get("resources", [])
                if not keys:
                    # Try nested data.resources structure
                    data = result_data.get("data", {})
                    if isinstance(data, dict):
                        keys = data.get("resources", [])
                    if not keys:
                        keys = result_data.get("data", [])
                
                # Find exact name match
                for key in keys:
                    key_name = key.get("key_name", "")
                    name = key.get("name", "")
                    
                    # Check multiple name variations
                    if (key_name == key_identifier or 
                        name == key_identifier or
                        key.get("azure_name") == key_identifier):
                        return key.get("id", key_identifier)
                
            except Exception:
                continue
        
        # If no match found, return original identifier
        return key_identifier
    
    async def resolve_certificate_id(self, cert_identifier: str, azure_params: Dict[str, Any], cloud_provider: str = "azure") -> str:
        """Resolve certificate identifier to UUID."""
        # If already a UUID, return as is
        if self.is_uuid(cert_identifier):
            return cert_identifier
        
        # If it's an Azure resource ID, return as is
        if self.is_azure_resource_id(cert_identifier):
            return cert_identifier
        
        # Prepare the list parameters for certificate search
        list_params = {
            "cloud_provider": cloud_provider,
            "azure_certificates_params": {}
        }
        
        # Add vault filter if available
        if "vault_name" in azure_params:
            list_params["azure_certificates_params"]["vault_name"] = azure_params["vault_name"]
        if "key_vault" in azure_params:
            list_params["azure_certificates_params"]["vault_name"] = azure_params["key_vault"]
        
        # Call the list operation
        try:
            result = await self.operations.execute_operation("certificates_list", list_params)
            
            # Parse the result
            if isinstance(result, str):
                result_data = json.loads(result)
            else:
                result_data = result
            
            # Look for matching certificates
            certificates = result_data.get("resources", [])
            if not certificates:
                # Try nested data.resources structure
                data = result_data.get("data", {})
                if isinstance(data, dict):
                    certificates = data.get("resources", [])
                if not certificates:
                    certificates = result_data.get("data", [])
            
            # Find exact name match
            for cert in certificates:
                if cert.get("name") == cert_identifier:
                    return cert.get("id", cert_identifier)
            
            # If no exact match found, return original identifier
            return cert_identifier
            
        except Exception:
            # If resolution fails, return original identifier
            return cert_identifier
    
    async def resolve_vault_id(self, vault_identifier: str, azure_params: Dict[str, Any], cloud_provider: str = "azure") -> str:
        """Resolve vault identifier to UUID."""
        # If already a UUID, return as is
        if self.is_uuid(vault_identifier):
            return vault_identifier
        
        # If it's an Azure resource ID, return as is
        if "/subscriptions/" in vault_identifier and "/providers/Microsoft.KeyVault/vaults/" in vault_identifier:
            return vault_identifier
        
        # Get subscription context
        subscription_id = azure_params.get("subscription_id")
        context = self.get_subscription_context(subscription_id)
        
        # Normalize the vault name to CCKM format
        normalized_name = self.normalize_vault_name(vault_identifier, subscription_id)
        
        # Try multiple search strategies
        search_strategies = [
            {},  # Get all vaults and search through them
            {"subscription_id": subscription_id} if subscription_id else {},
            {"subscription_id": context.get("subscription_id")} if context.get("subscription_id") else {}
        ]
        
        for strategy in search_strategies:
            if not strategy:  # Skip empty strategies
                strategy = {}
                
            # Prepare the list parameters for vault search
            list_params = {
                "cloud_provider": cloud_provider,
                "azure_vaults_params": strategy.copy()
            }
            
            # Call the list operation
            try:
                result = await self.operations.execute_operation("vaults_list", list_params)
                
                # Parse the result
                if isinstance(result, str):
                    result_data = json.loads(result)
                else:
                    result_data = result
                
                # Look for matching vaults
                vaults = result_data.get("resources", [])
                if not vaults:
                    # Try nested data.resources structure
                    data = result_data.get("data", {})
                    if isinstance(data, dict):
                        vaults = data.get("resources", [])
                    if not vaults:
                        vaults = result_data.get("data", [])
                
                # Find exact name match (try multiple name variations)
                for vault in vaults:
                    vault_name = vault.get("name", "")
                    azure_name = vault.get("azure_name", "")
                    
                    # Check multiple name variations
                    if (vault_name == vault_identifier or 
                        vault_name == normalized_name or
                        azure_name == vault_identifier or
                        vault.get("vault_name") == vault_identifier or
                        vault_name.startswith(f"{vault_identifier}::")):
                        return vault.get("id", vault_identifier)
                
            except Exception:
                continue
        
        # If no match found, return original identifier
        return vault_identifier
    
    async def resolve_secret_id(self, secret_identifier: str, azure_params: Dict[str, Any], cloud_provider: str = "azure") -> str:
        """Resolve secret identifier to UUID."""
        # If already a UUID, return as is
        if self.is_uuid(secret_identifier):
            return secret_identifier
        
        # If it's an Azure resource ID, return as is
        if self.is_azure_resource_id(secret_identifier):
            return secret_identifier
        
        # Prepare the list parameters for secret search
        list_params = {
            "cloud_provider": cloud_provider,
            "azure_secrets_params": {}
        }
        
        # Add vault filter if available
        if "vault_name" in azure_params:
            list_params["azure_secrets_params"]["vault_name"] = azure_params["vault_name"]
        if "key_vault" in azure_params:
            list_params["azure_secrets_params"]["vault_name"] = azure_params["key_vault"]
        
        # Call the list operation
        try:
            result = await self.operations.execute_operation("secrets_list", list_params)
            
            # Parse the result
            if isinstance(result, str):
                result_data = json.loads(result)
            else:
                result_data = result
            
            # Look for matching secrets
            secrets = result_data.get("resources", [])
            if not secrets:
                # Try nested data.resources structure
                data = result_data.get("data", {})
                if isinstance(data, dict):
                    secrets = data.get("resources", [])
                if not secrets:
                    secrets = result_data.get("data", [])
            
            # Find exact name match
            for secret in secrets:
                secret_name = secret.get("secret_name", "")
                name = secret.get("name", "")
                
                # Check multiple name variations
                if (secret_name == secret_identifier or 
                    name == secret_identifier):
                    return secret.get("id", secret_identifier)
            
            # If no exact match found, return original identifier
            return secret_identifier
            
        except Exception:
            # If resolution fails, return original identifier
            return secret_identifier
