"""Smart ID resolver for OCI operations."""

import json
import re
from typing import Any, Dict, Optional, Union


class OCISmartIDResolver:
    """Smart ID resolver for OCI resources (keys, vaults, compartments)."""
    
    def __init__(self, operations):
        self.operations = operations
    
    def is_uuid(self, identifier: str) -> bool:
        """Check if the identifier is a UUID."""
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, identifier.lower()))
    
    def is_ocid(self, identifier: str) -> bool:
        """Check if the identifier is an OCI OCID."""
        # OCI OCIDs follow pattern: ocid1.<resource-type>.<realm>.[region].<unique-id>
        # Example: ocid1.key.oc1.iad.amaaaaaaexampleuniqueid
        ocid_pattern = r'^ocid1\.[a-z]+\.oc1(\.[a-z0-9]+)?\..*'
        return bool(re.match(ocid_pattern, identifier))
    
    def convert_key_size(self, algorithm: str, length: Union[int, str]) -> int:
        """
        Convert key size from bits to bytes or bytes to bits as needed for OCI operations.
        
        This function is more flexible and handles both bit and byte inputs for all algorithms,
        automatically determining the correct format for the algorithm.
        
        Args:
            algorithm: Key algorithm (AES, RSA, ECDSA)
            length: Key length in bits or bytes
            
        Returns:
            Key length in the proper format for OCI (bytes for AES and ECDSA, bits for RSA)
            
        Raises:
            ValueError: If the key size is not valid for the algorithm
        """
        # Convert to int if string
        if isinstance(length, str):
            try:
                length = int(length)
            except ValueError:
                raise ValueError(f"Invalid key length: {length}")
        
        algorithm_upper = algorithm.upper()
        
        if algorithm_upper == "AES":
            # AES: Check for common bit sizes (128, 192, 256) and convert to bytes (16, 24, 32)
            if length in [128, 192, 256]:
                # Convert bits to bytes
                return length // 8
            elif length in [16, 24, 32]:
                # Already in bytes
                return length
            else:
                raise ValueError(f"Invalid AES key length: {length}. Valid sizes are 128, 192, 256 bits or 16, 24, 32 bytes")
        
        elif algorithm_upper == "RSA":
            # RSA: Check for both common bit sizes and byte sizes
            # For RSA, OCI expects bit sizes: 2048, 3072, 4096
            # But users might provide byte sizes: 256, 384, 512
            
            # If given in bytes (256, 384, 512), convert to bits (2048, 3072, 4096)
            if length in [256, 384, 512]:
                return length * 8
            # If already in bits (2048, 3072, 4096), leave as is
            elif length in [2048, 3072, 4096]:
                return length
            else:
                raise ValueError(
                    f"Invalid RSA key length: {length}. "
                    f"Valid sizes are 2048, 3072, 4096 bits or 256, 384, 512 bytes"
                )
        
        elif algorithm_upper == "ECDSA":
            # ECDSA: Check for both bit sizes (256, 384, 521) and byte sizes (32, 48, 66)
            
            # If given in bits, convert to bytes
            if length == 256:
                return 32
            elif length == 384:
                return 48
            elif length == 521:
                return 66
            # If already in bytes, leave as is
            elif length in [32, 48, 66]:
                return length
            else:
                raise ValueError(
                    f"Invalid ECDSA key length: {length}. "
                    f"Valid sizes are 256, 384, 521 bits or 32, 48, 66 bytes"
                )
        
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}. Supported algorithms are AES, RSA, ECDSA")
    
    async def resolve_vault_name_to_ocid_for_creation(self, vault_name: str, oci_params: Dict[str, Any], cloud_provider: str = "oci", context: Optional[Dict[str, Any]] = None) -> str:
        """
        Resolve vault display name to OCID for key creation/upload operations.
        Uses vaults_list with proper filtering and parses stdout/data robustly.
        """
        # If already an OCID, return as is
        if self.is_ocid(vault_name):
            return vault_name
        
        # Build filtered list params
        list_params = {
            "cloud_provider": cloud_provider,
            "oci_vaults_params": {
                "oci_vault_display_name": vault_name,
                "limit": 10
            }
        }
        # Propagate helpful filters
        for key in ["oci_region", "cloud_name", "oci_tenancy", "oci_compartment_name", "connection_identifier"]:
            if key in oci_params:
                list_params["oci_vaults_params"][key] = oci_params[key]
        # Propagate domain context
        if context:
            if context.get("domain"):
                list_params["domain"] = context["domain"]
            if context.get("auth_domain"):
                list_params["auth_domain"] = context["auth_domain"]
        
        # Execute and parse
        result = await self.operations.execute_operation("vaults_list", list_params)
        vaults = []
        try:
            # Common wrappers
            if isinstance(result, dict):
                if "data" in result and isinstance(result["data"], dict):
                    vaults = result["data"].get("resources", []) or result["data"].get("data", [])
                # Some runners expose parsed data directly
                if not vaults and "resources" in result:
                    vaults = result.get("resources", [])
                # Parse stdout JSON if present
                if not vaults and "stdout" in result and result["stdout"]:
                    data = json.loads(result["stdout"]) if isinstance(result["stdout"], str) else result["stdout"]
                    vaults = data.get("resources", []) or data.get("data", [])
            elif isinstance(result, str):
                data = json.loads(result)
                vaults = data.get("resources", []) or data.get("data", [])
        except Exception:
            pass
        
        if not vaults:
            raise ValueError(f"No vault found with display name '{vault_name}'. Please check the vault name and try again.")
        if len(vaults) > 1:
            names = [v.get("display_name") or v.get("name") for v in vaults]
            raise ValueError(f"Multiple vaults found with similar names: {names}. Provide a more specific name or the OCID.")
        
        vault = vaults[0]
        # Prefer top-level vault_id, fallback to nested
        vault_ocid = (
            vault.get("vault_id")
            or vault.get("oci_params", {}).get("vault_id")
            or vault.get("oci_vault_id")
        )
        if not vault_ocid:
            raise ValueError(f"Vault found but no OCI vault_id present for '{vault_name}'")
        return vault_ocid
    
    async def resolve_compartment_name_to_ocid(self, compartment_name: str, oci_params: Dict[str, Any], cloud_provider: str = "oci", context: Optional[Dict[str, Any]] = None) -> str:
        """Resolve an OCI compartment display name to its OCID using compartments_list with filters."""
        # If already OCID/UUID, return
        if self.is_ocid(compartment_name) or self.is_uuid(compartment_name):
            return compartment_name
        
        list_params = {
            "cloud_provider": cloud_provider,
            "oci_compartments_params": {
                "oci_compartment_name": compartment_name,
                "limit": 10
            }
        }
        # Propagate helpful filters
        for key in ["connection_identifier", "oci_tenancy"]:
            if key in oci_params:
                list_params["oci_compartments_params"][key] = oci_params[key]
        # Propagate domain context
        if context:
            if context.get("domain"):
                list_params["domain"] = context["domain"]
            if context.get("auth_domain"):
                list_params["auth_domain"] = context["auth_domain"]
        
        result = await self.operations.execute_operation("compartments_list", list_params)
        compartments = []
        try:
            if isinstance(result, dict):
                if "data" in result and isinstance(result["data"], dict):
                    compartments = result["data"].get("resources", []) or result["data"].get("data", [])
                if not compartments and "resources" in result:
                    compartments = result.get("resources", [])
                if not compartments and "stdout" in result and result["stdout"]:
                    data = json.loads(result["stdout"]) if isinstance(result["stdout"], str) else result["stdout"]
                    compartments = data.get("resources", []) or data.get("data", [])
            elif isinstance(result, str):
                data = json.loads(result)
                compartments = data.get("resources", []) or data.get("data", [])
        except Exception:
            pass
        
        # Filter exact match by name
        compartments = [c for c in compartments if c.get("name") == compartment_name or c.get("compartment_name") == compartment_name]
        if not compartments:
            raise ValueError(f"No compartment found with name '{compartment_name}'.")
        if len(compartments) > 1:
            names = [c.get("name") or c.get("compartment_name") for c in compartments]
            raise ValueError(f"Multiple compartments matched: {names}. Specify tenancy or use OCID.")
        comp = compartments[0]
        comp_ocid = comp.get("compartment_id") or comp.get("oci_params", {}).get("compartment_id")
        if not comp_ocid:
            raise ValueError(f"Compartment found but missing compartment_id for '{compartment_name}'.")
        return comp_ocid
    
    async def resolve_key_id(self, key_identifier: str, oci_params: Dict[str, Any], cloud_provider: str = "oci", context: Optional[Dict[str, Any]] = None) -> str:
        """Resolve key identifier to UUID."""
        # If already a UUID, return as is
        if self.is_uuid(key_identifier):
            return key_identifier
        
        # If it's an OCID, return as is (OCI accepts these)
        if self.is_ocid(key_identifier):
            return key_identifier
        
        # Prepare the list parameters for key search
        list_params = {
            "cloud_provider": cloud_provider,
            "oci_keys_params": {
                "key_name": key_identifier,
                "limit": 20  # Increase limit to ensure we find the key
            }
        }
        
        # Add any additional filters that might help
        if "oci_compartment_id" in oci_params:
            list_params["oci_keys_params"]["oci_compartment_id"] = oci_params["oci_compartment_id"]
        if "oci_vault" in oci_params:
            list_params["oci_keys_params"]["oci_vault"] = oci_params["oci_vault"]
        if "oci_vault_name" in oci_params:
            list_params["oci_keys_params"]["oci_vault_name"] = oci_params["oci_vault_name"]
        
        # Propagate domain context
        if context:
            if context.get("domain"):
                list_params["domain"] = context["domain"]
            if context.get("auth_domain"):
                list_params["auth_domain"] = context["auth_domain"]
        
        # Call the list operation
        try:
            result = await self.operations.execute_operation("keys_list", list_params)
            
            # Parse the result
            keys = []
            try:
                if isinstance(result, dict):
                    if "data" in result and isinstance(result["data"], dict):
                        keys = result["data"].get("resources", []) or result["data"].get("data", [])
                    # Some runners expose parsed data directly
                    if not keys and "resources" in result:
                        keys = result.get("resources", [])
                    # Parse stdout JSON if present
                    if not keys and "stdout" in result and result["stdout"]:
                        data = json.loads(result["stdout"]) if isinstance(result["stdout"], str) else result["stdout"]
                        keys = data.get("resources", []) or data.get("data", [])
                elif isinstance(result, str):
                    data = json.loads(result)
                    keys = data.get("resources", []) or data.get("data", [])
            except Exception as parse_error:
                # If parsing fails, try to extract from error message or return original
                print(f"Warning: Failed to parse key list result: {parse_error}")
                return key_identifier
            
            # Find exact name match
            matching_keys = []
            for key in keys:
                key_name = key.get("name", "")
                display_name = key.get("display_name", "")
                key_name_field = key.get("key_name", "")
                
                # Also check inside oci_params for display_name (OCI specific structure)
                oci_params = key.get("oci_params", {})
                oci_display_name = oci_params.get("display_name", "")
                
                # Check multiple name variations
                if (key_name == key_identifier or 
                    display_name == key_identifier or 
                    key_name_field == key_identifier or
                    oci_display_name == key_identifier):
                    matching_keys.append(key)
            
            if not matching_keys:
                raise ValueError(f"No key found with name '{key_identifier}'. Please check the key name and try again.")
            
            if len(matching_keys) > 1:
                names = [k.get("name", k.get("display_name", "unknown")) for k in matching_keys]
                raise ValueError(f"Multiple keys found with name '{key_identifier}': {names}. Please provide a more specific name or the key ID directly.")
            
            # Return the UUID of the found key
            key_id = matching_keys[0].get("id")
            if not key_id:
                raise ValueError(f"Key found but no ID available for '{key_identifier}'")
            
            return key_id
            
        except Exception as e:
            if "No key found" in str(e) or "Multiple keys found" in str(e):
                raise e
            else:
                raise ValueError(f"Failed to resolve key '{key_identifier}': {str(e)}")
    
    async def resolve_vault_id(self, vault_identifier: str, oci_params: Dict[str, Any], cloud_provider: str = "oci", context: Optional[Dict[str, Any]] = None) -> str:
        """Resolve vault identifier to UUID.
        
        This method is for vault operations (delete, get, etc.) where we need the CCKM vault ID.
        It uses the existing vault list filtering mechanism.
        
        Args:
            vault_identifier: Vault name, UUID, or OCID
            oci_params: OCI parameters for the operation
            cloud_provider: Cloud provider (default: oci)
            
        Returns:
            Resolved vault UUID
            
        Raises:
            ValueError: If vault cannot be found or resolved
            
        Note:
            This method demonstrates proper filtering usage by using oci_vault_display_name
            for exact name matching. AI assistants should follow this pattern when listing
            vaults for any operation.
        """
        # If already a UUID, return as is
        if self.is_uuid(vault_identifier):
            return vault_identifier
        
        # If it's an OCID, return as is
        if self.is_ocid(vault_identifier):
            return vault_identifier
        
        # Prepare the list parameters for vault search with PROPER FILTERING
        list_params = {
            "cloud_provider": cloud_provider,
            "oci_vaults_params": {
                # ALWAYS use filtering parameters for better performance
                "oci_vault_display_name": vault_identifier,  # Exact name matching
                "limit": 10  # Control result size
            }
        }
        
        # Add any additional parameters that might help with filtering
        for key in ["oci_compartment_id", "oci_region", "cloud_name", "oci_tenancy"]:
            if key in oci_params:
                list_params["oci_vaults_params"][key] = oci_params[key]
        # Propagate domain context
        if context:
            if context.get("domain"):
                list_params["domain"] = context["domain"]
            if context.get("auth_domain"):
                list_params["auth_domain"] = context["auth_domain"]
        
        try:
            # Call the vault list operation to find the vault
            # This demonstrates the CORRECT way to list vaults with filtering
            result = await self.operations.execute_operation("vaults_list", list_params)
            
            # Parse the result
            if isinstance(result, dict) and "data" in result:
                vaults = result["data"].get("resources", [])
            elif isinstance(result, str):
                # Try to parse JSON string
                import json
                data = json.loads(result)
                vaults = data.get("resources", [])
            else:
                vaults = result.get("resources", []) if hasattr(result, "get") else []
            
            if not vaults:
                raise ValueError(f"No vault found with display name '{vault_identifier}'. Please check the vault name and try again.")
            
            if len(vaults) > 1:
                # Multiple vaults found, provide more specific error
                vault_names = [v.get("display_name", "unknown") for v in vaults]
                raise ValueError(f"Multiple vaults found with similar names: {vault_names}. Please use a more specific vault name or provide the vault ID directly.")
            
            # Return the UUID of the found vault (CCKM vault ID)
            vault_id = vaults[0].get("id")
            if not vault_id:
                raise ValueError(f"Vault found but no ID available for '{vault_identifier}'")
            
            return vault_id
            
        except Exception as e:
            if "No vault found" in str(e) or "Multiple vaults found" in str(e):
                raise e
            else:
                raise ValueError(f"Failed to resolve vault '{vault_identifier}': {str(e)}")
    
    async def resolve_compartment_id(self, compartment_identifier: str, oci_params: Dict[str, Any], cloud_provider: str = "oci", context: Optional[Dict[str, Any]] = None) -> str:
        """Resolve compartment identifier to UUID."""
        # If already a UUID, return as is
        if self.is_uuid(compartment_identifier):
            return compartment_identifier
        
        # If it's an OCID, return as is
        if self.is_ocid(compartment_identifier):
            return compartment_identifier
        
        # Prepare the list parameters for compartment search
        list_params = {
            "cloud_provider": cloud_provider,
            "oci_compartments_params": {}
        }
        
        # Call the list operation
        try:
            result = await self.operations.execute_operation("compartments_list", list_params)
            
            # Parse the result
            if isinstance(result, str):
                result_data = json.loads(result)
            else:
                result_data = result
            
            # Look for matching compartments
            compartments = result_data.get("resources", [])
            if not compartments:
                compartments = result_data.get("data", [])
            
            # Find exact name match
            for compartment in compartments:
                if compartment.get("name") == compartment_identifier or compartment.get("compartment_name") == compartment_identifier:
                    return compartment.get("id", compartment_identifier)
            
            # If no exact match found, return original identifier
            return compartment_identifier
            
        except Exception:
            # If resolution fails, return original identifier
            return compartment_identifier 