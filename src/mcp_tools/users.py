"""Wakapi Users tool."""

from mcp_server import app
from wakapi_sdk.client import UserViewModel


@app.tool
async def get_user(user: str = "current") -> UserViewModel:
    """Retrieve the given user.

    operationId: get-wakatime-user
    summary: Retrieve the given user
    description: Mimics https://wakatime.com/developers#users
    tags: [wakatime]
    parameters:
      - name: user
        in: path
        description: User ID to fetch (or 'current')
        required: true
        schema:
          type: string
    responses:
      200:
        description: OK
        schema: v1.UserViewModel

    Requires ApiKeyAuth: Set header `Authorization` to your API Key
    encoded as Base64 and prefixed with `Basic`.
    """
    from mcp_tools.dependency_injection import get_wakapi_client

    client = get_wakapi_client()

    try:
        user_model: UserViewModel = await client.get_user(user=user)
        return user_model
    except Exception as e:
        raise ValueError(f"Failed to fetch user: {e}") from e
