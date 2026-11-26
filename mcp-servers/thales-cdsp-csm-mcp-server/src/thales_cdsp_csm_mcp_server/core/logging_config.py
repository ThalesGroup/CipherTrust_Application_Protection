#!/usr/bin/env python3
"""
Logging configuration for Thales CDSP CSM MCP Server.
"""

import os
import logging
import logging.handlers
from pathlib import Path
from typing import Optional


# HYBRID LOGGING SYSTEM: This module provides traditional Python logging
# while the MCP server provides MCP protocol logging. Both systems work together.
def setup_logging(log_level: Optional[str] = None, log_file: Optional[str] = None) -> None:
    """
    Setup logging configuration with both console and file handlers.
    
    Args:
        log_level: Log level (DEBUG, INFO, NOTICE, WARNING, ERROR, CRITICAL, ALERT, EMERGENCY). Defaults to INFO.
        log_file: Path to log file. Defaults to logs/thales-csm-mcp.log in repo root.
    """
    # Get log level from environment or use default
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Validate log level - Support all 8 MCP log levels
    valid_levels = {"DEBUG", "INFO", "NOTICE", "WARNING", "ERROR", "CRITICAL", "ALERT", "EMERGENCY"}
    if log_level not in valid_levels:
        print(f"⚠️  Invalid LOG_LEVEL '{log_level}'. Using INFO instead.")
        log_level = "INFO"
    
    # Convert string to logging level
    numeric_level = getattr(logging, log_level)
    
    # Determine log file path
    if log_file is None:
        # Get the repository root directory (where main.py is located)
        repo_root = Path(__file__).parent.parent.parent.parent
        logs_dir = repo_root / "logs"
        logs_dir.mkdir(exist_ok=True)
        log_file = logs_dir / "thales-csm-mcp.log"
    
    # Create logs directory if it doesn't exist
    log_file.parent.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation (10MB max size, keep 5 backup files)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Set specific logger levels for our package
    package_logger = logging.getLogger("src.thales_cdsp_csm_mcp_server")
    package_logger.setLevel(numeric_level)
    
    # Fix HTTPX logging - don't log 4xx/5xx errors as INFO
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(logging.WARNING)  # Only log warnings and errors
    
    # Fix other noisy loggers
    urllib3_logger = logging.getLogger("urllib3")
    urllib3_logger.setLevel(logging.WARNING)
    
    # Log the configuration (only if level allows)
    if numeric_level <= logging.INFO:
        logging.info(f"Logging configured - Level: {log_level}, File: {log_file}")
        logging.info(f"Console and file logging enabled")
        logging.info(f"HTTPX and urllib3 loggers set to WARNING level to reduce noise")
    
    # Log rotation info (only if level allows)
    if numeric_level <= logging.DEBUG:
        logging.debug(f"Log rotation: Max 10MB per file, keeping 5 backup files") 