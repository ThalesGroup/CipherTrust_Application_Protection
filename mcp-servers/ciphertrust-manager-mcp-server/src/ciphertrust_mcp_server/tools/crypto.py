"""Cryptographic operations tools for CipherTrust Manager with built-in domain support."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


# Encryption Parameter Models
class CryptoEncryptParams(BaseModel):
    """Parameters for encrypting data."""
    key_name: str = Field(..., description="The name, ID or URI of the key")
    plaintext: Optional[str] = Field(None, description="Text string to encrypt")
    plaintext_file: Optional[str] = Field(None, description="File containing plaintext to encrypt")
    key_version: Optional[int] = Field(None, description="Key version number (defaults to 0)")
    mode: Optional[str] = Field(None, description="Crypto mode (ecb, cbc, gcm, ctr for AES)")
    pad: Optional[str] = Field(None, description="Padding mode (none, pkcs7 for symmetric; pkcs1, oaep for RSA)")
    iv: Optional[str] = Field(None, description="Initialization Vector in hex (generated if not provided)")
    aad: Optional[str] = Field(None, description="Additional Authentication Data for AEAD")
    aad_file: Optional[str] = Field(None, description="File containing AAD")
    tag_length: int = Field(12, description="AES-GCM tag length in bytes")
    nae_key_version_header: bool = Field(False, description="Prepend 3-byte NAE key-version header")
    ciphertext_file: Optional[str] = Field(None, description="Output file for ciphertext JSON blob")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to operate in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class CryptoDecryptParams(BaseModel):
    """Parameters for decrypting data."""
    ciphertext_blob: Optional[str] = Field(None, description="JSON encoded ciphertext blob from encrypt")
    ciphertext_file: Optional[str] = Field(None, description="File containing ciphertext JSON blob")
    plaintext_file: Optional[str] = Field(None, description="Output file for decrypted plaintext")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to operate in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class CryptoReencryptParams(BaseModel):
    """Parameters for re-encrypting data."""
    key_name: str = Field(..., description="The name, ID or URI of the new key")
    ciphertext_blob: Optional[str] = Field(None, description="JSON encoded ciphertext blob")
    ciphertext_file: Optional[str] = Field(None, description="File containing ciphertext JSON blob")
    key_version: Optional[int] = Field(None, description="Key version number for new encryption")
    mode: Optional[str] = Field(None, description="Crypto mode for new encryption")
    pad: Optional[str] = Field(None, description="Padding mode for new encryption")
    iv: Optional[str] = Field(None, description="IV for new encryption")
    aad: Optional[str] = Field(None, description="AAD for new encryption")
    aad_file: Optional[str] = Field(None, description="File containing AAD for new encryption")
    tag_length: int = Field(12, description="AES-GCM tag length for new encryption")
    nae_key_version_header: bool = Field(False, description="Prepend NAE header to new ciphertext")
    reencrypt_ciphertext_file: Optional[str] = Field(None, description="Output file for re-encrypted ciphertext")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to operate in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


# Signing Parameter Models
class CryptoSignParams(BaseModel):
    """Parameters for signing data."""
    key_name: str = Field(..., description="The name, ID or URI of the signing key")
    body: str = Field(..., description="The data to sign")
    hash_algo: str = Field(..., description="Hash algorithm (SHA1, SHA-256, SHA-384, SHA-512, none)")
    key_version: Optional[int] = Field(None, description="Key version number (defaults to 0)")
    sign_algo: str = Field("RSA", description="Signing algorithm (RSA or ECDSA)")
    sign_pad: str = Field("PKCS1", description="RSA padding (PKCS1 or PSS)")
    salt_length: Optional[int] = Field(None, description="Salt length for PSS padding")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to operate in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class CryptoVerifyParams(BaseModel):
    """Parameters for verifying signatures."""
    key_name: str = Field(..., description="The name, ID or URI of the verification key")
    body: str = Field(..., description="The data that was signed")
    signature: str = Field(..., description="Hex encoded signature to verify")
    hash_algo: str = Field(..., description="Hash algorithm used for signing")
    key_version: Optional[int] = Field(None, description="Key version number (defaults to 0)")
    sign_algo: str = Field("RSA", description="Signing algorithm (RSA or ECDSA)")
    sign_pad: str = Field("PKCS1", description="RSA padding (PKCS1 or PSS)")
    salt_length: Optional[int] = Field(None, description="Salt length for PSS padding")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to operate in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


# Format Preserving Encryption Parameter Models
class CryptoHideParams(BaseModel):
    """Parameters for format preserving encryption (hide)."""
    key_name: str = Field(..., description="The name, ID or URI of the FPE key")
    hint: str = Field(..., description="FPE hint (required for hide/unhide operations)")
    plaintext: Optional[str] = Field(None, description="Text string to encrypt")
    plaintext_file: Optional[str] = Field(None, description="File containing plaintext")
    key_version: Optional[int] = Field(None, description="Key version number (defaults to 0)")
    iv: Optional[str] = Field(None, description="Initialization Vector in hex")
    charset: Optional[str] = Field(None, description="Charset for unicode operations")
    tweak: Optional[str] = Field(None, description="Tweak for FPE operation")
    tweakalg: Optional[str] = Field(None, description="Tweak algorithm (SHA1, SHA256, SHA512)")
    ciphertext_file: Optional[str] = Field(None, description="Output file for ciphertext")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to operate in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class CryptoUnhideParams(BaseModel):
    """Parameters for format preserving decryption (unhide)."""
    key_name: str = Field(..., description="The name, ID or URI of the FPE key")
    hint: str = Field(..., description="FPE hint (required for hide/unhide operations)")
    plaintext: Optional[str] = Field(None, description="Ciphertext to decrypt")
    plaintext_file: Optional[str] = Field(None, description="File containing ciphertext")
    key_version: Optional[int] = Field(None, description="Key version number (defaults to 0)")
    iv: Optional[str] = Field(None, description="Initialization Vector in hex")
    charset: Optional[str] = Field(None, description="Charset for unicode operations")
    tweak: Optional[str] = Field(None, description="Tweak for FPE operation")
    tweakalg: Optional[str] = Field(None, description="Tweak algorithm (SHA1, SHA256, SHA512)")
    ciphertext_file: Optional[str] = Field(None, description="Output file for plaintext")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to operate in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


# Cryptographic Operation Tools
class CryptoOperationsTool(BaseTool):
    name = "crypto_operations"
    description = "Cryptographic operations (encrypt, decrypt, reencrypt, sign, verify, hide, unhide)"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["encrypt", "decrypt", "reencrypt", "sign", "verify", "hide", "unhide"]},
                **CryptoEncryptParams.model_json_schema()["properties"],
                **CryptoDecryptParams.model_json_schema()["properties"],
                **CryptoReencryptParams.model_json_schema()["properties"],
                **CryptoSignParams.model_json_schema()["properties"],
                **CryptoVerifyParams.model_json_schema()["properties"],
                **CryptoHideParams.model_json_schema()["properties"],
                **CryptoUnhideParams.model_json_schema()["properties"],
            },
            "required": ["action"],
        }

    async def execute(self, **kwargs: Any) -> Any:
        action = kwargs.get("action")
        
        if action == "encrypt":
            params = CryptoEncryptParams(**kwargs)
            if not params.plaintext and not params.plaintext_file:
                raise ValueError("Either plaintext or plaintext_file must be specified")
            args = ["crypto", "encrypt", "--key-name", params.key_name]
            if params.plaintext:
                args.extend(["--plaintext", params.plaintext])
            if params.plaintext_file:
                args.extend(["--plaintext-file", params.plaintext_file])
            if params.key_version is not None:
                args.extend(["--key-version", str(params.key_version)])
            if params.mode:
                args.extend(["--mode", params.mode])
            if params.pad:
                args.extend(["--pad", params.pad])
            if params.iv:
                args.extend(["--iv", params.iv])
            if params.aad:
                args.extend(["--aad", params.aad])
            if params.aad_file:
                args.extend(["--aad-file", params.aad_file])
            if params.tag_length != 12:
                args.extend(["--tag-length", str(params.tag_length)])
            if params.nae_key_version_header:
                args.append("--nae-key-version-header")
            if params.ciphertext_file:
                args.extend(["--ciphertext-file", params.ciphertext_file])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
            
        elif action == "decrypt":
            params = CryptoDecryptParams(**kwargs)
            if not params.ciphertext_blob and not params.ciphertext_file:
                raise ValueError("Either ciphertext_blob or ciphertext_file must be specified")
            args = ["crypto", "decrypt"]
            if params.ciphertext_blob:
                args.extend(["--ciphertext-blob", params.ciphertext_blob])
            if params.ciphertext_file:
                args.extend(["--ciphertext-file", params.ciphertext_file])
            if params.plaintext_file:
                args.extend(["--plaintext-file", params.plaintext_file])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
            
        elif action == "reencrypt":
            params = CryptoReencryptParams(**kwargs)
            if not params.ciphertext_blob and not params.ciphertext_file:
                raise ValueError("Either ciphertext_blob or ciphertext_file must be specified")
            args = ["crypto", "reencrypt", "--key-name", params.key_name]
            if params.ciphertext_blob:
                args.extend(["--ciphertext-blob", params.ciphertext_blob])
            if params.ciphertext_file:
                args.extend(["--ciphertext-file", params.ciphertext_file])
            if params.key_version is not None:
                args.extend(["--key-version", str(params.key_version)])
            if params.mode:
                args.extend(["--mode", params.mode])
            if params.pad:
                args.extend(["--pad", params.pad])
            if params.iv:
                args.extend(["--iv", params.iv])
            if params.aad:
                args.extend(["--aad", params.aad])
            if params.aad_file:
                args.extend(["--aad-file", params.aad_file])
            if params.tag_length != 12:
                args.extend(["--tag-length", str(params.tag_length)])
            if params.nae_key_version_header:
                args.append("--nae-key-version-header")
            if params.reencrypt_ciphertext_file:
                args.extend(["--reencryptciphertext-file", params.reencrypt_ciphertext_file])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
            
        elif action == "sign":
            params = CryptoSignParams(**kwargs)
            args = ["crypto", "sign", "--key-name", params.key_name, "--body", params.body, "--hash-algo", params.hash_algo]
            if params.key_version is not None:
                args.extend(["--key-version", str(params.key_version)])
            if params.sign_algo != "RSA":
                args.extend(["--sign-algo", params.sign_algo])
            if params.sign_pad != "PKCS1":
                args.extend(["--sign-pad", params.sign_pad])
            if params.salt_length is not None:
                args.extend(["--salt-length", str(params.salt_length)])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
            
        elif action == "verify":
            params = CryptoVerifyParams(**kwargs)
            args = ["crypto", "verify", "--key-name", params.key_name, "--body", params.body, "--signature", params.signature, "--hash-algo", params.hash_algo]
            if params.key_version is not None:
                args.extend(["--key-version", str(params.key_version)])
            if params.sign_algo != "RSA":
                args.extend(["--sign-algo", params.sign_algo])
            if params.sign_pad != "PKCS1":
                args.extend(["--sign-pad", params.sign_pad])
            if params.salt_length is not None:
                args.extend(["--salt-length", str(params.salt_length)])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
            
        elif action == "hide":
            params = CryptoHideParams(**kwargs)
            if not params.plaintext and not params.plaintext_file:
                raise ValueError("Either plaintext or plaintext_file must be specified")
            args = ["crypto", "hide", "--key-name", params.key_name, "--hint", params.hint]
            if params.plaintext:
                args.extend(["--plaintext", params.plaintext])
            if params.plaintext_file:
                args.extend(["--plaintext-file", params.plaintext_file])
            if params.key_version is not None:
                args.extend(["--key-version", str(params.key_version)])
            if params.iv:
                args.extend(["--iv", params.iv])
            if params.charset:
                args.extend(["--charset", params.charset])
            if params.tweak:
                args.extend(["--tweak", params.tweak])
            if params.tweakalg:
                args.extend(["--tweakalg", params.tweakalg])
            if params.ciphertext_file:
                args.extend(["--ciphertext-file", params.ciphertext_file])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
            
        elif action == "unhide":
            params = CryptoUnhideParams(**kwargs)
            if not params.plaintext and not params.plaintext_file:
                raise ValueError("Either plaintext (ciphertext) or plaintext_file must be specified")
            args = ["crypto", "unhide", "--key-name", params.key_name, "--hint", params.hint]
            if params.plaintext:
                args.extend(["--plaintext", params.plaintext])
            if params.plaintext_file:
                args.extend(["--plaintext-file", params.plaintext_file])
            if params.key_version is not None:
                args.extend(["--key-version", str(params.key_version)])
            if params.iv:
                args.extend(["--iv", params.iv])
            if params.charset:
                args.extend(["--charset", params.charset])
            if params.tweak:
                args.extend(["--tweak", params.tweak])
            if params.tweakalg:
                args.extend(["--tweakalg", params.tweakalg])
            if params.ciphertext_file:
                args.extend(["--ciphertext-file", params.ciphertext_file])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
            
        else:
            raise ValueError(f"Unknown action: {action}")

CRYPTO_TOOLS = [CryptoOperationsTool]
