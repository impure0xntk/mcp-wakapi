import base64
import pytest
from unittest.mock import AsyncMock, Mock, patch, ANY
import httpx

from wakapi_sdk.client import (
    WakapiClient,
    WakapiConfig,
)
from wakapi_sdk.core.exceptions import ApiError


@pytest.fixture
def config():
    """Create a default WakapiConfig instance for testing."""
    return WakapiConfig(base_url="http://localhost:3000/", api_key="test_api_key", api_path="/compat/wakatime/v1")


@pytest.fixture
def mock_httpx_client():
    """Provide a mocked AsyncClient from httpx for testing API calls."""
    with patch("httpx.AsyncClient") as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


class TestWakapiClient:
    """Test suite for WakapiClient functionality."""

    @pytest.mark.asyncio
    async def test_get_stats_success(self, config, mock_httpx_client):
        """Test successful retrieval of user statistics for the 'today' range."""
        mock_response = Mock()
        mock_data = {
            "total_seconds": 3600.0,
            "human_readable_total": "1h 0m",
            "daily_average": 3600.0,
            "human_readable_daily_average": "1h 0m",
            "languages": [
                {
                    "name": "Python",
                    "percent": 55.56,
                    "total_seconds": 2000.0,
                    "text": "33m 20s",
                    "digital": "33:20",
                    "hours": 0,
                    "minutes": 33,
                    "seconds": 20,
                }
            ],
            "projects": [
                {
                    "name": "test_project",
                    "percent": 100.0,
                    "total_seconds": 3600.0,
                    "text": "1h 0m",
                    "digital": "1:00",
                    "hours": 1,
                    "minutes": 0,
                }
            ],
            "editors": [],
            "operating_systems": [],
            "machines": [],
            "range": "today",
            "start": "2023-01-01",
            "end": "2023-01-01",
            "status": "OK",
            "is_coding_activity_visible": True,
            "is_other_usage_visible": True,
            "days_including_holidays": 1,
            "user_id": "current",
            "username": "test_user",
        }
        mock_response.json.return_value = {"data": mock_data}
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.get.return_value = mock_response

        client = WakapiClient(config)
        stats = await client.get_stats(range="today")

        assert stats.data.total_seconds == 3600.0
        assert stats.data.languages[0].name == "Python"
        assert stats.data.projects[0].name == "test_project"

        mock_httpx_client.get.assert_called_once_with(
            "http://localhost:3000/api/compat/wakatime/v1/users/current/stats/today",
            params={},
            headers=ANY,
        )

    @pytest.mark.asyncio
    async def test_get_projects_success(self, config, mock_httpx_client):
        """Test successful retrieval of user's projects."""
        mock_response = Mock()
        mock_data = [
            {
                "id": "1",
                "name": "project1",
                "urlencoded_name": "project1",
                "created_at": "2023-01-01",
                "last_heartbeat_at": "2023-01-01",
                "human_readable_last_heartbeat_at": "1 day ago",
            }
        ]
        mock_response.json.return_value = {"data": mock_data}
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.get.return_value = mock_response

        client = WakapiClient(config)
        projects = await client.get_projects()

        assert len(projects.data) == 1
        assert projects.data[0].name == "project1"

        mock_httpx_client.get.assert_called_once_with(
            "http://localhost:3000/api/compat/wakatime/v1/users/current/projects",
            params={},
            headers=ANY,
        )

    @pytest.mark.asyncio
    async def test_http_error_handling(self, config, mock_httpx_client):
        """Test handling of HTTP errors in API calls."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            message="404 Client Error: Not Found",
            request=Mock(),
            response=mock_response,
        )
        mock_httpx_client.get.return_value = mock_response

        client = WakapiClient(config)

        with pytest.raises(ApiError):
            await client.get_user()

    @pytest.mark.asyncio
    async def test_client_context_manager(self, config, mock_httpx_client):
        """Test WakapiClient as an async context manager."""
        async with WakapiClient(config) as client:
            assert client.client is not None

        # Confirm that the client is closed
        mock_httpx_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_headers_with_base64_encoding(self, config):
        """Test generation of headers with Base64-encoded API key."""
        client = WakapiClient(config)
        headers = client._get_headers()

        # Confirm that the Authorization header is correctly set
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Basic ")

        # Confirm that Base64 encoding is correctly performed
        encoded_token = headers["Authorization"].replace("Basic ", "")
        decoded_token = base64.b64decode(encoded_token.encode()).decode()
        assert decoded_token == "test_api_key"

        # Confirm that the Content-Type header is correctly set
        assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_get_heartbeats_success(self, config, mock_httpx_client):
        """Test successful retrieval of heartbeats with parameters."""
        mock_response = Mock()
        mock_data = [
            {
                "id": "1",
                "project": "test_project",
                "language": "Python",
                "entity": "file.py",
                "time": 1690000000.0,
                "is_write": True,
                "branch": "main",
            }
        ]
        mock_response.json.return_value = {
            "data": mock_data,
            "start": "2023-01-01",
            "end": "2023-01-01",
            "timezone": "UTC",
        }
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.get.return_value = mock_response

        client = WakapiClient(config)
        heartbeats = await client.get_heartbeats(
            date="2023-01-01", project="test_project", limit=10
        )

        assert len(heartbeats.data) == 1
        assert heartbeats.data[0].project == "test_project"
        assert heartbeats.start == "2023-01-01"

        mock_httpx_client.get.assert_called_once_with(
            "http://localhost:3000/api/compat/wakatime/v1/users/current/heartbeats",
            params={"date": "2023-01-01", "project": "test_project", "limit": 10},
            headers=ANY,
        )

    @pytest.mark.asyncio
    async def test_get_heartbeats_empty(self, config, mock_httpx_client):
        """Test retrieval of heartbeats when no data is present."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [],
            "start": "2023-01-01",
            "end": "2023-01-01",
            "timezone": "UTC",
        }
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.get.return_value = mock_response

        client = WakapiClient(config)
        heartbeats = await client.get_heartbeats(date="2023-01-01")

        assert len(heartbeats.data) == 0

    @pytest.mark.asyncio
    async def test_get_user_success(self, config, mock_httpx_client):
        """Test successful retrieval of user information."""
        mock_response = Mock()
        mock_data = {
            "id": "1",
            "username": "test_user",
            "display_name": "Test User",
            "full_name": "Test User",
            "email": "test@example.com",
            "photo": "",
            "website": "",
            "timezone": "UTC",
            "created_at": "2023-01-01",
            "modified_at": "2023-01-01",
            "last_heartbeat_at": "2023-01-01",
            "last_plugin_name": "",
            "last_project": "",
            "is_email_confirmed": True,
            "is_email_public": False,
        }
        mock_response.json.return_value = {"data": mock_data}
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.get.return_value = mock_response

        client = WakapiClient(config)
        user = await client.get_user("current")

        assert user.data.username == "test_user"
        assert user.data.email == "test@example.com"

        mock_httpx_client.get.assert_called_once_with(
            "http://localhost:3000/api/compat/wakatime/v1/users/current", headers=ANY
        )

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, config, mock_httpx_client):
        """Test handling of user not found (404) error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            message="404 Client Error: Not Found",
            request=Mock(),
            response=mock_response,
        )
        mock_httpx_client.get.return_value = mock_response

        client = WakapiClient(config)

        with pytest.raises(ApiError):
            await client.get_user("nonexistent")

    @pytest.mark.asyncio
    async def test_get_leaders_success(self, config, mock_httpx_client):
        """Test successful retrieval of leaderboard."""
        mock_response = Mock()
        mock_data = [
            {
                "rank": 1,
                "running_total": {
                    "daily_average": 7200,
                    "human_readable_daily_average": "2h 0m",
                    "human_readable_total": "2h 0m",
                    "languages": [{"name": "Python", "total_seconds": 7200}],
                    "total_seconds": 7200,
                },
                "user": {
                    "id": "1",
                    "username": "leader1",
                    "display_name": "Leader 1",
                    "full_name": "Leader 1",
                    "email": "leader1@example.com",
                    "photo": "",
                    "website": "",
                    "timezone": "UTC",
                    "created_at": "2023-01-01",
                    "modified_at": "2023-01-01",
                    "last_heartbeat_at": "2023-01-01",
                    "last_plugin_name": "",
                    "last_project": "",
                    "is_email_confirmed": True,
                    "is_email_public": False,
                },
            },
            {
                "rank": 2,
                "running_total": {
                    "daily_average": 5400,
                    "human_readable_daily_average": "1h 30m",
                    "human_readable_total": "1h 30m",
                    "languages": [{"name": "JavaScript", "total_seconds": 5400}],
                    "total_seconds": 5400,
                },
                "user": {
                    "id": "2",
                    "username": "leader2",
                    "display_name": "Leader 2",
                    "full_name": "Leader 2",
                    "email": "leader2@example.com",
                    "photo": "",
                    "website": "",
                    "timezone": "UTC",
                    "created_at": "2023-01-01",
                    "modified_at": "2023-01-01",
                    "last_heartbeat_at": "2023-01-01",
                    "last_plugin_name": "",
                    "last_project": "",
                    "is_email_confirmed": True,
                    "is_email_public": False,
                },
            },
        ]
        mock_response.json.return_value = {
            "data": mock_data,
            "language": "all",
            "page": 1,
            "range": {
                "end_date": "2023-01-01",
                "end_text": "Jan 1st, 2023",
                "name": "last_7_days",
                "start_date": "2022-12-25",
                "start_text": "Dec 25th, 2022",
                "text": "Last 7 days",
            },
            "total_pages": 1,
        }
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.get.return_value = mock_response

        client = WakapiClient(config)
        leaders = await client.get_leaders()

        assert len(leaders.data) == 2
        assert leaders.data[0].user.username == "leader1"
        assert leaders.data[0].running_total.total_seconds == 7200
        assert leaders.data[1].user.username == "leader2"

        mock_httpx_client.get.assert_called_once_with(
            "http://localhost:3000/api/compat/wakatime/v1/leaders", headers=ANY
        )
