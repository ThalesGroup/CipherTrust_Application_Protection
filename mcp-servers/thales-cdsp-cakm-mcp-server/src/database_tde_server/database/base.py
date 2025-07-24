"""
Base database interface for TDE operations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple

from ..models import DatabaseConnection, EncryptionStatusInfo

class DatabaseInterface(ABC):
    """Abstract base class for database TDE operations"""
    
    def __init__(self, connection: DatabaseConnection):
        self.connection = connection
    
    @abstractmethod
    async def connect(self) -> bool:
        """Test database connectivity"""
        pass
    
    @abstractmethod
    async def execute_sql(self, sql: str, database: Optional[str] = None) -> Dict[str, Any]:
        """Execute SQL command"""
        pass
    
    @abstractmethod
    async def check_encryption_status(self, database_name: Optional[str] = None) -> List[EncryptionStatusInfo]:
        """Check encryption status of databases"""
        pass
    
    @abstractmethod
    async def list_cryptographic_providers(self) -> List[Dict[str, Any]]:
        """List cryptographic providers"""
        pass
    
    @abstractmethod
    async def list_master_keys(self, key_type: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """List master keys"""
        pass
    
    @abstractmethod
    async def create_tde_infrastructure(
        self, 
        key_name: str,
        provider_name: str, 
        ciphertrust_username: str,
        ciphertrust_password: str,
        ciphertrust_domain: str,
        key_size: int,
        key_type: str
    ) -> Dict[str, Any]:
        """Create TDE infrastructure (keys, credentials, logins)"""
        pass
    
    @abstractmethod
    async def encrypt_database(
        self,
        database_name: str,
        key_name: str,
        is_asymmetric: bool
    ) -> Dict[str, Any]:
        """Encrypt a database with TDE"""
        pass
    
    @abstractmethod
    async def rotate_database_encryption_key(
        self,
        database_name: str,
        algorithm: Optional[str] = None
    ) -> Dict[str, Any]:
        """Rotate database encryption key"""
        pass
    
    @abstractmethod
    async def rotate_master_key(
        self,
        database_name: str,
        new_key_name: str,
        provider_name: str,
        ciphertrust_username: str,
        ciphertrust_password: str,
        ciphertrust_domain: str,
        key_size: int,
        key_type: str
    ) -> Dict[str, Any]:
        """Rotate master key"""
        pass
    
    def parse_key_algorithm(self, key_type: str, key_size: int) -> Tuple[str, bool]:
        """Parse key type and size into database-specific algorithm format"""
        is_asymmetric = key_type.upper() == "RSA"
    
        if is_asymmetric:
            # SQL Server supports these RSA key sizes
            valid_rsa_sizes = [512, 1024, 2048, 3072, 4096]
            if key_size in valid_rsa_sizes:
                return f"RSA_{key_size}", True
            else:
                raise ValueError(f"Invalid RSA key size: {key_size}. Valid sizes are: {valid_rsa_sizes}")
        else:  # AES symmetric
            # SQL Server supports these AES key sizes
            valid_aes_sizes = [128, 192, 256]
            if key_size in valid_aes_sizes:
                return f"AES_{key_size}", False
            else:
                raise ValueError(f"Invalid AES key size: {key_size}. Valid sizes are: {valid_aes_sizes}")