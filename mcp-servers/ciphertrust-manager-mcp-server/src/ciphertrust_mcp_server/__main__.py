"""Main entry point for CipherTrust MCP Server."""

import asyncio
import logging
import sys

from .config import settings
from .server import CipherTrustMCPServer


def setup_logging() -> None:
    """Configure logging."""
    # For MCP servers, we should log to stderr to avoid interfering with stdio communication
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )
    
    # Set httpx logging to WARNING unless in debug mode
    if not settings.debug_mode:
        logging.getLogger("httpx").setLevel(logging.WARNING)


async def async_main() -> None:
    """Async main function."""
    setup_logging()
    
    server = CipherTrustMCPServer()
    await server.run()


def main() -> None:
    """Main entry point."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
