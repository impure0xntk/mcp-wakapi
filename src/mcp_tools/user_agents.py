"""Wakapi User Agents tool."""

from typing import Any
from mcp_server import app
from mcp_tools.dependency_injection import get_wakapi_client


@app.tool
async def get_user_agents(user: str) -> dict[str, Any]:
    """Retrieve the list of unique user agents for the given user.

    Parameters:
        user (str) - User ID (or 'current').

    Returns:
        List[UserAgentEntry] - List of user agent entries.
    """
    client = get_wakapi_client()

    try:
        result = await client.get_user_agents(user=user)
        return {
            "data": [entry.model_dump() for entry in (result.data if result else [])],
            "total_pages": result.total_pages if result else 0,
        }
    except Exception as e:
        raise ValueError(f"Failed to fetch user agents: {e}") from e
