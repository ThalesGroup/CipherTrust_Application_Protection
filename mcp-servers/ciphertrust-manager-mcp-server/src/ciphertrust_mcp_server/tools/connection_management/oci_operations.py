"""OCI connection operations for Connection Management."""

import os
import json
import tempfile
import re
from typing import Any, Dict, List, Optional
from .base import ConnectionOperations
from .constants import OCI_PARAMETERS, CONNECTION_OPERATIONS


class OCIOperations(ConnectionOperations):
    """OCI connection operations for Connection Management."""
    
    def _preserve_fingerprint_format(self, fingerprint: str) -> str:
        """Preserve the original fingerprint format (don't normalize)."""
        if not fingerprint:
            return fingerprint
        # Return the fingerprint as-is, preserving the original format
        return fingerprint
    
    def _validate_pem_content(self, content: str) -> str:
        """Validate PEM content format."""
        content = content.strip()
        
        # More flexible PEM validation - check for common PEM patterns
        pem_patterns = [
            '-----BEGIN PRIVATE KEY-----',
            '-----BEGIN RSA PRIVATE KEY-----',
            '-----BEGIN DSA PRIVATE KEY-----',
            '-----BEGIN EC PRIVATE KEY-----',
            '-----BEGIN OPENSSH PRIVATE KEY-----'
        ]
        
        end_patterns = [
            '-----END PRIVATE KEY-----',
            '-----END RSA PRIVATE KEY-----',
            '-----END DSA PRIVATE KEY-----',
            '-----END EC PRIVATE KEY-----',
            '-----END OPENSSH PRIVATE KEY-----'
        ]
        
        # Check if content starts with any valid PEM header
        starts_with_pem = any(content.startswith(pattern) for pattern in pem_patterns)
        
        if not starts_with_pem:
            # Provide more detailed error information
            first_line = content.split('\n')[0] if content else "empty content"
            raise ValueError(f"Invalid PEM format: content must start with a valid PEM header. First line: '{first_line[:50]}...' (truncated)")
        
        # Check if content contains any valid PEM footer (more flexible than exact end match)
        contains_pem_footer = any(pattern in content for pattern in end_patterns)
        
        if not contains_pem_footer:
            # Provide more detailed error information
            last_line = content.split('\n')[-1] if content else "empty content"
            raise ValueError(f"Invalid PEM format: content must contain a valid PEM footer. Last line: '{last_line[:50]}...' (truncated)")
        
        # Extract the PEM content up to the footer (handle extra content after footer)
        lines = content.split('\n')
        pem_lines = []
        found_end = False
        
        for line in lines:
            # Check if this line contains a PEM footer
            if any(pattern in line.strip() for pattern in end_patterns):
                pem_lines.append(line)
                found_end = True
                break
            pem_lines.append(line)
        
        if not found_end:
            raise ValueError("Invalid PEM format: could not find PEM footer")
        
        # Return the clean PEM content
        return '\n'.join(pem_lines)
    
    def _read_pem_file_content(self, pem_file_path: str) -> str:
        """Read and validate PEM file content."""
        try:
            # Check if file exists first
            if not os.path.exists(pem_file_path):
                raise FileNotFoundError(f"PEM file not found: {pem_file_path}")
            
            # Check file size
            file_size = os.path.getsize(pem_file_path)
            if file_size == 0:
                raise ValueError(f"PEM file is empty: {pem_file_path}")
            
            with open(pem_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if content is empty after reading
            if not content.strip():
                raise ValueError(f"PEM file contains no readable content: {pem_file_path}")
            
            # Log the first few characters for debugging (without exposing sensitive data)
            first_chars = content[:100].replace('\n', '\\n')
            print(f"Debug: First 100 chars of PEM file: {first_chars}")
            
            return self._validate_pem_content(content)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"PEM file not found: {pem_file_path}")
        except UnicodeDecodeError as e:
            raise ValueError(f"PEM file encoding error: {pem_file_path}. Try saving the file as UTF-8. Error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error reading PEM file {pem_file_path}: {str(e)}")
    
    def _create_conn_creds_file_from_pem_content(self, pem_content: str, pass_phrase: Optional[str] = None) -> str:
        """Create a temporary conn_creds JSON file from PEM content."""
        try:
            # Validate the PEM content
            pem_content = self._validate_pem_content(pem_content)
            
            # Create the conn_creds JSON structure
            conn_creds = {
                "key_file": pem_content
            }
            
            if pass_phrase:
                conn_creds["pass_phrase"] = pass_phrase
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            try:
                json.dump(conn_creds, temp_file, indent=2)
                temp_file.close()
                return temp_file.name
            except Exception as e:
                # Clean up on error
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
                raise e
                
        except Exception as e:
            raise ValueError(f"Failed to create conn_creds file from PEM content: {str(e)}")
    
    def _create_conn_creds_file_from_pem(self, pem_file_path: str, pass_phrase: Optional[str] = None) -> str:
        """Create a temporary conn_creds JSON file from PEM file for OCI connection."""
        try:
            # Read the PEM file content
            pem_content = self._read_pem_file_content(pem_file_path)
            
            # Create conn_creds file from content
            return self._create_conn_creds_file_from_pem_content(pem_content, pass_phrase)
                
        except Exception as e:
            raise ValueError(f"Failed to create conn_creds file from PEM file: {str(e)}")
    
    def _is_file_path(self, key_file_input: str) -> bool:
        """Check if the input is a file path or PEM content."""
        # Remove leading/trailing whitespace
        key_file_input = key_file_input.strip()
        
        # Check if it looks like PEM content first (more specific check)
        if key_file_input.startswith('-----BEGIN'):
            return False
        
        # Check if it looks like a file path
        # Windows paths
        if ':' in key_file_input and ('\\' in key_file_input or '/' in key_file_input):
            return True
        
        # Unix/Linux paths
        if key_file_input.startswith('/') or key_file_input.startswith('./') or key_file_input.startswith('../'):
            return True
        
        # Check for file extensions that suggest it's a file path
        if any(key_file_input.lower().endswith(ext) for ext in ['.pem', '.key', '.crt', '.cert', '.p12', '.pfx']):
            return True
        
        # If it contains path separators, treat as file path
        if os.path.sep in key_file_input or '/' in key_file_input:
            return True
        
        # If it's short and doesn't look like PEM content, might be a relative path
        if len(key_file_input) < 100 and not key_file_input.startswith('-----'):
            return True
        
        # Default to treating as PEM content if unclear
        return False
    
    def _cleanup_temp_file(self, file_path: str):
        """Clean up temporary file if it exists."""
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
        except Exception:
            pass  # Ignore cleanup errors
    
    def get_operations(self) -> List[str]:
        """Return list of supported OCI operations."""
        return CONNECTION_OPERATIONS["oci"]
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Return schema properties for OCI operations."""
        return {
            "oci_params": {
                "type": "object",
                "properties": OCI_PARAMETERS,
                "description": "OCI-specific parameters"
            }
        }
    
    def get_action_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return action-specific parameter requirements for OCI."""
        return {
            "create": {
                "required": ["oci_params"],
                "optional": ["domain", "auth_domain"],
                "note": "All OCI parameters must be provided within the 'oci_params' object. Required within oci_params: 'name'. Optional: 'tenancy_ocid', 'user_ocid', 'fingerprint', 'oci_region', 'key_file', 'products', etc. See tool documentation for full list."
            },
            "list": {
                "required": [],
                "optional": ["name", "cloudname", "category", "products", "limit", "skip", "fields", "labels_query", "lastconnectionafter", "lastconnectionbefore", "lastconnectionok", "domain", "auth_domain"]
            },
            "get": {
                "required": ["id"],
                "optional": ["domain", "auth_domain"]
            },
            "delete": {
                "required": ["id"],
                "optional": ["force", "domain", "auth_domain"]
            },
            "modify": {
                "required": ["oci_params"],
                "optional": ["domain", "auth_domain"],
                "note": "All OCI parameters must be provided within the 'oci_params' object. Required within oci_params: 'id'. Optional: 'name', 'tenancy_ocid', etc."
            },
            "test": {
                "required": ["oci_params"],
                "optional": ["domain", "auth_domain"],
                "note": "The 'id' of the connection to test must be provided within the 'oci_params' object."
            }
        }
    
    async def execute_operation(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute OCI connection operation."""
        oci_params = params.get("oci_params", {})
        temp_creds_file = None
        
        try:
            # Build base command
            cmd = ["connectionmgmt", "oci", action]
            
            # Add action-specific parameters
            if action == "create":
                if oci_params.get("name"):
                    cmd.extend(["--name", oci_params["name"]])
                if oci_params.get("tenancy_ocid"):
                    cmd.extend(["--tenancy-ocid", oci_params["tenancy_ocid"]])
                if oci_params.get("user_ocid"):
                    cmd.extend(["--user-ocid", oci_params["user_ocid"]])
                if oci_params.get("fingerprint"):
                    # Preserve original fingerprint format (don't normalize)
                    fingerprint = self._preserve_fingerprint_format(oci_params["fingerprint"])
                    cmd.extend(["--fingerprint", fingerprint])
                if oci_params.get("oci_region"):
                    cmd.extend(["--oci-region", oci_params["oci_region"]])
                
                # Handle conn_creds - always use conn_creds as top-level parameter
                if oci_params.get("conn_creds"):
                    # If conn_creds is provided directly, use it
                    cmd.extend(["--conn-creds", oci_params["conn_creds"]])
                elif oci_params.get("key_file"):
                    # If key_file is provided, determine if it's a file path or content
                    key_file_input = oci_params["key_file"]
                    
                    if self._is_file_path(key_file_input):
                        # Treat as file path
                        temp_creds_file = self._create_conn_creds_file_from_pem(
                            key_file_input, 
                            oci_params.get("pass_phrase")
                        )
                    else:
                        # Treat as pasted PEM content
                        temp_creds_file = self._create_conn_creds_file_from_pem_content(
                            key_file_input, 
                            oci_params.get("pass_phrase")
                        )
                    
                    cmd.extend(["--conn-creds", temp_creds_file])
                
                if oci_params.get("products"):
                    cmd.extend(["--products", oci_params["products"]])
                if oci_params.get("description"):
                    cmd.extend(["--description", oci_params["description"]])
                if oci_params.get("meta"):
                    cmd.extend(["--meta", oci_params["meta"]])
                if oci_params.get("labels"):
                    cmd.extend(["--labels", oci_params["labels"]])
                if oci_params.get("json_file"):
                    cmd.extend(["--json-file", oci_params["json_file"]])
                
            elif action == "list":
                if oci_params.get("name"):
                    cmd.extend(["--name", oci_params["name"]])
                if oci_params.get("cloudname"):
                    cmd.extend(["--cloudname", oci_params["cloudname"]])
                if oci_params.get("category"):
                    cmd.extend(["--category", oci_params["category"]])
                if oci_params.get("products"):
                    cmd.extend(["--products", oci_params["products"]])
                if oci_params.get("limit"):
                    cmd.extend(["--limit", str(oci_params["limit"])])
                if oci_params.get("skip"):
                    cmd.extend(["--skip", str(oci_params["skip"])])
                if oci_params.get("fields"):
                    cmd.extend(["--fields", oci_params["fields"]])
                if oci_params.get("labels_query"):
                    cmd.extend(["--labels-query", oci_params["labels_query"]])
                if oci_params.get("lastconnectionafter"):
                    cmd.extend(["--lastconnectionafter", oci_params["lastconnectionafter"]])
                if oci_params.get("lastconnectionbefore"):
                    cmd.extend(["--lastconnectionbefore", oci_params["lastconnectionbefore"]])
                if oci_params.get("lastconnectionok"):
                    cmd.extend(["--lastconnectionok", oci_params["lastconnectionok"]])
                    
            elif action == "get":
                cmd.extend(["--id", oci_params["id"]])
                
            elif action == "delete":
                cmd.extend(["--id", oci_params["id"]])
                if oci_params.get("force"):
                    cmd.append("--force")
                    
            elif action == "modify":
                cmd.extend(["--id", oci_params["id"]])
                if oci_params.get("name"):
                    cmd.extend(["--name", oci_params["name"]])
                if oci_params.get("tenancy_ocid"):
                    cmd.extend(["--tenancy-ocid", oci_params["tenancy_ocid"]])
                if oci_params.get("user_ocid"):
                    cmd.extend(["--user-ocid", oci_params["user_ocid"]])
                if oci_params.get("fingerprint"):
                    # Preserve original fingerprint format for modify as well
                    fingerprint = self._preserve_fingerprint_format(oci_params["fingerprint"])
                    cmd.extend(["--fingerprint", fingerprint])
                if oci_params.get("oci_region"):
                    cmd.extend(["--oci-region", oci_params["oci_region"]])
                
                # Handle conn_creds for modify - always use conn_creds as top-level parameter
                if oci_params.get("conn_creds"):
                    # If conn_creds is provided directly, use it
                    cmd.extend(["--conn-creds", oci_params["conn_creds"]])
                elif oci_params.get("key_file"):
                    # If key_file is provided, determine if it's a file path or content
                    key_file_input = oci_params["key_file"]
                    
                    if self._is_file_path(key_file_input):
                        # Treat as file path
                        temp_creds_file = self._create_conn_creds_file_from_pem(
                            key_file_input, 
                            oci_params.get("pass_phrase")
                        )
                    else:
                        # Treat as pasted PEM content
                        temp_creds_file = self._create_conn_creds_file_from_pem_content(
                            key_file_input, 
                            oci_params.get("pass_phrase")
                        )
                    
                    cmd.extend(["--conn-creds", temp_creds_file])
                
                if oci_params.get("products"):
                    cmd.extend(["--products", oci_params["products"]])
                if oci_params.get("description"):
                    cmd.extend(["--description", oci_params["description"]])
                if oci_params.get("meta"):
                    cmd.extend(["--meta", oci_params["meta"]])
                if oci_params.get("labels"):
                    cmd.extend(["--labels", oci_params["labels"]])
                if oci_params.get("json_file"):
                    cmd.extend(["--json-file", oci_params["json_file"]])
                    
            elif action == "test":
                cmd.extend(["--id", oci_params["id"]])
                
            else:
                raise ValueError(f"Unsupported OCI action: {action}")
            
            # Execute command
            result = self.execute_command(cmd, params.get("domain"), params.get("auth_domain"))
            return result.get("data", result.get("stdout", ""))
            
        finally:
            # Clean up temporary credentials file
            if temp_creds_file:
                self._cleanup_temp_file(temp_creds_file) 