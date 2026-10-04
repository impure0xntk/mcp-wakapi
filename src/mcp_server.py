"""Wakapi MCP server.

MCP 2026-07-28 (protocol revision "v2") server surface. The FastMCP 4 line is
the only one that speaks that revision, so the SSE-era ``create_sse_app`` wiring
is gone: HTTP clients connect to the Streamable HTTP endpoint at ``/mcp``.
"""

from dataclasses import dataclass
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.http import create_streamable_http_app

SERVER_NAME = "Wakapi MCP Server"
SERVER_VERSION = "0.2.0"
SERVER_INSTRUCTIONS = (
    "Retrieve Wakapi development-time data. Use `get_recent_logs` for raw "
    "heartbeats and the `get_*` summary tools for aggregates. Every tool takes "
    "an optional `user` argument; pass it only when querying another account."
)

app = FastMCP(
    SERVER_NAME,
    instructions=SERVER_INSTRUCTIONS,
    version=SERVER_VERSION,
    website_url="https://github.com/impure0xntk/mcp-wakapi",
    # Errors are surfaced as opaque "Error calling tool" text; the exception
    # detail would otherwise leak Wakapi response bodies (and the API key path).
    mask_error_details=True,
)


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

    def http_app(self, path: str = "/mcp", stateless_http: bool = False):
        """Return the Streamable HTTP ASGI app (MCP 2026-07-28; no SSE app).

        ``create_sse_app`` was removed for this revision, so a single
        Streamable HTTP endpoint serves initialize, tools/list and tools/call.
        """
        return create_streamable_http_app(
            app,
            streamable_http_path=path,
            stateless_http=stateless_http,
        )


@dataclass
class Config:
    """Configuration class for backward compatibility."""

    wakapi_url: str
    api_key: str
    user_id: str


def get_config(config: dict[str, Any] | None = None) -> Config:
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
