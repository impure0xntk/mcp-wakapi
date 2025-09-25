import pytest
import asyncio
from unittest.mock import patch, AsyncMock

from mcp_server import app

from wakapi_sdk.client import ProjectsViewModel, Project, ProjectViewModel


class TestProjects:
    """Tests for get_projects"""

    @pytest.mark.asyncio
    async def test_projects_success(self, mock_wakapi_client):
        """Successfully retrieves project list"""
        with patch(
            "mcp_tools.dependency_injection.get_wakapi_client",
            return_value=mock_wakapi_client,
        ):
            tool = await app.get_tool("get_projects")
            result = await tool.run({"user": "current"})

            assert len(result.structured_content["data"]) == 1
            assert result.structured_content["data"][0]["name"] == "test_project"
            mock_wakapi_client.get_projects.assert_called_once_with(
                user="current", q=None
            )

    @pytest.mark.asyncio
    async def test_projects_with_query_empty(self, mock_wakapi_client):
        """Empty response with query filter"""
        empty_projects = []
        with patch(
            "mcp_tools.dependency_injection.get_wakapi_client",
            return_value=mock_wakapi_client,
        ):
            with patch.object(
                mock_wakapi_client, "get_projects", new_callable=AsyncMock
            ) as mock_get_projects:
                mock_get_projects.return_value = ProjectsViewModel(data=empty_projects)
                tool = await app.get_tool("get_projects")
                result = await tool.run({"user": "current", "q": "nonexistent"})
                assert len(result.structured_content["data"]) == 0

    @pytest.mark.asyncio
    async def test_projects_timeout(self, mock_wakapi_client):
        """Timeout"""
        with patch(
            "mcp_tools.dependency_injection.get_wakapi_client",
            return_value=mock_wakapi_client,
        ):
            with patch.object(
                mock_wakapi_client, "get_projects", new_callable=AsyncMock
            ) as mock_get_projects:
                mock_get_projects.side_effect = asyncio.TimeoutError()
                tool = await app.get_tool("get_projects")
                with pytest.raises(ValueError):
                    await tool.run({"user": "current"})

    @pytest.mark.asyncio
    async def test_project_detail_success(self, mock_wakapi_client):
        """Successfully retrieves project detail"""
        from mcp_tools.dependency_injection import register_wakapi_client, get_injector

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

        # Register mock client with dependency injection system
        register_wakapi_client(mock_wakapi_client)

        mock_wakapi_client.get_project_detail = AsyncMock(
            return_value=mock_project_detail
        )

        tool = await app.get_tool("get_project_detail")
        result = await tool.run({"id": "1"})

        assert result.structured_content["data"]["id"] == "1"
        assert result.structured_content["data"]["name"] == "test_project"
        mock_wakapi_client.get_project_detail.assert_called_once_with(
            id="1", user="current"
        )

        # Clean up: clear the injector for other tests
        get_injector().clear()

    @pytest.mark.asyncio
    async def test_project_detail_empty(self, mock_wakapi_client):
        """Error response when project not found"""
        from mcp_tools.dependency_injection import register_wakapi_client, get_injector

        # Register mock client with dependency injection system
        register_wakapi_client(mock_wakapi_client)

        mock_wakapi_client.get_project_detail = AsyncMock(
            side_effect=Exception("Project not found")
        )
        tool = await app.get_tool("get_project_detail")
        with pytest.raises(ValueError, match=r"Failed to fetch project detail"):
            await tool.run({"id": "999"})
        mock_wakapi_client.get_project_detail.assert_called_once_with(
            id="999", user="current"
        )

        # Clean up: clear the injector for other tests
        get_injector().clear()

    @pytest.mark.asyncio
    async def test_project_detail_timeout(self, mock_wakapi_client):
        """Timeout"""
        from mcp_tools.dependency_injection import register_wakapi_client, get_injector

        # Register mock client with dependency injection system
        register_wakapi_client(mock_wakapi_client)

        mock_wakapi_client.get_project_detail = AsyncMock(
            side_effect=asyncio.TimeoutError()
        )
        tool = await app.get_tool("get_project_detail")
        with pytest.raises(ValueError, match=r"Failed to fetch project detail"):
            await tool.run({"id": "1"})
        mock_wakapi_client.get_project_detail.assert_called_once_with(
            id="1", user="current"
        )

        # Clean up: clear the injector for other tests
        get_injector().clear()
