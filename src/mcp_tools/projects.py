"""Wakapi project retrieval tool."""

from typing import Optional

from mcp_server import app
from wakapi_sdk.client import (
    ProjectsViewModel,
)

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.tool
async def get_projects(
    user: str = "current", q: Optional[str] = None
) -> ProjectsViewModel:
    """Retrieve and filter the user's projects.

    operationId: get-wakatime-projects
    summary: Retrieve and filter the user's projects
    description: Mimics https://wakatime.com/developers#projects
    tags: [wakatime]
    parameters:
      - name: user
        in: path
        description: User ID to fetch data for (or 'current')
        required: true
        schema:
          type: string
      - name: q
        in: query
        description: Query to filter projects by
        schema:
          type: string
    responses:
      200:
        description: OK
        schema: v1.ProjectsViewModel

    Requires ApiKeyAuth: Set header `Authorization` to your API Key
    encoded as Base64 and prefixed with `Basic`.
    """
    from mcp_tools.dependency_injection import get_wakapi_client

    logger.info(f"get_projects called with user={user}, q={q}")
    client = get_wakapi_client()

    try:
        projects = await client.get_projects(user=user, q=q)
        logger.info(f"get_projects result type: {type(projects)}")
        return projects
    except Exception as e:
        logger.error(f"Error in get_projects: {e}")
        raise ValueError(f"Failed to fetch projects: {e}") from e
