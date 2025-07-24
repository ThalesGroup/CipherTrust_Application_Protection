"""Manager for ksctl CLI tool."""

import json
import logging
import os
import platform
import stat
import subprocess
import zipfile
from pathlib import Path
from typing import Any, Optional

import httpx

from .config import settings
from .utils.helpers import sanitize_command_args

logger = logging.getLogger(__name__)


class KsctlError(Exception):
    """Base exception for ksctl errors."""
    pass


class KsctlManager:
    """Manages ksctl CLI tool installation and execution."""

    def __init__(self):
        self.ksctl_path = settings.ksctl_path
        self._ensure_ksctl()

    def _ensure_ksctl(self) -> None:
        """Ensure ksctl is downloaded and available."""
        if not self.ksctl_path.exists():
            logger.info("ksctl not found, downloading...")
            self._download_ksctl()
        else:
            logger.info(f"ksctl found at {self.ksctl_path}")

    def _download_ksctl(self) -> None:
        """Download ksctl from CipherTrust Manager."""
        try:
            # Create directory if it doesn't exist
            self.ksctl_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download ksctl_images.zip
            download_url = settings.ksctl_download_url_full
            logger.info(f"Downloading ksctl from {download_url}")
            
            with httpx.Client(verify=not settings.ciphertrust_nosslverify) as client:
                response = client.get(download_url, timeout=60.0)
                response.raise_for_status()
            
            # Save zip file
            zip_path = self.ksctl_path.parent / "ksctl_images.zip"
            zip_path.write_bytes(response.content)
            
            # Extract the appropriate binary
            system = platform.system().lower()
            arch = platform.machine().lower()
            
            if system == "linux":
                if arch in ["x86_64", "amd64"]:
                    binary_name = "ksctl-linux-amd64"
                elif arch == "aarch64":
                    binary_name = "ksctl-linux-arm64"
                else:
                    raise KsctlError(f"Unsupported architecture: {arch}")
            elif system == "darwin":
                if arch in ["x86_64", "amd64"]:
                    binary_name = "ksctl-darwin-amd64"
                elif arch == "arm64":
                    binary_name = "ksctl-darwin-arm64"
                else:
                    raise KsctlError(f"Unsupported architecture: {arch}")
            elif system == "windows":
                binary_name = "ksctl-win-amd64.exe"
            else:
                raise KsctlError(f"Unsupported system: {system}")
            
            # Extract binary
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                # Find the binary in the zip
                for file_info in zip_file.filelist:
                    if file_info.filename.endswith(binary_name):
                        logger.info(f"Extracting {file_info.filename}")
                        zip_file.extract(file_info, self.ksctl_path.parent)
                        
                        # Move and rename to ksctl
                        extracted_path = self.ksctl_path.parent / file_info.filename
                        extracted_path.rename(self.ksctl_path)
                        break
                else:
                    raise KsctlError(f"Binary {binary_name} not found in zip file")
            
            # Make executable on Unix-like systems
            if system in ["linux", "darwin"]:
                st = os.stat(self.ksctl_path)
                os.chmod(self.ksctl_path, st.st_mode | stat.S_IEXEC)
            
            # Clean up zip file
            zip_path.unlink()
            
            logger.info(f"ksctl successfully installed to {self.ksctl_path}")
            
        except Exception as e:
            logger.error(f"Failed to download ksctl: {e}")
            raise KsctlError(f"Failed to download ksctl: {e}") from e

    def execute(self, args: list[str], input_data: Optional[str] = None) -> dict[str, Any]:
        """Execute ksctl command with given arguments.
        
        Args:
            args: Command arguments (e.g., ["users", "list"])
            input_data: Optional input data for commands that require it
            
        Returns:
            Dictionary with status, stdout, stderr, and parsed JSON output if applicable
        """
        cmd = [str(self.ksctl_path)]
        
        # Add authentication parameters
        cmd.extend(["--url", settings.ciphertrust_url])
        
        if settings.ciphertrust_user and settings.ciphertrust_password:
            cmd.extend(["--user", settings.ciphertrust_user])
            cmd.extend(["--password", settings.ciphertrust_password])
        elif settings.ciphertrust_jwt:
            cmd.extend(["--jwt", settings.ciphertrust_jwt])
        
        # Add optional parameters
        if settings.ciphertrust_nosslverify:
            cmd.append("--nosslverify")
        
        if settings.ciphertrust_timeout != 30:  # Only add if not default
            cmd.extend(["--timeout", str(settings.ciphertrust_timeout)])
        
        if settings.ciphertrust_domain != "root":
            cmd.extend(["--domain", settings.ciphertrust_domain])
        
        if settings.ciphertrust_auth_domain != "root":
            cmd.extend(["--auth-domain", settings.ciphertrust_auth_domain])
        
        # Add the actual command arguments
        cmd.extend(args)
        
        # Always add --respfmt json for consistent output
        if "--respfmt" not in args:
            cmd.extend(["--respfmt", "json"])
        
        if settings.debug_mode:
            logger.debug(f"Executing: {' '.join(sanitize_command_args(cmd))}")
        else:
            logger.info(f"Executing ksctl command: {args[0] if args else 'unknown'}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                input=input_data,
                timeout=settings.ciphertrust_timeout,
            )
            
            response = {
                "status": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
            
            # Try to parse JSON output
            if result.returncode == 0 and result.stdout:
                try:
                    response["data"] = json.loads(result.stdout)
                except json.JSONDecodeError:
                    # Not all commands return JSON
                    response["data"] = result.stdout.strip()
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                logger.error(f"ksctl command failed: {error_msg}")
                raise KsctlError(f"Command failed: {error_msg}")
            
            return response
            
        except subprocess.TimeoutExpired as e:
            logger.error(f"ksctl command timed out: {e}")
            raise KsctlError("Command timed out") from e
        except Exception as e:
            logger.error(f"Failed to execute ksctl: {e}")
            raise KsctlError(f"Failed to execute command: {e}") from e

    def test_connection(self) -> bool:
        """Test connection to CipherTrust Manager."""
        try:
            result = self.execute(["system", "info", "get"])
            return result["status"] == 0
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Global ksctl manager instance
_ksctl_manager: Optional[KsctlManager] = None


def get_ksctl_manager() -> KsctlManager:
    """Get or create the global ksctl manager instance."""
    global _ksctl_manager
    if _ksctl_manager is None:
        _ksctl_manager = KsctlManager()
    return _ksctl_manager
