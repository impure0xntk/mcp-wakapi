"""Configuration management class for Wakapi MCP server."""

import configparser
import json
import logging
import os
import re
import shlex
import subprocess
import toml
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass

from .exceptions import ConfigurationError

logger = logging.getLogger(__name__)


@dataclass
class WakapiConfig:
    """Wakapi configuration data class."""

    url: str
    api_key: str
    api_path: str = "/compat/wakatime/v1"
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

    def __init__(
        self,
        config_path: Optional[Path] = None,
        wakatime_config_path: Optional[Path] = None,
    ):
        """Initialize the config manager."""
        if self._initialized:
            return
        self.config_path = config_path
        self.wakatime_config_path = wakatime_config_path
        self._wakapi_config: Optional[WakapiConfig] = None
        self._server_config: Optional[ServerConfig] = None
        self._logging_config: Optional[LoggingConfig] = None
        self._load_config()
        self._initialized = True

    @classmethod
    def _reset_instance(cls) -> None:
        """Clear the cached singleton so the next construction re-reads config.

        Tests need this because the singleton would otherwise keep serving the
        config parsed for whichever temporary file was created first.
        """
        cls._instance = None
        cls._initialized = False

    def _load_config(self):
        """Load configuration."""
        config_data = {}

        # Load from configuration file
        if self.config_path and self.config_path.exists():
            config_data = self._load_from_file(self.config_path)

        # WakaTime-compatible config is the lowest-precedence source
        wakatime_data: dict[str, Any] = {}
        if self.wakatime_config_path and self.wakatime_config_path.exists():
            wakatime_data = self._load_from_wakatime_config(self.wakatime_config_path)

        # Configuration validation and application
        self._validate_and_apply_config(config_data, wakatime_data)

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
        for key in ["WAKAPI_URL", "WAKAPI_API_KEY", "WAKAPI_API_PATH", "DEBUG"]:
            value = os.getenv(key)
            if value is not None:
                config_data[key] = value

        return config_data

    def _load_from_wakatime_config(self, wakatime_config_path: Path) -> dict[str, Any]:
        """Read WakaTime-compatible ``~/.wakatime.cfg`` into env-style keys.

        The result is kept separate from the config file and applied as defaults
        so the priority order cannot depend on dictionary insertion order.
        """
        parser = configparser.ConfigParser()
        try:
            if not parser.read(wakatime_config_path):
                return {}
            settings = parser["settings"] if parser.has_section("settings") else {}
        except configparser.Error as e:
            raise ConfigurationError(
                f"Failed to load WakaTime config file: {e}"
            ) from e

        data: dict[str, Any] = {}
        if settings.get("api_url"):
            data["WAKAPI_URL"] = self._strip_api_suffix(settings["api_url"])

        api_key = self._resolve_wakatime_api_key(settings)
        if api_key:
            data["WAKAPI_API_KEY"] = api_key

        return data

    @staticmethod
    def _strip_api_suffix(api_url: str) -> str:
        """Drop a trailing ``/api`` so the base server URL is kept.

        WakaTime configs point at a full API endpoint; this SDK appends the
        compatibility path itself.
        """
        return re.sub(r"/api/?$", "", api_url.strip().rstrip("/"))

    def _resolve_wakatime_api_key(self, settings: Any) -> str:
        """Resolve the API key, preferring the vault command when present."""
        vault_cmd = settings.get("api_key_vault_cmd")
        if vault_cmd:
            try:
                key = self._run_vault_command(vault_cmd)
            except (OSError, subprocess.SubprocessError):
                key = ""
            if key:
                return key
        return settings.get("api_key", "").strip()

    @staticmethod
    def _run_vault_command(vault_cmd: str) -> str:
        """Execute the configured vault command and return the key it prints."""
        result = subprocess.run(
            shlex.split(vault_cmd),
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip()

    def _check_duplicate_config(self, config_data: dict[str, Any]) -> None:
        """Warn when several sources set the same key.

        Duplicates are no longer an error: WakaTime configs commonly sit next to
        a dedicated config file, and the precedence rules resolve them cleanly.
        """
        keys = {"WAKAPI_URL", "WAKAPI_API_KEY"}
        present = sorted(k for k in keys if config_data.get(k))
        if len(present) > 1 and os.getenv("WAKAPI_DEBUG"):
            logger.debug("Config keys set more than once, precedence applied: %s", present)

    def _validate_and_apply_config(
        self,
        config_data: dict[str, Any],
        wakatime_data: Optional[dict[str, Any]] = None,
    ):
        """Validate and apply configuration."""
        # WakaTime defaults are applied first so the config file always wins,
        # independent of the order the keys happened to be inserted.
        flat_config = {**(wakatime_data or {}), **self._flatten_config(config_data)}
        self._check_duplicate_config(flat_config)

        # Wakapi configuration (standard TOML key mapping)
        # Environment variables win so deployments can override a baked-in file.
        wakapi_url = (
            os.getenv("WAKAPI_URL")
            or flat_config.get("WAKAPI_URL")
            or flat_config.get("WAKAPI_CONNECTION_URL")
            or "http://localhost:3000"
        )
        api_key = (
            os.getenv("WAKAPI_API_KEY")
            or flat_config.get("WAKAPI_API_KEY")
            or flat_config.get("WAKAPI_AUTH_API_KEY")
            or ""
        )
        api_path = (
            os.getenv("WAKAPI_API_PATH")
            or flat_config.get("WAKAPI_API_PATH")
            or "/compat/wakatime/v1"
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
                error_msg += r"""

Config methods:

- Set environment variables:
WAKAPI_URL=http://your-wakapi-server:3000
WAKAPI_API_KEY=your-api-key

- Or, set config.json or toml and set file path to --config option.
```toml
[wakapi]
url = "http://localhost:3000"
api_key = "your-api-key"
```

"""
            raise ConfigurationError(error_msg)

        self._wakapi_config = WakapiConfig(
            url=wakapi_url.strip(),
            api_key=api_key.strip(),
            api_path=api_path.strip(),
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
        print(f"INFO: API Path: {api_path}")

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
