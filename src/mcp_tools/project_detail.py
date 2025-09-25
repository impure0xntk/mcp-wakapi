"""Wakapi Project Detail tool."""

from typing import Any

from mcp_server import app
from mcp_tools.dependency_injection import get_wakapi_client


@app.tool
async def get_project_detail(id: str, user: str = "current") -> dict[str, Any]:
    """Retrieve a single project.

    Mimics undocumented endpoint related to https://wakatime.com/developers#projects.

    Requires ApiKeyAuth: Set header `Authorization` to your API Key encoded as Base64
    and prefixed with `Basic`.

    Args:
        id (str, required): Project ID to fetch.
        user (str, required, default="current"): User ID to fetch data for
        (or 'current').

    Returns:
        v1.ProjectViewModel:
        - data (Project):
          - id (str): Project ID.
          - name (str): Project name.
          - urlencoded_name (str): URL encoded name.
          - created_at (str): Creation timestamp.
          - last_heartbeat_at (str): Last activity timestamp.
          - human_readable_last_heartbeat_at (str): Human readable last activity.
    """
    client = get_wakapi_client()

    try:
        project = await client.get_project_detail(user=user, id=id)
        return project.model_dump()
    except Exception as e:
        raise ValueError(f"Failed to fetch project detail: {e}") from e
