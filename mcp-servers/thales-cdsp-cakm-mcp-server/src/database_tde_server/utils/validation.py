"""
Validation helpers for Database TDE operations
"""

import re
from typing import List, Tuple, Optional

from .exceptions import ValidationError

# SQL Server identifier naming rules
SQL_IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_$]*$')
DATABASE_NAME_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_-]*$')

def validate_database_name(database_name: str) -> bool:
    """
    Validate database name according to SQL Server rules
    
    Args:
        database_name: Database name to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If database name is invalid
    """
    if not database_name:
        raise ValidationError("Database name cannot be empty")
    
    if len(database_name) > 128:
        raise ValidationError("Database name cannot exceed 128 characters")
    
    if not DATABASE_NAME_PATTERN.match(database_name):
        raise ValidationError(
            "Database name must start with a letter and contain only letters, numbers, underscores, and hyphens"
        )
    
    # Check for reserved words
    reserved_words = {'master', 'tempdb', 'model', 'msdb', 'sys', 'information_schema'}
    if database_name.lower() in reserved_words:
        raise ValidationError(f"'{database_name}' is a reserved database name")
    
    return True

def validate_key_name(key_name: str) -> bool:
    """
    Validate encryption key name
    
    Args:
        key_name: Key name to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If key name is invalid
    """
    if not key_name:
        raise ValidationError("Key name cannot be empty")
    
    if len(key_name) > 128:
        raise ValidationError("Key name cannot exceed 128 characters")
    
    if not SQL_IDENTIFIER_PATTERN.match(key_name):
        raise ValidationError(
            "Key name must start with a letter or underscore and contain only letters, numbers, underscores, and dollar signs"
        )
    
    return True

def validate_connection_name(connection_name: str) -> bool:
    """
    Validate database connection name
    
    Args:
        connection_name: Connection name to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If connection name is invalid
    """
    if not connection_name:
        raise ValidationError("Connection name cannot be empty")
    
    if len(connection_name) > 64:
        raise ValidationError("Connection name cannot exceed 64 characters")
    
    # Allow alphanumeric, underscore, and hyphen
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', connection_name):
        raise ValidationError(
            "Connection name must start with a letter and contain only letters, numbers, underscores, and hyphens"
        )
    
    return True

def validate_key_parameters(key_type: str, key_size: int) -> Tuple[str, bool]:
    """
    Validate and normalize key parameters
    
    Args:
        key_type: Key type (RSA or AES)
        key_size: Key size in bits
        
    Returns:
        Tuple of (normalized_key_type, is_asymmetric)
        
    Raises:
        ValidationError: If parameters are invalid
    """
    key_type = key_type.upper()
    
    if key_type not in ['RSA', 'AES']:
        raise ValidationError("Key type must be 'RSA' or 'AES'")
    
    if key_type == 'RSA':
        if key_size not in [2048, 4096]:
            raise ValidationError("RSA key size must be 2048 or 4096 bits")
        return key_type, True
    else:  # AES
        if key_size not in [192, 256]:
            raise ValidationError("AES key size must be 192 or 256 bits")
        return key_type, False

def parse_database_list(input_text: str, available_databases: Optional[List[str]] = None) -> List[str]:
    """
    Parse database names from user input text
    
    Args:
        input_text: User input containing database names
        available_databases: List of available databases for "all" expansion
        
    Returns:
        List of database names
        
    Raises:
        ValidationError: If parsing fails or databases are invalid
    """
    input_text = input_text.strip()
    
    # Handle "all databases" case
    if "all databases" in input_text.lower() or "all database" in input_text.lower():
        if not available_databases:
            raise ValidationError("Cannot expand 'all databases' - no available databases provided")
        return available_databases
    
    # Parse comma-separated list
    # Handle patterns like "db1, db2, db3" or "database1 and database2"
    # Replace "and" with commas for easier parsing
    normalized_text = re.sub(r'\s+and\s+', ', ', input_text, flags=re.IGNORECASE)
    
    # Split by comma and clean up
    database_names = []
    for name in normalized_text.split(','):
        name = name.strip()
        if name:
            # Validate each database name
            validate_database_name(name)
            database_names.append(name)
    
    if not database_names:
        raise ValidationError("No valid database names found in input")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_names = []
    for name in database_names:
        if name not in seen:
            seen.add(name)
            unique_names.append(name)
    
    return unique_names

def validate_ciphertrust_domain(domain: str) -> str:
    """
    Validate and normalize CipherTrust domain name
    
    Args:
        domain: Domain name to validate
        
    Returns:
        Normalized domain name
        
    Raises:
        ValidationError: If domain is invalid
    """
    if not domain:
        return "root"  # Default domain
    
    domain = domain.strip()
    
    if len(domain) > 64:
        raise ValidationError("Domain name cannot exceed 64 characters")
    
    # Allow alphanumeric, underscore, hyphen, and period
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9._-]*$', domain):
        raise ValidationError(
            "Domain name must start with a letter and contain only letters, numbers, periods, underscores, and hyphens"
        )
    
    return domain

def validate_provider_name(provider_name: str) -> bool:
    """
    Validate cryptographic provider name
    
    Args:
        provider_name: Provider name to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If provider name is invalid
    """
    if not provider_name:
        raise ValidationError("Provider name cannot be empty")
    
    if len(provider_name) > 128:
        raise ValidationError("Provider name cannot exceed 128 characters")
    
    if not SQL_IDENTIFIER_PATTERN.match(provider_name):
        raise ValidationError(
            "Provider name must start with a letter or underscore and contain only letters, numbers, underscores, and dollar signs"
        )
    
    return True

