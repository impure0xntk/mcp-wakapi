"""Tools module for Wakapi MCP server."""

from .dependency_injection import (
    DependencyInjector,
    get_injector,
    register_config_manager,
    register_wakapi_client,
    inject_dependencies,
)

# Import function-based tools (lazy to avoid circular imports)
# These are imported directly in main.py to trigger registration

__all__ = [
    "DependencyInjector",
    "get_injector",
    "inject_dependencies",
    "register_config_manager",
    "register_wakapi_client",
]
