import pytest
import asyncio
from unittest.mock import patch, AsyncMock

from mcp_server import app

from wakapi_sdk.client import UserAgentsViewModel


class TestUserAgents:
    """Test for get_user_agents"""

    @pytest.mark.asyncio
    async def test_success(self, mock_wakapi_client):
        """Successfully retrieve user agents"""

        async def async_return(result):
            return result

        with (
            patch(
                "src.mcp_tools.dependency_injection.get_wakapi_client",
                return_value=mock_wakapi_client,
            ),
            patch(
                "src.mcp_tools.user_agents.get_wakapi_client",
                return_value=mock_wakapi_client,
            ),
        ):
            # mock_wakapi_client.get_user_agents is already set up in conftest.py
            tool = await app.get_tool("get_user_agents")
            result = await tool.run({"user": "current"})

            assert len(result.structured_content["data"]) == 2
            assert result.structured_content["data"][0]["value"] == "VSCode"
            mock_wakapi_client.get_user_agents.assert_called_once_with(user="current")

    @pytest.mark.asyncio
    async def test_empty_response(self, mock_wakapi_client):
        """Empty response"""
        empty_agents = []
        with (
            patch(
                "src.mcp_tools.dependency_injection.get_wakapi_client",
                return_value=mock_wakapi_client,
            ),
            patch(
                "src.mcp_tools.user_agents.get_wakapi_client",
                return_value=mock_wakapi_client,
            ),
        ):
            with patch.object(
                mock_wakapi_client, "get_user_agents", new_callable=AsyncMock
            ) as mock_get_agents:
                empty_agents_model = UserAgentsViewModel(
                    data=empty_agents, total_pages=1
                )
                mock_get_agents.return_value = empty_agents_model
                tool = await app.get_tool("get_user_agents")
                result = await tool.run({"user": "current"})
                assert len(result.structured_content["data"]) == 0

    @pytest.mark.asyncio
    async def test_timeout(self, mock_wakapi_client):
        """Timeout"""
        with (
            patch(
                "src.mcp_tools.dependency_injection.get_wakapi_client",
                return_value=mock_wakapi_client,
            ),
            patch(
                "src.mcp_tools.user_agents.get_wakapi_client",
                return_value=mock_wakapi_client,
            ),
        ):
            mock_wakapi_client.get_user_agents = AsyncMock(
                side_effect=asyncio.TimeoutError()
            )
            tool = await app.get_tool("get_user_agents")
            with pytest.raises(ValueError, match=r"Failed to fetch user agents"):
                await tool.run({"user": "current"})
