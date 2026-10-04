import os
import subprocess
import sys
from pathlib import Path

import pytest
from fastmcp.client import Client
from fastmcp.client.transports import PythonStdioTransport

PROJECT_ROOT = Path(__file__).parent.parent.parent

EXPECTED_TOOLS = [
    "get_leaders",
    "get_user",
    "get_projects",
    "get_project_detail",
    "get_recent_logs",
    "get_stats",
    "test_connection",
    "get_all_time_since_today",
]


def build_stdio_transport():
    env = os.environ.copy()
    env["PYTHONPATH"] = (
        str(PROJECT_ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    )
    return PythonStdioTransport(
        script_path=PROJECT_ROOT / "main.py",
        args=[
            "--transport",
            "stdio",
            "--config",
            str(PROJECT_ROOT / "tests/integration/test_config.toml"),
        ],
        cwd=str(PROJECT_ROOT),
        env=env,
        keep_alive=False,
    )


class TestServerStartup:
    @pytest.mark.asyncio
    async def test_http_startup(self, mcp_server, live_wakapi):
        """Streamable HTTP startup, tool listing, and a basic tool call."""
        uri, server_info, protocol_version = mcp_server

        assert protocol_version == "2026-07-28"
        assert server_info.name == "Wakapi MCP Server"
        assert server_info.version

        async with Client(uri) as client:
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            for expected in EXPECTED_TOOLS:
                assert expected in tool_names, (
                    f"Expected tool '{expected}' not found in {tool_names}"
                )

            result = await client.call_tool("test_connection", {})
            assert result.structured_content["status"] == "success"

    @pytest.mark.asyncio
    async def test_http_handshake_without_wakapi(self, mcp_server):
        """Protocol negotiation and tool listing must not need a live Wakapi."""
        uri, server_info, _ = mcp_server

        async with Client(uri) as client:
            assert client.protocol_version == "2026-07-28"
            assert client.server_info.name == "Wakapi MCP Server"
            assert client.server_info.version == server_info.version
            tools = await client.list_tools()
            assert {tool.name for tool in tools} == set(EXPECTED_TOOLS)

    @pytest.mark.asyncio
    async def test_http_endpoint_rejects_legacy_sse_path(self, mcp_server):
        """The removed SSE route must not answer on the HTTP transport."""
        import httpx

        uri, _, _ = mcp_server
        legacy = uri.removesuffix("/mcp") + "/sse"
        async with httpx.AsyncClient() as http:
            response = await http.get(legacy)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_stateless_http_startup(self, mcp_server_factory):
        """`--stateless-http` must negotiate the revision and drop the GET stream.

        Stateless servers keep no session state, so the SDK removes GET from the
        `/mcp` route. A stateful server still answers GET, so this also proves the
        flag reaches the transport instead of being silently ignored.
        """
        import httpx

        uri, server_info, protocol_version, stop = await mcp_server_factory(
            "--stateless-http"
        )
        try:
            assert protocol_version == "2026-07-28"
            assert server_info.name == "Wakapi MCP Server"

            async with Client(uri) as client:
                assert client.protocol_version == "2026-07-28"
                tools = await client.list_tools()
                assert {tool.name for tool in tools} == set(EXPECTED_TOOLS)

            # The MCP handshake above uses POST; GET is what stateless mode drops.
            async with httpx.AsyncClient() as http:
                response = await http.get(uri)
            assert response.status_code == 405, (
                f"expected GET to be rejected in stateless mode, got "
                f"{response.status_code}"
            )
        finally:
            stop()

    @pytest.mark.asyncio
    async def test_stateful_http_serves_get_stream(self, mcp_server):
        """A stateful server keeps GET for server-initiated SSE streams."""
        import httpx

        uri, _, _ = mcp_server
        async with httpx.AsyncClient() as http:
            response = await http.get(uri)
        assert response.status_code != 405, "stateful mode must still route GET"

    @pytest.mark.asyncio
    async def test_every_tool_is_discoverable_and_annotated(self, mcp_server):
        """All tools must survive 2026 protocol validation with readable schemas.

        Optional parameters are modelled as nullable `anyOf`, which the 2026
        revision rejects for `x-mcp-header` annotations. No unsafe annotation is
        added for them; the invariant that matters is that no tool silently
        disappears from `tools/list` and every schema stays machine-readable.
        """
        uri, _, _ = mcp_server

        async with Client(uri) as client:
            tools = await client.list_tools()

        by_name = {tool.name: tool for tool in tools}
        assert set(by_name) == set(EXPECTED_TOOLS), (
            f"tools/list lost tools: {set(EXPECTED_TOOLS) - set(by_name)}"
        )

        for name, tool in by_name.items():
            assert tool.input_schema.get("type") == "object", name
            assert tool.input_schema.get("additionalProperties") is False, name

        # Nullable optionals are the reason no header annotations are declared.
        optional = by_name["get_recent_logs"].input_schema["properties"]["project_name"]
        assert "null" in [entry["type"] for entry in optional["anyOf"]]

        # Required params must still be enforced by the server.
        assert by_name["get_stats"].input_schema["required"] == ["user", "range"]
        assert by_name["get_project_detail"].input_schema["required"] == ["id"]

    @pytest.mark.asyncio
    async def test_stdio_startup(self):
        """STDIO server startup and tool listing."""
        async with Client(transport=build_stdio_transport()) as client:
            assert client.protocol_version == "2026-07-28"
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            for expected in EXPECTED_TOOLS:
                assert expected in tool_names, (
                    f"Expected tool '{expected}' not found in {tool_names}"
                )


def test_http_entry_point_reaches_uvicorn(monkeypatch, temp_server_config, request):
    """`main.main()` must reach `uvicorn.run` when HTTP mode is selected.

    The console script calls `main()` as an imported function, not as
    `__main__`, so an import guarded by `if __name__ == "__main__"` resolves
    during tests yet raises NameError for a real `wakapi-mcp` invocation.
    """
    import uvicorn

    import main
    import mcp_server

    # main() builds the server in-process, which binds the module-level
    # _config_manager. A finalizer (not monkeypatch, which would restore the
    # leaked value) keeps unit tests that assert the uninitialized path from
    # failing based on collection order.
    original = mcp_server._config_manager
    mcp_server._config_manager = None

    def restore() -> None:
        mcp_server._config_manager = original

    request.addfinalizer(restore)

    port, temp_config = temp_server_config(8700)
    calls = []

    def fake_run(app, **kwargs):
        calls.append((app, kwargs))
        raise _Stopped

    class _Stopped(Exception):
        """Stops main() where uvicorn would start blocking."""

    monkeypatch.setattr(uvicorn, "run", fake_run)
    monkeypatch.setattr(
        sys, "argv", ["wakapi-mcp", "--transport", "http", "--config", temp_config]
    )

    with pytest.raises(SystemExit):
        main.main()

    assert len(calls) == 1, f"uvicorn.run was not called: {calls}"
    app, kwargs = calls[0]
    assert kwargs["port"] == port
    assert callable(app), "HTTP mode must hand uvicorn an ASGI app"


def test_invalid_transport():
    """Test server startup with invalid transport fails."""
    proc = subprocess.Popen(
        [sys.executable, "main.py", "--transport", "invalid"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode != 0, "Server should fail to start with invalid transport"
    stderr_str = stderr.decode()
    assert "invalid" in stderr_str.lower() or "error" in stderr_str.lower(), (
        f"Expected error in stderr: {stderr_str}"
    )


def test_sse_transport_is_rejected():
    """`--transport sse` was removed with the 2026-07-28 revision."""
    proc = subprocess.Popen(
        [sys.executable, "main.py", "--transport", "sse"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode != 0
    assert "invalid choice" in stderr.decode().lower()
