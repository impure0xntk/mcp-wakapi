"""Wakapi All Time tool."""

from mcp_server import app
from wakapi_sdk.client import AllTimeViewModel


@app.tool
async def get_all_time_since_today(user: str = "current") -> AllTimeViewModel:
    """Retrieve summary for all time since today for the specified user.

    operationId: get-all-time
    summary: Retrieve summary for all time
    description: Mimics https://wakatime.com/developers#all_time_since_today
    tags: [wakatime]
    parameters:
      - name: user
        in: path
        description: User ID to fetch data for (or 'current')
        required: true
        schema:
          type: string
    responses:
      200:
        description: OK
        schema: v1.AllTimeViewModel

    Requires ApiKeyAuth: Set header `Authorization` to your API Key
    encoded as Base64 and prefixed with `Basic`.
    """
    from mcp_tools.dependency_injection import get_wakapi_client

    client = get_wakapi_client()

    try:
        model: AllTimeViewModel = await client.get_all_time_since_today(user=user)
        return model
    except Exception as e:
        raise ValueError(f"Failed to fetch all time stats: {e}") from e
