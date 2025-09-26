"""Configuration management class for Wakapi MCP server."""

import os
import json
import toml
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass

from .exceptions import ConfigurationError


@dataclass
class WakapiConfig:
    """Wakapi configuration data class."""

    url: str
    api_key: str
    timeout: int = 30
    retry_count: int = 3


@dataclass
class ServerConfig:
    """Server configuration data class."""

    host: str = "0.0.0.0"
    port: int = 8000


@dataclass
class LoggingConfig:
    """Logging configuration data class."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class ConfigManager:
    """Configuration manager class."""

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Singleton constructor."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the config manager."""
        if self._initialized:
            return
        self.config_path = config_path
        self._wakapi_config: Optional[WakapiConfig] = None
        self._server_config: Optional[ServerConfig] = None
        self._logging_config: Optional[LoggingConfig] = None
        self._load_config()
        self._initialized = True

    def _load_config(self):
        """Load configuration."""
        config_data = {}

        # Load from configuration file
        if self.config_path and self.config_path.exists():
            config_data = self._load_from_file(self.config_path)

        # Configuration validation and application
        self._validate_and_apply_config(config_data)

    def _load_from_file(self, config_path: Path) -> dict[str, Any]:
        """Load configuration from file."""
        try:
            if config_path.suffix.lower() == ".json":
                with open(config_path, encoding="utf-8") as f:
                    return json.load(f)
            elif config_path.suffix.lower() == ".toml":
                return toml.load(config_path)
            else:
                # Unsupported file format
                return {}
        except (json.JSONDecodeError, toml.TomlDecodeError) as e:
            raise ConfigurationError(f"Invalid configuration file format: {e}") from e
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration file: {e}") from e

        config_data = {}
        # Map environment variables to configuration data
        for key in ["WAKAPI_URL", "WAKAPI_API_KEY", "DEBUG"]:
            value = os.getenv(key)
            if value is not None:
                config_data[key] = value

        return config_data

    def _validate_and_apply_config(self, config_data: dict[str, Any]):
        """Validate and apply configuration."""
        # Flatten nested structure from TOML file
        flat_config = self._flatten_config(config_data)

        # Wakapi configuration (standard TOML key mapping)
        wakapi_url = (
            flat_config.get("WAKAPI_URL")
            or flat_config.get("WAKAPI_CONNECTION_URL")
            or os.getenv("WAKAPI_URL", "http://localhost:3000")
        )
        api_key = (
            flat_config.get("WAKAPI_API_KEY")
            or flat_config.get("WAKAPI_AUTH_API_KEY")
            or os.getenv("WAKAPI_API_KEY", "")
        )

        # Validate required settings (with more detailed error messages)
        missing_keys = []
        validation_errors = []

        if not wakapi_url or wakapi_url.strip() == "":
            validation_errors.append(
                "WAKAPI_URL is required. Default: http://localhost:3000"
            )
        elif not wakapi_url.startswith(("http://", "https://")):
            validation_errors.append("WAKAPI_URL must be a valid URL format")

        if not api_key or api_key.strip() == "":
            missing_keys.append("WAKAPI_API_KEY")
            validation_errors.append(
                "WAKAPI_API_KEY is required. Please check your Wakapi API key settings"
            )
        # Relax API key length validation (UUID format check is optional)
        elif len(api_key.strip()) < 3:  # Minimum 3 characters
            validation_errors.append(
                "WAKAPI_API_KEY is too short. Please verify it is a valid API key"
            )

        if missing_keys or validation_errors:
            error_msg = "Configuration validation error:\n" + "\n".join(
                validation_errors
            )
            if missing_keys:
                error_msg += "\n\nConfig method:\n- Create .env file:\n"
                error_msg += "WAKAPI_URL=http://your-wakapi-server:3000\n"
                error_msg += "WAKAPI_API_KEY=your-api-key\n"
                error_msg += "\n- Copy .env.example"
            raise ConfigurationError(error_msg)

        self._wakapi_config = WakapiConfig(
            url=wakapi_url.strip(),
            api_key=api_key.strip(),
            timeout=int(
                flat_config.get(
                    "WAKAPI_TIMEOUT", flat_config.get("WAKAPI_CONNECTION_TIMEOUT", 30)
                )
            ),
            retry_count=int(
                flat_config.get(
                    "WAKAPI_RETRY_COUNT",
                    flat_config.get("WAKAPI_CONNECTION_RETRY_COUNT", 3),
                )
            ),
        )

        # Server configuration
        self._server_config = ServerConfig(
            host=flat_config.get("SERVER_HOST")
            or flat_config.get("SERVER_NETWORK_HOST", "0.0.0.0"),
            port=int(
                flat_config.get(
                    "SERVER_PORT", flat_config.get("SERVER_NETWORK_PORT", 8000)
                )
            ),
        )

        # Logging configuration
        self._logging_config = LoggingConfig(
            level=flat_config.get("LOG_LEVEL", "INFO"),
            format=flat_config.get(
                "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            ),
        )

        # Log successful configuration loading
        print(f"INFO: Configuration loaded successfully - URL: {wakapi_url}")

    def get_wakapi_config(self) -> WakapiConfig:
        """Get Wakapi configuration."""
        if self._wakapi_config is None:
            raise ConfigurationError("Wakapi configuration has not been initialized")
        return self._wakapi_config

    def get_server_config(self) -> ServerConfig:
        """Get server configuration."""
        if self._server_config is None:
            return ServerConfig()
        return self._server_config

    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration."""
        if self._logging_config is None:
            return LoggingConfig()
        return self._logging_config

    def _flatten_config(self, config_data: dict[str, Any]) -> dict[str, Any]:
        """Convert nested configuration to a flat dictionary."""
        flat_config = {}

        def _flatten(prefix: str, data: Any):
            if isinstance(data, dict):
                for key, value in data.items():
                    new_prefix = f"{prefix}_{key}" if prefix else key
                    _flatten(new_prefix.upper(), value)
            elif isinstance(data, list):
                # Lists are not supported
                pass
            else:
                flat_config[prefix] = data

        _flatten("", config_data)
        return flat_config
