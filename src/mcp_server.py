from dataclasses import dataclass
from typing import Any, Optional

from fastmcp import FastMCP
from fastmcp.server.http import create_sse_app


app = FastMCP("Wakapi MCP Server")


# Global configuration manager
_config_manager = None


class WakapiMCPServer:
    """Wakapi MCP server class."""

    def __init__(self, config_manager=None) -> None:
        """Initialize the Wakapi MCP server."""
        global _config_manager
        if config_manager:
            _config_manager = config_manager
        self.app = app
        # FastMCP has no 'tools' attribute; use get_tools() if needed

        self._initialize_tool_system()

        # Update global settings (new FastMCP API)
        message_path = "/messages/"
        sse_path = "/sse"

        self.sse_app = create_sse_app(
            self.app, message_path=message_path, sse_path=sse_path
        )

    def _initialize_tool_system(self) -> None:
        """Initialize new tool system."""
        # Already registered in main.py, so do nothing

    def call_tool(self, tool_name: str, **kwargs):
        """Call a tool by name."""
        # Function-based tools, so call directly
        tool_func = globals().get(tool_name)
        if tool_func:
            return tool_func(**kwargs)

        # Fallback if tool not found in globals
        tool = getattr(self.app, tool_name)
        return tool(**kwargs)


@dataclass
class Config:
    """Configuration class for backward compatibility."""

    wakapi_url: str
    api_key: str
    user_id: str


def get_config(config: Optional[dict[str, Any]] = None) -> Config:
    """
    Load configuration from config manager.

    Returns:
        Config object.
    """
    global _config_manager

    # Try to get config manager from global variable first
    if _config_manager is None:
        raise ValueError("ConfigManager is not initialized.")

    wakapi_config = _config_manager.get_wakapi_config()
    return Config(
        wakapi_url=wakapi_config.url,
        api_key=wakapi_config.api_key,
        user_id="current",
    )


def create_server(config_manager):
    """Create server receiving config_manager."""
    global _config_manager
    _config_manager = config_manager
    server = WakapiMCPServer(config_manager)
    return server.app
