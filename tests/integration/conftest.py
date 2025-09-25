import pytest_asyncio
import asyncio
import subprocess
import socket
import shutil
import tempfile
import os
from pathlib import Path
from fastmcp.client import Client


def pytest_addoption(parser):
    parser.addoption(
        "--config",
        action="store",
        default="tests/integration/test_config.toml",
        help="Path to configuration file for MCP server",
    )


@pytest_asyncio.fixture(scope="function")
async def mcp_server():
    """MCP server fixture: starts SSE server if not running, connects to it."""
    project_root = Path(__file__).parent.parent.parent
    main_py_path = project_root / "main.py"
    config_path = project_root / "tests/integration/test_config.toml"

    def find_free_port(start_port=8000):
        port = start_port
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("localhost", port))
                    return port
                except OSError:
                    port += 1

    dynamic_port = find_free_port()

    # Create temporary config with dynamic port
    temp_config = tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False)
    shutil.copyfile(config_path, temp_config.name)
    import toml

    config_data = toml.load(temp_config.name)
    config_data["server"]["port"] = dynamic_port
    with open(temp_config.name, "w") as f:
        toml.dump(config_data, f)

    # Start MCP server process if not already running
    print("Starting MCP server subprocess...")
    process = subprocess.Popen(
        [
            "python",
            str(main_py_path),
            "--transport",
            "sse",
            "--config",
            temp_config.name,
        ],
        cwd=str(project_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    print(f"MCP server PID: {process.pid}")

    # Wait for server to start (simple sleep, or poll connection)
    print("Waiting 2 seconds for server startup...")
    await asyncio.sleep(2)  # Give time for server to start
    print("Sleep completed, attempting connection...")

    uri = f"http://localhost:{dynamic_port}/sse"
    session = Client(uri)
    try:
        await session.__aenter__()
        # Verify connection by listing tools
        print("Calling list_tools...")
        tools = await session.list_tools()
        print(f"list_tools returned {len(tools)} tools")
        assert len(tools) > 0, "No tools found, server may not be ready"
    except Exception as e:
        process.terminate()
        process.wait()
        await session.__aexit__(None, None, None)
        raise Exception(f"Failed to connect to MCP server: {e}") from e

    yield session, uri, "sse"

    await session.__aexit__(None, None, None)
    process.terminate()
    process.wait()
    os.unlink(temp_config.name)
