"""Wakapi Leaders tool."""

from mcp_server import app
from wakapi_sdk.client import LeadersViewModel


@app.tool
async def get_leaders() -> LeadersViewModel:
    """List of users ranked by coding activity in descending order.

    operationId: get-wakatime-leaders
    summary: List of users ranked by coding activity in descending order.
    description: Mimics https://wakatime.com/developers#leaders
    tags: [wakatime]
    responses:
      200:
        description: OK
        schema: v1.LeadersViewModel

    Requires ApiKeyAuth: Set header `Authorization` to your API Key
    encoded as Base64 and prefixed with `Basic`.
    """
    from mcp_tools.dependency_injection import get_wakapi_client

    client = get_wakapi_client()

    try:
        return await client.get_leaders()
    except Exception as e:
        raise ValueError(f"Failed to fetch leaders: {e}") from e
