"""Wakapi statistics retrieval tool."""

from typing import Optional

from mcp_server import app
from wakapi_sdk.client import StatsViewModel


@app.tool
async def get_stats(
    user: str,
    range: str,
    project: Optional[str] = None,
    language: Optional[str] = None,
    editor: Optional[str] = None,
    operating_system: Optional[str] = None,
    machine: Optional[str] = None,
    label: Optional[str] = None,
) -> StatsViewModel:
    """
    Retrieve statistics for a given user.

    operationId: get-wakatime-stats
    summary: Retrieve statistics for a given user
    description: Mimics https://wakatime.com/developers#stats
    tags: [wakatime]
    parameters:
      - name: user
        in: path
        description: User ID to fetch data for (or 'current')
        required: true
        schema:
          type: string
      - name: range
        in: path
        description: Range interval identifier
        required: true
        schema:
          type: string
          enum: [
              "today", "yesterday", "week", "month", "year", "7_days",
              "last_7_days", "30_days", "last_30_days", "6_months",
              "last_6_months", "12_months", "last_12_months", "last_year",
              "any", "all_time"
          ]
      - name: project
        in: query
        description: Project to filter by
        schema:
          type: string
      - name: language
        in: query
        description: Language to filter by
        schema:
          type: string
      - name: editor
        in: query
        description: Editor to filter by
        schema:
          type: string
      - name: operating_system
        in: query
        description: OS to filter by
        schema:
          type: str
      - name: machine
        in: query
        description: Machine to filter by
        schema:
          type: string
      - name: label
        in: query
        description: Project label to filter by
        schema:
          type: string
    responses:
      200:
        description: OK
        schema: v1.StatsViewModel

    Requires ApiKeyAuth: Set header `Authorization` to your API Key
    encoded as Base64 and prefixed with `Basic`.
    """
    from mcp_tools.dependency_injection import get_wakapi_client

    client = get_wakapi_client()

    try:
        stats_data: StatsViewModel = await client.get_stats(
            range=range,
            user=user,
            project=project,
            language=language,
            editor=editor,
            operating_system=operating_system,
            machine=machine,
            label=label,
        )
        return stats_data
    except Exception as e:
        raise ValueError(f"Failed to fetch stats: {e}") from e
