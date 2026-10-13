"""Main MCP server implementation for CipherTrust Manager."""

import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Resource, Tool, Prompt, GetPromptResult, PromptMessage, TextContent

from .config import settings
from .ksctl_cli_manager import get_ksctl_manager
from .tools import ALL_TOOLS

logger = logging.getLogger(__name__)


class CipherTrustMCPServer:
    """MCP Server for CipherTrust Manager."""

    def __init__(self):
        self.server = Server(settings.mcp_server_name)
        self.tools: dict[str, Any] = {}
        self._setup_tools()
        self._setup_handlers()

    def _setup_tools(self) -> None:
        """Initialize all available tools."""
        logger.info(f"Starting tool registration. Total tools to register: {len(ALL_TOOLS)}")
        
        # Log each tool class before instantiation
        for tool_class in ALL_TOOLS:
            logger.info(f"Found tool class: {tool_class.__name__}")
        
        # Initialize tools
        for tool_class in ALL_TOOLS:
            try:
                logger.info(f"Initializing tool: {tool_class.__name__}")
                tool = tool_class()
                self.tools[tool.name] = tool
                logger.info(f"Successfully registered tool: {tool.name}")
            except Exception as e:
                logger.error(f"Failed to register tool {tool_class.__name__}: {str(e)}", exc_info=True)
        
        logger.info(f"Tool registration complete. Registered {len(self.tools)} tools")
        logger.info(f"Available tools: {list(self.tools.keys())}")

    def _setup_handlers(self) -> None:
        """Set up MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List all available tools."""
            return [tool.to_mcp_tool() for tool in self.tools.values()]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[Any]:
            """Handle tool execution."""
            if name not in self.tools:
                raise ValueError(f"Unknown tool: {name}")
            
            tool = self.tools[name]
            try:
                result = await tool.execute(**(arguments or {}))
                # MCP expects results in a specific format
                return [{
                    "type": "text",
                    "text": json.dumps(result, indent=2) if isinstance(result, (dict, list)) else str(result)
                }]
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                raise

        @self.server.list_resources()
        async def handle_list_resources() -> list[Resource]:
            """List available resources."""
            # Currently, no resources are exposed
            # Potentially could expose CT configuration, policies, etc.
            return []

        @self.server.list_prompts()
        async def handle_list_prompts() -> list[Prompt]:
            """List available prompts."""
            # Currently, no prompts are available
            # Potentially could add prompts for common CipherTrust workflows
            return []

        @self.server.get_prompt()
        async def handle_get_prompt(name: str, arguments: dict[str, str] | None = None) -> GetPromptResult:
            """Handle get prompt requests."""
            # Currently, no prompts are available
            raise ValueError(f"Unknown prompt: {name}")

    async def run(self) -> None:
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server
        
        print("Starting MCP server...")
        
        logger.info(f"Starting {settings.mcp_server_name} v{settings.mcp_server_version}")
        
        # Test connection to CipherTrust Manager
        try:
            ksctl = get_ksctl_manager()
            if ksctl.test_connection():
                logger.info("Successfully connected to CipherTrust Manager")
            else:
                logger.warning("Failed to connect to CipherTrust Manager")
        except Exception as e:
            logger.error(f"Error testing connection: {e}")
        
        logger.info("MCP server ready and waiting for JSON-RPC messages on stdin...")
        
        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=settings.mcp_server_name,
                    server_version=settings.mcp_server_version,
                    capabilities={
                        "tools": {},
                        "resources": {},
                        "prompts": {},
                    },
                ),
            )

        print("MCP server started successfully!")
