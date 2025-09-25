"""Wakapi recent logs retrieval tool."""

from datetime import datetime, timedelta
from typing import Any, Optional

from mcp_server import app
from mcp_tools.dependency_injection import get_wakapi_client


@app.tool
async def get_recent_logs(
    user: str = "current",
    project_name: Optional[str] = None,
    days: int = 7,
    limit: int = 1000,
) -> list[dict[str, Any]]:
    """Get heartbeats of user for recent days (extension of heartbeats GET).

    Mimics https://wakatime.com/api/v1/users/{user}/heartbeats for multiple days.

    Requires ApiKeyAuth: Set header `Authorization` to your API Key encoded as Base64
    and prefixed with `Basic`.

    Args:
        user (str, required, default="current"): Username (or current).
        project_name (str, optional): Filter by project.
        days (int, default=7): Number of days to retrieve.
        limit (int, default=1000): Maximum number of heartbeats.

    Returns:
        List of HeartbeatEntry: Each with id (str), project (str), language (str),
        entity (str), time (number), is_write (bool), branch (str), category (str),
        cursorpos (int), line_additions (int), line_deletions (int), lineno (int),
        lines (int), type (str), user_agent_id (str), user_id (str),
        machine_name_id (str), created_at (str).
        Sorted by time descending.
    """
    client = get_wakapi_client()

    end_date = datetime.now()
    all_logs = []

    current_date = end_date.date()
    for i in range(days):
        day_date = current_date - timedelta(days=i)
        try:
            day_logs = await client.get_heartbeats(
                user=user,
                date=day_date,
                project=project_name,
                limit=limit // days + 1 if days > 0 else limit,
            )
            all_logs.extend(day_logs.data if hasattr(day_logs, "data") else day_logs)
        except Exception as e:
            raise ValueError(f"Failed to fetch recent logs: {e}") from e

    # Sort by time descending
    all_logs.sort(key=lambda log: log.time, reverse=True)

    # Limit total results
    all_logs = all_logs[:limit]

    # Convert to dict
    return [
        {
            "id": log.id,
            "project": log.project,
            "language": log.language,
            "entity": log.entity,
            "time": log.time.timestamp()
            if isinstance(log.time, datetime)
            else log.time,
            "is_write": log.is_write,
            "branch": log.branch,
            "category": getattr(log, "category", None),
            "cursorpos": getattr(log, "cursorpos", None),
            "line_additions": getattr(log, "line_additions", None),
            "line_deletions": getattr(log, "line_deletions", None),
            "lineno": getattr(log, "lineno", None),
            "lines": getattr(log, "lines", None),
            "type": log.type,
            "user_agent_id": getattr(log, "user_agent_id", None),
            "user_id": log.user_id,
            "machine_name_id": getattr(log, "machine_name_id", None),
            "created_at": log.time.isoformat()
            if isinstance(log.time, datetime)
            else None,
        }
        for log in all_logs
    ]
