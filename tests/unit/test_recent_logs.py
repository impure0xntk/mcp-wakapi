import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from datetime import datetime

from mcp_server import app

from wakapi_sdk.client import HeartbeatsResult, HeartbeatEntry


class TestRecentLogs:
    """Tests for recent_logs"""

    @pytest.mark.asyncio
    async def test_success(self, mock_wakapi_client):
        """Successfully retrieves recent logs"""
        mock_recent_heartbeats_data = HeartbeatsResult(
            data=[
                HeartbeatEntry(
                    id="1",
                    project="test_project",
                    language="Python",
                    entity="test.py",
                    time=datetime.now().timestamp(),
                    is_write=True,
                    branch="main",
                    category=None,
                    cursorpos=None,
                    line_additions=None,
                    line_deletions=None,
                    lineno=None,
                    lines=None,
                    type="file",
                    user_agent_id=None,
                    user_id="current",
                    machine_name_id=None,
                    created_at=None,
                )
            ],
            start="2023-01-01",
            end="2023-01-01",
            timezone="UTC",
        )

        async def async_return(result):
            return result

        with (
            patch(
                "mcp_tools.dependency_injection.get_wakapi_client",
                return_value=mock_wakapi_client,
            ),
            patch(
                "mcp_tools.recent_logs.get_wakapi_client",
                return_value=mock_wakapi_client,
            ),
        ):
            mock_wakapi_client.get_heartbeats = AsyncMock(
                return_value=mock_recent_heartbeats_data
            )
            tool = await app.get_tool("get_recent_logs")
            result = await tool.run({"days": 1, "limit": 100})

            assert len(result.structured_content["result"]) == 1
            assert result.structured_content["result"][0]["project"] == "test_project"
            mock_wakapi_client.get_heartbeats.assert_called_once()

    @pytest.mark.asyncio
    async def test_with_project_filter(self, mock_wakapi_client):
        """Retrieves logs with project filter"""
        filtered_heartbeats = HeartbeatsResult(
            data=[
                HeartbeatEntry(
                    id="2",
                    project="test_project",
                    language="Python",
                    entity="test.py",
                    time=datetime.now().timestamp(),
                    is_write=False,
                    branch="main",
                    category=None,
                    cursorpos=None,
                    line_additions=None,
                    line_deletions=None,
                    lineno=None,
                    lines=None,
                    type="file",
                    user_agent_id=None,
                    user_id="current",
                    machine_name_id=None,
                    created_at=None,
                )
            ],
            start="2023-01-01",
            end="2023-01-01",
            timezone="UTC",
        )

        async def async_return(result):
            return result

        with (
            patch(
                "mcp_tools.dependency_injection.get_wakapi_client",
                return_value=mock_wakapi_client,
            ),
            patch(
                "mcp_tools.recent_logs.get_wakapi_client",
                return_value=mock_wakapi_client,
            ),
        ):
            mock_wakapi_client.get_heartbeats = AsyncMock(
                return_value=filtered_heartbeats
            )
            tool = await app.get_tool("get_recent_logs")
            result = await tool.run(
                {"days": 1, "limit": 100, "project_name": "test_project"}
            )
            assert len(result.structured_content["result"]) == 1
            assert result.structured_content["result"][0]["project"] == "test_project"
            mock_wakapi_client.get_heartbeats.assert_called_once_with(
                user="current",
                date=datetime.now().date(),
                project="test_project",
                limit=101,
            )

    @pytest.mark.asyncio
    async def test_days_zero(self, mock_wakapi_client):
        """Empty list when days=0"""
        with (
            patch(
                "mcp_tools.dependency_injection.get_wakapi_client",
                return_value=mock_wakapi_client,
            ),
            patch(
                "mcp_tools.recent_logs.get_wakapi_client",
                return_value=mock_wakapi_client,
            ),
        ):
            mock_wakapi_client.get_heartbeats = AsyncMock(
                return_value=HeartbeatsResult(
                    data=[], start="2023-01-01", end="2023-01-01", timezone="UTC"
                )
            )
            tool = await app.get_tool("get_recent_logs")
            result = await tool.run({"days": 0, "limit": 100})
            assert len(result.structured_content["result"]) == 0

    @pytest.mark.asyncio
    async def test_limit_zero(self, mock_wakapi_client):
        """Empty list when limit=0"""
        with (
            patch(
                "mcp_tools.dependency_injection.get_wakapi_client",
                return_value=mock_wakapi_client,
            ),
            patch(
                "mcp_tools.recent_logs.get_wakapi_client",
                return_value=mock_wakapi_client,
            ),
        ):
            mock_wakapi_client.get_heartbeats = AsyncMock(
                return_value=HeartbeatsResult(
                    data=[], start="2023-01-01", end="2023-01-01", timezone="UTC"
                )
            )
            tool = await app.get_tool("get_recent_logs")
            result = await tool.run({"days": 1, "limit": 0})
            assert len(result.structured_content["result"]) == 0

    @pytest.mark.asyncio
    async def test_timeout(self, mock_wakapi_client):
        """Timeout"""
        with (
            patch(
                "mcp_tools.dependency_injection.get_wakapi_client",
                return_value=mock_wakapi_client,
            ),
            patch(
                "mcp_tools.recent_logs.get_wakapi_client",
                return_value=mock_wakapi_client,
            ),
        ):
            mock_wakapi_client.get_heartbeats = AsyncMock(
                side_effect=asyncio.TimeoutError()
            )
            tool = await app.get_tool("get_recent_logs")
            with pytest.raises(ValueError, match=r"Failed to fetch recent logs"):
                await tool.run({"days": 1, "limit": 100})
