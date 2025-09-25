import pytest
import asyncio
from unittest.mock import patch, AsyncMock

from mcp_server import app


class TestStats:
    """Test for stats"""

    @pytest.mark.asyncio
    async def test_stats_success(self, mock_wakapi_client):
        """Successfully retrieve statistics"""
        with patch(
            "mcp_tools.dependency_injection.get_wakapi_client",
            return_value=mock_wakapi_client,
        ):
            tool = await app.get_tool("get_stats")
            result = await tool.run({"user": "current", "range": "daily"})

            assert result.structured_content["data"]["total_seconds"] == 3600.0
            assert (
                result.structured_content["data"]["languages"][0]["total_seconds"]
                == 3600.0
            )
            mock_wakapi_client.get_stats.assert_called_once_with(
                range="daily",
                user="current",
                project=None,
                language=None,
                editor=None,
                operating_system=None,
                machine=None,
                label=None,
            )

    @pytest.mark.asyncio
    async def test_stats_with_filters(self, mock_wakapi_client):
        """Retrieves statistics with filters"""
        from wakapi_sdk.client import StatsData, StatsViewModel, SummariesEntry

        filtered_stats_data = StatsData(
            total_seconds=1800.0,
            human_readable_total="30m",
            daily_average=1800.0,
            human_readable_daily_average="30m",
            languages=[
                SummariesEntry(
                    name="Python",
                    percent=100.0,
                    total_seconds=1800.0,
                    text="30m",
                    digital="0:30",
                    hours=0,
                    minutes=30,
                )
            ],
            projects=[
                SummariesEntry(
                    name="test_project",
                    percent=100.0,
                    total_seconds=1800.0,
                    text="30m",
                    digital="0:30",
                    hours=0,
                    minutes=30,
                )
            ],
            editors=[
                SummariesEntry(
                    name="VSCode",
                    percent=100.0,
                    total_seconds=1800.0,
                    text="30m",
                    digital="0:30",
                    hours=0,
                    minutes=30,
                )
            ],
            operating_systems=[
                SummariesEntry(
                    name="Linux",
                    percent=100.0,
                    total_seconds=1800.0,
                    text="30m",
                    digital="0:30",
                    hours=0,
                    minutes=30,
                )
            ],
            machines=[
                SummariesEntry(
                    name="test-machine",
                    percent=100.0,
                    total_seconds=1800.0,
                    text="30m",
                    digital="0:30",
                    hours=0,
                    minutes=30,
                )
            ],
            range="daily",
            start="2023-01-01",
            end="2023-01-01",
            status="OK",
            is_coding_activity_visible=True,
            is_other_usage_visible=True,
            days_including_holidays=1,
            user_id="current",
            username="testuser",
        )
        filtered_stats = StatsViewModel(data=filtered_stats_data)
        with patch(
            "mcp_tools.dependency_injection.get_wakapi_client",
            return_value=mock_wakapi_client,
        ):
            with patch.object(
                mock_wakapi_client, "get_stats", new_callable=AsyncMock
            ) as mock_get_stats:
                mock_get_stats.return_value = filtered_stats
                tool = await app.get_tool("get_stats")
                result = await tool.run(
                    {
                        "user": "current",
                        "range": "daily",
                        "project": "test_project",
                        "language": "Python",
                        "editor": "VSCode",
                        "operating_system": "Linux",
                        "machine": "test-machine",
                    }
                )
                assert result.structured_content["data"]["total_seconds"] == 1800.0
                mock_get_stats.assert_called_once_with(
                    user="current",
                    range="daily",
                    project="test_project",
                    language="Python",
                    editor="VSCode",
                    operating_system="Linux",
                    machine="test-machine",
                    label=None,
                )

    @pytest.mark.asyncio
    async def test_stats_empty_response(self, mock_wakapi_client):
        """Case of empty response"""
        from wakapi_sdk.client import StatsData, StatsViewModel

        empty_stats_data = StatsData(
            total_seconds=0.0,
            human_readable_total="0s",
            daily_average=0.0,
            human_readable_daily_average="0s",
            languages=[],
            projects=[],
            editors=[],
            operating_systems=[],
            machines=[],
            range="daily",
            start="2023-01-01",
            end="2023-01-01",
            status="OK",
            is_coding_activity_visible=True,
            is_other_usage_visible=True,
            days_including_holidays=1,
            user_id="current",
            username="testuser",
        )
        empty_stats = StatsViewModel(data=empty_stats_data)
        with patch(
            "mcp_tools.dependency_injection.get_wakapi_client",
            return_value=mock_wakapi_client,
        ):
            with patch.object(
                mock_wakapi_client, "get_stats", new_callable=AsyncMock
            ) as mock_get_stats:
                mock_get_stats.return_value = empty_stats
                tool = await app.get_tool("get_stats")
                result = await tool.run({"user": "current", "range": "daily"})
                assert result.structured_content["data"]["total_seconds"] == 0.0

    @pytest.mark.asyncio
    async def test_stats_timeout(self, mock_wakapi_client):
        """Timeout error"""
        with patch(
            "mcp_tools.dependency_injection.get_wakapi_client",
            return_value=mock_wakapi_client,
        ):
            with patch.object(
                mock_wakapi_client, "get_stats", new_callable=AsyncMock
            ) as mock_get_stats:
                mock_get_stats.side_effect = asyncio.TimeoutError("Request timeout")
                tool = await app.get_tool("get_stats")
                with pytest.raises(ValueError):
                    await tool.run({"user": "current", "range": "daily"})
