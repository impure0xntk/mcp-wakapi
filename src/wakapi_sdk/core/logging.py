"""
Structured logging system for Wakapi MCP server.

Unified logging implementation using structlog.
"""

import structlog
from typing import Any, Optional
import os


class LoggingConfig:
    """Logging configuration class."""

    def __init__(self) -> None:
        """Initialize the logging configuration."""
        self.level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.format = os.getenv("LOG_FORMAT", "json").lower()
        self.processors = self._get_processors()
        self.logger = self._create_logger()

    def _get_processors(self) -> list:
        """Set up processor chain."""
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
        ]

        if self.format == "pretty":
            processors.extend(
                [
                    structlog.dev.ConsoleRenderer(),
                ]
            )
        else:
            processors.extend(
                [
                    structlog.processors.KeyValueRenderer(),
                ]
            )

        return processors

    def _create_logger(self) -> None:
        """Create structured logger."""
        return structlog.configure(
            processors=self.processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

    def get_logger(
        self, logger_name: str = "wakapi_mcp"
    ) -> structlog.stdlib.BoundLogger:
        """Get named logger."""
        return structlog.get_logger(logger_name)

    def get_configured_level(self) -> str:
        """Return current log level."""
        return self.level


# Global logging configuration
logging_config = LoggingConfig()


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """
    Get logger for the application.

    Args:
        name: Logger name (default if None).

    Returns:
        Structured logger.
    """
    if name is None:
        name = "wakapi_mcp"
    return logging_config.get_logger(name)


def setup_logging(
    level: Optional[str] = None, format_type: Optional[str] = None
) -> None:
    """
    Update logging configuration.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR).
        format_type: Output format (json, pretty).
    """
    global logging_config

    if level:
        os.environ["LOG_LEVEL"] = level
    if format_type:
        os.environ["LOG_FORMAT"] = format_type

    # Reinitialize configuration
    logging_config = LoggingConfig()


# Utility functions
def log_error(
    logger: structlog.stdlib.BoundLogger,
    message: str,
    error_type: str = "unknown",
    error_code: Optional[int] = None,
    details: Optional[dict[str, Any]] = None,
    exc_info: bool = False,
):
    """
    Output error log in structured format.

    Args:
        logger: Logger instance.
        message: Error message.
        error_type: Error type.
        error_code: Error code.
        details: Additional details.
        exc_info: Include exception info.
    """
    event_dict = {
        "error_type": error_type,
        "message": message,
    }

    if error_code:
        event_dict["error_code"] = error_code
    if details:
        event_dict.update(details)

    # Remove explicit event= to avoid duplicate event keys
    logger.error(**event_dict, exc_info=exc_info)


def log_info(
    logger: structlog.stdlib.BoundLogger,
    message: str,
    operation: str = "unknown",
    details: Optional[dict[str, Any]] = None,
):
    """
    Output info log.

    Args:
        logger: Logger instance.
        message: Message.
        operation: Executed operation.
        details: Additional details.
    """
    event_dict = {
        "event": "info",
        "operation": operation,
        "message": message,
    }

    if details:
        event_dict.update(details)

    # Remove explicit event= to avoid duplicate event keys
    event_dict.pop("event", None)
    logger.info(**event_dict)


def log_warning(
    logger: structlog.stdlib.BoundLogger,
    message: str,
    warning_type: str = "general",
    details: Optional[dict[str, Any]] = None,
):
    """
    Output warning log.

    Args:
        logger: Logger instance.
        message: Message.
        warning_type: Warning type.
        details: Additional details.
    """
    event_dict = {
        "event": "warning",
        "warning_type": warning_type,
        "message": message,
    }

    if details:
        event_dict.update(details)

    logger.warning(event=event_dict["event"], **event_dict)


def log_debug(
    logger: structlog.stdlib.BoundLogger,
    message: str,
    debug_info: str = "general",
    details: Optional[dict[str, Any]] = None,
):
    """
    Output debug log.

    Args:
        logger: Logger instance.
        message: Message.
        debug_info: Debug info type.
        details: Additional details.
    """
    event_dict = {
        "event": "debug",
        "debug_info": debug_info,
        "message": message,
    }

    if details:
        event_dict.update(details)

    logger.debug(event=event_dict["event"], **event_dict)


# Initialization log
if __name__ == "__main__":
    logger = get_logger()
    log_info(logger, "Structured logging system has been initialized", "system_init")
    print(
        "Logging configuration:",
        {"level": logging_config.level, "format": logging_config.format},
    )
