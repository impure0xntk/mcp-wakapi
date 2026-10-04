import pytest
from fastmcp.client import Client
from fastmcp.exceptions import ToolError


@pytest.mark.asyncio
async def test_get_leaders(mcp_server, live_wakapi):
    """Test get_leaders tool call succeeds with real API."""
    uri, _, _ = mcp_server
    async with Client(uri) as client:
        result = await client.call_tool("get_leaders", {})
        assert isinstance(result.structured_content, dict)
        assert "data" in result.structured_content


@pytest.mark.asyncio
async def test_get_project_detail(mcp_server, live_wakapi):
    """Test get_project_detail tool call handles API error."""
    uri, _, _ = mcp_server
    async with Client(uri) as client:
        with pytest.raises(ToolError):
            await client.call_tool(
                "get_project_detail", {"id": "test_project_id", "user": "current"}
            )


@pytest.mark.asyncio
async def test_get_recent_logs(mcp_server, live_wakapi):
    """Test get_recent_logs tool call succeeds with real API."""
    uri, _, _ = mcp_server
    async with Client(uri) as client:
        result = await client.call_tool("get_recent_logs", {"days": 7, "limit": 10})
        assert isinstance(result.structured_content, dict)
        assert "result" in result.structured_content


@pytest.mark.asyncio
async def test_get_stats(mcp_server, live_wakapi):
    """Test get_stats tool call succeeds with real API."""
    uri, _, _ = mcp_server
    async with Client(uri) as client:
        result = await client.call_tool(
            "get_stats", {"user": "current", "range": "today"}
        )
        assert isinstance(result.structured_content, dict)
        assert "data" in result.structured_content
        assert "total_seconds" in result.structured_content["data"]


@pytest.mark.asyncio
async def test_get_projects(mcp_server, live_wakapi):
    """Test get_projects tool call succeeds with real API."""
    uri, _, _ = mcp_server
    async with Client(uri) as client:
        result = await client.call_tool("get_projects", {"user": "current"})
        assert isinstance(result.structured_content, dict)
        assert "data" in result.structured_content


@pytest.mark.asyncio
async def test_get_user(mcp_server, live_wakapi):
    """Test get_user tool call succeeds with real API."""
    uri, _, _ = mcp_server
    async with Client(uri) as client:
        result = await client.call_tool("get_user", {"user": "current"})
        assert isinstance(result.structured_content, dict)
        assert "data" in result.structured_content
        assert "id" in result.structured_content["data"]


@pytest.mark.asyncio
async def test_get_all_time_since_today(mcp_server, live_wakapi):
    """Test get_all_time_since_today tool call succeeds with real API."""
    uri, _, _ = mcp_server
    async with Client(uri) as client:
        result = await client.call_tool("get_all_time_since_today", {"user": "current"})
        assert isinstance(result.structured_content, dict)
        assert "data" in result.structured_content
        assert "total_seconds" in result.structured_content["data"]


@pytest.mark.asyncio
async def test_test_connection(mcp_server, live_wakapi):
    """Test test_connection tool call succeeds with real API."""
    uri, _, _ = mcp_server
    async with Client(uri) as client:
        result = await client.call_tool("test_connection", {})
        assert result.structured_content["status"] == "success"


@pytest.mark.asyncio
async def test_invalid_argument_is_rejected(mcp_server):
    """A missing required argument fails schema validation, without Wakapi."""
    uri, _, _ = mcp_server
    async with Client(uri) as client:
        with pytest.raises(ToolError):
            await client.call_tool("get_stats", {"range": "today"})


@pytest.mark.asyncio
async def test_unknown_tool_is_rejected(mcp_server):
    """An unknown tool name fails tools/call, without Wakapi."""
    uri, _, _ = mcp_server
    async with Client(uri) as client:
        with pytest.raises(ToolError):
            await client.call_tool("no_such_tool", {})
