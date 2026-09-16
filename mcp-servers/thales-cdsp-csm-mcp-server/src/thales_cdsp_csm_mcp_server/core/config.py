"""
Thales CDSP CSM MCP Server - Configuration Module

This module handles configuration management for the Thales CDSP CSM MCP server.
"""

import os
from pydantic import BaseModel, Field, field_validator
from typing import Literal


class ThalesCDSPCSMConfig(BaseModel):
    """Configuration for Thales CDSP CSM client."""
    
    api_url: str = Field(default_factory=lambda: os.getenv("AKEYLESS_API_URL", "https://api.akeyless.io"))
    access_id: str = Field(default_factory=lambda: os.getenv("AKEYLESS_ACCESS_ID", ""))
    access_key: str = Field(default_factory=lambda: os.getenv("AKEYLESS_ACCESS_KEY", ""))
    verify_ssl: bool = Field(default_factory=lambda: os.getenv("AKEYLESS_VERIFY_SSL", "true").lower() == "true")
    log_level: Literal["DEBUG", "INFO", "NOTICE", "WARNING", "ERROR", "CRITICAL", "ALERT", "EMERGENCY"] = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").upper()
    )
    
    @field_validator('log_level', mode='before')
    @classmethod
    def validate_log_level(cls, v):
        """Validate and normalize log level according to MCP specification."""
        if isinstance(v, str):
            v = v.upper()
        valid_levels = {"DEBUG", "INFO", "NOTICE", "WARNING", "ERROR", "CRITICAL", "ALERT", "EMERGENCY"}
        if v not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}, got {v}")
        return v 