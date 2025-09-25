import pytest
import subprocess
from fastmcp.client import Client


class TestServerStartup:
    @pytest.mark.asyncio
    async def test_sse_startup(self, mcp_server):
        """Test SSE server startup, tool listing, and basic tool call."""
        session, uri, transport = mcp_server
        async with session as session:
            tools = await session.list_tools()
            expected_tools = [
                "get_leaders",
                "get_user",
                "get_projects",
                "get_project_detail",
                "get_recent_logs",
                "get_stats",
                "test_connection",
                "get_all_time_since_today",
            ]
            tool_names = [tool.name for tool in tools]
            for expected in expected_tools:
                assert expected in tool_names, (
                    f"Expected tool '{expected}' not found in {tool_names}"
                )

            # Basic tool call: test_connection
            print("Calling test_connection tool...")
            result = await session.call_tool("test_connection", {})
            print("test_connection completed")
            # Confirm no exception in test_connection (auth dependent)
            assert result.structured_content["status"] == "success"

    @pytest.mark.asyncio
    async def test_stdio_startup(self):
        """Test STDIO server startup and tool listing (skip Wakapi-dependent calls)."""
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent
        main_py_path = project_root / "main.py"
        config_path = project_root / "tests/integration/test_config.toml"
        import os

        env = os.environ.copy()
        env["PYTHONPATH"] = str(project_root / "src") + ":" + env.get("PYTHONPATH", "")
        from fastmcp.client.transports import PythonStdioTransport

        transport = PythonStdioTransport(
            script_path=main_py_path,
            args=["--transport", "stdio", "--config", str(config_path)],
            cwd=str(project_root),
            env=env,
            keep_alive=False,
        )

        async with Client(transport=transport) as session:
            tools = await session.list_tools()
            expected_tools = [
                "get_leaders",
                "get_user",
                "get_projects",
                "get_project_detail",
                "get_recent_logs",
                "get_stats",
                "test_connection",
                "get_all_time_since_today",
            ]
            tool_names = [tool.name for tool in tools]
            for expected in expected_tools:
                assert expected in tool_names, (
                    f"Expected tool '{expected}' not found in {tool_names}"
                )

            # Skip test_connection call to avoid Wakapi dependency issues in mock mode


def test_invalid_transport():
    """Test server startup with invalid transport fails."""
    from pathlib import Path

    proc = subprocess.Popen(
        ["python", "main.py", "--transport", "invalid", "config.example.json"],
        cwd=Path(__file__).parent.parent.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode != 0, "Server should fail to start with invalid transport"
    stderr_str = stderr.decode()
    assert "invalid" in stderr_str.lower() or "error" in stderr_str.lower(), (
        f"Expected error in stderr: {stderr_str}"
    )
