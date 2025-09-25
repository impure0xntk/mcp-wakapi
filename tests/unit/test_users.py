import pytest
import asyncio
from unittest.mock import patch, AsyncMock

from mcp_server import app


class TestUsers:
    """Tests for get_user"""

    @pytest.mark.asyncio
    async def test_success(self, mock_wakapi_client):
        """Successfully retrieves user information"""
        with patch(
            "mcp_tools.dependency_injection.get_wakapi_client",
            return_value=mock_wakapi_client,
        ):
            tool = await app.get_tool("get_user")
            result = await tool.run({"user": "testuser"})

            assert result.structured_content["data"]["username"] == "testuser"
            assert result.structured_content["data"]["full_name"] == "Test User"
            mock_wakapi_client.get_user.assert_called_once_with(user="testuser")

    @pytest.mark.asyncio
    async def test_user_empty(self, mock_wakapi_client):
        """Empty response"""
        with patch(
            "mcp_tools.dependency_injection.get_wakapi_client",
            return_value=mock_wakapi_client,
        ):
            with patch.object(
                mock_wakapi_client, "get_user", new_callable=AsyncMock
            ) as mock_get_user:
                mock_get_user.side_effect = Exception("User not found")
                tool = await app.get_tool("get_user")
                with pytest.raises(ValueError):
                    await tool.run({"user": "nonexistent"})

    @pytest.mark.asyncio
    async def test_user_timeout(self, mock_wakapi_client):
        """Timeout"""
        with patch(
            "mcp_tools.dependency_injection.get_wakapi_client",
            return_value=mock_wakapi_client,
        ):
            with patch.object(
                mock_wakapi_client, "get_user", new_callable=AsyncMock
            ) as mock_get_user:
                mock_get_user.side_effect = asyncio.TimeoutError()
                tool = await app.get_tool("get_user")
                with pytest.raises(ValueError):
                    await tool.run({"user": "testuser"})
