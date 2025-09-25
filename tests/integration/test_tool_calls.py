import pytest
from fastmcp.exceptions import ToolError
from fastmcp.client import Client


@pytest.mark.asyncio
async def test_get_leaders(mcp_server):
    """Test get_leaders tool call succeeds with real API."""
    session, uri, _ = mcp_server
    async with Client(uri) as client:
        result = await client.call_tool("get_leaders", {})
        assert isinstance(result.structured_content, dict)
        assert "data" in result.structured_content


@pytest.mark.asyncio
async def test_get_project_detail(mcp_server):
    """Test get_project_detail tool call handles API error."""
    session, uri, _ = mcp_server
    test_project_id = "test_project_id"
    async with Client(uri) as client:
        with pytest.raises(ToolError):
            await client.call_tool(
                "get_project_detail", {"id": test_project_id, "user": "current"}
            )


@pytest.mark.asyncio
async def test_get_recent_logs(mcp_server):
    """Test get_recent_logs tool call succeeds with real API."""
    session, uri, _ = mcp_server
    async with Client(uri) as client:
        result = await client.call_tool("get_recent_logs", {"days": 7, "limit": 10})
        assert isinstance(result.structured_content, dict)
        assert "result" in result.structured_content


@pytest.mark.asyncio
async def test_get_stats(mcp_server):
    """Test get_stats tool call succeeds with real API."""
    session, uri, _ = mcp_server
    async with Client(uri) as client:
        result = await client.call_tool(
            "get_stats", {"user": "current", "range": "today"}
        )
        assert isinstance(result.structured_content, dict)
        assert "data" in result.structured_content
        assert "total_seconds" in result.structured_content["data"]


@pytest.mark.asyncio
async def test_get_projects(mcp_server):
    """Test get_projects tool call succeeds with real API."""
    session, uri, _ = mcp_server
    async with Client(uri) as client:
        result = await client.call_tool("get_projects", {"user": "current"})
        assert isinstance(result.structured_content, dict)
        assert "data" in result.structured_content


@pytest.mark.asyncio
async def test_get_user(mcp_server):
    """Test get_user tool call succeeds with real API."""
    session, uri, _ = mcp_server
    async with Client(uri) as client:
        result = await client.call_tool("get_user", {"user": "current"})
        assert isinstance(result.structured_content, dict)
        assert "data" in result.structured_content
        assert "id" in result.structured_content["data"]


@pytest.mark.asyncio
async def test_get_all_time_since_today(mcp_server):
    """Test get_all_time_since_today tool call succeeds with real API."""
    session, uri, _ = mcp_server
    async with Client(uri) as client:
        result = await client.call_tool("get_all_time_since_today", {"user": "current"})
        assert isinstance(result.structured_content, dict)
        assert "data" in result.structured_content
        assert "total_seconds" in result.structured_content["data"]


@pytest.mark.asyncio
async def test_test_connection(mcp_server):
    """Test test_connection tool call succeeds with real API."""
    session, uri, _ = mcp_server
    async with Client(uri) as client:
        result = await client.call_tool("test_connection", {})
        assert result.structured_content["status"] == "success"


@pytest.mark.asyncio
async def test_get_projects_error(mcp_server, monkeypatch):
    """Test get_projects with invalid user raises error."""
    session, uri, _ = mcp_server

    async def mock_tool_call(*args, **kwargs):
        raise ValueError("Invalid user")

    async with Client(uri) as client:
        monkeypatch.setattr(client, "call_tool", mock_tool_call)
        with pytest.raises(ValueError):
            await client.call_tool("get_projects", {"user": "invalid"})


@pytest.mark.asyncio
async def test_get_stats_error(mcp_server, monkeypatch):
    """Test get_stats with invalid range raises error."""
    session, uri, _ = mcp_server

    async def mock_tool_call(*args, **kwargs):
        raise ValueError("Invalid range")

    async with Client(uri) as client:
        monkeypatch.setattr(client, "call_tool", mock_tool_call)
        with pytest.raises(ValueError):
            await client.call_tool(
                "get_stats", {"user": "current", "range": "invalid_range"}
            )
