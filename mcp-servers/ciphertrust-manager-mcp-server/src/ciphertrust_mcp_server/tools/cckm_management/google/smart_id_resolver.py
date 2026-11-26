"""Smart ID Resolution for Google Cloud CCKM operations."""

import re
from typing import Protocol, Optional, Dict, Any, List
import asyncio


class OperationsProtocol(Protocol):
    """Protocol for operations interface to avoid circular imports."""
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute an operation."""
        ...


class GoogleSmartIDResolver:
    """Resolves Google Cloud key names and resource URLs to proper key IDs automatically."""
    
    def __init__(self, operations: OperationsProtocol):
        self.operations = operations
        self._cache = {}  # Simple cache for resolved IDs
        self._location_cache = {}  # Cache for project locations
        self._keyring_location_cache = {}  # Cache for keyring-to-location mappings
    
    def is_uuid(self, identifier: str) -> bool:
        """Check if the identifier is a UUID."""
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, identifier.lower()))
    
    # Common GCP locations to try when searching
    COMMON_LOCATIONS = [
        'global', 'us-central1', 'us-east1', 'us-west1', 'us-west2', 
        'europe-west1', 'europe-west2', 'europe-west3', 'europe-west4',
        'asia-east1', 'asia-northeast1', 'asia-southeast1', 'australia-southeast1'
    ]
    
    def is_resource_url(self, identifier: str) -> bool:
        """Check if the identifier is a Google Cloud resource URL."""
        return bool(re.match(r'^projects/[^/]+/locations/[^/]+/keyRings/[^/]+/cryptoKeys/[^/]+', identifier))
    
    def is_keyring_resource_url(self, identifier: str) -> bool:
        """Check if the identifier is a Google Cloud keyring resource URL."""
        return bool(re.match(r'^projects/[^/]+/locations/[^/]+/keyRings/[^/]+', identifier))
    
    def is_key_name_only(self, identifier: str) -> bool:
        """Check if the identifier is just a key name (no path components)."""
        return '/' not in identifier and not self.is_resource_url(identifier)
    
    def is_keyring_name_only(self, identifier: str) -> bool:
        """Check if the identifier is just a keyring name (no path components)."""
        return '/' not in identifier and not self.is_keyring_resource_url(identifier)
    
    def is_partial_path(self, identifier: str) -> bool:
        """Check if the identifier is a partial path (keyring/key format)."""
        parts = identifier.split('/')
        return len(parts) == 2 and not self.is_resource_url(identifier)
    
    def needs_resolution(self, identifier: str) -> bool:
        """Check if the identifier needs resolution to a full resource URL."""
        if not identifier:
            return False
        # If it's already a UUID, no resolution needed
        if self.is_uuid(identifier):
            return False
        # If it's already a full resource URL, no resolution needed
        if self.is_resource_url(identifier) or self.is_keyring_resource_url(identifier):
            return False
        # If it's a key name only or partial path, it needs resolution
        return self.is_key_name_only(identifier) or self.is_partial_path(identifier)
    
    def needs_keyring_resolution(self, identifier: str) -> bool:
        """Check if the keyring identifier needs resolution."""
        if not identifier:
            return False
        if self.is_keyring_resource_url(identifier):
            return False
        return self.is_keyring_name_only(identifier)
    
    def extract_components_from_url(self, resource_url: str) -> Optional[Dict[str, str]]:
        """Extract project, location, keyring, and key from a resource URL."""
        # Try key URL pattern first
        key_pattern = r'^projects/([^/]+)/locations/([^/]+)/keyRings/([^/]+)/cryptoKeys/([^/]+)'
        key_match = re.match(key_pattern, resource_url)
        if key_match:
            return {
                'project_id': key_match.group(1),
                'location': key_match.group(2),
                'key_ring': key_match.group(3),
                'key_name': key_match.group(4)
            }
        
        # Try keyring URL pattern
        keyring_pattern = r'^projects/([^/]+)/locations/([^/]+)/keyRings/([^/]+)'
        keyring_match = re.match(keyring_pattern, resource_url)
        if keyring_match:
            return {
                'project_id': keyring_match.group(1),
                'location': keyring_match.group(2),
                'key_ring': keyring_match.group(3)
            }
        
        return None
    
    def construct_full_resource_name(self, resource_type: str, project_id: str, location: str, resource_name: str) -> str:
        """
        Construct full GCP resource name in the format:
        projects/{project_id}/locations/{location}/{resource_type}/{resource_name}
        
        Args:
            resource_type: The resource type (e.g., 'keyRings', 'cryptoKeys')
            project_id: GCP project ID
            location: GCP location (e.g., 'global', 'us-central1')
            resource_name: The resource name
        
        Returns:
            Full GCP resource name
        """
        return f"projects/{project_id}/locations/{location}/{resource_type}/{resource_name}"
    
    async def get_project_locations(self, project_id: str, connection_identifier: str = None) -> List[str]:
        """
        Get available locations for a project. Uses cache if available.
        
        Args:
            project_id: GCP project ID
            connection_identifier: Connection identifier for the project
            
        Returns:
            List of available locations
        """
        cache_key = f"project_locations:{project_id}"
        if cache_key in self._location_cache:
            return self._location_cache[cache_key]
        
        locations = []
        try:
            if connection_identifier:
                # Try to get locations using the API
                list_params = {
                    "cloud_provider": "google",
                    "google_locations_params": {
                        "connection_identifier": connection_identifier,
                        "project_id": project_id,
                        "page_size": 100  # Get a good number of locations
                    }
                }
                
                result = await self.operations.execute_operation("locations_get_locations", list_params)
                
                if result and "data" in result and "locations" in result["data"]:
                    for location in result["data"]["locations"]:
                        loc_name = location.get("name", "")
                        if loc_name:
                            # Extract location ID from the full name
                            # Format: projects/{project}/locations/{location}
                            parts = loc_name.split('/')
                            if len(parts) >= 4 and parts[-2] == 'locations':
                                locations.append(parts[-1])
        except Exception:
            # If API call fails, fall back to common locations
            pass
        
        # If we couldn't get locations from API, use common locations
        if not locations:
            locations = self.COMMON_LOCATIONS.copy()
        
        # Cache the result
        self._location_cache[cache_key] = locations
        return locations
    
    async def find_keyring_across_locations(self, keyring_name: str, project_id: str, 
                                          connection_identifier: str = None, 
                                          preferred_locations: List[str] = None) -> Optional[str]:
        """
        Find a keyring across multiple locations.
        
        Args:
            keyring_name: Name of the keyring to find
            project_id: GCP project ID
            connection_identifier: Connection identifier for the project
            preferred_locations: List of preferred locations to check first
            
        Returns:
            Full resource URL if found, None otherwise
        """
        # Check cache first
        cache_key = f"keyring_location:{project_id}:{keyring_name}"
        if cache_key in self._keyring_location_cache:
            cached_location = self._keyring_location_cache[cache_key]
            return self.construct_full_resource_name('keyRings', project_id, cached_location, keyring_name)
        
        # Get available locations
        locations = await self.get_project_locations(project_id, connection_identifier)
        
        # If preferred locations are specified, try them first
        search_locations = []
        if preferred_locations:
            search_locations.extend(preferred_locations)
        
        # Add other locations
        for loc in locations:
            if loc not in search_locations:
                search_locations.append(loc)
        
        # Search for the keyring in each location
        for location in search_locations:
            try:
                list_params = {
                    "cloud_provider": "google",
                    "google_keyrings_params": {
                        "project_id": project_id,
                        "location": location,
                        "limit": 1000
                    }
                }
                
                if connection_identifier:
                    list_params["google_keyrings_params"]["connection_identifier"] = connection_identifier
                
                result = await self.operations.execute_operation("keyrings_get_key_rings", list_params)
                
                if result and "data" in result and "key_rings" in result["data"]:
                    for keyring in result["data"]["key_rings"]:
                        keyring_uri = keyring.get("name", "")
                        if keyring_uri:
                            components = self.extract_components_from_url(keyring_uri)
                            if components and components.get("key_ring") == keyring_name:
                                # Cache the location for this keyring
                                self._keyring_location_cache[cache_key] = location
                                return keyring_uri
            except Exception:
                # Continue searching in other locations
                continue
        
        return None

    async def resolve_key_id(self, identifier: str, cloud_provider: str, context_params: Dict[str, Any] = None) -> str:
        """
        Resolve a key identifier to a CCKM UUID for efficient operations.
        
        Args:
            identifier: The key identifier (name, partial path, or full URL)
            cloud_provider: Should be 'google'
            context_params: Additional context parameters (project_id, location, key_ring)
        
        Returns:
            CCKM UUID for the key (preferred) or full resource URL as fallback
        """
        if not self.needs_resolution(identifier):
            return identifier
        
        # Check cache first
        cache_key = f"key:{identifier}:{str(context_params)}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        context_params = context_params or {}
        
        # PRIORITY 1: Efficient filtered search by key name (returns UUID)
        # This is the most efficient approach - uses key_id filter to avoid costly full list operations
        if self.is_key_name_only(identifier):
            try:
                resolved_id = await self._find_key_by_name(identifier, cloud_provider, context_params)
                if resolved_id and resolved_id != identifier:
                    # _find_key_by_name returns UUID, which is what ksctl expects for get operations
                    self._cache[cache_key] = resolved_id
                    return resolved_id
            except Exception:
                # If filtered search fails, continue to fallback methods
                pass

        # PRIORITY 2: If it's a key name only, try to construct full resource name from context
        # This is useful when we have complete context but filtered search failed
        if self.is_key_name_only(identifier) and context_params:
            project_id = context_params.get('project_id')
            location = context_params.get('location')
            key_ring = context_params.get('key_ring')
            
            if project_id and location and key_ring:
                full_resource_name = self.construct_full_resource_name(
                    'cryptoKeys', project_id, location, key_ring
                ) + f"/{identifier}"
                self._cache[cache_key] = full_resource_name
                return full_resource_name
        
        # PRIORITY 3: If it's a partial path (keyring/key format)
        if self.is_partial_path(identifier) and context_params:
            parts = identifier.split('/')
            keyring_name = parts[0]
            key_name = parts[1]
            
            project_id = context_params.get('project_id')
            location = context_params.get('location')
            
            if project_id and location:
                full_resource_name = self.construct_full_resource_name(
                    'cryptoKeys', project_id, location, keyring_name
                ) + f"/{key_name}"
                self._cache[cache_key] = full_resource_name
                return full_resource_name
        
        # If all else fails, return the original identifier
        return identifier

    async def resolve_keyring_id(self, identifier: str, cloud_provider: str, context_params: Dict[str, Any] = None) -> str:
        """
        Resolve a keyring identifier to a full Google Cloud resource URL.
        Enhanced to search across multiple locations when no specific location is provided.
        
        Args:
            identifier: The keyring identifier (name or full URL)
            cloud_provider: Should be 'google'
            context_params: Additional context parameters (project_id, location, connection_identifier)
        
        Returns:
            Full Google Cloud resource URL for the keyring
        """
        if not self.needs_keyring_resolution(identifier):
            return identifier
        
        # Check cache first
        cache_key = f"keyring:{identifier}:{str(context_params)}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        context_params = context_params or {}
        project_id = context_params.get('project_id')
        location = context_params.get('location')
        connection_identifier = context_params.get('connection_identifier')
        
        # If it's a keyring name only, try to construct full resource name from context
        if self.is_keyring_name_only(identifier) and project_id:
            if location:
                # We have a specific location, use it
                full_resource_name = self.construct_full_resource_name(
                    'keyRings', project_id, location, identifier
                )
                self._cache[cache_key] = full_resource_name
                return full_resource_name
            else:
                # No specific location provided, search across all locations
                try:
                    resolved_url = await self.find_keyring_across_locations(
                        identifier, project_id, connection_identifier
                    )
                    if resolved_url:
                        self._cache[cache_key] = resolved_url
                        return resolved_url
                except Exception:
                    # If async search fails, fall back to sync search
                    pass
        
        # Fallback to searching for the keyring (async version)
        try:
            resolved_id = await self._find_keyring_by_name(identifier, cloud_provider, context_params)
            if resolved_id:
                self._cache[cache_key] = resolved_id
                return resolved_id
        except Exception:
            # If async search fails, return original identifier
            pass
        
        # If all else fails, return the original identifier
        return identifier
    
    async def resolve_keyring_list(self, keyring_list: str, cloud_provider: str, context_params: Dict[str, Any] = None) -> str:
        """
        Resolve a comma-separated list of keyring identifiers to full Google Cloud resource URLs.
        Supports three scenarios:
        1. Single keyring with location: "key-ring-1" + location context
        2. Multiple keyrings in same location: "key-ring-1,key-ring-2" + location context  
        3. Multiple keyrings with location prefixes: "us-central1/key-ring-1,us-west1/key-ring-2,global/key-ring-3"
        
        Args:
            keyring_list: Comma-separated list of keyring identifiers
            cloud_provider: Should be 'google'
            context_params: Additional context parameters (project_id, location)
        
        Returns:
            Comma-separated list of full Google Cloud resource URLs
        """
        if not keyring_list:
            return keyring_list
        
        context_params = context_params or {}
        project_id = context_params.get('project_id')
        default_location = context_params.get('location')
        
        if not project_id:
            # If no project_id, return as-is (let the CLI handle it)
            return keyring_list
        
        keyring_items = [item.strip() for item in keyring_list.split(',')]
        resolved_keyrings = []
        
        for item in keyring_items:
            # Check if item has location prefix (scenario 3)
            if '/' in item and not item.startswith('projects/'):
                # Format: "location/keyring-name"
                parts = item.split('/', 1)
                if len(parts) == 2:
                    location, keyring_name = parts
                    full_resource_name = self.construct_full_resource_name('keyRings', project_id, location, keyring_name)
                    resolved_keyrings.append(full_resource_name)
                else:
                    # Invalid format, return as-is
                    resolved_keyrings.append(item)
            else:
                # No location prefix - use default location (scenarios 1 & 2)
                if default_location:
                    full_resource_name = self.construct_full_resource_name('keyRings', project_id, default_location, item)
                    resolved_keyrings.append(full_resource_name)
                else:
                    # No location specified, return as-is
                    resolved_keyrings.append(item)
        
        return ','.join(resolved_keyrings)

    async def _find_key_by_name(self, key_name: str, cloud_provider: str, context_params: Dict[str, Any]) -> str:
        """Find a key by name using the operations interface with proper filtering."""
        try:
            # Always use the key_id filter for efficient searching - this is crucial for performance
            # The key_id filter ensures we only get keys that match the exact name, avoiding costly full list operations
            list_params = {
                "cloud_provider": cloud_provider,
                "google_keys_params": {
                    "key_id": key_name,  # Filter by key ID directly in the API - this is the key name filter
                    **context_params  # Include project_id, location, key_ring for targeted search
                }
            }
            
            # Execute the filtered list operation
            result = await self.operations.execute_operation("keys_list", list_params)
            
            if result and "resources" in result:
                for key in result["resources"]:
                    # Check multiple possible name fields (key_id is the actual field name in API)
                    if (key.get("key_id") == key_name or 
                        key.get("name") == key_name or 
                        key.get("key_name") == key_name):
                        # Return the key ID (UUID) which is what ksctl expects for get operations
                        return key.get("id", key_name)
            
            return key_name
        except Exception:
            return key_name

    async def _find_key_by_partial_path(self, partial_path: str, cloud_provider: str, context_params: Dict[str, Any]) -> str:
        """Find a key by partial path (keyring/key format)."""
        try:
            parts = partial_path.split('/')
            if len(parts) != 2:
                return partial_path
            
            keyring_name, key_name = parts
            
            # First resolve the keyring
            keyring_params = {**context_params, "keyring_name": keyring_name}
            resolved_keyring = await self.resolve_keyring_id(keyring_name, cloud_provider, context_params)
            
            if resolved_keyring and resolved_keyring != keyring_name:
                # Extract project and location from resolved keyring
                components = self.extract_components_from_url(resolved_keyring)
                if components:
                    # Construct full key resource name
                    return self.construct_full_resource_name(
                        'cryptoKeys', 
                        components['project_id'], 
                        components['location'], 
                        components['key_ring']
                    ) + f"/{key_name}"
            
            return partial_path
        except Exception:
            return partial_path

    async def _find_keyring_by_name(self, keyring_name: str, cloud_provider: str, context_params: Dict[str, Any]) -> str:
        """Find a keyring by name using the operations interface."""
        try:
            # Try to list keyrings and find the one with matching name
            list_params = {
                "cloud_provider": cloud_provider,
                "google_keyrings_params": {
                    "limit": 1000,  # Get a large number to search through
                    **context_params
                }
            }
            
            result = await self.operations.execute_operation("keyrings_get_key_rings", list_params)
            
            if result and "data" in result and "key_rings" in result["data"]:
                for keyring in result["data"]["key_rings"]:
                    keyring_uri = keyring.get("name", "")
                    # Extract keyring name from full URI for comparison
                    if keyring_uri:
                        components = self.extract_components_from_url(keyring_uri)
                        if components and components.get("key_ring") == keyring_name:
                            return keyring_uri
            
            return keyring_name
        except Exception:
            return keyring_name

    def _convert_uri_to_resource_url(self, uri: str) -> str:
        """Convert a CCKM URI to a Google Cloud resource URL."""
        # Extract the resource path from the URI
        # Example: kylo:kylo-xxx:cckm:gcp-key:xxx -> projects/xxx/locations/xxx/keyRings/xxx/cryptoKeys/xxx
        if "cckm:gcp-key:" in uri:
            # This is a key URI, extract the key ID and construct resource URL
            key_id = uri.split("cckm:gcp-key:")[-1]
            # Note: This is a simplified conversion - in practice, you'd need to look up the key details
            return key_id
        elif "cckm:gcp-ring:" in uri:
            # This is a keyring URI, extract the keyring ID and construct resource URL
            keyring_id = uri.split("cckm:gcp-ring:")[-1]
            # Note: This is a simplified conversion - in practice, you'd need to look up the keyring details
            return keyring_id
        return uri

    def clear_cache(self):
        """Clear all resolution caches."""
        self._cache.clear()
        self._location_cache.clear()
        self._keyring_location_cache.clear()


def create_google_smart_resolver(operations: OperationsProtocol) -> GoogleSmartIDResolver:
    """Create a new Google Smart ID Resolver instance."""
    return GoogleSmartIDResolver(operations) 