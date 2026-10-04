#!/usr/bin/env python3
"""MCP server for collecting logs from Wakapi.

Serves MCP 2026-07-28 (protocol revision "v2"). `--transport stdio` keeps the
original JSON-RPC-over-stdout path; `--transport http` exposes the Streamable
HTTP endpoint at `/mcp`. The SSE transport was removed in this revision, so
there is no `--transport sse`.
"""

import argparse
import sys
from pathlib import Path

import uvicorn
from wakapi_sdk.core.config import ConfigManager
from wakapi_sdk.core.exceptions import ConfigurationError

STREAMABLE_HTTP_PATH = "/mcp"


def main():
    """Run the main application."""
    parser = argparse.ArgumentParser(
        description="MCP server for collecting logs from Wakapi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --config /path/to/config.toml
  %(prog)s --transport stdio  # STDIO transport (default)
  %(prog)s --transport http   # Streamable HTTP transport (port from config)
        """,
    )

    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default=None,
        help="Path to config file (default: config/default.toml or env vars)",
    )

    parser.add_argument(
        "--transport",
        type=str,
        default="stdio",
        choices=["stdio", "http"],
        help="Transport method: stdio (default) or http (Streamable HTTP)",
    )

    parser.add_argument(
        "--stateless-http",
        action="store_true",
        help="Use a fresh transport per request instead of keeping sessions (http only)",
    )

    args = parser.parse_args()

    # Load configuration
    config_path = None
    if args.config:
        config_path = Path(args.config)
    else:
        # Check default configuration file path
        default_config = Path(__file__).parent / "config" / "default.toml"
        if default_config.exists():
            config_path = default_config

    try:
        config_manager = ConfigManager(config_path)
        print("✓ Configuration loaded successfully", file=sys.stderr)

        # Display configuration information (for debugging)
        wakapi_config = config_manager.get_wakapi_config()
        print(f"  - WAKAPI_URL: {wakapi_config.url}", file=sys.stderr)
        print("  - WAKAPI_USER_ID: current", file=sys.stderr)
        print(f"  - WAKAPI_API_PATH: {wakapi_config.api_path}", file=sys.stderr)
        api_key_len = len(wakapi_config.api_key)
        if api_key_len > 8:
            masked_key = "*" * 8 + "..."
        else:
            masked_key = "*" * api_key_len
        print(f"  - WAKAPI_API_KEY: {masked_key}", file=sys.stderr)
        print(f"    (length: {api_key_len})", file=sys.stderr)

        # Register config manager with tool system
        from mcp_tools.dependency_injection import register_config_manager

        register_config_manager(config_manager)

    except ConfigurationError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        import traceback

        print(f"Unexpected error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    # Add src directory to Python path (for backward compatibility)
    sys.path.insert(0, str(Path(__file__).parent / "src"))

    # Import MCP server and start based on transport
    try:
        from mcp_server import WakapiMCPServer

        server = WakapiMCPServer(config_manager)

        # Initialize tools
        initialize_tools()

        if args.transport == "http":
            server_config = config_manager.get_server_config()
            print(
                f"Starting Wakapi MCP Server on "
                f"http://{server_config.host}:{server_config.port}{STREAMABLE_HTTP_PATH}",
                file=sys.stderr,
            )

            # MCP 2026-07-28 dropped the standalone SSE endpoint; a single
            # Streamable HTTP endpoint now carries initialize, tools/list and
            # tools/call, including server-initiated SSE streams on one route.
            app = server.http_app(
                path=STREAMABLE_HTTP_PATH,
                stateless_http=args.stateless_http,
            )
            uvicorn.run(
                app,
                host=server_config.host,
                port=server_config.port,
                log_level="info",
            )
        else:
            print("Starting Wakapi MCP Server in STDIO mode", file=sys.stderr)
            server.app.run(transport="stdio")
    except ImportError as e:
        print(f"Error: Failed to import MCP server: {e}", file=sys.stderr)
        print("Please ensure the server modules are available", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to start MCP server: {e}", file=sys.stderr)
        sys.exit(1)


def initialize_tools():
    """Initialize and register all Wakapi tools."""
    try:
        # Direct imports to avoid circular import in __init__.py
        from mcp_tools.stats import get_stats

        _ = get_stats  # Trigger registration
        from mcp_tools.projects import get_projects

        _ = get_projects  # Trigger registration
        from mcp_tools.leaders import get_leaders

        _ = get_leaders  # Trigger registration
        from mcp_tools.users import get_user

        _ = get_user  # Trigger registration
        from mcp_tools.all_time import get_all_time_since_today

        _ = get_all_time_since_today  # Trigger registration
        from mcp_tools.project_detail import get_project_detail

        _ = get_project_detail  # Trigger registration
        from mcp_tools.recent_logs import get_recent_logs

        _ = get_recent_logs  # Trigger registration
        from mcp_tools.connection import test_connection

        _ = test_connection  # Trigger registration
        print("All Wakapi tools registered successfully.", file=sys.stderr)
    except ImportError as e:
        print(f"Warning: Failed to import some tools: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
