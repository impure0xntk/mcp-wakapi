"""Wakapi connection test tool."""

from typing import Any

from mcp_server import app
from wakapi_sdk.core.logging import get_logger


@app.tool
async def test_connection() -> dict[str, Any]:
    """Test Wakapi server connection via simple API call to fetch projects.

    Returns:
        A dictionary with the connection test result, including:
        - status (str): 'success' or 'error'.
        - message (str): Description of the result.
        - projects_count (int, optional): Number of projects if successful.
        - server_url (str): The Wakapi server URL.
        - api_path (str): The API path used for requests.
        - error (str, optional): Error message if failed.
    """
    logger = get_logger("connection_tool")
    from mcp_tools.dependency_injection import get_wakapi_client

    logger.info("Starting connection test", method="test_connection")

    client = get_wakapi_client()

    try:
        # Test connection with a simple API call
        projects = await client.get_projects()
        logger.debug(
            f"Projects type: {type(projects)}, data length: "
            f"{len(projects.data) if hasattr(projects, 'data') else 'No data attr'}"
        )

        return {
            "status": "success",
            "message": f"Successfully connected to Wakapi server "
            f"({client.config.base_url})",
            "projects_count": len(projects.data),
            "server_url": client.config.base_url,
            "api_path": client.config.api_path,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to connect to Wakapi server: {e!s}",
            "server_url": client.config.base_url,
            "api_path": client.config.api_path,
            "error": str(e),
        }
