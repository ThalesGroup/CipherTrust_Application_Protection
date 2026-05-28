"""
Thales CDSP CSM Client for Thales CSM Akeyless Vault

This module provides a client for interacting with the Thales CSM Akeyless Vault API.
It handles authentication, token management, and provides methods for all secret operations.
"""

import logging
import time
from typing import Dict, Any, List, Optional
import httpx
import json

from .config import ThalesCDSPCSMConfig
from .exceptions import AuthenticationError, APIError, ValidationError

logger = logging.getLogger(__name__)


class ThalesCDSPCSMClient:
    """Client for interacting with Thales CSM Akeyless Vault API."""
    
    def __init__(self, config: ThalesCDSPCSMConfig):
        self.config = config
        self._token = None
        self._token_expiry = 0
        self._client = httpx.AsyncClient(
            timeout=30.0,
            verify=self.config.verify_ssl
        )
        
        # Validate configuration
        if not config.access_id or not config.access_key:
            raise ValidationError("AKEYLESS_ACCESS_ID and AKEYLESS_ACCESS_KEY must be set")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
    
    def _normalize_path(self, path: str) -> str:
        """
        Normalize a path to ensure it starts with / and is cleaned.
        
        Args:
            path: The path to normalize
            
        Returns:
            Normalized path starting with /
        """
        if not path:
            return "/"
        
        # Remove leading/trailing whitespace
        path = path.strip()
        
        # Ensure path starts with /
        if not path.startswith("/"):
            path = "/" + path
        
        # Remove duplicate slashes and normalize
        path = "/".join(part for part in path.split("/") if part)
        path = "/" + path
        
        return path
    
    async def _ensure_valid_token(self):
        """Ensure we have a valid authentication token."""
        current_time = time.time()
        
        # Check if token is expired or will expire soon (within 5 minutes)
        if not self._token or current_time >= (self._token_expiry - 300):
            await self._refresh_auth_token()
    
    async def _refresh_auth_token(self):
        """Refresh the authentication token."""
        try:
            self._token = await self._get_auth_token()
            # Set token expiry (Thales CSM Akeyless Vault tokens typically expire in 1 hour)
            self._token_expiry = time.time() + 3600
        except Exception as e:
            logger.error(f"Failed to refresh authentication token: {e}")
            raise AuthenticationError(f"Failed to refresh authentication token: {e}")
    
    async def _get_auth_token(self) -> str:
        """Get authentication token from Thales CSM Akeyless Vault."""
        auth_data = {
            "access-id": self.config.access_id,
            "access-key": self.config.access_key
        }
        
        try:
            response = await self._client.post(f"{self.config.api_url}/auth", json=auth_data)
            response.raise_for_status()
            result = response.json()
            
            if "token" not in result:
                raise AuthenticationError("No token in authentication response")
            
            return result["token"]
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise AuthenticationError(f"Authentication failed: {e}")
    
    async def _make_request(self, command: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the Thales CSM Akeyless Vault API."""
        await self._ensure_valid_token()
        
        url = f"{self.config.api_url}/{command}"
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add token to request data (AKeyless API expects token in body, not Authorization header)
        request_data = data.copy()
        request_data["token"] = self._token
        
        try:
            response = await self._client.post(url, json=request_data, headers=headers)
            response.raise_for_status()
            
            return response.json()
        except httpx.HTTPStatusError as e:
            error_data = self._parse_error_response(e.response)
            logger.error(f"HTTP error {e.response.status_code}: {error_data}")
            raise APIError(error_data, e.response.status_code, e.response.json() if e.response.content else None)
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise APIError(f"Request failed: {e}")
    
    def _parse_error_response(self, response: httpx.Response) -> str:
        """Parse error response and return user-friendly message."""
        try:
            error_data = response.json()
            error_msg = error_data.get("error", "")
            
            # Check for specific encryption key errors
            if "customer fragment" in error_msg.lower():
                return "Customer Fragment Not Available"
            elif "derived key" in error_msg.lower():
                return "Encryption Key Derivation Failed"
            elif "encryption" in error_msg.lower():
                return "Encryption Key Access Required"
            
            # Return generic error message
            return error_msg or f"HTTP {response.status_code} error"
            
        except Exception:
            return f"HTTP {response.status_code} error"
    
    def _looks_like_key_value(self, value: str) -> bool:
        """
        Detect if a string looks like key-value format.
        
        Args:
            value: String to check
            
        Returns:
            True if it appears to be key-value format
        """
        if not value or not isinstance(value, str):
            return False
            
        # Check for key=value pattern
        if '=' not in value:
            return False
            
        # Count key=value pairs
        pairs = value.replace(';', ',').replace('\n', ',').split(',')
        key_value_count = 0
        total_pairs = 0
        
        for pair in pairs:
            pair = pair.strip()
            if not pair:
                continue
                
            total_pairs += 1
            if '=' in pair:
                key, val = pair.split('=', 1)
                if key.strip() and val.strip():
                    key_value_count += 1
        
        # If more than 50% of pairs are key=value format, consider it key-value
        if total_pairs > 0 and (key_value_count / total_pairs) >= 0.5:
            return True
            
        return False

    def _convert_key_value_to_json(self, key_value_str: str) -> str:
        """
        Convert key-value string format to JSON format.
        
        Supports formats like:
        - key1=value1;key2=value2
        - key1=value1,key2=value2
        - key1=value1\nkey2=value2
        
        Args:
            key_value_str: String in key=value format
            
        Returns:
            JSON string representation
        """
        try:
            # Try different separators
            if ';' in key_value_str:
                pairs = key_value_str.split(';')
            elif ',' in key_value_str:
                pairs = key_value_str.split(',')
            elif '\n' in key_value_str:
                pairs = key_value_str.split('\n')
            else:
                # Single key-value pair
                pairs = [key_value_str]
            
            result = {}
            for pair in pairs:
                pair = pair.strip()
                if not pair:
                    continue
                    
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Handle quoted values
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    if key:  # Only add if key is not empty
                        result[key] = value
            
            return json.dumps(result)
            
        except Exception as e:
            logger.warning(f"Failed to convert key-value string to JSON: {e}")
            # Return original string if conversion fails
            return key_value_str

    async def create_static_secret(self, name: str, value: str, description: Optional[str] = None, 
                                   protection_key: Optional[str] = None, format: str = "text",
                                   accessibility: str = "regular", delete_protection: Optional[str] = None,
                                   multiline_value: bool = True, json: bool = False,
                                   tags: Optional[List[str]] = None, custom_field: Optional[Dict[str, str]] = None,
                                   inject_url: Optional[List[str]] = None, password: Optional[str] = None,
                                   username: Optional[str] = None, change_event: Optional[str] = None,
                                   max_versions: Optional[str] = None, metadata: Optional[str] = None) -> Dict[str, Any]:
        """Create a new static secret in Thales CSM Akeyless Vault with core parameter support."""
        full_path = self._normalize_path(name)
        
        logger.info(f"Creating static secret at full path: {full_path}...")
        
        # Auto-convert key-value format to JSON if needed
        processed_value = value
        if format == "key-value" or self._looks_like_key_value(value):
            processed_value = self._convert_key_value_to_json(value)
            logger.info(f"Auto-detected key-value format and converted to JSON: {processed_value}")
            # Update format to key-value for consistency
            format = "key-value"
        
        data = {
            "name": full_path,  # Thales CSM Akeyless Vault uses 'name' not 'path'
            "value": processed_value,
            "type": "generic",  # Thales CSM Akeyless Vault expects 'generic' not 'static-secret'
            "format": format,
            "accessibility": accessibility,
            "multiline_value": multiline_value,
            "json": json,
        }
        
        # Add optional parameters if provided
        if description:
            data["description"] = description
        if protection_key:
            data["protection_key"] = protection_key
        if delete_protection is not None:
            # Convert boolean to string format expected by API
            # True -> "1", False -> "0"
            data["delete_protection"] = "1" if delete_protection else "0"
        if tags:
            data["tags"] = tags
        if custom_field:
            data["custom-field"] = custom_field
        if inject_url:
            data["inject-url"] = inject_url
        if password:
            data["password"] = password
        if username:
            data["username"] = username
        if change_event:
            data["change-event"] = change_event
        if max_versions:
            data["max-versions"] = max_versions
        if metadata:
            data["metadata"] = metadata
        
        result = await self._make_request("create-secret", data)
        
        logger.info(f"Static secret '{name}' created successfully")
        return result
    
    async def list_customer_fragments(self, json_output: bool = False) -> Dict[str, Any]:
        """List all available customer fragments from Thales CSM Akeyless Vault."""
        logger.info("Listing all available customer fragments...")
        
        data = {
            "json": json_output
        }
        
        result = await self._make_request("gateway-list-customer-fragments", data)
        logger.info("Customer fragments listed successfully")
        return result
    
    async def export_customer_fragments(self, json: bool = False) -> Dict[str, Any]:
        """Export customer fragments from Thales CSM Akeyless Vault."""
        logger.info("Exporting customer fragments...")
        
        data = {
            "json": json
        }
        
        result = await self._make_request("gateway-download-customer-fragments", data)
        logger.info("Customer fragments exported successfully")
        return result
    
    async def create_api_key_auth_method(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new API key authentication method."""
        logger.info("Creating API key authentication method...")
        
        result = await self._make_request("auth-method-create-api-key", data)
        logger.info("API key authentication method created successfully")
        return result
    
    async def list_auth_methods(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """List authentication methods."""
        logger.info("Listing authentication methods...")
        
        result = await self._make_request("auth-method-list", data)
        logger.info("Authentication methods listed successfully")
        return result
    
    async def get_auth_method(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific authentication method."""
        logger.info("Getting authentication method...")
        
        result = await self._make_request("auth-method-get", data)
        logger.info("Authentication method retrieved successfully")
        return result
    
    async def delete_auth_method(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a specific authentication method."""
        logger.info("Deleting authentication method...")
        
        result = await self._make_request("auth-method-delete", data)
        logger.info("Authentication method deleted successfully")
        return result
    
    async def update_api_key_auth_method(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an API key authentication method."""
        logger.info("Updating API key authentication method...")
        
        result = await self._make_request("auth-method-update-api-key", data)
        logger.info("API key authentication method updated successfully")
        return result
    
    async def delete_auth_methods(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Delete all authentication methods within a specific path."""
        logger.info("Deleting authentication methods within path...")
        
        result = await self._make_request("delete-auth-methods", data)
        logger.info("Authentication methods deleted successfully")
        return result
    
    async def create_email_auth_method(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new email authentication method."""
        logger.info("Creating email authentication method...")
        
        result = await self._make_request("auth-method-create-email", data)
        logger.info("Email authentication method created successfully")
        return result
    
    async def update_email_auth_method(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an email authentication method."""
        logger.info("Updating email authentication method...")
        
        result = await self._make_request("auth-method-update-email", data)
        logger.info("Email authentication method updated successfully")
        return result
    
    async def _find_matching_customer_fragment(self, partial_uuid: str) -> Optional[str]:
        """
        Find a customer fragment that contains the partial UUID.
        
        Args:
            partial_uuid: Partial UUID string to search for
            
        Returns:
            Full UUID if found, None if no match
        """
        try:
            logger.info(f"Searching for customer fragment containing partial UUID: {partial_uuid}")
            
            # Get all customer fragments
            fragments_result = await self.list_customer_fragments(json_output=True)
            logger.info(f"Raw fragments result: {fragments_result}")
            
            # Try different response structures that might be returned
            fragments = None
            
            # Structure 1: customer_fragment_file_content.customer_fragments
            if fragments_result and 'customer_fragment_file_content' in fragments_result:
                customer_fragments_content = fragments_result['customer_fragment_file_content']
                if 'customer_fragments' in customer_fragments_content:
                    fragments = customer_fragments_content['customer_fragments']
                    logger.info("Using structure: customer_fragment_file_content.customer_fragments")
            
            # Structure 2: direct customer_fragments
            elif fragments_result and 'customer_fragments' in fragments_result:
                fragments = fragments_result['customer_fragments']
                logger.info("Using structure: customer_fragments")
            
            # Structure 3: direct fragments
            elif fragments_result and 'fragments' in fragments_result:
                fragments = fragments_result['fragments']
                logger.info("Using structure: fragments")
            
            # Structure 4: try to find any array that might contain customer fragments
            else:
                # Look for any array in the response that might contain customer fragments
                for key, value in fragments_result.items():
                    if isinstance(value, list) and len(value) > 0:
                        # Check if first item has an 'id' field (likely a customer fragment)
                        if value[0].get('id'):
                            fragments = value
                            logger.info(f"Using structure: {key} (detected as customer fragments)")
                            break
            
            if not fragments:
                logger.warning("No customer fragments found or invalid response format")
                logger.warning(f"Available keys in response: {list(fragments_result.keys()) if fragments_result else 'None'}")
                return None
            
            logger.info(f"Found {len(fragments)} customer fragments to search through")
            logger.info(f"Fragment IDs: {[f.get('id', 'NO_ID') for f in fragments]}")
            
            # Search for fragment containing the partial UUID
            # Handle MCP truncation by checking if the start of full UUID matches partial UUID
            for fragment in fragments:
                fragment_id = fragment.get('id', '')
                if fragment_id:
                    # Strategy 1: Direct substring match
                    if partial_uuid in fragment_id:
                        logger.info(f"Found matching customer fragment (direct match): {fragment_id}")
                        return fragment_id
                    
                    # Strategy 2: Check if fragment starts with the partial UUID (handling truncation)
                    if fragment_id.startswith(partial_uuid):
                        logger.info(f"Found matching customer fragment (prefix match): {fragment_id}")
                        return fragment_id
                    
                    # Strategy 3: Handle MCP mid-character truncation
                    # Try matching progressively shorter prefixes to handle truncation
                    for i in range(len(partial_uuid), 0, -1):
                        prefix = partial_uuid[:i]
                        if len(prefix) >= 10 and fragment_id.startswith(prefix):  # Minimum meaningful length
                            logger.info(f"Found matching customer fragment (prefix {i} chars): {fragment_id}")
                            return fragment_id
            
            logger.warning(f"No customer fragment found containing partial UUID: {partial_uuid}")
            return None
            
        except Exception as e:
            logger.error(f"Error searching for customer fragment: {e}")
            logger.error(f"Exception details: {type(e).__name__}: {str(e)}")
            return None
    
    async def create_dfc_key(self, name: str, alg: str, customer_frg_id: Optional[str] = None,
                             description: Optional[str] = None, auto_rotate: Optional[str] = None,
                             rotation_interval: Optional[str] = None, delete_protection: Optional[str] = None,
                             split_level: Optional[int] = None, tag: Optional[List[str]] = None,
                             generate_self_signed_certificate: Optional[bool] = None,
                             certificate_ttl: Optional[int] = None, certificate_common_name: Optional[str] = None,
                             certificate_organization: Optional[str] = None, certificate_country: Optional[str] = None,
                             certificate_province: Optional[str] = None, certificate_locality: Optional[str] = None,
                             certificate_digest_algo: Optional[str] = None, certificate_format: Optional[str] = None,
                             conf_file_data: Optional[str] = None, expiration_event_in: Optional[List[str]] = None,
                             rotation_event_in: Optional[List[str]] = None, metadata: Optional[str] = None) -> Dict[str, Any]:
        """Create a new DFC key in Thales CSM Akeyless Vault."""
        full_path = self._normalize_path(name)
        
        logger.info(f"Creating DFC key at full path: {full_path}...")
        
        data = {
            "name": full_path,
            "alg": alg
        }
        
        # Smart UUID matching: if customer_frg_id is provided, try to find the full UUID
        final_customer_frg_id = None
        if customer_frg_id:
            # Check if this looks like a partial UUID (less than 36 characters)
            if len(customer_frg_id) < 36:
                logger.info(f"Partial UUID detected ({len(customer_frg_id)} chars), searching for full match...")
                full_uuid = await self._find_matching_customer_fragment(customer_frg_id)
                if full_uuid:
                    final_customer_frg_id = full_uuid
                    logger.info(f"Using full UUID from search: {full_uuid}")
                else:
                    logger.warning(f"No matching customer fragment found for partial UUID: {customer_frg_id}")
                    # Fall back to using the partial UUID as-is
                    final_customer_frg_id = customer_frg_id
            else:
                # Full UUID provided, use as-is
                final_customer_frg_id = customer_frg_id
                logger.info(f"Full UUID provided: {customer_frg_id}")
        
        # Add optional parameters if provided
        if final_customer_frg_id:
            data["customer-frg-id"] = final_customer_frg_id
        if description:
            data["description"] = description
        
        # Handle auto-rotation parameters - only send if explicitly provided
        if auto_rotate is not None:
            data["auto-rotate"] = auto_rotate  # API expects string "true"/"false"
            # Only send rotation_interval if auto_rotate is "true"
            if auto_rotate == "true" and rotation_interval is not None:
                data["rotation-interval"] = rotation_interval  # API expects string
        # If auto_rotate not specified, don't send any rotation parameters
        # Let the API use its defaults (typically auto-rotation enabled with default period)
        
        if delete_protection is not None:
            # Convert boolean to string format expected by API
            # True -> "1", False -> "0"
            data["delete_protection"] = "1" if delete_protection else "0"
        if split_level:
            data["split-level"] = split_level
        if tag:
            data["tag"] = tag
        if generate_self_signed_certificate is not None:
            data["generate-self-signed-certificate"] = generate_self_signed_certificate
        if certificate_ttl:
            data["certificate-ttl"] = certificate_ttl
        if certificate_common_name:
            data["certificate-common-name"] = certificate_common_name
        if certificate_organization:
            data["certificate-organization"] = certificate_organization
        if certificate_country:
            data["certificate-country"] = certificate_country
        if certificate_province:
            data["certificate-province"] = certificate_province
        if certificate_locality:
            data["certificate-locality"] = certificate_locality
        if certificate_digest_algo:
            data["certificate-digest-algo"] = certificate_digest_algo
        if certificate_format:
            data["certificate-format"] = certificate_format
        if conf_file_data:
            data["conf-file-data"] = conf_file_data
        if expiration_event_in:
            data["expiration-event-in"] = expiration_event_in
        if rotation_event_in:
            data["rotation-event-in"] = rotation_event_in
        if metadata:
            data["metadata"] = metadata
        
        try:
            result = await self._make_request("create-dfc-key", data)
            logger.info(f"DFC key '{name}' created successfully")
            return result
        except Exception as e:
            # Enhance error messages for common DFC key creation issues
            error_msg = str(e)
            if "auto-rotate" in error_msg.lower() and "rsa" in alg.lower():
                enhanced_error = (
                    f"❌ RSA key creation failed due to auto-rotation incompatibility!\n"
                    f"  • Key type: {alg}\n"
                    f"  • Error: {error_msg}\n"
                    f"  • Reason: RSA keys (asymmetric) do not support auto-rotation\n"
                    f"  • Solution: Set auto_rotate to 'false' for RSA keys, or use AES key types for auto-rotation"
                )
                logger.error(enhanced_error)
                raise ValueError(enhanced_error)
            elif "rotation" in error_msg.lower():
                enhanced_error = (
                    f"❌ DFC key creation failed due to rotation configuration!\n"
                    f"  • Key type: {alg}\n"
                    f"  • Error: {error_msg}\n"
                    f"  • Common issues:\n"
                    f"    - RSA keys don't support auto-rotation\n"
                    f"    - rotation_interval requires auto_rotate='true'\n"
                    f"    - Invalid rotation period (should be 7-365 days)"
                )
                logger.error(enhanced_error)
                raise ValueError(enhanced_error)
            else:
                # Re-raise the original error
                raise
    
    async def list_items(self, path: Optional[str] = None, auto_pagination: bool = True, pagination_token: Optional[str] = None, 
                          filter_by: Optional[str] = None, advanced_filter: Optional[str] = None, minimal_view: Optional[bool] = None, 
                          tag: Optional[str] = None, item_type: Optional[List[str]] = None) -> Dict[str, Any]:
        """List items in Thales CSM Akeyless Vault with auto-pagination and filtering support."""
        full_path = self._normalize_path(path) if path else "/"
        
        logger.info(f"Listing secrets from path: {full_path}")
        
        data = {
            "path": full_path,
            "pagination-token": pagination_token or "",
            "limit": 1000,  # Maximum allowed by API
            "accessibility": "regular",
            "auto-pagination": "enabled" if auto_pagination else "disabled",
            "json": False,
            "sra-only": False
        }
        
        # Add filtering parameters if provided
        if filter_by:
            data["filter"] = filter_by
        if advanced_filter:
            data["advanced-filter"] = advanced_filter
        if minimal_view is not None:
            data["minimal-view"] = minimal_view
        if tag:
            data["tag"] = tag
        if item_type:
            data["type"] = item_type
        
        result = await self._make_request("list-items", data)
        
        # Handle auto-pagination if enabled
        if auto_pagination and result.get("next_page_token"):
            all_items = result.get("items", [])
            next_token = result.get("next_page_token")
            
            while next_token:
                data["pagination-token"] = next_token
                page_result = await self._make_request("list-items", data)
                all_items.extend(page_result.get("items", []))
                next_token = page_result.get("next_page_token")
            
            result["items"] = all_items
            result["next_page_token"] = None
        
        return result
    
    async def get_secret(self, names: List[str]) -> Dict[str, Any]:
        """Get secret values from Thales CSM Akeyless Vault. Supports both single and multiple secrets."""
        full_names = [self._normalize_path(name) for name in names]
        
        logger.info(f"Getting secrets: {full_names}")
        
        data = {
            "names": full_names,  # Thales CSM Akeyless Vault expects 'names' array for both single and multiple
            "ignore-cache": "false",  # String value as expected by API
            "json": False  # Boolean value as expected by API
        }
        
        result = await self._make_request("get-secret-value", data)
        return result
    
    async def delete_item(self, name: str, accessibility: str = "regular", delete_immediately: bool = False, 
                         delete_in_days: int = 7, version: int = -1) -> Dict[str, Any]:
        """Delete a single item from Thales CSM Akeyless Vault."""
        full_name = self._normalize_path(name)
        
        logger.info(f"Deleting item: {full_name}")
        
        data = {
            "name": full_name,  # Thales CSM Akeyless Vault uses 'name' not 'path'
            "accessibility": accessibility,
            "delete-immediately": delete_immediately,
            "version": version
        }
        
        # Set delete-in-days based on delete_immediately flag
        if delete_immediately:
            # For immediate deletion, delete-in-days must be -1
            data["delete-in-days"] = -1
        elif delete_in_days is not None:
            data["delete-in-days"] = delete_in_days
        
        logger.info(f"Delete item request data: {data}")
        
        result = await self._make_request("delete-item", data)
        return result
    
    async def delete_items(self, path: str = None, items: List[str] = None) -> Dict[str, Any]:
        """Delete multiple items from Thales CSM Akeyless Vault by directory path or specific item list."""
        data = {}
        
        if path:
            full_path = self._normalize_path(path)
            data["path"] = full_path
            logger.info(f"Deleting all items from directory: {full_path}")
        elif items:
            full_items = [self._normalize_path(item) for item in items]
            data["item"] = full_items
            logger.info(f"Deleting specific items: {full_items}")
        else:
            raise ValidationError("Either 'path' or 'items' must be provided")
        
        result = await self._make_request("delete-items", data)
        return result
    
    async def update_secret_value(self, name: str, value: str, accessibility: str = "regular", 
                                 custom_field: Optional[Dict[str, str]] = None, format: str = "text",
                                 inject_url: Optional[List[str]] = None, json: bool = False,
                                 keep_prev_version: Optional[str] = None, key: Optional[str] = None,
                                 last_version: int = 0, multiline: bool = True, password: Optional[str] = None,
                                 username: Optional[str] = None) -> Dict[str, Any]:
        """Update the value of an existing secret in Thales CSM Akeyless Vault."""
        full_path = self._normalize_path(name)
        
        logger.info(f"Updating secret value at full path: {full_path}...")
        
        data = {
            "name": full_path,
            "value": value,
            "accessibility": accessibility,
            "format": format,
            "json": json,
            "multiline": multiline,
            "last_version": last_version
        }
        
        # Add optional parameters if provided
        if custom_field:
            data["custom-field"] = custom_field
        if inject_url:
            data["inject-url"] = inject_url
        if keep_prev_version:
            data["keep-prev-version"] = keep_prev_version
        if key:
            data["key"] = key
        if password:
            data["password"] = password
        if username:
            data["username"] = username
        
        result = await self._make_request("update-secret-val", data)
        logger.info(f"Secret '{name}' value updated successfully")
        return result

    async def update_item(self, name: str, new_name: Optional[str] = None, 
                          description: Optional[str] = None, accessibility: str = "regular",
                          delete_protection: Optional[str] = None, change_event: Optional[str] = None,
                          max_versions: Optional[str] = None, add_tags: Optional[List[str]] = None,
                          rm_tags: Optional[List[str]] = None, json: bool = False,
                          rotate_after_disconnect: Optional[str] = None,
                          expiration_event_in: Optional[List[str]] = None,
                          rotation_event_in: Optional[List[str]] = None,
                          provider_type: Optional[str] = None, cert_file_data: Optional[str] = None,
                          certificate_format: Optional[str] = None, host_provider: Optional[str] = None,
                          new_metadata: Optional[str] = None) -> Dict[str, Any]:
        """Update item properties in Thales CSM Akeyless Vault."""
        full_path = self._normalize_path(name)
        
        logger.info(f"Updating item at full path: {full_path}...")
        
        data = {
            "name": full_path,
            "accessibility": accessibility,
            "json": json
        }
        
        # Add optional parameters if provided
        if new_name:
            data["new-name"] = new_name
        if description:
            data["description"] = description
        if delete_protection is not None:
            # Convert boolean to string format expected by API
            # True -> "1", False -> "0"
            data["delete_protection"] = "1" if delete_protection else "0"
        if change_event:
            data["change-event"] = change_event
        if max_versions:
            data["max-versions"] = max_versions
        if add_tags:
            data["add-tag"] = add_tags
        if rm_tags:
            data["rm-tag"] = rm_tags
        if rotate_after_disconnect:
            data["rotate-after-disconnect"] = rotate_after_disconnect
        if expiration_event_in:
            data["expiration-event-in"] = expiration_event_in
        if rotation_event_in:
            data["rotation-event-in"] = rotation_event_in
        if provider_type:
            data["ProviderType"] = provider_type
        if cert_file_data:
            data["cert-file-data"] = cert_file_data
        if certificate_format:
            data["certificate-format"] = certificate_format
        if host_provider:
            data["host-provider"] = host_provider
        if new_metadata:
            data["new-metadata"] = new_metadata
        
        result = await self._make_request("update-item", data)
        logger.info(f"Item '{name}' updated successfully")
        return result

    async def set_item_state(self, name: str, desired_state: str, json: bool = False, version: int = 0) -> Dict[str, Any]:
        """Set the state of an item in Thales CSM Akeyless Vault (Enabled/Disabled)."""
        full_path = self._normalize_path(name)
        
        logger.info(f"Setting item state at full path: {full_path} to '{desired_state}'...")
        
        data = {
            "name": full_path,
            "desired-state": desired_state,
            "json": json,
            "version": version
        }
        
        result = await self._make_request("set-item-state", data)
        logger.info(f"Item '{name}' state set to '{desired_state}' successfully")
        return result
    
    async def update_rotation_settings(self, name: str, auto_rotate: bool, rotation_interval: Optional[int] = None,
                                      rotation_event_in: Optional[List[str]] = None, json: bool = False) -> Dict[str, Any]:
        """Update rotation settings for an item in Thales CSM Akeyless Vault."""
        full_path = self._normalize_path(name)
        
        logger.info(f"Updating rotation settings at full path: {full_path}...")
        
        data = {
            "name": full_path,
            "auto-rotate": auto_rotate,  # Send as boolean, not string
            "json": json
        }
        
        # Add optional parameters if provided
        # Allow rotation_interval to be set independently (API will handle validation)
        if rotation_interval is not None:
            data["rotation-interval"] = rotation_interval
        if rotation_event_in:
            data["rotation-event-in"] = rotation_event_in
        
        result = await self._make_request("update-rotation-settings", data)
        logger.info(f"Rotation settings for '{name}' updated successfully")
        return result

    async def gateway_update_item(self, name: str, protection_key: Optional[str] = None,
                                 description: Optional[str] = None, add_tags: Optional[List[str]] = None,
                                 rm_tags: Optional[List[str]] = None, delete_protection: Optional[bool] = None,
                                 keep_prev_version: Optional[bool] = None, item_type: str = "STATIC_SECRET",
                                 json: bool = False) -> Dict[str, Any]:
        """Update item properties using the gateway-update-item endpoint (includes protection key updates)."""
        full_path = self._normalize_path(name)
        
        logger.info(f"Updating item at full path: {full_path} using gateway-update-item...")
        
        data = {
            "name": full_path,
            "json": json
        }
        
        # Only add type if explicitly provided and not the default
        if item_type and item_type != "STATIC_SECRET":
            data["type"] = item_type
        else:
            # Use generic as default since STATIC_SECRET seems to cause issues
            data["type"] = "generic"
        
        # Add optional parameters if provided
        if protection_key is not None:
            data["key"] = protection_key  # This is the protection key parameter
        if description:
            data["description"] = description
        if add_tags:
            data["add-tag"] = add_tags
        if rm_tags:
            data["rm-tag"] = rm_tags
        if delete_protection is not None:
            # Convert boolean to string format expected by API
            # True -> "1", False -> "0"
            data["delete_protection"] = "1" if delete_protection else "0"
        if keep_prev_version is not None:
            data["keep-prev-version"] = str(keep_prev_version).lower()
        
        result = await self._make_request("gateway-update-item", data)
        logger.info(f"Item '{name}' updated successfully using gateway-update-item")
        return result 

    async def rotate_key(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Rotate a DFC key on demand with new certificate and key data."""
        logger.info(f"Rotating DFC key: {data.get('name', 'unknown')}")
        
        result = await self._make_request("rotate-key", data)
        logger.info(f"DFC key '{data.get('name', 'unknown')}' rotated successfully")
        return result

    async def list_gateways(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """List available Akeyless gateways."""
        logger.info("Listing available gateways")
        
        result = await self._make_request("list-gateways", data)
        logger.info("Gateways listed successfully")
        return result

    async def list_shared_items(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """List shared items in the secrets manager."""
        logger.info(f"Listing shared items with accessibility: {data.get('accessibility', 'regular')}")
        
        result = await self._make_request("list-shared-items", data)
        logger.info("Shared items listed successfully")
        return result 