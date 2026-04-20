"""Key management tools for CipherTrust Manager with built-in domain support."""

import base64
import json
import os
import secrets
import tempfile
from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


# Core CRUD Parameter Models
class KeyListParams(BaseModel):
    """Parameters for listing keys."""
    limit: int = Field(10, description="Maximum number of keys to return")
    skip: int = Field(0, description="Offset at which to start the search")
    name: Optional[str] = Field(None, description="Filter by key name (supports wildcards)")
    alias: Optional[str] = Field(None, description="Filter by key alias (supports wildcards)")
    fields: Optional[str] = Field(None, description="Comma separated fields to include (meta, links, certFields)")
    state: Optional[str] = Field(None, description="Filter by key state (Pre-Active, Active, Deactivated, etc.)")
    object_type: Optional[str] = Field(None, description="Filter by object type (Symmetric Key, Public Key, etc.)")
    usage_mask: Optional[int] = Field(None, description="Filter by key usage mask")
    labels_query: Optional[str] = Field(None, description="Filter by label selector expressions")
    key_check_value: Optional[str] = Field(None, description="Filter by key check value")
    link_type: Optional[str] = Field(None, description="Filter by link type")
    sha1_fingerprint: Optional[str] = Field(None, description="Filter by SHA1 fingerprint")
    sha256_fingerprint: Optional[str] = Field(None, description="Filter by SHA256 fingerprint")
    compare_id_with_uuid: Optional[str] = Field(None, description="Compare ID with UUID (equal/notequal)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to list keys from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class KeyCreateParams(BaseModel):
    """Parameters for creating a key with all advanced options."""
    # Basic key parameters
    name: Optional[str] = Field(None, description="Key name (use autoname for automatic naming)")
    autoname: bool = Field(False, description="Generate automatic name for key")
    algorithm: str = Field("AES", description="Key algorithm (AES, RSA, EC, etc.)")
    size: Optional[int] = Field(None, description="Key size in bits")
    curve_id: Optional[str] = Field(None, description="Elliptic curve ID for EC keys")
    usage_mask: Optional[int] = Field(None, description="Key usage mask")
    description: Optional[str] = Field(None, description="Key description")
    labels: Optional[str] = Field(None, description="Comma-separated key=value labels")
    aliases: Optional[str] = Field(None, description="Comma-separated list of aliases")
    
    # Key material and format
    material: Optional[str] = Field(
        None, 
        description="Key material. Format depends on algorithm: "
                   "AES/TDES/HMAC/SEED/ARIA: hex-encoded bytes; "
                   "RSA/EC: PKCS8 PEM format; "
                   "X.509: PEM certificate with \\n line breaks"
    )
    format: Optional[str] = Field(None, description="Key format (pkcs1, pkcs8, base64, etc.)")
    encoding: Optional[str] = Field(None, description="Encoding for material (hex, base64)")
    include_material: bool = Field(False, description="Include key material in response")
    empty_material: bool = Field(False, description="Create key without material")
    
    # Key properties
    xts: bool = Field(False, description="Create XTS/CBC-CS1 key (AES only)")
    undeletable: bool = Field(False, description="Key cannot be deleted")
    unexportable: bool = Field(False, description="Key cannot be exported")
    
    # Object and certificate types
    object_type: Optional[str] = Field(None, description="Object type (Symmetric Key, Certificate, etc.)")
    cert_type: Optional[str] = Field(None, description="Certificate type (x509-pem, x509-der)")
    cert_filename: Optional[str] = Field(None, description="Certificate file name")
    
    # JSON configuration
    jsonfile: Optional[str] = Field(None, description="JSON file with key parameters")
    
    # Wrapping and encryption
    wrap_key_name: Optional[str] = Field(None, description="Wrap key name for encryption")
    wrap_public_key: Optional[str] = Field(None, description="Public key for wrapping")
    
    # Rotation
    rotation_frequency_days: Optional[str] = Field(None, description="Auto-rotation frequency in days")
    
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to create key in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")
    
    # CTE-specific parameters
    cte_key_type: Optional[str] = Field(None, description="CTE key type: 'standard', 'ldt', or 'xts'")
    cte_persistent_on_client: Optional[bool] = Field(None, description="Make key persistent on CTE client")
    cte_permissions_groups: Optional[str] = Field(None, description="Comma-separated groups for permissions (default: 'CTE Clients')")
    cte_encryption_mode: Optional[str] = Field(None, description="CTE encryption mode: CBC, CBC_CS1, or XTS (default: CBC)")
    
    # Additional parameters
    
    # Critical missing parameters
    ret: bool = Field(False, description="Return existing key with same name if it exists")
    template_id: Optional[str] = Field(None, description="Template ID for creating key using template")
    owner_id: Optional[str] = Field(None, description="The user's ID (owner of the key)")
    id: Optional[str] = Field(None, description="Specific key identifier")
    uuid: Optional[str] = Field(None, description="UUID identifier (32 hex digits with 4 dashes)")
    muid: Optional[str] = Field(None, description="Additional identifier (MUID)")
    key_id: Optional[str] = Field(None, description="Additional key identifier")
    
    # Advanced wrapping parameters
    hkdf: Optional[str] = Field(None, description="HKDF parameters in JSON format")
    hkdf_jsonfile: Optional[str] = Field(None, description="HKDF parameters via JSON file")
    wrap_pbe: Optional[str] = Field(None, description="PBE wrap parameters in JSON format")
    wrap_pbe_jsonfile: Optional[str] = Field(None, description="PBE wrap parameters via JSON file")
    wrap_hkdf: Optional[str] = Field(None, description="HKDF wrap parameters in JSON format")
    wrap_hkdf_jsonfile: Optional[str] = Field(None, description="HKDF wrap parameters via JSON file")
    wrap_rsa_aes: Optional[str] = Field(None, description="RSA AES KWP parameters in JSON format")
    wrap_rsa_aes_jsonfile: Optional[str] = Field(None, description="RSA AES KWP parameters via JSON file")
    
    # Wrapping method configuration
    wrapping_method: Optional[str] = Field(None, description="Wrapping method: encrypt, mac/sign")
    wrapping_encryption_algo: Optional[str] = Field(None, description="Encryption algorithm for wrapping (Algorithm/Mode/Padding)")
    wrapping_hashing_algo: Optional[str] = Field(None, description="Hashing algorithm for mac/sign wrapping")
    
    # MAC/Signature generation
    macsign_key_id: Optional[str] = Field(None, description="Key ID for MAC/signature generation")
    macsign_key_id_type: Optional[str] = Field(None, description="MAC/sign key ID type (name, id, alias)")
    signing_algo: Optional[str] = Field(None, description="Signing algorithm (RSA, RSA-PSS)")
    
    # PKCS12 support
    passwordkey: Optional[str] = Field(None, description="Password key for PKCS12 format (ID or name of Secret Data)")
    secretdatalink: Optional[str] = Field(None, description="Base64 encoded password for PKCS12 format")
    secretdataencoding: Optional[str] = Field(None, description="Encoding method for secretDataLink material")
    
    # File-based parameters
    public_key_jsonfile: Optional[str] = Field(None, description="Public key parameters via JSON file")
    wrap_public_key_file: Optional[str] = Field(None, description="File containing base64 public key for wrapping")
    
    # Additional wrapping options
    padded: bool = Field(False, description="Use RFC-5649 padding for wrap-key-name (symmetric keys only)")
    wrapkey_id_type: Optional[str] = Field(None, description="Wrap key ID type (name, id, alias)")
    
    # Size and ID configuration
    id_size: Optional[int] = Field(None, description="Size of ID for the key")
    
    # Deprecated but supported
    defaultiv: Optional[str] = Field(None, description="Deprecated: Default IV (hex encoded)")
    usage: Optional[str] = Field(None, description="Deprecated: Key usage (use usage_mask instead)")

    def calculate_material_size(self) -> int:
        """Calculate material size in bits."""
        if not self.material:
            return 0
        
        if self.encoding == 'hex':
            return len(self.material) * 4  # 4 bits per hex char
        elif self.encoding == 'base64':
            return len(self.material) * 6  # 6 bits per base64 char
        return len(self.material) * 8  # Assume bytes

    def get_material_format_help(self) -> str:
        """Return format guidance based on algorithm."""
        help_text = {
            'AES': "hex-encoded bytes (e.g., 'a1b2c3d4...')",
            'TDES': "hex-encoded bytes (e.g., 'a1b2c3d4e5f6789012345678901234567890abcdef123456')",
            'HMAC-SHA256': "hex-encoded bytes (e.g., 'deadbeef1234567890abcdef1234567890abcdef1234567890abcdef12345678')",
            'RSA': "PKCS8 PEM format (e.g., '-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----')",
            'EC': "PKCS8 PEM format for private key",
            'X.509': "PEM certificate format with \\n line breaks"
        }
        return help_text.get(self.algorithm.upper(), "Check algorithm documentation")

    def validate_material_format(self) -> bool:
        """Validate material format based on algorithm."""
        if not self.material:
            return True
        
        algorithm_upper = self.algorithm.upper()
        
        # Symmetric keys (AES, TDES, HMAC, SEED, ARIA)
        if algorithm_upper in ['AES', 'TDES', 'HMAC-SHA1', 'HMAC-SHA256', 'HMAC-SHA384', 'HMAC-SHA512', 'SEED', 'ARIA']:
            # Validate hex format
            if not all(c in '0123456789abcdefABCDEF' for c in self.material):
                raise ValueError(f"Material for {algorithm_upper} must be hex-encoded. {self.get_material_format_help()}")
            
            # Validate size
            expected_bits = self.size or 256
            actual_bits = len(self.material) * 4  # 4 bits per hex char
            if actual_bits != expected_bits:
                raise ValueError(f"Material length: {actual_bits} bits, expected: {expected_bits} bits. {self.get_material_format_help()}")
        
        # RSA keys
        elif algorithm_upper == 'RSA':
            if not self.material.startswith('-----BEGIN PRIVATE KEY-----'):
                raise ValueError(f"RSA material must be PKCS8 PEM format. {self.get_material_format_help()}")
            if '-----END PRIVATE KEY-----' not in self.material:
                raise ValueError(f"RSA material must end with '-----END PRIVATE KEY-----'. {self.get_material_format_help()}")
        
        # EC keys
        elif algorithm_upper == 'EC':
            if not self.material.startswith('-----BEGIN PRIVATE KEY-----'):
                raise ValueError(f"EC material must be PKCS8 PEM format. {self.get_material_format_help()}")
            if '-----END PRIVATE KEY-----' not in self.material:
                raise ValueError(f"EC material must end with '-----END PRIVATE KEY-----'. {self.get_material_format_help()}")
        
        # Certificates
        elif self.object_type == 'Certificate':
            if self.cert_type == 'x509-pem':
                if not self.material.startswith('-----BEGIN CERTIFICATE-----'):
                    raise ValueError(f"X.509 PEM certificate must start with '-----BEGIN CERTIFICATE-----'. {self.get_material_format_help()}")
                if '-----END CERTIFICATE-----' not in self.material:
                    raise ValueError(f"X.509 PEM certificate must end with '-----END CERTIFICATE-----'. {self.get_material_format_help()}")
            
            elif self.cert_type == 'x509-der':
                if not all(c in '0123456789abcdefABCDEF' for c in self.material):
                    raise ValueError(f"X.509 DER certificate must be hex-encoded. {self.get_material_format_help()}")
        
        return True

    def convert_material_format(self) -> Optional[str]:
        """Attempt to convert material to the expected format."""
        print(f"DEBUG: Attempting to convert material: {self.material}")
        if not self.material:
            return None
        
        algorithm_upper = self.algorithm.upper()
        
        if algorithm_upper in ['AES', 'TDES', 'HMAC-SHA1', 'HMAC-SHA256', 'HMAC-SHA384', 'HMAC-SHA512', 'SEED', 'ARIA']:
            material_clean = self.material.strip().replace(' ', '').replace('\\n', '').replace('\\r', '')
            print(f"DEBUG: Cleaned material: {material_clean}")
            if len(material_clean) % 4 == 0 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in material_clean):
                try:
                    decoded = base64.b64decode(material_clean)
                    hex_material = decoded.hex()
                    print(f"DEBUG: Converted from Base64 to Hex: {hex_material}")
                    return hex_material
                except Exception as e:
                    print(f"DEBUG: Base64 decoding failed: {e}")
                    pass
            elif all(c in '0123456789abcdefABCDEF ' for c in material_clean):
                hex_material = ''.join(c for c in material_clean if c in '0123456789abcdefABCDEF').lower()
                print(f"DEBUG: Cleaned hex material: {hex_material}")
                return hex_material

        elif algorithm_upper in ['RSA', 'EC']:
            material_clean = self.material.strip().replace('\\n', '\n')
            print(f"DEBUG: Cleaned PEM material: {material_clean}")
            if '-----BEGIN' in material_clean and '-----END' in material_clean and '\n' not in material_clean.strip():
                 pem_type = "PRIVATE KEY" if "PRIVATE KEY" in material_clean else "CERTIFICATE"
                 start_marker = f"-----BEGIN {pem_type}-----"
                 end_marker = f"-----END {pem_type}-----"
                 start_index = material_clean.find(start_marker) + len(start_marker)
                 end_index = material_clean.find(end_marker)
                 body = material_clean[start_index:end_index].replace(" ", "").replace("\n", "")
                 formatted_body = '\n'.join([body[i:i+64] for i in range(0, len(body), 64)])
                 pem_material = f"{start_marker}\n{formatted_body}\n{end_marker}"
                 print(f"DEBUG: Formatted PEM material: {pem_material}")
                 return pem_material
            return material_clean

        print("DEBUG: No conversion applied.")
        return None

    def validate_and_convert_material(self) -> dict:
        """Validate material format and attempt conversion if needed."""
        try:
            self.validate_material_format()
            return {"valid": True, "converted": False}
        except ValueError as e:
            original_error = str(e)
            converted_material = self.convert_material_format()
            if converted_material:
                original_material_val = self.material
                self.material = converted_material
                try:
                    self.validate_material_format()
                    return {"valid": True, "converted": True, "new_material": self.material, "original_error": original_error}
                except ValueError as e2:
                    self.material = original_material_val
                    return {"valid": False, "error": original_error, "conversion_error": str(e2)}
            return {"valid": False, "error": original_error}

    def generate_test_key_material(self) -> Optional[str]:
        """Generate test key material for the specified algorithm."""
        
        algorithm_upper = self.algorithm.upper()
        
        if algorithm_upper == 'AES':
            size_bytes = (self.size or 256) // 8
            return secrets.token_hex(size_bytes)
        
        elif algorithm_upper == 'TDES':
            return secrets.token_hex(24)  # 192 bits = 24 bytes
        
        elif algorithm_upper.startswith('HMAC'):
            size_bytes = (self.size or 256) // 8
            return secrets.token_hex(size_bytes)
        
        return None

    def validate_import_parameters(self) -> dict:
        """Validate import parameters without creating the key."""
        result = self.validate_and_convert_material()
        result.update({
            "material_size_bits": self.calculate_material_size(),
            "format_help": self.get_material_format_help(),
            "algorithm": self.algorithm,
            "size": self.size
        })
        return result


class KeyGetParams(BaseModel):
    """Parameters for getting a key."""
    name: str = Field(..., description="Key name, ID, URI, or alias")
    type: Optional[str] = Field(None, description="Identifier type (name, id, uri, alias)")
    version: int = Field(-1, description="Key version (-1 for latest)")
    usage_mask: Optional[int] = Field(None, description="Key usage mask for validation")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to get key from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class KeyDeleteParams(BaseModel):
    """Parameters for deleting a key."""
    name: str = Field(..., description="Key name, ID, URI, or alias")
    type: Optional[str] = Field(None, description="Identifier type (name, id, uri, alias)")
    version: int = Field(-1, description="Key version (-1 for latest)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to delete key from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class KeyModifyParams(BaseModel):
    """Parameters for modifying a key."""
    name: str = Field(..., description="Key name, ID, URI, or alias")
    type: Optional[str] = Field(None, description="Identifier type (name, id, uri, alias)")
    description: Optional[str] = Field(None, description="New key description")
    labels: Optional[str] = Field(None, description="Labels to add/modify")
    remove_labels: Optional[str] = Field(None, description="Labels to remove")
    rotation_frequency_days: Optional[str] = Field(None, description="Auto-rotation frequency")
    
    # Key property flags
    undeletable: Optional[bool] = Field(None, description="Set key as undeletable (true) or deletable (false)")
    unexportable: Optional[bool] = Field(None, description="Set key as unexportable (true) or exportable (false)")
    
    # JSON file support
    jsonfile: Optional[str] = Field(None, description="JSON file with modification parameters")
    json_content: Optional[str] = Field(None, description="JSON content for modification (alternative to jsonfile)")
    
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to modify key in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")
    
    def create_json_file(self) -> Optional[str]:
        """Create a temporary JSON file with modification parameters."""
        
        mod_data = {}
        
        if self.description is not None:
            mod_data["description"] = self.description
        
        if self.undeletable is not None:
            mod_data["undeletable"] = self.undeletable
            
        if self.unexportable is not None:
            mod_data["unexportable"] = self.unexportable
            
        if self.rotation_frequency_days is not None:
            mod_data["rotationFrequencyDays"] = self.rotation_frequency_days
        
        if not mod_data:
            return None
            
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(mod_data, temp_file, indent=2)
        temp_file.close()
        
        return temp_file.name


# Lifecycle Parameter Models
class KeyArchiveParams(BaseModel):
    """Parameters for archiving a key."""
    name: str = Field(..., description="Key name, ID, URI, or alias")
    type: Optional[str] = Field(None, description="Identifier type (name, id, uri, alias)")
    version: int = Field(-1, description="Key version (-1 for latest)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to archive key in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class KeyRecoverParams(BaseModel):
    """Parameters for recovering an archived key."""
    name: str = Field(..., description="Key name, ID, URI, or alias")
    type: Optional[str] = Field(None, description="Identifier type (name, id, uri, alias)")
    version: int = Field(-1, description="Key version (-1 for latest)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to recover key in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class KeyRevokeParams(BaseModel):
    """Parameters for revoking a key."""
    name: str = Field(..., description="Key name, ID, URI, or alias")
    type: Optional[str] = Field(None, description="Identifier type (name, id, uri, alias)")
    version: int = Field(-1, description="Key version (-1 for latest)")
    reason: str = Field(..., description="Revocation reason (Unspecified, KeyCompromise, CACompromise, etc.)")
    message: Optional[str] = Field(None, description="Optional revocation message")
    compromise_occurrence_date: Optional[str] = Field(None, description="When compromise occurred")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to revoke key in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class KeyReactivateParams(BaseModel):
    """Parameters for reactivating a key."""
    name: str = Field(..., description="Key name, ID, URI, or alias")
    type: Optional[str] = Field(None, description="Identifier type (name, id, uri, alias)")
    version: int = Field(-1, description="Key version (-1 for latest)")
    reason_to_reactivate: str = Field(..., description="Reactivation reason")
    message_for_reactivate: Optional[str] = Field(None, description="Optional reactivation message")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to reactivate key in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class KeyDestroyParams(BaseModel):
    """Parameters for destroying a key."""
    name: str = Field(..., description="Key name, ID, URI, or alias")
    type: Optional[str] = Field(None, description="Identifier type (name, id, uri, alias)")
    version: int = Field(-1, description="Key version (-1 for latest)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to destroy key in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


# Key Operations Parameter Models
class KeyExportParams(BaseModel):
    """Parameters for exporting a key."""
    name: str = Field(..., description="Key name, ID, URI, or alias")
    type: Optional[str] = Field(None, description="Identifier type (name, id, uri, alias)")
    format: Optional[str] = Field(None, description="Export format (pkcs1, pkcs8, base64, etc.)")
    encoding: Optional[str] = Field(None, description="Encoding (hex, base64)")
    wrap_key_name: Optional[str] = Field(None, description="Wrap key name")
    wrap_public_key: Optional[str] = Field(None, description="Public key for wrapping")
    cxts: bool = Field(False, description="Export full XTS/CBC-CS1 key material")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to export key from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class KeyCloneParams(BaseModel):
    """Parameters for cloning a key."""
    name: str = Field(..., description="Key name, ID, URI, or alias")
    type: Optional[str] = Field(None, description="Identifier type (name, id, uri, alias)")
    version: int = Field(-1, description="Key version (-1 for latest)")
    new_key_name: str = Field(..., description="Name for the cloned key")
    include_material: bool = Field(False, description="Include key material in response")
    jsonfile: Optional[str] = Field(None, description="JSON file for modifying meta values")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to clone key in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class KeyGenerateKcvParams(BaseModel):
    """Parameters for generating key check value."""
    name: str = Field(..., description="Key name, ID, URI, or alias")
    type: Optional[str] = Field(None, description="Identifier type (name, id, uri, alias)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to get key from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


# Alias Parameter Models
class KeyAliasAddParams(BaseModel):
    """Parameters for adding a key alias."""
    name: str = Field(..., description="Key name, ID, URI, or alias")
    alias: str = Field(..., description="Alias to add")
    alias_type: str = Field("string", description="Alias type (string or uri)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to modify key in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class KeyAliasDeleteParams(BaseModel):
    """Parameters for deleting a key alias."""
    name: str = Field(..., description="Key name, ID, URI, or alias")
    alias_index: int = Field(..., description="Index of alias to delete")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to modify key in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class KeyAliasModifyParams(BaseModel):
    """Parameters for modifying a key alias."""
    name: str = Field(..., description="Key name, ID, URI, or alias")
    alias_index: int = Field(..., description="Index of alias to modify")
    alias: str = Field(..., description="New alias value")
    alias_type: str = Field("string", description="Alias type (string or uri)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to modify key in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


# Advanced Parameter Models
class KeyQueryParams(BaseModel):
    """Parameters for complex key queries."""
    query: Optional[str] = Field(None, description="Query parameters in JSON format")
    query_jsonfile: Optional[str] = Field(None, description="JSON file with query parameters")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to query keys in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class KeyListLabelsParams(BaseModel):
    """Parameters for listing key labels."""
    limit: int = Field(10, description="Maximum number of labels to return")
    skip: int = Field(0, description="Offset at which to start the search")
    label: Optional[str] = Field(None, description="Filter by label selector expression")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to list labels from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


# Tool Implementations - Core CRUD
class KeyListTool(BaseTool):
    """
    List cryptographic keys.

    Implements all options from ksctl keys list:
    - --alias, --compare-id-with-uuid, --fields, --key-check-value, --labels-query, --limit, --link-type, --name, --object-type, --sha1-fingerprint, --sha256-fingerprint, --skip, --state, --usage-mask
    - Label selector expressions for --labels-query (see examples below)
    - Usage mask bitwise logic
    - Inherited options: --domain, --auth-domain, etc.

    Examples:
        ksctl keys list --link-type <privateKey,replacedObject> --fields <links,meta,certFields>
        ksctl keys list --labels 'critical=,region=noram'
        ksctl keys list --key-check-value 148b33
        ksctl keys list --usage-mask 12
        ksctl keys list --labels-query 'region=noram,team!=sales'
    """

    @property
    def name(self) -> str:
        return "ct_key_list"

    @property
    def description(self) -> str:
        return "List cryptographic keys with extensive filtering options"

    def get_schema(self) -> dict[str, Any]:
        return KeyListParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute key list command."""
        params = KeyListParams(**kwargs)
        
        args = ["keys", "list"]
        args.extend(["--limit", str(params.limit)])
        args.extend(["--skip", str(params.skip)])
        
        if params.name:
            args.extend(["--name", params.name])
        if params.alias:
            args.extend(["--alias", params.alias])
        if params.fields:
            args.extend(["--fields", params.fields])
        if params.state:
            args.extend(["--state", params.state])
        if params.object_type:
            args.extend(["--object-type", params.object_type])
        if params.usage_mask is not None:
            args.extend(["--usage-mask", str(params.usage_mask)])
        if params.labels_query:
            args.extend(["--labels-query", params.labels_query])
        if params.key_check_value:
            args.extend(["--key-check-value", params.key_check_value])
        if params.link_type:
            args.extend(["--link-type", params.link_type])
        if params.sha1_fingerprint:
            args.extend(["--sha1-fingerprint", params.sha1_fingerprint])
        if params.sha256_fingerprint:
            args.extend(["--sha256-fingerprint", params.sha256_fingerprint])
        if params.compare_id_with_uuid:
            args.extend(["--compare-id-with-uuid", params.compare_id_with_uuid])
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


class KeyCreateTool(BaseTool):
    """
    Create a cryptographic key with comprehensive configuration options.
    
    **Advanced Features:**
    
    **Template-based Creation:**
    - Use --template_id to create keys from predefined templates (accepts template names directly)
    - When using templates, algorithm and size are automatically taken from the template
    - Template parameters can be overridden by request parameters (for privileged users)
    - Restricted users have limited override capabilities
    - Direct template name usage with ksctl --templateId parameter
    
    **Enterprise Identity Management:**
    - Set --owner-id to specify key ownership
    - Configure --id, --uuid, --muid, --key-id for specific identifier requirements
    - Use --ret to return existing keys with same name instead of failing
    
    **Advanced Wrapping and Security:**
    - HKDF parameters via --hkdf or --hkdf-jsonfile
    - PBE wrapping via --wrap-pbe or --wrap-pbe-jsonfile  
    - RSA AES KWP via --wrap-rsa-aes or --wrap-rsa-aes-jsonfile
    - MAC/Signature generation via --macsign-key-id and --signing-algo
    - Custom wrapping methods via --wrapping-method, --wrapping-encryption-algo
    
    **PKCS12 Support:**
    - Password management via --passwordkey or --secretdatalink
    - Encoding control via --secretdataencoding
    
    **File-based Configuration:**
    - Public key parameters via --public-key-jsonfile
    - Wrap public key from file via --wrap-public-key-file
    
    **CTE Integration:**
    - Full CTE key support with --cte-key-type (standard, ldt, xts)
    - Encryption modes: CBC, CBC_CS1, XTS via --cte-encryption-mode
    - Client persistence via --cte-persistent-on-client
    - Permission groups via --cte-permissions-groups
    """

    @property
    def name(self) -> str:
        return "ct_key_create"

    @property
    def description(self) -> str:
        return "Create a cryptographic key with comprehensive configuration options including templates, advanced wrapping, and CTE support"

    def get_schema(self) -> dict[str, Any]:
        return KeyCreateParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute key create command with full parameter support."""
        params = KeyCreateParams(**kwargs)
        
        # Pre-validate material format if material is provided
        if params.material:
            validation_result = params.validate_and_convert_material()
            if not validation_result["valid"]:
                return {
                    "error": "Material format validation failed",
                    "details": validation_result.get("error"),
                    "format_help": params.get_material_format_help(),
                    "conversion_error": validation_result.get("conversion_error")
                }
            if validation_result.get("converted"):
                params.material = validation_result.get("new_material", params.material)
        
        # Handle CTE key creation (existing logic preserved)
        if params.cte_key_type:
            # Build the full key JSON structure
            key_json = {
                "algorithm": params.algorithm.lower(),  # Ensure lowercase
                "size": params.size if params.size else 256,
                "undeletable": params.undeletable,
                "unexportable": False,  # Always false for CTE keys
            }
            
            # Add name if provided
            if params.name:
                key_json["name"] = params.name
            elif params.autoname:
                # Let the system generate a name
                pass
            
            # Add owner_id if provided
            if params.owner_id:
                key_json["meta"] = key_json.get("meta", {})
                key_json["meta"]["ownerId"] = params.owner_id
                
            # Add CTE-specific attributes
            key_json["meta"] = key_json.get("meta", {})
            key_json["meta"]["permissions"] = {
                "ExportKey": params.cte_permissions_groups.split(',') if params.cte_permissions_groups else ["CTE Clients"],
                "ReadKey": params.cte_permissions_groups.split(',') if params.cte_permissions_groups else ["CTE Clients"]
            }
            key_json["meta"]["cte"] = {
                "persistent_on_client": params.cte_persistent_on_client if params.cte_persistent_on_client is not None else True,
                "encryption_mode": params.cte_encryption_mode.upper() if params.cte_encryption_mode else "CBC",
                "cte_versioned": params.cte_key_type == 'ldt'
            }
            
            if params.cte_key_type == 'xts' or (params.cte_encryption_mode and params.cte_encryption_mode.upper() == 'XTS'):
                key_json["xts"] = True
            
            # Convert to JSON string and create temporary file
            
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            json.dump(key_json, temp_file, indent=2)
            temp_file.close()
            
            # Execute with jsonfile
            args = ["keys", "create", "--jsonfile", temp_file.name]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            
            # Clean up temporary file
            os.unlink(temp_file.name)
            
            return result.get("data", result.get("stdout", ""))
            
        # Standard key creation (non-CTE)
        args = ["keys", "create"]
        
        # Add all other parameters
        if params.name:
            args.extend(["--name", params.name])
        elif params.autoname:
            args.append("--autoname")
        
        if params.algorithm:
            args.extend(["--alg", params.algorithm])
        if params.size:
            args.extend(["--size", str(params.size)])
        if params.curve_id:
            args.extend(["--curve-id", params.curve_id])
        if params.usage_mask is not None:
            args.extend(["--usage-mask", str(params.usage_mask)])
        if params.description:
            args.extend(["--description", params.description])
        if params.labels:
            args.extend(["--labels", params.labels])
        if params.aliases:
            args.extend(["--aliases", params.aliases])
        
        # Material and format
        if params.material:
            args.extend(["--material", params.material])
        if params.format:
            args.extend(["--format", params.format])
        if params.encoding:
            args.extend(["--encoding", params.encoding])
        if params.include_material:
            args.append("--include-material")
        if params.empty_material:
            args.append("--empty-material")
        
        # Key properties
        if params.xts:
            args.append("--xts")
        if params.undeletable:
            args.append("--nodelete")
        if params.unexportable:
            args.append("--noexport")
        
        # Object and certificate types
        if params.object_type:
            args.extend(["--object-type", params.object_type])
        if params.cert_type:
            args.extend(["--cert-type", params.cert_type])
        if params.cert_filename:
            args.extend(["--cert-filename", params.cert_filename])
        
        # JSON configuration
        if params.jsonfile:
            args.extend(["--jsonfile", params.jsonfile])
        
        # Wrapping and encryption
        if params.wrap_key_name:
            args.extend(["--wrap-key-name", params.wrap_key_name])
        if params.wrap_public_key:
            args.extend(["--wrap-public-key", params.wrap_public_key])
        
        # Rotation
        if params.rotation_frequency_days:
            args.extend(["--rotation-frequency-days", params.rotation_frequency_days])
        
        # Critical missing parameters
        if params.ret:
            args.append("--ret")
        if params.template_id:
            args.extend(["--templateId", params.template_id])
        if params.owner_id:
            args.extend(["--ownerid", params.owner_id])
        if params.id:
            args.extend(["--id", params.id])
        if params.uuid:
            args.extend(["--uuid", params.uuid])
        if params.muid:
            args.extend(["--muid", params.muid])
        if params.key_id:
            args.extend(["--key-id", params.key_id])
        
        # Advanced wrapping parameters
        if params.hkdf:
            args.extend(["--hkdf", params.hkdf])
        if params.hkdf_jsonfile:
            args.extend(["--hkdf-jsonfile", params.hkdf_jsonfile])
        if params.wrap_pbe:
            args.extend(["--wrap-pbe", params.wrap_pbe])
        if params.wrap_pbe_jsonfile:
            args.extend(["--wrap-pbe-jsonfile", params.wrap_pbe_jsonfile])
        if params.wrap_hkdf:
            args.extend(["--wrap-hkdf", params.wrap_hkdf])
        if params.wrap_hkdf_jsonfile:
            args.extend(["--wrap-hkdf-jsonfile", params.wrap_hkdf_jsonfile])
        if params.wrap_rsa_aes:
            args.extend(["--wrap-rsa-aes", params.wrap_rsa_aes])
        if params.wrap_rsa_aes_jsonfile:
            args.extend(["--wrap-rsa-aes-jsonfile", params.wrap_rsa_aes_jsonfile])
        
        # Wrapping method configuration
        if params.wrapping_method:
            args.extend(["--wrapping-method", params.wrapping_method])
        if params.wrapping_encryption_algo:
            args.extend(["--wrapping-encryption-algo", params.wrapping_encryption_algo])
        if params.wrapping_hashing_algo:
            args.extend(["--wrapping-hashing-algo", params.wrapping_hashing_algo])
        
        # MAC/Signature generation
        if params.macsign_key_id:
            args.extend(["--macsign-key-id", params.macsign_key_id])
        if params.macsign_key_id_type:
            args.extend(["--macsign-key-id-type", params.macsign_key_id_type])
        if params.signing_algo:
            args.extend(["--signing-algo", params.signing_algo])
        
        # PKCS12 support
        if params.passwordkey:
            args.extend(["--passwordkey", params.passwordkey])
        if params.secretdatalink:
            args.extend(["--secretdatalink", params.secretdatalink])
        if params.secretdataencoding:
            args.extend(["--secretdataencoding", params.secretdataencoding])
        
        # File-based parameters
        if params.public_key_jsonfile:
            args.extend(["--public-key-jsonfile", params.public_key_jsonfile])
        if params.wrap_public_key_file:
            args.extend(["--wrap-public-key-file", params.wrap_public_key_file])
        
        # Additional wrapping options
        if params.padded:
            args.append("--padded")
        if params.wrapkey_id_type:
            args.extend(["--wrapkey-id-type", params.wrapkey_id_type])
        
        # Size and ID configuration
        if params.id_size:
            args.extend(["--id-size", str(params.id_size)])
        
        # Deprecated but supported
        if params.defaultiv:
            args.extend(["--defaultiv", params.defaultiv])
        if params.usage:
            args.extend(["--usage", params.usage])
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


class KeyGetTool(BaseTool):
    """Get information about a cryptographic key."""

    @property
    def name(self) -> str:
        return "ct_key_get"

    @property
    def description(self) -> str:
        return "Get detailed information about a cryptographic key"

    def get_schema(self) -> dict[str, Any]:
        return KeyGetParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute key get command."""
        params = KeyGetParams(**kwargs)
        
        args = ["keys", "get", "--name", params.name]
        if params.type:
            args.extend(["--type", params.type])
        if params.version != -1:
            args.extend(["--version", str(params.version)])
        if params.usage_mask is not None:
            args.extend(["--usage-mask", str(params.usage_mask)])
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


class KeyDeleteTool(BaseTool):
    """Delete a cryptographic key."""

    @property
    def name(self) -> str:
        return "ct_key_delete"

    @property
    def description(self) -> str:
        return "Delete a cryptographic key or managed object"

    def get_schema(self) -> dict[str, Any]:
        return KeyDeleteParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute key delete command."""
        params = KeyDeleteParams(**kwargs)
        
        args = ["keys", "delete", "--name", params.name]
        if params.type:
            args.extend(["--type", params.type])
        if params.version != -1:
            args.extend(["--version", str(params.version)])
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


class KeyModifyTool(BaseTool):
    """Modify key metadata."""

    @property
    def name(self) -> str:
        return "ct_key_modify"

    @property
    def description(self) -> str:
        return "Modify key metadata including labels, description, and rotation settings"

    def get_schema(self) -> dict[str, Any]:
        return KeyModifyParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute key modify command."""
        params = KeyModifyParams(**kwargs)
        
        args = ["keys", "modify", "--name", params.name]
        if params.type:
            args.extend(["--type", params.type])
        if params.labels:
            args.extend(["--labels", params.labels])
        if params.remove_labels:
            args.extend(["--remove-labels", params.remove_labels])
        
        json_file_path = None
        try:
            if params.jsonfile:
                json_file_path = params.jsonfile
            elif params.json_content:
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
                json.dump(json.loads(params.json_content), temp_file, indent=2)
                temp_file.close()
                json_file_path = temp_file.name
            else:
                json_file_path = params.create_json_file()
            
            if json_file_path:
                args.extend(["--jsonfile", json_file_path])
            
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
            
        finally:
            if json_file_path and json_file_path != params.jsonfile:
                try:
                    os.unlink(json_file_path)
                except:
                    pass


# Lifecycle Tools
class KeyArchiveTool(BaseTool):
    """Archive a key."""

    @property
    def name(self) -> str:
        return "ct_key_archive"

    @property
    def description(self) -> str:
        return "Archive a key, taking it offline"

    def get_schema(self) -> dict[str, Any]:
        return KeyArchiveParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute key archive command."""
        params = KeyArchiveParams(**kwargs)
        
        args = ["keys", "archive", "--name", params.name]
        if params.type:
            args.extend(["--type", params.type])
        if params.version != -1:
            args.extend(["--version", str(params.version)])
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


class KeyRecoverTool(BaseTool):
    """Recover an archived key."""

    @property
    def name(self) -> str:
        return "ct_key_recover"

    @property
    def description(self) -> str:
        return "Recover an archived key, bringing it back online"

    def get_schema(self) -> dict[str, Any]:
        return KeyRecoverParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute key recover command."""
        params = KeyRecoverParams(**kwargs)
        
        args = ["keys", "recover", "--name", params.name]
        if params.type:
            args.extend(["--type", params.type])
        if params.version != -1:
            args.extend(["--version", str(params.version)])
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


class KeyRevokeTool(BaseTool):
    """Revoke a key."""

    @property
    def name(self) -> str:
        return "ct_key_revoke"

    @property
    def description(self) -> str:
        return "Revoke a key, marking it deactivated or compromised"

    def get_schema(self) -> dict[str, Any]:
        return KeyRevokeParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute key revoke command."""
        params = KeyRevokeParams(**kwargs)
        
        args = ["keys", "revoke", "--name", params.name, "--reason", params.reason]
        if params.type:
            args.extend(["--type", params.type])
        if params.version != -1:
            args.extend(["--version", str(params.version)])
        if params.message:
            args.extend(["--message", params.message])
        if params.compromise_occurrence_date:
            args.extend(["--compromise-occurrence-date", params.compromise_occurrence_date])
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


class KeyReactivateTool(BaseTool):
    """Reactivate a key."""

    @property
    def name(self) -> str:
        return "ct_key_reactivate"

    @property
    def description(self) -> str:
        return "Reactivate a key to Active state"

    def get_schema(self) -> dict[str, Any]:
        return KeyReactivateParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute key reactivate command."""
        params = KeyReactivateParams(**kwargs)
        
        args = ["keys", "reactivate", "--name", params.name, "--reasontoreactivate", params.reason_to_reactivate]
        if params.type:
            args.extend(["--type", params.type])
        if params.version != -1:
            args.extend(["--version", str(params.version)])
        if params.message_for_reactivate:
            args.extend(["--messageforreactivate", params.message_for_reactivate])
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


class KeyDestroyTool(BaseTool):
    """Destroy a key's material."""

    @property
    def name(self) -> str:
        return "ct_key_destroy"

    @property
    def description(self) -> str:
        return "Destroy a key's cryptographic material"

    def get_schema(self) -> dict[str, Any]:
        return KeyDestroyParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute key destroy command."""
        params = KeyDestroyParams(**kwargs)
        
        args = ["keys", "destroy", "--name", params.name]
        if params.type:
            args.extend(["--type", params.type])
        if params.version != -1:
            args.extend(["--version", str(params.version)])
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


# Key Operations Tools
class KeyExportTool(BaseTool):
    """Export a key."""

    @property
    def name(self) -> str:
        return "ct_key_export"

    @property
    def description(self) -> str:
        return "Export a key to get the key material"

    def get_schema(self) -> dict[str, Any]:
        return KeyExportParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute key export command."""
        params = KeyExportParams(**kwargs)
        
        args = ["keys", "export", "--name", params.name]
        if params.type:
            args.extend(["--type", params.type])
        if params.format:
            args.extend(["--format", params.format])
        if params.encoding:
            args.extend(["--encoding", params.encoding])
        if params.wrap_key_name:
            args.extend(["--wrap-key-name", params.wrap_key_name])
        if params.wrap_public_key:
            args.extend(["--wrap-public-key", params.wrap_public_key])
        if params.cxts:
            args.append("--cxts")
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


class KeyCloneTool(BaseTool):
    """Clone an existing key."""

    @property
    def name(self) -> str:
        return "ct_key_clone"

    @property
    def description(self) -> str:
        return "Clone an existing key to create a new copy"

    def get_schema(self) -> dict[str, Any]:
        return KeyCloneParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute key clone command."""
        params = KeyCloneParams(**kwargs)
        
        args = ["keys", "clone", "--name", params.name, "--new-key-name", params.new_key_name]
        if params.type:
            args.extend(["--type", params.type])
        if params.version != -1:
            args.extend(["--version", str(params.version)])
        if params.include_material:
            args.append("--include-material")
        if params.jsonfile:
            args.extend(["--jsonfile", params.jsonfile])
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


class KeyGenerateKcvTool(BaseTool):
    """Generate Key Check Value for symmetric keys."""

    @property
    def name(self) -> str:
        return "ct_key_generate_kcv"

    @property
    def description(self) -> str:
        return "Generate Key Check Value for AES or TDES keys"

    def get_schema(self) -> dict[str, Any]:
        return KeyGenerateKcvParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute key generate-kcv command."""
        params = KeyGenerateKcvParams(**kwargs)
        
        args = ["keys", "generate-kcv", "--name", params.name]
        if params.type:
            args.extend(["--type", params.type])
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


# Alias Management Tools
class KeyAliasAddTool(BaseTool):
    """Add a key alias."""

    @property
    def name(self) -> str:
        return "ct_key_alias_add"

    @property
    def description(self) -> str:
        return "Add an alias to a key"

    def get_schema(self) -> dict[str, Any]:
        return KeyAliasAddParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute key alias add command."""
        params = KeyAliasAddParams(**kwargs)
        
        args = ["keys", "alias", "add", "--name", params.name, "--alias", params.alias, "--alias-type", params.alias_type]
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


class KeyAliasDeleteTool(BaseTool):
    """Delete a key alias."""

    @property
    def name(self) -> str:
        return "ct_key_alias_delete"

    @property
    def description(self) -> str:
        return "Delete a key alias by index"

    def get_schema(self) -> dict[str, Any]:
        return KeyAliasDeleteParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute key alias delete command."""
        params = KeyAliasDeleteParams(**kwargs)
        
        args = ["keys", "alias", "delete", "--name", params.name, "--alias-index", str(params.alias_index)]
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


class KeyAliasModifyTool(BaseTool):
    """Modify a key alias."""

    @property
    def name(self) -> str:
        return "ct_key_alias_modify"

    @property
    def description(self) -> str:
        return "Modify an existing key alias"

    def get_schema(self) -> dict[str, Any]:
        return KeyAliasModifyParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute key alias modify command."""
        params = KeyAliasModifyParams(**kwargs)
        
        args = ["keys", "alias", "modify", "--name", params.name, "--alias-index", str(params.alias_index), "--alias", params.alias, "--alias-type", params.alias_type]
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


# Advanced Tools
class KeyQueryTool(BaseTool):
    """
    Complex query for keys.

    Implements all options from ksctl keys query:
    - Accepts a JSON query via --query or --query-jsonfile
    - Supports all documented query fields: algorithm, owner, labels, permissions, etc.
    - Advanced filtering (arrays, wildcards, metaContains, etc.)
    - Inherited options

    Examples:
        ksctl keys query --query '{"algorithm": "AES", "owner": "user1"}'
        ksctl keys query --query-jsonfile myquery.json
        ksctl keys query --query '{"labels": ["region=noram", "team!=sales"]}'
        ksctl keys query --query '{"permissions": ["ReadKey","UseKey"]}'
    """

    @property
    def name(self) -> str:
        return "ct_key_query"

    @property
    def description(self) -> str:
        return "Perform complex queries for keys using JSON parameters"

    def get_schema(self) -> dict[str, Any]:
        return KeyQueryParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute key query command."""
        params = KeyQueryParams(**kwargs)
        
        args = ["keys", "query"]
        if params.query:
            args.extend(["--query", params.query])
        if params.query_jsonfile:
            args.extend(["--query-jsonfile", params.query_jsonfile])
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


class KeyListLabelsTool(BaseTool):
    """
    List key labels.

    Implements all options from ksctl keys list-labels:
    - --label for selector expressions
    - --limit, --skip
    - Inherited options

    Examples:
        ksctl keys list-labels
        ksctl keys list-labels --label 'env=test'
        ksctl keys list-labels --label 'region=noram'
        ksctl keys list-labels --label '!region'
    """

    @property
    def name(self) -> str:
        return "ct_key_list_labels"

    @property
    def description(self) -> str:
        return "List available key labels with filtering"

    def get_schema(self) -> dict[str, Any]:
        return KeyListLabelsParams.model_json_schema()

    async def execute(self, **kwargs: Any) -> Any:
        """Execute key list-labels command."""
        params = KeyListLabelsParams(**kwargs)
        
        args = ["keys", "list-labels"]
        args.extend(["--limit", str(params.limit)])
        args.extend(["--skip", str(params.skip)])
        if params.label:
            args.extend(["--label", params.label])
        
        result = self.execute_with_domain(args, params.domain, params.auth_domain)
        return result.get("data", result.get("stdout", ""))


# Export all key tools

class KeyManagementTool(BaseTool):
    name = "key_management"
    description = "Comprehensive key management operations with advanced features including templates, enterprise identity management, advanced wrapping, CTE integration, and PKCS12 support"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": [
                    "list", "create", "get", "delete", "modify", "archive", "recover", "revoke", "reactivate", "destroy", "export", "clone", "generate_kcv", "alias_add", "alias_delete", "alias_modify", "query", "list_labels", "validate_import", "generate_test_key_material"
                ]},
                # List parameters
                "limit": {"type": "integer", "default": 10},
                "skip": {"type": "integer", "default": 0},
                "name": {"type": "string"},
                "alias": {"type": "string"},
                "fields": {"type": "string"},
                "state": {"type": "string"},
                "object_type": {"type": "string"},
                "usage_mask": {"type": "integer"},
                "labels_query": {"type": "string"},
                "key_check_value": {"type": "string"},
                "link_type": {"type": "string"},
                "sha1_fingerprint": {"type": "string"},
                "sha256_fingerprint": {"type": "string"},
                "compare_id_with_uuid": {"type": "string"},
                # Create parameters
                "autoname": {"type": "boolean", "default": False},
                "algorithm": {"type": "string", "default": "AES"},
                "size": {"type": "integer"},
                "curve_id": {"type": "string"},
                "description": {"type": "string"},
                "labels": {"type": "string"},
                "aliases": {"type": "string"},
                "material": {"type": "string"},
                "format": {"type": "string"},
                "encoding": {"type": "string"},
                "xts": {"type": "boolean", "default": False},
                "undeletable": {"type": "boolean", "default": False},
                "unexportable": {"type": "boolean", "default": False},
                "include_material": {"type": "boolean", "default": False},
                "empty_material": {"type": "boolean", "default": False},
                "cert_type": {"type": "string"},
                "cert_filename": {"type": "string"},
                "jsonfile": {"type": "string"},
                "wrap_key_name": {"type": "string"},
                "wrap_public_key": {"type": "string"},
                "rotation_frequency_days": {"type": "string"},
                # CTE-specific parameters
                "cte_key_type": {"type": "string", "enum": ["standard", "ldt", "xts"]},
                "cte_persistent_on_client": {"type": "boolean"},
                "cte_permissions_groups": {"type": "string"},
                "cte_encryption_mode": {"type": "string", "enum": ["CBC", "CBC_CS1", "XTS"]},
                # Common parameters
                "type": {"type": "string"},
                "version": {"type": "integer", "default": -1},
                "domain": {"type": "string"},
                "auth_domain": {"type": "string"},
                # Alias parameters
                "alias_index": {"type": "integer"},
                "alias_type": {"type": "string", "default": "string"},
                # Query parameters
                "query": {"type": "string"},
                "query_jsonfile": {"type": "string"},
                # Revoke/Reactivate parameters
                "reason": {"type": "string"},
                "message": {"type": "string"},
                "compromise_occurrence_date": {"type": "string"},
                "reason_to_reactivate": {"type": "string"},
                "message_for_reactivate": {"type": "string"},
                # Clone parameters
                "new_key_name": {"type": "string"},
                # Export parameters
                "cxts": {"type": "boolean", "default": False},
                # Label parameters
                "label": {"type": "string"},
                # Modify parameters
                "remove_labels": {"type": "string"},
                
                # Additional parameters
                
                # Critical missing parameters
                "ret": {"type": "boolean", "default": False, "description": "Return existing key with same name if it exists"},
                "template_id": {"type": "string", "description": "Template ID for creating key using template"},
                "owner_id": {"type": "string", "description": "The user's ID (owner of the key)"},
                "id": {"type": "string", "description": "Specific key identifier"},
                "uuid": {"type": "string", "description": "UUID identifier (32 hex digits with 4 dashes)"},
                "muid": {"type": "string", "description": "Additional identifier (MUID)"},
                "key_id": {"type": "string", "description": "Additional key identifier"},
                
                # Advanced wrapping parameters
                "hkdf": {"type": "string", "description": "HKDF parameters in JSON format"},
                "hkdf_jsonfile": {"type": "string", "description": "HKDF parameters via JSON file"},
                "wrap_pbe": {"type": "string", "description": "PBE wrap parameters in JSON format"},
                "wrap_pbe_jsonfile": {"type": "string", "description": "PBE wrap parameters via JSON file"},
                "wrap_hkdf": {"type": "string", "description": "HKDF wrap parameters in JSON format"},
                "wrap_hkdf_jsonfile": {"type": "string", "description": "HKDF wrap parameters via JSON file"},
                "wrap_rsa_aes": {"type": "string", "description": "RSA AES KWP parameters in JSON format"},
                "wrap_rsa_aes_jsonfile": {"type": "string", "description": "RSA AES KWP parameters via JSON file"},
                
                # Wrapping method configuration
                "wrapping_method": {"type": "string", "description": "Wrapping method: encrypt, mac/sign"},
                "wrapping_encryption_algo": {"type": "string", "description": "Encryption algorithm for wrapping (Algorithm/Mode/Padding)"},
                "wrapping_hashing_algo": {"type": "string", "description": "Hashing algorithm for mac/sign wrapping"},
                
                # MAC/Signature generation
                "macsign_key_id": {"type": "string", "description": "Key ID for MAC/signature generation"},
                "macsign_key_id_type": {"type": "string", "description": "MAC/sign key ID type (name, id, alias)"},
                "signing_algo": {"type": "string", "description": "Signing algorithm (RSA, RSA-PSS)"},
                
                # PKCS12 support
                "passwordkey": {"type": "string", "description": "Password key for PKCS12 format (ID or name of Secret Data)"},
                "secretdatalink": {"type": "string", "description": "Base64 encoded password for PKCS12 format"},
                "secretdataencoding": {"type": "string", "description": "Encoding method for secretDataLink material"},
                
                # File-based parameters
                "public_key_jsonfile": {"type": "string", "description": "Public key parameters via JSON file"},
                "wrap_public_key_file": {"type": "string", "description": "File containing base64 public key for wrapping"},
                
                # Additional wrapping options
                "padded": {"type": "boolean", "default": False, "description": "Use RFC-5649 padding for wrap-key-name (symmetric keys only)"},
                "wrapkey_id_type": {"type": "string", "description": "Wrap key ID type (name, id, alias)"},
                
                # Size and ID configuration
                "id_size": {"type": "integer", "description": "Size of ID for the key"},
                
                # Deprecated but supported
                "defaultiv": {"type": "string", "description": "Deprecated: Default IV (hex encoded)"},
                "usage": {"type": "string", "description": "Deprecated: Key usage (use usage_mask instead)"},
                # Test material generation parameters
                "count": {"type": "integer", "default": 1, "description": "Number of test materials to generate"},
                "format": {"type": "string", "enum": ["hex", "pem"], "description": "Output format"}
            },
            "required": ["action"]
        }

    async def execute(self, **kwargs: Any) -> Any:
        action = kwargs.get("action")
        if action == "list":
            params = KeyListParams(**kwargs)
            args = ["keys", "list"]
            args.extend(["--limit", str(params.limit)])
            args.extend(["--skip", str(params.skip)])
            if params.name:
                args.extend(["--name", params.name])
            if params.alias:
                args.extend(["--alias", params.alias])
            if params.fields:
                args.extend(["--fields", params.fields])
            if params.state:
                args.extend(["--state", params.state])
            if params.object_type:
                args.extend(["--object-type", params.object_type])
            if params.usage_mask is not None:
                args.extend(["--usage-mask", str(params.usage_mask)])
            if params.labels_query:
                args.extend(["--labels-query", params.labels_query])
            if params.key_check_value:
                args.extend(["--key-check-value", params.key_check_value])
            if params.link_type:
                args.extend(["--link-type", params.link_type])
            if params.sha1_fingerprint:
                args.extend(["--sha1-fingerprint", params.sha1_fingerprint])
            if params.sha256_fingerprint:
                args.extend(["--sha256-fingerprint", params.sha256_fingerprint])
            if params.compare_id_with_uuid:
                args.extend(["--compare-id-with-uuid", params.compare_id_with_uuid])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "create":
            params = KeyCreateParams(**kwargs)
            if params.cte_key_type:
                key_json = {
                    "algorithm": params.algorithm.lower(),
                    "size": params.size if params.size else 256,
                    "undeletable": params.undeletable,
                    "unexportable": False,
                }
                
                # Add name if provided
                if params.name:
                    key_json["name"] = params.name
                elif params.autoname:
                    # Let the system generate a name
                    pass
                
                # Add owner_id if provided
                if params.owner_id:
                    key_json["meta"] = key_json.get("meta", {})
                    key_json["meta"]["ownerId"] = params.owner_id
                
                # Build meta object for CTE keys
                permissions_groups = params.cte_permissions_groups.split(",") if params.cte_permissions_groups else ["CTE Clients"]
                if "meta" not in key_json:
                    key_json["meta"] = {}
                key_json["meta"]["permissions"] = {
                    "ExportKey": permissions_groups,
                    "ReadKey": permissions_groups
                }
                key_json["meta"]["cte"] = {}
                
                # Determine encryption mode
                encryption_mode = params.cte_encryption_mode or "CBC"
                
                # Validate encryption mode based on xts flag
                if encryption_mode in ["CBC_CS1", "XTS"] and not params.xts:
                    raise ValueError(f"Encryption mode '{encryption_mode}' requires xts flag to be true")
                
                # Configure based on CTE key type
                if params.cte_key_type == "standard":
                    key_json["meta"]["cte"]["cte_versioned"] = False
                    key_json["meta"]["cte"]["encryption_mode"] = encryption_mode
                    key_json["xts"] = params.xts
                elif params.cte_key_type == "ldt":
                    key_json["meta"]["cte"]["cte_versioned"] = True
                    key_json["meta"]["cte"]["encryption_mode"] = encryption_mode
                    key_json["xts"] = params.xts
                elif params.cte_key_type == "xts":
                    key_json["meta"]["cte"]["cte_versioned"] = True
                    key_json["meta"]["cte"]["encryption_mode"] = "XTS"
                    key_json["xts"] = True
                
                # Add optional CTE settings
                if params.cte_persistent_on_client is not None:
                    key_json["meta"]["cte"]["persistent_on_client"] = params.cte_persistent_on_client
                
                # Add other parameters if specified
                if params.description:
                    key_json["description"] = params.description
                if params.labels:
                    # Convert labels string to dictionary
                    labels_dict = {}
                    for label in params.labels.split(","):
                        if "=" in label:
                            key, value = label.split("=", 1)
                            labels_dict[key.strip()] = value.strip()
                    key_json["labels"] = labels_dict
                if params.aliases:
                    key_json["aliases"] = [{"alias": alias.strip(), "type": "string"} for alias in params.aliases.split(",")]
                if params.usage_mask is not None:
                    key_json["usage_mask"] = params.usage_mask
                
                # Write to temporary JSON file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(key_json, f, indent=2)
                    temp_file = f.name
                
                try:
                    args = ["keys", "create", "--jsonfile", temp_file]
                    if params.include_material:
                        args.append("--include-material")
                    if params.ret:
                        args.append("--ret")
                    
                    result = self.execute_with_domain(args, params.domain, params.auth_domain)
                    return result.get("data", result.get("stdout", ""))
                finally:
                    # Clean up temp file
                    os.unlink(temp_file)
            
            # Standard key creation with all parameters
            args = ["keys", "create"]
            if params.name:
                args.extend(["--name", params.name])
            if params.autoname:
                args.append("--autoname")
            
            # Only add algorithm and size if NOT using a template
            # Templates define these attributes and adding them would override the template
            if not params.template_id:
                args.extend(["--alg", params.algorithm])
                # For EC keys, use curve_id instead of size to avoid conflicts
                if params.algorithm.upper() == "EC":
                    if params.curve_id:
                        args.extend(["--curve-id", params.curve_id])
                    else:
                        # Default to a standard curve if none specified
                        args.extend(["--curve-id", "prime256v1"])
                elif params.size:  # For non-EC keys, use size parameter
                    args.extend(["--size", str(params.size)])
            
            if params.curve_id and params.algorithm.upper() != "EC":
                args.extend(["--curve-id", params.curve_id])
            if params.usage_mask is not None:
                args.extend(["--usage-mask", str(params.usage_mask)])
            if params.description:
                args.extend(["--description", params.description])
            if params.labels:
                args.extend(["--labels", params.labels])
            if params.aliases:
                args.extend(["--aliases", params.aliases])
            if params.material:
                args.extend(["--material", params.material])
            if params.format:
                args.extend(["--format", params.format])
            if params.encoding:
                args.extend(["--encoding", params.encoding])
            if params.xts:
                args.append("--xts")
            if params.undeletable:
                args.append("--nodelete")
            if params.unexportable:
                args.append("--noexport")
            if params.include_material:
                args.append("--include-material")
            if params.empty_material:
                args.append("--empty-material")
            if params.object_type:
                args.extend(["--object-type", params.object_type])
            if params.cert_type:
                args.extend(["--cert-type", params.cert_type])
            if params.cert_filename:
                args.extend(["--cert-filename", params.cert_filename])
            if params.jsonfile:
                args.extend(["--jsonfile", params.jsonfile])
            if params.wrap_key_name:
                args.extend(["--wrap-key-name", params.wrap_key_name])
            if params.wrap_public_key:
                args.extend(["--wrap-public-key", params.wrap_public_key])
            if params.rotation_frequency_days:
                args.extend(["--rotation-frequency-days", params.rotation_frequency_days])
            
            # Add all new parameters
            if params.ret:
                args.append("--ret")
            if params.template_id:
                # Use template name directly with ksctl --templateId
                args.extend(["--templateId", params.template_id])
            if params.owner_id:
                args.extend(["--ownerid", params.owner_id])
            if params.id:
                args.extend(["--id", params.id])
            if params.uuid:
                args.extend(["--uuid", params.uuid])
            if params.muid:
                args.extend(["--muid", params.muid])
            if params.key_id:
                args.extend(["--key-id", params.key_id])
            if params.hkdf:
                args.extend(["--hkdf", params.hkdf])
            if params.hkdf_jsonfile:
                args.extend(["--hkdf-jsonfile", params.hkdf_jsonfile])
            if params.wrap_pbe:
                args.extend(["--wrap-pbe", params.wrap_pbe])
            if params.wrap_pbe_jsonfile:
                args.extend(["--wrap-pbe-jsonfile", params.wrap_pbe_jsonfile])
            if params.wrap_hkdf:
                args.extend(["--wrap-hkdf", params.wrap_hkdf])
            if params.wrap_hkdf_jsonfile:
                args.extend(["--wrap-hkdf-jsonfile", params.wrap_hkdf_jsonfile])
            if params.wrap_rsa_aes:
                args.extend(["--wrap-rsa-aes", params.wrap_rsa_aes])
            if params.wrap_rsa_aes_jsonfile:
                args.extend(["--wrap-rsa-aes-jsonfile", params.wrap_rsa_aes_jsonfile])
            if params.wrapping_method:
                args.extend(["--wrapping-method", params.wrapping_method])
            if params.wrapping_encryption_algo:
                args.extend(["--wrapping-encryption-algo", params.wrapping_encryption_algo])
            if params.wrapping_hashing_algo:
                args.extend(["--wrapping-hashing-algo", params.wrapping_hashing_algo])
            if params.macsign_key_id:
                args.extend(["--macsign-key-id", params.macsign_key_id])
            if params.macsign_key_id_type:
                args.extend(["--macsign-key-id-type", params.macsign_key_id_type])
            if params.signing_algo:
                args.extend(["--signing-algo", params.signing_algo])
            if params.passwordkey:
                args.extend(["--passwordkey", params.passwordkey])
            if params.secretdatalink:
                args.extend(["--secretdatalink", params.secretdatalink])
            if params.secretdataencoding:
                args.extend(["--secretdataencoding", params.secretdataencoding])
            if params.public_key_jsonfile:
                args.extend(["--public-key-jsonfile", params.public_key_jsonfile])
            if params.wrap_public_key_file:
                args.extend(["--wrap-public-key-file", params.wrap_public_key_file])
            if params.padded:
                args.append("--padded")
            if params.wrapkey_id_type:
                args.extend(["--wrapkey-id-type", params.wrapkey_id_type])
            if params.id_size:
                args.extend(["--id-size", str(params.id_size)])
            if params.defaultiv:
                args.extend(["--defaultiv", params.defaultiv])
            if params.usage:
                args.extend(["--usage", params.usage])
            
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "get":
            params = KeyGetParams(**kwargs)
            args = ["keys", "get", "--name", params.name]
            if params.type:
                args.extend(["--type", params.type])
            if params.version != -1:
                args.extend(["--version", str(params.version)])
            if params.usage_mask is not None:
                args.extend(["--usage-mask", str(params.usage_mask)])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "delete":
            params = KeyDeleteParams(**kwargs)
            args = ["keys", "delete", "--name", params.name]
            if params.type:
                args.extend(["--type", params.type])
            if params.version != -1:
                args.extend(["--version", str(params.version)])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "modify":
            params = KeyModifyParams(**kwargs)
            args = ["keys", "modify", "--name", params.name]
            if params.type:
                args.extend(["--type", params.type])
            if params.labels:
                args.extend(["--labels", params.labels])
            if params.remove_labels:
                args.extend(["--remove-labels", params.remove_labels])
            
            json_file_path = None
            try:
                if params.jsonfile:
                    json_file_path = params.jsonfile
                elif params.json_content:
                    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
                    json.dump(json.loads(params.json_content), temp_file, indent=2)
                    temp_file.close()
                    json_file_path = temp_file.name
                else:
                    json_file_path = params.create_json_file()
                
                if json_file_path:
                    args.extend(["--jsonfile", json_file_path])
                
                result = self.execute_with_domain(args, params.domain, params.auth_domain)
                return result.get("data", result.get("stdout", ""))
                
            finally:
                if json_file_path and json_file_path != params.jsonfile:
                    try:
                        os.unlink(json_file_path)
                    except:
                        pass
        elif action == "archive":
            params = KeyArchiveParams(**kwargs)
            args = ["keys", "archive", "--name", params.name]
            if params.type:
                args.extend(["--type", params.type])
            if params.version != -1:
                args.extend(["--version", str(params.version)])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "recover":
            params = KeyRecoverParams(**kwargs)
            args = ["keys", "recover", "--name", params.name]
            if params.type:
                args.extend(["--type", params.type])
            if params.version != -1:
                args.extend(["--version", str(params.version)])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "revoke":
            params = KeyRevokeParams(**kwargs)
            args = ["keys", "revoke", "--name", params.name, "--reason", params.reason]
            if params.type:
                args.extend(["--type", params.type])
            if params.version != -1:
                args.extend(["--version", str(params.version)])
            if params.message:
                args.extend(["--message", params.message])
            if params.compromise_occurrence_date:
                args.extend(["--compromise-occurrence-date", params.compromise_occurrence_date])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "reactivate":
            params = KeyReactivateParams(**kwargs)
            args = ["keys", "reactivate", "--name", params.name, "--reasontoreactivate", params.reason_to_reactivate]
            if params.type:
                args.extend(["--type", params.type])
            if params.version != -1:
                args.extend(["--version", str(params.version)])
            if params.message_for_reactivate:
                args.extend(["--messageforreactivate", params.message_for_reactivate])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "destroy":
            params = KeyDestroyParams(**kwargs)
            args = ["keys", "destroy", "--name", params.name]
            if params.type:
                args.extend(["--type", params.type])
            if params.version != -1:
                args.extend(["--version", str(params.version)])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "export":
            params = KeyExportParams(**kwargs)
            args = ["keys", "export", "--name", params.name]
            if params.type:
                args.extend(["--type", params.type])
            if params.format:
                args.extend(["--format", params.format])
            if params.encoding:
                args.extend(["--encoding", params.encoding])
            if params.wrap_key_name:
                args.extend(["--wrap-key-name", params.wrap_key_name])
            if params.wrap_public_key:
                args.extend(["--wrap-public-key", params.wrap_public_key])
            if params.cxts:
                args.append("--cxts")
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "clone":
            params = KeyCloneParams(**kwargs)
            args = ["keys", "clone", "--name", params.name, "--new-key-name", params.new_key_name]
            if params.type:
                args.extend(["--type", params.type])
            if params.version != -1:
                args.extend(["--version", str(params.version)])
            if params.include_material:
                args.append("--include-material")
            if params.jsonfile:
                args.extend(["--jsonfile", params.jsonfile])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "generate_kcv":
            params = KeyGenerateKcvParams(**kwargs)
            args = ["keys", "generate-kcv", "--name", params.name]
            if params.type:
                args.extend(["--type", params.type])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "alias_add":
            params = KeyAliasAddParams(**kwargs)
            args = ["keys", "alias", "add", "--name", params.name, "--alias", params.alias, "--alias-type", params.alias_type]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "alias_delete":
            params = KeyAliasDeleteParams(**kwargs)
            args = ["keys", "alias", "delete", "--name", params.name, "--alias-index", str(params.alias_index)]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "alias_modify":
            params = KeyAliasModifyParams(**kwargs)
            args = ["keys", "alias", "modify", "--name", params.name, "--alias-index", str(params.alias_index), "--alias", params.alias, "--alias-type", params.alias_type]
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "query":
            params = KeyQueryParams(**kwargs)
            args = ["keys", "query"]
            if params.query:
                args.extend(["--query", params.query])
            if params.query_jsonfile:
                args.extend(["--query-jsonfile", params.query_jsonfile])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "list_labels":
            params = KeyListLabelsParams(**kwargs)
            args = ["keys", "list-labels"]
            args.extend(["--limit", str(params.limit)])
            args.extend(["--skip", str(params.skip)])
            if params.label:
                args.extend(["--label", params.label])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "validate_import":
            # Validate import parameters without creating the key
            params = KeyCreateParams(**kwargs)
            return params.validate_import_parameters()
        elif action == "generate_test_key_material":
            # Generate test key material by creating and then deleting a key
            algorithm = (kwargs.get("algorithm") or kwargs.get("type", "AES")).upper()
            size = kwargs.get("size")
            curve_id = kwargs.get("curve_id")
            count = kwargs.get("count", 1)
            format_type = kwargs.get("format", "hex")
            domain = kwargs.get("domain")
            
            results = []
            
            for i in range(count):
                # Create a random key name to avoid conflicts
                key_name = f"temp_test_material_{secrets.token_hex(8)}"
                
                # Prepare parameters based on key type
                create_params = {
                    "action": "create",
                    "name": key_name,
                    "algorithm": algorithm,
                    "include_material": True,
                    "domain": domain
                }
                
                if algorithm in ["AES", "TDES", "HMAC-SHA256"] and size:
                    create_params["size"] = size
                elif algorithm == "RSA":
                    create_params["size"] = size or 2048
                elif algorithm == "EC":
                    # EC keys require curve_id but not size
                    # Valid curve IDs include: prime256v1, secp384r1, secp521r1, etc.
                    create_params["curve_id"] = curve_id or "prime256v1"
                    # Remove size for EC keys to avoid conflicts
                    if "size" in create_params:
                        del create_params["size"]
                
                try:
                    # Create a temporary key to get its material
                    result = await self.execute(**create_params)
                    
                    # Extract material and metadata
                    material_info = {
                        "algorithm": algorithm,
                        "size_bits": result.get("size"),
                        "material": result.get("material"),
                        "format": result.get("format", "raw"),
                        "description": f"{algorithm} key material"
                    }
                    
                    # For EC keys, add curve ID
                    if algorithm == "EC" and "curveid" in result:
                        material_info["curve_id"] = result.get("curveid")
                    
                    # For RSA/EC keys, detect format
                    if "BEGIN PRIVATE KEY" in str(result.get("material", "")):
                        material_info["format"] = "pem"
                    elif result.get("format") == "raw" and algorithm in ["AES", "TDES", "HMAC-SHA256"]:
                        # Format is already raw, but for symmetric keys convert to hex if requested
                        material_info["format"] = "hex"
                    
                    # If key material is in bytes, convert to hex
                    if material_info["format"] == "raw":
                        material_info["format"] = "hex"
                    
                    # Add to results
                    results.append(material_info)
                    
                finally:
                    # Always clean up by deleting the temporary key
                    await self.execute(action="delete", name=key_name, domain=domain)
                    
                    # For asymmetric keys (RSA, EC), also delete the corresponding public key
                    # which is automatically created with the naming convention {key_name}-pub
                    if algorithm in ["RSA", "EC"]:
                        try:
                            pub_key_name = f"{key_name}-pub"
                            await self.execute(action="delete", name=pub_key_name, domain=domain)
                        except Exception as e:
                            # Log but continue if public key deletion fails
                            print(f"Warning: Could not delete public key {pub_key_name}: {e}")
            
            return {
                "generated_materials": results,
                "count": len(results),
                "note": "Test key material generated using actual CipherTrust Manager key creation and deletion."
            }
        else:
            raise ValueError(f"Unknown action: {action}")
KEY_TOOLS = [KeyManagementTool]

# Export all key tools
KEY_TOOLS = [KeyManagementTool]
