import sys
from pathlib import Path
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, date

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wakapi_sdk.core.config import ConfigManager
from wakapi_sdk.core.models import WakapiSummary
from wakapi_sdk.client import (
    StatsViewModel,
    StatsData,
    SummariesEntry,
    ProjectsViewModel,
    Project,
    LeadersViewModel,
    LeadersEntry,
    LeadersRunningTotal,
    LeadersLanguage,
    User,
    LeadersRange,
    UserViewModel,
    AllTimeViewModel,
    AllTimeData,
    AllTimeRange,
    ProjectViewModel,
    UserAgentsViewModel,
    UserAgentEntry,
    HeartbeatEntry,
    HeartbeatsResult,
)

from mcp_tools.dependency_injection import (
    register_config_manager,
    register_wakapi_client,
)

# Import tool modules to trigger registration


@pytest.fixture(autouse=True)
def register_tools():
    """Register tools using the same flow as main.py"""
    # Add root directory to path to import from main.py
    import sys
    from pathlib import Path

    root_path = Path(__file__).parent.parent.parent
    if str(root_path) not in sys.path:
        sys.path.insert(0, str(root_path))

    from main import initialize_tools

    initialize_tools()


@pytest.fixture(autouse=True)
def setup_config_manager(mock_config_manager, mock_wakapi_client):
    """Register mock config manager and client automatically for all tests"""
    register_config_manager(mock_config_manager)
    register_wakapi_client(mock_wakapi_client)
    yield
    # Optional cleanup if needed


@pytest.fixture
def mock_config_manager():
    """Mock config manager"""
    mock_manager = MagicMock(spec=ConfigManager)
    mock_wakapi_config = MagicMock()
    mock_wakapi_config.url = "http://localhost:3000"
    mock_wakapi_config.api_key = "test_api_key"
    mock_manager.get_wakapi_config.return_value = mock_wakapi_config
    return mock_manager


@pytest.fixture
def mock_wakapi_client():
    """Mock Wakapi client"""
    mock_client = MagicMock()

    # Add config attribute
    mock_config = MagicMock()
    mock_config.api_key = "test_api_key"
    mock_config.base_url = "http://localhost:3000"
    mock_client.config = mock_config

    # Mock heartbeats data
    mock_heartbeats_data = HeartbeatsResult(
        data=[
            HeartbeatEntry(
                id="1",
                project="test_project",
                language="Python",
                entity="test.py",
                time=datetime.now().timestamp(),
                is_write=True,
                branch="main",
                category=None,
                cursorpos=None,
                line_additions=None,
                line_deletions=None,
                lineno=None,
                lines=None,
                type="file",
                user_agent_id=None,
                user_id="current",
                machine_name_id=None,
                created_at=None,
            )
        ],
        start="2023-01-01",
        end="2023-01-01",
        timezone="UTC",
    )

    # Mock statistics data
    mock_stats = StatsViewModel(
        data=StatsData(
            total_seconds=3600.0,
            human_readable_total="1h 0m",
            daily_average=3600.0,
            human_readable_daily_average="1h 0m",
            languages=[
                SummariesEntry(
                    name="Python",
                    percent=100.0,
                    total_seconds=3600.0,
                    text="1h 0m",
                    digital="1:00",
                    hours=1,
                    minutes=0,
                )
            ],
            projects=[
                SummariesEntry(
                    name="test_project",
                    percent=100.0,
                    total_seconds=3600.0,
                    text="1h 0m",
                    digital="1:00",
                    hours=1,
                    minutes=0,
                )
            ],
            editors=[],
            operating_systems=[],
            machines=[],
            range="daily",
            start="2023-01-01",
            end="2023-01-01",
            status="OK",
            is_coding_activity_visible=True,
            is_other_usage_visible=True,
            days_including_holidays=1,
            user_id="current",
            username="testuser",
        )
    )

    # Mock project list
    mock_projects = ProjectsViewModel(
        data=[
            Project(
                id="1",
                name="test_project",
                urlencoded_name="test_project",
                created_at="2023-01-01",
                last_heartbeat_at="2023-01-01",
                human_readable_last_heartbeat_at="1 day ago",
            )
        ]
    )

    # Mock user
    mock_user = UserViewModel(
        data=User(
            id="1",
            username="testuser",
            display_name="Test User",
            full_name="Test User",
            email="test@example.com",
            photo="",
            website="",
            timezone="UTC",
            created_at="2023-01-01",
            modified_at="2023-01-01",
            last_heartbeat_at="2023-01-01",
            last_plugin_name="",
            last_project="",
            is_email_confirmed=True,
            is_email_public=False,
        )
    )

    # Mock leaders
    mock_leaders = LeadersViewModel(
        data=[
            LeadersEntry(
                rank=1,
                running_total=LeadersRunningTotal(
                    daily_average=7200.0,
                    human_readable_daily_average="2h 0m",
                    human_readable_total="2h 0m",
                    languages=[LeadersLanguage(name="Python", total_seconds=7200.0)],
                    total_seconds=7200.0,
                ),
                user=User(
                    id="1",
                    username="leader1",
                    display_name="Leader 1",
                    full_name="Leader 1",
                    email="leader1@example.com",
                    photo="",
                    website="",
                    timezone="UTC",
                    created_at="2023-01-01",
                    modified_at="2023-01-01",
                    last_heartbeat_at="2023-01-01",
                    last_plugin_name="",
                    last_project="",
                    is_email_confirmed=True,
                    is_email_public=False,
                ),
            ),
            LeadersEntry(
                rank=2,
                running_total=LeadersRunningTotal(
                    daily_average=5400.0,
                    human_readable_daily_average="1h 30m",
                    human_readable_total="1h 30m",
                    languages=[
                        LeadersLanguage(name="JavaScript", total_seconds=5400.0)
                    ],
                    total_seconds=5400.0,
                ),
                user=User(
                    id="2",
                    username="leader2",
                    display_name="Leader 2",
                    full_name="Leader 2",
                    email="leader2@example.com",
                    photo="",
                    website="",
                    timezone="UTC",
                    created_at="2023-01-01",
                    modified_at="2023-01-01",
                    last_heartbeat_at="2023-01-01",
                    last_plugin_name="",
                    last_project="",
                    is_email_confirmed=True,
                    is_email_public=False,
                ),
            ),
        ],
        language="all",
        page=1,
        range=LeadersRange(
            end_date="2023-01-01",
            end_text="Jan 1st, 2023",
            name="last_7_days",
            start_date="2022-12-25",
            start_text="Dec 25th, 2022",
            text="Last 7 days",
        ),
        total_pages=1,
    )

    # Mock all-time statistics
    mock_all_time = AllTimeViewModel(
        data=AllTimeData(
            total_seconds=100000.0,
            text="1 day 3h 46m",
            is_up_to_date=True,
            range=AllTimeRange(
                start="2023-01-01",
                start_date="2023-01-01",
                end="2023-01-01",
                end_date="2023-01-01",
                timezone="UTC",
            ),
        )
    )

    # Mock project detail
    mock_project_detail = ProjectViewModel(
        data=Project(
            id="1",
            name="test_project",
            urlencoded_name="test_project",
            created_at="2023-01-01",
            last_heartbeat_at="2023-01-01",
            human_readable_last_heartbeat_at="1 day ago",
        )
    )

    # Mock user agents
    mock_user_agents = UserAgentsViewModel(
        data=[
            UserAgentEntry(
                editor="VSCode",
                first_seen="2023-01-01",
                id="1",
                is_browser_extension=False,
                is_desktop_app=True,
                last_seen="2023-01-01",
                os="Linux",
                value="VSCode",
                version="1.85.0",
            ),
            UserAgentEntry(
                editor="Chrome",
                first_seen="2023-01-01",
                id="2",
                is_browser_extension=True,
                is_desktop_app=False,
                last_seen="2023-01-01",
                os="Linux",
                value="Chrome",
                version="120.0.0",
            ),
        ],
        total_pages=1,
    )

    # Mock summaries
    mock_summaries = [
        WakapiSummary(date=date(2024, 1, 1), total_time=3600, total_count=100)
    ]

    mock_client.get_heartbeats = AsyncMock(return_value=mock_heartbeats_data)
    mock_client.get_stats = AsyncMock(return_value=mock_stats)
    mock_client.get_projects = AsyncMock(return_value=mock_projects)
    mock_client.get_user = AsyncMock(return_value=mock_user)
    mock_client.get_leaders = AsyncMock(return_value=mock_leaders)
    mock_client.get_all_time_since_today = AsyncMock(return_value=mock_all_time)
    mock_client.get_project_detail = AsyncMock(return_value=mock_project_detail)
    mock_client.get_user_agents = AsyncMock(return_value=mock_user_agents)
    mock_client.get_summaries = AsyncMock(return_value=mock_summaries)
    mock_client.post_heartbeat = AsyncMock(
        return_value=HeartbeatEntry(
            id="posted",
            project="test_project",
            language="Python",
            entity="test.py",
            time=datetime.now().timestamp(),
            is_write=True,
            branch="main",
            category=None,
            cursorpos=None,
            line_additions=None,
            line_deletions=None,
            lineno=None,
            lines=None,
            type="file",
            user_agent_id=None,
            user_id="current",
            machine_name_id=None,
            created_at=None,
        )
    )

    # For connection test
    mock_client.test_connection = AsyncMock(return_value=True)

    return mock_client
