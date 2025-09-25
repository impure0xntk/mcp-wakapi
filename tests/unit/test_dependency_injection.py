"""
Tests for Wakapi MCP server dependency injection system
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / ".." / "src"))

from mcp_tools.dependency_injection import (
    DependencyInjector,
    get_injector,
    register_config_manager,
    register_wakapi_client,
    inject_dependencies,
)
from wakapi_sdk.core.config import ConfigManager
from wakapi_sdk.client import WakapiClient


@pytest.fixture
def mock_config_manager():
    """Mock config manager"""
    return MagicMock(spec=ConfigManager)


@pytest.fixture
def mock_wakapi_client():
    """Mock Wakapi client"""
    return MagicMock(spec=WakapiClient)


def test_dependency_injector_basic(mock_config_manager, mock_wakapi_client):
    """Basic dependency injection works correctly"""
    injector = DependencyInjector()
    injector.register_config_manager(mock_config_manager)
    injector.register_wakapi_client(mock_wakapi_client)

    assert injector.get_config_manager() == mock_config_manager
    assert injector.get_wakapi_client() == mock_wakapi_client


def test_get_injector(mock_config_manager, mock_wakapi_client):
    """Global injector works correctly"""
    register_config_manager(mock_config_manager)
    register_wakapi_client(mock_wakapi_client)

    injector = get_injector()
    assert injector.get_config_manager() == mock_config_manager
    assert injector.get_wakapi_client() == mock_wakapi_client


def test_create_wakapi_client(mock_config_manager):
    """Wakapi client is automatically created"""
    injector = DependencyInjector()
    injector.register_config_manager(mock_config_manager)

    client = injector.get_wakapi_client()
    assert isinstance(client, WakapiClient)


def test_inject_dependencies():
    """Dependency injection works correctly"""

    # Dummy class for testing
    class TestTool:
        def __init__(self, config_manager, wakapi_client):
            self.config_manager = config_manager
            self.wakapi_client = wakapi_client

    mock_config_manager = MagicMock(spec=ConfigManager)
    mock_wakapi_client = MagicMock(spec=WakapiClient)

    injector = DependencyInjector()
    injector.register_config_manager(mock_config_manager)
    injector.register_wakapi_client(mock_wakapi_client)

    tool = injector.inject(TestTool)
    assert tool.config_manager == mock_config_manager
    assert tool.wakapi_client == mock_wakapi_client


def test_global_inject():
    """Global injection works correctly"""
    mock_config_manager = MagicMock(spec=ConfigManager)
    mock_wakapi_client = MagicMock(spec=WakapiClient)

    register_config_manager(mock_config_manager)
    register_wakapi_client(mock_wakapi_client)

    # Dummy class for testing
    class TestTool:
        def __init__(self, config_manager, wakapi_client):
            self.config_manager = config_manager
            self.wakapi_client = wakapi_client

    tool = inject_dependencies(TestTool)
    assert tool.config_manager == mock_config_manager
    assert tool.wakapi_client == mock_wakapi_client
