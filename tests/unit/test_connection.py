import pytest
import asyncio
from unittest.mock import patch, AsyncMock

from mcp_server import app


class TestConnectionTest:
    """Tests for test_connection"""

    @pytest.mark.asyncio
    async def test_success(self, mock_wakapi_client):
        """Successfully test connection"""
        with patch(
            "mcp_tools.dependency_injection.get_wakapi_client",
            return_value=mock_wakapi_client,
        ):
            with patch.object(
                mock_wakapi_client, "get_projects", new_callable=AsyncMock
            ) as mock_get_projects:
                tool = await app.get_tool("test_connection")
                result = await tool.run({})

                assert result.structured_content["status"] == "success"
                assert (
                    "Successfully connected to Wakapi server"
                    in result.structured_content["message"]
                )
                mock_get_projects.assert_called_once()

    @pytest.mark.asyncio
    async def test_connection_failure(self, mock_wakapi_client):
        """Connection failure"""
        with patch(
            "mcp_tools.dependency_injection.get_wakapi_client",
            return_value=mock_wakapi_client,
        ):
            with patch.object(
                mock_wakapi_client, "get_projects", new_callable=AsyncMock
            ) as mock_get_projects:
                mock_get_projects.side_effect = Exception("Connection failed")
                tool = await app.get_tool("test_connection")
                result = await tool.run({})

                assert result.structured_content["status"] == "error"
                assert "Failed to connect" in result.structured_content["message"]

    @pytest.mark.asyncio
    async def test_connection_timeout(self, mock_wakapi_client):
        """Timeout"""
        with patch(
            "mcp_tools.dependency_injection.get_wakapi_client",
            return_value=mock_wakapi_client,
        ):
            with patch.object(
                mock_wakapi_client, "get_projects", new_callable=AsyncMock
            ) as mock_get_projects:
                mock_get_projects.side_effect = asyncio.TimeoutError()
                tool = await app.get_tool("test_connection")
                result = await tool.run({})

                assert result.structured_content["status"] == "error"
                assert "Failed to connect" in result.structured_content["message"]
