"""Data model classes for Wakapi MCP server."""

from dataclasses import dataclass
from typing import Optional, Any
from datetime import datetime, date


@dataclass
class WakapiLog:
    """Wakapi log data model."""

    id: str
    user_id: str
    project_name: str
    language: str
    editor: str
    operating_system: str
    machine: str
    entity: str
    type: str
    time: datetime
    data: dict[str, Any]
    branch: Optional[str] = None
    is_write: bool = False


@dataclass
class WakapiStats:
    """Wakapi statistics data model."""

    total_time: float
    total_count: int
    languages: dict[str, int]
    projects: dict[str, int]
    editors: dict[str, int] = None
    operating_systems: dict[str, int] = None
    machines: dict[str, int] = None


@dataclass
class WakapiUser:
    """Wakapi user data model."""

    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None


@dataclass
class WakapiSummary:
    """Wakapi summary data model."""

    date: date
    total_time: float
    total_count: int


@dataclass
class WakapiLeader:
    """Wakapi leaderboard data model."""

    username: str
    total_seconds: int


@dataclass
class WakapiProject:
    """Wakapi project data model."""

    id: str
    name: str
    color: Optional[str] = None


@dataclass
class WakapiAllTime:
    """Wakapi all-time statistics data model."""

    total_seconds: int
    total_days: int
