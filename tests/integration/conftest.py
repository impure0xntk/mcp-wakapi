import asyncio
import os
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import pytest_asyncio
import toml
from fastmcp.client import Client

STREAMABLE_HTTP_PATH = "/mcp"


def pytest_addoption(parser):
    parser.addoption(
        "--config",
        action="store",
        default="tests/integration/test_config.toml",
        help="Path to configuration file for MCP server",
    )


def find_free_port(start_port=8000):
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("localhost", port))
                return port
            except OSError:
                port += 1


async def wait_until_ready(uri, process, timeout=30.0):
    """Poll the Streamable HTTP endpoint until it answers tools/list."""
    deadline = asyncio.get_running_loop().time() + timeout
    last_error = None
    while asyncio.get_running_loop().time() < deadline:
        if process.poll() is not None:
            stderr = process.stderr.read().decode(errors="replace")
            raise RuntimeError(
                f"MCP server exited with code {process.returncode}:\n{stderr}"
            )
        try:
            async with Client(uri, init_timeout=5) as client:
                tools = await client.list_tools()
                if tools:
                    return client.server_info, client.protocol_version
        except Exception as exc:  # server not listening yet
            last_error = exc
        await asyncio.sleep(0.2)
    raise RuntimeError(f"MCP server did not become ready at {uri}: {last_error}")


def build_config(project_root: Path, port: int) -> str:
    """Write a config.toml pointing at a free port and return its path."""
    config_path = project_root / "tests" / "integration" / "test_config.toml"
    temp = tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False)
    shutil.copyfile(config_path, temp.name)
    config_data = toml.load(temp.name)
    config_data["server"]["port"] = port
    with open(temp.name, "w") as handle:
        toml.dump(config_data, handle)
    return temp.name


PROJECT_ROOT = Path(__file__).parent.parent.parent


@pytest.fixture
def temp_server_config():
    """Return a factory yielding `(port, config_path)` on a free port.

    The tests directory is not a package, so test modules cannot import these
    helpers directly; a fixture keeps the single definition in conftest.
    """
    made: list[str] = []

    def factory(start_port: int = 8000) -> tuple[int, str]:
        port = find_free_port(start_port)
        path = build_config(PROJECT_ROOT, port)
        made.append(path)
        return port, path

    try:
        yield factory
    finally:
        for path in made:
            try:
                os.unlink(path)
            except OSError:
                pass


@pytest_asyncio.fixture(scope="function")
async def mcp_server_factory():
    """Start `main.py` over Streamable HTTP and yield its client transport URL.

    Extra CLI flags can be appended so transport variants (for example
    `--stateless-http`) are exercised through the real entry point.
    """
    project_root = Path(__file__).parent.parent.parent
    main_py_path = project_root / "main.py"

    async def start(*extra_args: str):
        dynamic_port = find_free_port()
        temp_config = build_config(project_root, dynamic_port)

        process = subprocess.Popen(
            [
                sys.executable,
                str(main_py_path),
                "--transport",
                "http",
                "--config",
                temp_config,
                *extra_args,
            ],
            cwd=str(project_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        uri = f"http://localhost:{dynamic_port}{STREAMABLE_HTTP_PATH}"

        def stop() -> None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
            # Reading the pipes closes them; skipping this leaks the fds and
            # trips ResourceWarning once the interpreter collects the objects.
            for stream in (process.stdout, process.stderr):
                if stream is not None:
                    try:
                        stream.read()
                    finally:
                        stream.close()
            os.unlink(temp_config)

        try:
            server_info, protocol_version = await wait_until_ready(uri, process)
        except BaseException:
            stop()
            raise

        return uri, server_info, protocol_version, stop

    return start


@pytest_asyncio.fixture(scope="function")
async def mcp_server(mcp_server_factory):
    """A default (stateful) Streamable HTTP server, torn down after the test."""
    uri, server_info, protocol_version, stop = await mcp_server_factory()
    try:
        yield uri, server_info, protocol_version
    finally:
        stop()


@pytest_asyncio.fixture(scope="function")
async def no_server():
    """Yield the exception raised when connecting to a dead Streamable HTTP port."""
    uri = f"http://localhost:{find_free_port(9900)}{STREAMABLE_HTTP_PATH}"
    try:
        async with Client(uri, init_timeout=2) as client:
            await client.list_tools()
    except Exception as exc:
        yield exc
    else:
        raise AssertionError("Expected a connection error against a dead port")


@pytest.fixture(scope="session")
def wakapi_url():
    """Base URL of the Wakapi instance the integration tests exercise."""
    import os as _os

    config_path = Path("tests/integration/test_config.toml")
    if config_path.exists():
        return toml.load(config_path)["wakapi"]["url"]
    return _os.environ.get("WAKAPI_URL", "http://localhost:3000")


@pytest.fixture(scope="session")
def live_wakapi(wakapi_url):
    """Skip when no Wakapi instance is reachable.

    These tests assert real API responses, so they cannot pass without a live
    server plus a valid key. Skipping states that fact; silently accepting an
    `"error"` status would hide a broken deployment.
    """
    import httpx

    try:
        response = httpx.get(f"{wakapi_url.rstrip('/')}/api/v1/status", timeout=5)
        response.raise_for_status()
    except Exception as exc:
        pytest.skip(f"No live Wakapi at {wakapi_url}: {exc}")
