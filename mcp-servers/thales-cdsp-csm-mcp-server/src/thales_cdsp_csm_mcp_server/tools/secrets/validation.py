"""
Thales CDSP CSM MCP Server - Secret Validation

This module provides validation logic for secret operations.
"""

import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SecretValidator:
    """Validator for secret operations."""
    
    @staticmethod
    def validate_key_value_format(value: str) -> Dict[str, Any]:
        """Validate key-value format for secrets."""
        try:
            parsed_value = json.loads(value)
            
            if not isinstance(parsed_value, dict):
                return {
                    "valid": False,
                    "error": "Value must be a JSON object, not a primitive type or array"
                }
            
            if not parsed_value:
                return {
                    "valid": False,
                    "error": "Key-value object cannot be empty"
                }
            
            for key, val in parsed_value.items():
                if not isinstance(key, str):
                    return {
                        "valid": False,
                        "error": f"All keys must be strings, found key '{key}' of type {type(key).__name__}"
                    }
                
                if not key.strip():
                    return {
                        "valid": False,
                        "error": "Keys cannot be empty or whitespace-only"
                    }
                
                if val is not None and not isinstance(val, str):
                    return {
                        "valid": False,
                        "error": f"All values must be strings or null, found value '{val}' of type {type(val).__name__} for key '{key}'"
                    }
                
                if isinstance(val, (dict, list)):
                    return {
                        "valid": False,
                        "error": f"Nested objects and arrays are not allowed in key-value format. Key '{key}' has value of type {type(val).__name__}"
                    }
            
            return {"valid": True, "error": None}
            
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "error": f"Invalid JSON format: {str(e)}"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }
    
    @staticmethod
    def validate_json_format(value: str) -> Dict[str, Any]:
        """Validate JSON format for secrets."""
        try:
            # Strip whitespace to handle potential leading/trailing spaces
            cleaned_value = value.strip()
            
            # Check if the value is empty after stripping
            if not cleaned_value:
                return {
                    "valid": False,
                    "error": "JSON value cannot be empty or whitespace-only"
                }
            
            # Try to parse the JSON
            parsed_value = json.loads(cleaned_value)
            
            # Additional validation like the old implementation
            if parsed_value is None:
                return {
                    "valid": False,
                    "error": "JSON value cannot be null"
                }
            
            if isinstance(parsed_value, str) and not parsed_value.strip():
                return {
                    "valid": False,
                    "error": "JSON value cannot be an empty string"
                }
            
            if isinstance(parsed_value, dict) and not parsed_value:
                return {
                    "valid": False,
                    "error": "JSON value cannot be an empty object"
                }
            
            if isinstance(parsed_value, list) and not parsed_value:
                return {
                    "valid": False,
                    "error": "JSON value cannot be an empty array"
                }
            
            return {"valid": True, "error": None}
            
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "error": f"Invalid JSON format: {str(e)}"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }
    
    @staticmethod
    def validate_text_format(value: str) -> Dict[str, Any]:
        """Validate text format for secrets."""
        if not isinstance(value, str):
            return {
                "valid": False,
                "error": f"Value must be a string, found type {type(value).__name__}"
            }
        
        if not value.strip():
            return {
                "valid": False,
                "error": "Text value cannot be empty or whitespace-only"
            }
        
        return {"valid": True, "error": None} 