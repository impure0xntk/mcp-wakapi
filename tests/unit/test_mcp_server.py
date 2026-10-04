import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / ".." / "src"))

from wakapi_sdk.core.config import ConfigManager

from mcp_server import create_server, get_config
from mcp_tools.dependency_injection import get_injector, register_config_manager


class TestConfig:
    def test_get_config_with_env(self):
        mock_manager = MagicMock(spec=ConfigManager)
        mock_config = MagicMock()
        mock_config.url = "http://localhost:3000"
        mock_config.api_key = "test_api_key"
        mock_manager.get_wakapi_config.return_value = mock_config

        # Error case: WakapiMCPServer get_config raise exception
        # when server is uninitialized.
        #
        # Completely clear environment variables and test without config_manager
        with patch.dict(os.environ, {}, clear=True):
            # Clear dependency injection system
            get_injector().clear()

            # Verify that an exception is raised when config_manager is not initialized
            with pytest.raises(ValueError, match="ConfigManager is not initialized"):
                get_config()

            # Clean up: clear the injector for other tests
            get_injector().clear()

        # Register mock manager with dependency injection system
        register_config_manager(mock_manager)
        create_server(mock_manager)

        with patch("mcp_server._config_manager", mock_manager):
            config = get_config()
            assert config.wakapi_url == "http://localhost:3000"
            assert config.api_key == "test_api_key"

        # Clean up: clear the injector for other tests
        get_injector().clear()


# Tool function tests are separated into another file
# Functions with FastMCP decorators cannot be tested directly
@pytest.mark.asyncio
async def test_tools_list():
    from mcp_server import app

    # FastMCP 4 exposes `list_tools()` as a coroutine returning a sequence of
    # Tool objects; the pre-4.0 `get_tools()` dict accessor is gone.
    tools = await app.list_tools()
    assert len(tools) == 8
    names = [tool.name for tool in tools]
    expected_names = [
        "get_stats",
        "get_projects",
        "get_recent_logs",
        "test_connection",
        "get_leaders",
        "get_user",
        "get_all_time_since_today",
        "get_project_detail",
    ]
    assert set(expected_names) == set(names)


@pytest.mark.asyncio
async def test_server_advertises_2026_07_28_metadata():
    """Server metadata required by the MCP 2026-07-28 initialize result."""
    from mcp_server import SERVER_VERSION, app

    assert app.name == "Wakapi MCP Server"
    assert app.version == SERVER_VERSION
    assert app.instructions


@pytest.mark.asyncio
async def test_get_tool_resolves_registered_tool():
    """FastMCP 4 `get_tool()` is a coroutine returning a Tool or None."""
    from mcp_server import app

    assert (await app.get_tool("get_stats")) is not None
    assert await app.get_tool("no_such_tool") is None


@pytest.mark.asyncio
async def test_tool_schemas_avoid_invalid_x_mcp_header():
    """No tool may annotate a nullable property with `x-mcp-header`.

    A 2026-07-28 client drops any tool whose schema carries an invalid
    `x-mcp-header`, and `Optional[str]` renders as `anyOf[string, null]`,
    which the spec forbids. Annotating one makes the tool disappear.
    """
    from mcp.shared.inbound import find_invalid_x_mcp_header

    from mcp_server import app

    for tool in await app.list_tools():
        # `parameters` is FastMCP's field name; the MCP wire name is
        # `input_schema` (renamed by SDK v2).
        reason = find_invalid_x_mcp_header(tool.parameters)
        assert reason is None, f"{tool.name}: {reason}"


@pytest.mark.asyncio
async def test_http_app_exposes_streamable_http_only():
    """The 2026-07-28 revision serves one Streamable HTTP route, not SSE."""
    from mcp_server import WakapiMCPServer

    server = WakapiMCPServer()
    asgi_app = server.http_app(path="/mcp")
    paths = {getattr(route, "path", None) for route in getattr(asgi_app, "routes", [])}
    assert "/mcp" in paths
    assert "/sse" not in paths
