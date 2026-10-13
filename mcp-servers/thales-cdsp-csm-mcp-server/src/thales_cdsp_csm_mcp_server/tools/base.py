"""
Thales CDSP CSM MCP Server - Base Tools

This module provides the base classes and tool registry for all MCP tools.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Dict, List, Type

from ..core.client import ThalesCDSPCSMClient

logger = logging.getLogger(__name__)


class BaseThalesCDSPCSMTool:
    """Base class for all Thales CDSP CSM MCP tools."""
    
    def __init__(self, client: ThalesCDSPCSMClient):
        self.client = client
        self._setup_tool_logging()
    
    def _setup_tool_logging(self):
        """Setup tool-specific logging with both Python logging and MCP protocol support."""
        # Create tool-specific logger
        tool_name = self.__class__.__name__.lower()
        self.logger = logging.getLogger(f"thales_csm_mcp.tools.{tool_name}")
        
        # Setup tool-specific file logging
        self._setup_tool_file_logging(tool_name)
    
    def _setup_tool_file_logging(self, tool_name: str):
        """Setup tool-specific file logging."""
        try:
            # Create tools log directory
            tools_log_dir = Path("logs/tools")
            tools_log_dir.mkdir(parents=True, exist_ok=True)
            
            # Create tool-specific log file
            log_file = tools_log_dir / f"{tool_name}.log"
            
            # Create file handler with rotation
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=5*1024*1024,  # 5MB
                backupCount=3,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            
            # Add handler to tool logger
            self.logger.addHandler(file_handler)
            
            # Prevent propagation to avoid duplicate logs
            self.logger.propagate = False
            
        except Exception as e:
            # Fallback to standard logging if file setup fails
            self.logger = logging.getLogger(self.__class__.__name__)
            self.logger.warning(f"Could not setup tool-specific file logging: {e}")
    
    def log(self, level: str, message: str, data: dict = None):
        """Log message with both tool-specific file logging and MCP protocol support."""
        # Convert MCP level to Python logging level
        level_mapping = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'notice': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL,
            'alert': logging.CRITICAL,
            'emergency': logging.CRITICAL
        }
        
        python_level = level_mapping.get(level.lower(), logging.INFO)
        
        # Format message with data
        formatted_message = message
        if data:
            formatted_message = f"{message} | Data: {data}"
        
        # Log to tool-specific file
        self.logger.log(python_level, formatted_message)
        
        # Note: MCP protocol logging is handled by the server's log() method
        # Tools should call the server's log() method for MCP protocol logging
    
    def _should_log(self, level: str) -> bool:
        """Check if a log level should be emitted based on current setting."""
        # Get log level from client config
        log_level = getattr(self.client.config, 'log_level', 'INFO').lower()
        
        level_priority = {
            "debug": 0, "info": 1, "notice": 2, "warning": 3, 
            "error": 4, "critical": 5, "alert": 6, "emergency": 7
        }
        current_priority = level_priority.get(log_level, 1)
        message_priority = level_priority.get(level.lower(), 1)
        return message_priority >= current_priority
    
    async def hybrid_log(self, ctx, level: str, message: str, data: dict = None):
        """
        Hybrid logging that respects log level configuration.
        Logs to both MCP client (if level is appropriate) AND file.
        """
        # Always log to file (respects logger's own level)
        self.log(level, message, data)
        
        # Only log to MCP client if level is appropriate
        if self._should_log(level):
            if level.lower() == 'debug':
                await ctx.debug(message)
            elif level.lower() in ['info', 'notice']:
                await ctx.info(message)
            elif level.lower() == 'warning':
                await ctx.warning(message)
            elif level.lower() in ['error', 'critical', 'alert', 'emergency']:
                await ctx.error(message)


class ThalesCDSPCSMTools:
    """Registry and manager for all Thales CDSP CSM MCP tools."""
    
    def __init__(self, client: ThalesCDSPCSMClient):
        self.client = client
        self.tools: Dict[str, BaseThalesCDSPCSMTool] = {}
        self._register_default_tools()
    
    def add_tool_class(self, tool_instance: BaseThalesCDSPCSMTool):
        """Add a tool class instance to the registry."""
        # Convert PascalCase to snake_case and remove 'Tools' suffix
        class_name = tool_instance.__class__.__name__
        
        # Remove 'Tools' suffix first
        if class_name.endswith('Tools'):
            class_name = class_name[:-5]  # Remove 'Tools'
        
        # Convert to snake_case with acronym handling (e.g., DFCKeys -> dfc_keys)
        import re
        # First split when a sequence of capitals is followed by a lowercase letter
        name_with_acronyms_split = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', class_name)
        # Then do the standard lower-to-upper boundary split
        tool_name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name_with_acronyms_split).lower()
        
        self.tools[tool_name] = tool_instance
        if logger.isEnabledFor(logging.INFO):
            logger.info(f"Registered tool: {tool_name}")
    
    def get_tool(self, tool_name: str) -> BaseThalesCDSPCSMTool:
        """Get a tool by name."""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self.tools.keys())
    
    def _register_default_tools(self):
        """Register the default set of tools in alphabetical order."""
        # Import all tool classes first
        from .secrets.manage_secrets import ManageSecretsTools
        from .dfc_keys.manage_dfc_keys import ManageDFCKeysTools
        from .auth_methods.auth_methods_manager import AuthMethodsManager
        from .customer_fragments.manage_customer_fragments import ManageCustomerFragmentsTools
        from .guidelines.security_guidelines import SecurityGuidelinesTools
        from .rotation.manage_rotation import ManageRotationTools
        from .roles.manage_roles import ManageRolesTools
        from .targets.manage_targets import ManageTargetsTools
        from .monitoring.manage_analytics import ManageAnalyticsTools
        from .administration.manage_account import ManageAccountTools
        from .api_reference import GetAPIReferenceTools
        from .gateways.manage_gateways import ManageGatewaysTools
        
        # Create a list of tool classes with their expected names for sorting
        tool_classes = [
            (ManageSecretsTools, "manage_secrets"),
            (ManageDFCKeysTools, "manage_dfc_keys"),
            (AuthMethodsManager, "auth_methods_manager"),
            (ManageCustomerFragmentsTools, "manage_customer_fragments"),
            (SecurityGuidelinesTools, "security_guidelines"),
            (ManageRotationTools, "manage_rotation"),
            (ManageRolesTools, "manage_roles"),
            (ManageTargetsTools, "manage_targets"),
            (ManageAnalyticsTools, "manage_analytics"),
            (ManageAccountTools, "manage_account"),
            (GetAPIReferenceTools, "get_api_reference"),
            (ManageGatewaysTools, "manage_gateways")
        ]
        
        # Sort tools alphabetically by their expected names
        tool_classes.sort(key=lambda x: x[1])
        
        # Register tools in alphabetical order
        for tool_class, expected_name in tool_classes:
            self.add_tool_class(tool_class(self.client))
        
        if logger.isEnabledFor(logging.INFO):
            logger.info(f"Registered {len(self.tools)} consolidated tools in alphabetical order") 