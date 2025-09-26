"""Dependency injection system for Wakapi MCP server."""

from typing import Any, Optional
from wakapi_sdk.core.config import ConfigManager
from wakapi_sdk.client import WakapiClient, WakapiConfig


class DependencyInjector:
    """Dependency injection class."""

    def __init__(self) -> None:
        """Initialize the dependency injector."""
        self._dependencies: dict[str, Any] = {}
        self._config_manager: Optional[ConfigManager] = None
        self._wakapi_client: Optional[WakapiClient] = None

    def register_config_manager(self, config_manager: ConfigManager) -> None:
        """Register config manager."""
        self._config_manager = config_manager
        self._dependencies["config_manager"] = config_manager

    def register_wakapi_client(self, wakapi_client: WakapiClient) -> None:
        """Register Wakapi client."""
        self._wakapi_client = wakapi_client
        self._dependencies["wakapi_client"] = wakapi_client

    def create_wakapi_client(self) -> WakapiClient:
        """Create Wakapi client."""
        if self._wakapi_client is not None:
            return self._wakapi_client

        if self._config_manager is None:
            raise ValueError("ConfigManager has not been registered")

        wakapi_config = self._config_manager.get_wakapi_config()

        return WakapiClient(
            WakapiConfig(
                base_url=wakapi_config.url,
                api_key=wakapi_config.api_key,
                api_path=wakapi_config.api_path,
            )
        )

    def get_config_manager(self) -> ConfigManager:
        """Get config manager."""
        if self._config_manager is None:
            raise ValueError("ConfigManager has not been registered")
        return self._config_manager

    def get_wakapi_client(self) -> WakapiClient:
        """Get Wakapi client."""
        if self._wakapi_client is None:
            self._wakapi_client = self.create_wakapi_client()
        return self._wakapi_client

    def inject(self, tool_class) -> Any:
        """
        Create instance by injecting dependencies into tool class.

        Args:
            tool_class: Tool class to inject.

        Returns:
            Tool instance with injected dependencies.
        """
        if self._config_manager is None:
            raise ValueError("ConfigManager has not been registered")

        # Check constructor signature of the tool class
        import inspect

        signature = inspect.signature(tool_class.__init__)

        # Collect required dependencies
        dependencies = {}
        for param_name in signature.parameters:
            if param_name == "self":
                continue
            if param_name in self._dependencies:
                dependencies[param_name] = self._dependencies[param_name]
            elif param_name == "config_manager":
                dependencies[param_name] = self.get_config_manager()
            elif param_name == "wakapi_client":
                dependencies[param_name] = self.get_wakapi_client()

        return tool_class(**dependencies)

    def clear(self) -> None:
        """Clear all dependencies."""
        self._dependencies.clear()
        self._config_manager = None
        self._wakapi_client = None


# Global dependency injection instance
_injector = DependencyInjector()


def get_injector() -> DependencyInjector:
    """Get global dependency injection instance."""
    return _injector


def get_wakapi_client() -> WakapiClient:
    """Get global Wakapi client."""
    return _injector.get_wakapi_client()


def register_config_manager(config_manager: ConfigManager) -> None:
    """Register config manager globally."""
    _injector.register_config_manager(config_manager)


def register_wakapi_client(wakapi_client: WakapiClient) -> None:
    """Register Wakapi client globally."""
    _injector.register_wakapi_client(wakapi_client)


def inject_dependencies(tool_class) -> Any:
    """Create tool instance by injecting dependencies."""
    return _injector.inject(tool_class)
