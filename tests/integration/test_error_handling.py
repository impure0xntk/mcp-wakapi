import pytest
from fastmcp.client import Client
from fastmcp.exceptions import ToolError


@pytest.mark.asyncio
async def test_invalid_params(mcp_server, live_wakapi):
    """Test error handling with invalid parameters."""
    uri, _, _ = mcp_server
    async with Client(uri) as client:
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("get_stats", {"user": "current", "range": "invalid"})
        assert "invalid range" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_missing_required_param(mcp_server):
    """A schema violation is rejected by the server without reaching Wakapi.

    `get_stats` requires both `user` and `range`, so an empty argument object is
    refused by argument validation itself. `get_projects` cannot stand in here:
    every one of its parameters is optional, so an empty call is well-formed and
    only fails later on the Wakapi request, which would make this assertion
    depend on the configured upstream instead of on schema enforcement.
    """
    uri, _, _ = mcp_server
    async with Client(uri) as client:
        with pytest.raises(ToolError):
            await client.call_tool("get_stats", {})


@pytest.mark.asyncio
async def test_server_not_started(no_server):
    """Test error when the server is not started."""
    exception = no_server

    assert isinstance(exception, Exception)
    assert "connect" in str(exception).lower() or "refused" in str(exception).lower()


@pytest.mark.asyncio
async def test_wakapi_error(mcp_server, live_wakapi):
    """Test WakapiError handling."""
    uri, _, _ = mcp_server
    async with Client(uri) as client:
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "get_stats", {"user": "invalid_user", "range": "today"}
            )
        assert "user not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_error_details_are_masked(mcp_server):
    """`mask_error_details=True` keeps internals out of client-visible errors.

    Tool exceptions reach the client as "Error calling tool '<name>'" with no
    traceback, so a failing Wakapi call cannot leak response bodies.
    """
    uri, _, _ = mcp_server
    async with Client(uri) as client:
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "get_project_detail", {"id": "missing", "user": "current"}
            )

    message = str(exc_info.value)
    assert "Traceback" not in message
    assert "httpx" not in message
    assert "WakapiError" not in message
