from dataclasses import dataclass
from typing import Optional
from enum import Enum
import base64
from pydantic import BaseModel
import httpx
import logging
from .core.exceptions import ApiError


class TimeRange(Enum):
    """Time range enum for stats queries."""

    TODAY = "today"
    YESTERDAY = "yesterday"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    SEVEN_DAYS = "7_days"
    LAST_SEVEN_DAYS = "last_7_days"
    THIRTY_DAYS = "30_days"
    LAST_THIRTY_DAYS = "last_30_days"
    SIX_MONTHS = "6_months"
    LAST_SIX_MONTHS = "last_6_months"
    TWELVE_MONTHS = "12_months"
    LAST_TWELVE_MONTHS = "last_12_months"
    LAST_YEAR = "last_year"
    ANY = "any"
    ALL_TIME = "all_time"


class HeartbeatEntry(BaseModel):
    """Model for heartbeat entry."""

    id: str
    project: str
    language: str
    entity: str
    time: float
    is_write: bool
    branch: Optional[str] = None
    category: Optional[str] = None
    cursorpos: Optional[int] = None
    line_additions: Optional[int] = None
    line_deletions: Optional[int] = None
    lineno: Optional[int] = None
    lines: Optional[int] = None
    type: Optional[str] = None
    user_agent_id: Optional[str] = None
    user_id: Optional[str] = None
    machine_name_id: Optional[str] = None
    created_at: Optional[str] = None


class HeartbeatsResult(BaseModel):
    """Model for heartbeats result."""

    data: list[HeartbeatEntry]
    start: str
    end: str
    timezone: str


class SummariesEntry(BaseModel):
    """Model for summaries entry."""

    name: str
    percent: float
    total_seconds: float
    text: str
    digital: str
    hours: int
    minutes: int
    seconds: Optional[int] = None


class StatsData(BaseModel):
    """Model for stats data."""

    total_seconds: float
    human_readable_total: str
    daily_average: float
    human_readable_daily_average: str
    languages: list[SummariesEntry]
    projects: list[SummariesEntry]
    editors: list[SummariesEntry]
    operating_systems: list[SummariesEntry]
    machines: list[SummariesEntry]
    range: str
    start: str
    end: str
    status: str
    is_coding_activity_visible: bool
    is_other_usage_visible: bool
    days_including_holidays: int
    user_id: str
    username: str
    branches: Optional[list[SummariesEntry]] = []
    categories: Optional[list[SummariesEntry]] = []
    human_readable_range: Optional[str] = None


class StatsViewModel(BaseModel):
    """Model for stats view."""

    data: StatsData


class AllTimeRange(BaseModel):
    """Model for all time range."""

    start: str
    start_date: str
    end: str
    end_date: str
    timezone: str


class AllTimeData(BaseModel):
    """Model for all time data."""

    total_seconds: float
    text: str
    is_up_to_date: bool
    range: AllTimeRange


class AllTimeViewModel(BaseModel):
    """Model for all time view."""

    data: AllTimeData


class LeadersLanguage(BaseModel):
    """Model for leaders language."""

    name: str
    total_seconds: float


class LeadersRunningTotal(BaseModel):
    """Model for leaders running total."""

    daily_average: float
    human_readable_daily_average: str
    human_readable_total: str
    languages: list[LeadersLanguage]
    total_seconds: float


class User(BaseModel):
    """Model for user."""

    id: str
    username: str
    display_name: str
    full_name: str
    email: str
    photo: str
    website: str
    timezone: str
    created_at: str
    modified_at: str
    last_heartbeat_at: str
    last_plugin_name: str
    last_project: str
    is_email_confirmed: bool
    is_email_public: bool


class LeadersCurrentUser(BaseModel):
    """Model for leaders current user."""

    page: int
    rank: int
    user: User


class LeadersEntry(BaseModel):
    """Model for leaders entry."""

    rank: int
    running_total: LeadersRunningTotal
    user: User


class LeadersRange(BaseModel):
    """Model for leaders range."""

    end_date: str
    end_text: str
    name: str
    start_date: str
    start_text: str
    text: str


class LeadersViewModel(BaseModel):
    """Model for leaders view."""

    current_user: Optional[LeadersCurrentUser] = None
    data: list[LeadersEntry]
    language: str
    page: int
    range: LeadersRange
    total_pages: int


class Project(BaseModel):
    """Model for project."""

    id: str
    name: str
    urlencoded_name: str
    created_at: str
    last_heartbeat_at: str
    human_readable_last_heartbeat_at: str


class ProjectsViewModel(BaseModel):
    """Model for projects view."""

    data: list[Project]


class ProjectViewModel(BaseModel):
    """Model for project view."""

    data: Project


class UserViewModel(BaseModel):
    """Model for user view."""

    data: User


class SummariesGrandTotal(BaseModel):
    """Model for summaries grand total."""

    digital: str
    hours: int
    minutes: int
    text: str
    total_seconds: float


class SummariesRange(BaseModel):
    """Model for summaries range."""

    date: str
    end: str
    start: str
    text: str
    timezone: str


class SummariesCumulativeTotal(BaseModel):
    """Model for summaries cumulative total."""

    decimal: str
    digital: str
    seconds: float
    text: str


class SummariesDailyAverage(BaseModel):
    """Model for summaries daily average."""

    days_including_holidays: int
    days_minus_holidays: int
    holidays: int
    seconds: int
    seconds_including_other_language: int
    text: str
    text_including_other_language: str


class SummariesData(BaseModel):
    """Model for summaries data."""

    branches: list[SummariesEntry] = []
    categories: list[SummariesEntry] = []
    dependencies: list[SummariesEntry] = []
    editors: list[SummariesEntry] = []
    entities: list[SummariesEntry] = []
    grand_total: SummariesGrandTotal
    languages: list[SummariesEntry] = []
    machines: list[SummariesEntry] = []
    operating_systems: list[SummariesEntry] = []
    projects: list[SummariesEntry] = []
    range: SummariesRange


class SummariesViewModel(BaseModel):
    """Model for summaries view."""

    cumulative_total: SummariesCumulativeTotal
    daily_average: SummariesDailyAverage
    data: list[SummariesData]
    end: str
    start: str


@dataclass
class WakapiConfig:
    """Wakapi configuration dataclass."""

    base_url: str
    api_key: str
    api_path: str = "/compat/wakatime/v1"

    def __post_init__(self):
        """Post init to ensure base_url ends with slash."""
        if not self.base_url.endswith("/"):
            self.base_url += "/"


class WakapiClient:
    """Wakapi API client."""

    def __init__(self, config: WakapiConfig) -> None:
        """Initialize Wakapi client with config."""
        self.config = config
        self.base_url = f"{config.base_url.rstrip('/')}/api"
        self.api_path = config.api_path
        self.client = httpx.AsyncClient(timeout=0.1)

    async def __aenter__(self):
        """Enter async context."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        await self.client.aclose()

    def _get_headers(self) -> dict[str, str]:
        encoded_token = base64.b64encode(self.config.api_key.encode()).decode()
        return {
            "Authorization": f"Basic {encoded_token}",
            "Content-Type": "application/json",
        }

    async def get_heartbeats(
        self,
        date: str,
        user: str = "current",
        project: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> HeartbeatsResult:
        """
        Get heartbeats of user for specified date.

        operationId: get-heartbeats
        summary: Get heartbeats of user for specified date
        tags: [heartbeat]
        parameters:
          - name: date
            in: query
            description: Date
            required: true
            schema:
              type: string
          - name: user
            in: path
            description: Username (or current)
            required: true
            schema:
              type: string
          - name: project
            in: query
            description: Project to filter by
            schema:
              type: string
          - name: limit
            in: query
            description: Limit number of heartbeats
            schema:
              type: integer
        responses:
          200:
            description: OK
            schema: v1.HeartbeatsResult
          400:
            description: bad date
            schema:
              type: string

        Requires ApiKeyAuth: Set header `Authorization` to your API Key
        encoded as Base64 and prefixed with `Basic`.
        """
        params = {"date": date}
        if project:
            params["project"] = project
        if limit:
            params["limit"] = limit
        url = f"{self.base_url}{self.api_path}/users/{user}/heartbeats"

        response = await self.client.get(
            url, params=params, headers=self._get_headers()
        )
        response.raise_for_status()

        json_data = response.json()
        if "error" in json_data:
            raise ValueError(json_data["error"])

        return HeartbeatsResult.model_validate(json_data)

    async def get_stats(
        self,
        range: str,
        user: str = "current",
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
              type: string
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
        params = {}
        if project:
            params["project"] = project
        if language:
            params["language"] = language
        if editor:
            params["editor"] = editor
        if operating_system:
            params["operating_system"] = operating_system
        if machine:
            params["machine"] = machine
        if label:
            params["label"] = label

        url = f"{self.base_url}{self.api_path}/users/{user}/stats/{range}"

        try:
            response = await self.client.get(
                url, params=params, headers=self._get_headers()
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ApiError(
                f"Wakapi API error in get_stats: {e.response.status_code} - "
                f"{e.response.text}",
                details={"status_code": e.response.status_code, "method": "get_stats"},
            ) from e

        json_data = response.json()
        logger = logging.getLogger(__name__)
        logger.debug(f"Stats API response: {json_data}")
        logger.debug("Calling real Wakapi API for get_stats")
        return StatsViewModel.model_validate(json_data)

    async def get_projects(
        self, user: str = "current", q: Optional[str] = None
    ) -> ProjectsViewModel:
        """
        Retrieve and filter the user's projects.

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
        params = {}
        if q:
            params["q"] = q

        url = f"{self.base_url}{self.api_path}/users/{user}/projects"

        logger = logging.getLogger(__name__)
        logger.debug("Calling real Wakapi API for get_projects")
        try:
            response = await self.client.get(
                url, params=params, headers=self._get_headers()
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ApiError(
                f"Wakapi API error in get_projects: {e.response.status_code} - "
                f"{e.response.text}",
                details={
                    "status_code": e.response.status_code,
                    "method": "get_projects",
                },
            ) from e

        json_data = response.json()
        return ProjectsViewModel.model_validate(json_data)

    async def get_leaders(self) -> LeadersViewModel:
        """
        List of users ranked by coding activity in descending order.

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
        url = f"{self.base_url}{self.api_path}/leaders"

        logger = logging.getLogger(__name__)
        logger.debug("Calling real Wakapi API for get_leaders")
        try:
            response = await self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ApiError(
                f"Wakapi API error in get_leaders: {e.response.status_code} - "
                f"{e.response.text}",
                details={
                    "status_code": e.response.status_code,
                    "method": "get_leaders",
                },
            ) from e

        json_data = response.json()
        return LeadersViewModel.model_validate(json_data)

    async def get_user(self, user: str = "current") -> UserViewModel:
        """
        Retrieve the given user.

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
        url = f"{self.base_url}{self.api_path}/users/{user}"

        logger = logging.getLogger(__name__)
        logger.debug("Calling real Wakapi API for get_user")
        try:
            response = await self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ApiError(
                f"Wakapi API error in get_user: {e.response.status_code} - "
                f"{e.response.text}",
                details={"status_code": e.response.status_code, "method": "get_user"},
            ) from e

        json_data = response.json()
        return UserViewModel.model_validate(json_data)

    async def get_all_time_since_today(self, user: str = "current") -> AllTimeViewModel:
        """
        Retrieve summary for all time since today for the specified user.

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
        url = f"{self.base_url}{self.api_path}/users/{user}/all_time_since_today"

        logger = logging.getLogger(__name__)
        logger.debug("Calling real Wakapi API for get_all_time_since_today")
        try:
            response = await self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ApiError(
                f"Wakapi API error in get_all_time_since_today: "
                f"{e.response.status_code} - {e.response.text}",
                details={
                    "status_code": e.response.status_code,
                    "method": "get_all_time_since_today",
                },
            ) from e

        json_data = response.json()
        return AllTimeViewModel.model_validate(json_data)

    async def get_project_detail(
        self, user: str = "current", id: Optional[str] = None
    ) -> ProjectViewModel:
        """
        Retrieve a single project.

        operationId: get-wakatime-project
        summary: Retrieve a single project
        description: Mimics undocumented endpoint related to https://wakatime.com/developers#projects
        tags: [wakatime]
        parameters:
          - name: user
            in: path
            description: User ID to fetch data for (or 'current')
            required: true
            schema:
              type: string
          - name: id
            in: path
            description: Project ID to fetch
            required: true
            schema:
              type: string
        responses:
          200:
            description: OK
            schema: v1.ProjectViewModel

        Requires ApiKeyAuth: Set header `Authorization` to your API Key
        encoded as Base64 and prefixed with `Basic`.
        """
        if not id:
            raise ValueError("Project ID is required")
        url = f"{self.base_url}{self.api_path}/users/{user}/projects/{id}"

        logger = logging.getLogger(__name__)
        logger.debug("Calling real Wakapi API for get_project_detail")
        try:
            response = await self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ApiError(
                f"Wakapi API error in get_project_detail: {e.response.status_code} - "
                f"{e.response.text}",
                details={
                    "status_code": e.response.status_code,
                    "method": "get_project_detail",
                },
            ) from e

        json_data = response.json()
        return ProjectViewModel.model_validate(json_data)


    async def get_summaries(
        self,
        user: str = "current",
        range_: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        project: Optional[str] = None,
        language: Optional[str] = None,
        editor: Optional[str] = None,
        operating_system: Optional[str] = None,
        machine: Optional[str] = None,
        label: Optional[str] = None,
    ) -> SummariesViewModel:
        """
        Retrieve WakaTime-compatible summaries.

        operationId: get-wakatime-summaries
        summary: Retrieve WakaTime-compatible summaries
        description: Mimics https://wakatime.com/developers#summaries.
        tags: [wakatime]
        parameters:
          - name: user
            in: path
            description: User ID to fetch data for (or 'current')
            required: true
            schema:
              type: string
          - name: range
            in: query
            description: Range interval identifier
            schema:
              type: string
              enum: [
                  "today", "yesterday", "week", "month", "year", "7_days",
                  "last_7_days", "30_days", "last_30_days", "6_months",
                  "last_6_months", "12_months", "last_12_months", "last_year",
                  "any", "all_time"
              ]
          - name: start
            in: query
            description: Start date (e.g. '2021-02-07')
            schema:
              type: string
          - name: end
            in: query
            description: End date (e.g. '2021-02-08')
            schema:
              type: string
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
              type: string
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
            schema: v1.SummariesViewModel

        Requires ApiKeyAuth: Set header `Authorization` to your API Key
        encoded as Base64 and prefixed with `Basic`.
        """
        params = {}
        if range_:
            params["range"] = range_
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if project:
            params["project"] = project
        if language:
            params["language"] = language
        if editor:
            params["editor"] = editor
        if operating_system:
            params["operating_system"] = operating_system
        if machine:
            params["machine"] = machine
        if label:
            params["label"] = label

        url = f"{self.base_url}{self.api_path}/users/{user}/summaries"

        logger = logging.getLogger(__name__)
        logger.debug("Calling real Wakapi API for get_summaries")
        try:
            response = await self.client.get(
                url, params=params, headers=self._get_headers()
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ApiError(
                f"Wakapi API error in get_summaries: {e.response.status_code} - "
                f"{e.response.text}",
                details={
                    "status_code": e.response.status_code,
                    "method": "get_summaries",
                },
            ) from e

        json_data = response.json()
        return SummariesViewModel.model_validate(json_data)
