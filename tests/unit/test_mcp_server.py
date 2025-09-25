import os
import sys
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / ".." / "src"))

from mcp_server import get_config, create_server
from wakapi_sdk.core.config import ConfigManager
from mcp_tools.dependency_injection import register_config_manager, get_injector


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

        with patch("src.mcp_server._config_manager", mock_manager):
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

    tools = await app.get_tools()
    assert len(tools) == 8
    names = [tool.name for tool in tools.values()]
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
