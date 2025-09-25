import pytest
import asyncio
from unittest.mock import patch, AsyncMock

from mcp_server import app

from wakapi_sdk.client import AllTimeViewModel, AllTimeData, AllTimeRange


class TestAllTime:
    """Test for get_all_time_since_today"""

    @pytest.mark.asyncio
    async def test_success(self, mock_wakapi_client):
        """Successfully retrieve all-time statistics"""
        with patch(
            "mcp_tools.dependency_injection.get_wakapi_client",
            return_value=mock_wakapi_client,
        ):
            tool = await app.get_tool("get_all_time_since_today")
            result = await tool.run({})

            assert result.structured_content["data"]["total_seconds"] == 100000.0
            mock_wakapi_client.get_all_time_since_today.assert_called_once_with(
                user="current"
            )

    @pytest.mark.asyncio
    async def test_all_time_empty(self, mock_wakapi_client):
        """Empty response"""
        empty_all_time_data = AllTimeData(
            total_seconds=0.0,
            text="0s",
            is_up_to_date=False,
            range=AllTimeRange(
                start="2023-01-01",
                start_date="2023-01-01",
                end="2023-01-01",
                end_date="2023-01-01",
                timezone="UTC",
            ),
        )
        empty_all_time = AllTimeViewModel(data=empty_all_time_data)
        with patch(
            "mcp_tools.dependency_injection.get_wakapi_client",
            return_value=mock_wakapi_client,
        ):
            with patch.object(
                mock_wakapi_client, "get_all_time_since_today", new_callable=AsyncMock
            ) as mock_get_all:
                mock_get_all.return_value = empty_all_time
                tool = await app.get_tool("get_all_time_since_today")
                result = await tool.run({})
                assert result.structured_content["data"]["total_seconds"] == 0.0

    @pytest.mark.asyncio
    async def test_all_time_timeout(self, mock_wakapi_client):
        """Timeout"""
        with patch(
            "mcp_tools.dependency_injection.get_wakapi_client",
            return_value=mock_wakapi_client,
        ):
            with patch.object(
                mock_wakapi_client, "get_all_time_since_today", new_callable=AsyncMock
            ) as mock_get_all:
                mock_get_all.side_effect = asyncio.TimeoutError()
                tool = await app.get_tool("get_all_time_since_today")
                with pytest.raises(ValueError):
                    await tool.run({})
