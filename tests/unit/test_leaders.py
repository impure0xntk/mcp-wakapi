import pytest
import asyncio
from unittest.mock import patch, AsyncMock

from mcp_server import app

from wakapi_sdk.client import (
    LeadersViewModel,
    LeadersRange,
)


class TestLeaders:
    """Test for get_leaders"""

    @pytest.mark.asyncio
    async def test_success(self, mock_wakapi_client):
        """Successfully retrieve leaderboard"""
        with patch(
            "mcp_tools.dependency_injection.get_wakapi_client",
            return_value=mock_wakapi_client,
        ):
            tool = await app.get_tool("get_leaders")
            result = await tool.run({})

            assert len(result.structured_content["data"]) == 2
            assert result.structured_content["data"][0]["user"]["username"] == "leader1"
            mock_wakapi_client.get_leaders.assert_called_once()

    @pytest.mark.asyncio
    async def test_empty_response(self, mock_wakapi_client):
        """Empty response"""
        empty_leaders = []
        with patch(
            "mcp_tools.dependency_injection.get_wakapi_client",
            return_value=mock_wakapi_client,
        ):
            with patch.object(
                mock_wakapi_client, "get_leaders", new_callable=AsyncMock
            ) as mock_get_leaders:
                empty_leaders_model = LeadersViewModel(
                    data=empty_leaders,
                    language="all",
                    page=1,
                    range=LeadersRange(
                        end_date="2023-01-01",
                        end_text="Jan 1st, 2023",
                        name="last_7_days",
                        start_date="2022-12-25",
                        start_text="Dec 25th, 2022",
                        text="Last 7 days",
                    ),
                    total_pages=1,
                )
                mock_get_leaders.return_value = empty_leaders_model
                tool = await app.get_tool("get_leaders")
                result = await tool.run({})
                assert len(result.structured_content["data"]) == 0

    @pytest.mark.asyncio
    async def test_timeout(self, mock_wakapi_client):
        """Timeout"""
        with patch(
            "mcp_tools.dependency_injection.get_wakapi_client",
            return_value=mock_wakapi_client,
        ):
            with patch.object(
                mock_wakapi_client, "get_leaders", new_callable=AsyncMock
            ) as mock_get_leaders:
                mock_get_leaders.side_effect = asyncio.TimeoutError()
                tool = await app.get_tool("get_leaders")
                with pytest.raises(ValueError):
                    await tool.run({})
