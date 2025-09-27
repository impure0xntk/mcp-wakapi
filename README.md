# Wakapi MCP Server

This is an MCP (Model Context Protocol) server. It provides development time tracking tools by collecting logs from Wakapi REST API.
This repository is unofficial. Use at your own risk.

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Wakapi server with API access

### Configuration

The most common way to configure the server is through environment variables:

```bash
export WAKAPI_URL="http://your-wakapi-server:3000"
export WAKAPI_API_KEY="your_actual_api_key_here"
export WAKAPI_API_PATH="/compat/wakatime/v1"
```

### MCP Server Configuration Examples

#### Quickstart with Environment Variables

```json
{
  "mcpServers": {
    "wakapi": {
      "env": {
        "WAKAPI_URL": "http://localhost:3000",
        "WAKAPI_API_KEY": "your-api-key"
      },
      "command": "uv",
      "args": [
        "tool",
        "run",
        "--from",
        "git+https://github.com/impure0xntk/mcp-wakapi",
        "wakapi-mcp"
      ]
    }
  }
}
```

#### Enhanced Security with Configuration File

```json
{
  "mcpServers": {
    "wakapi": {
      "command": "uv",
      "args": [
        "tool",
        "run",
        "--from",
        "git+https://github.com/impure0xntk/mcp-wakapi",
        "wakapi-mcp",
        "--config",
        "/path/to/config.toml"
      ]
    }
  }
}
```

## Features

- Collects development time logs via the Wakapi API
- Provides MCP tools for retrieving development data
- Fast processing using FastMCP
- Reproducible development environment with Nix flakes
- Modular tool architecture
- Improved testability through dependency injection
- Design based on the single responsibility principle

## Provided Tools

This server provides the following tools that can be used by MCP-compatible clients:
Note: {api_path} is configurable: by default, `/compat/wakatime/v1`.
Please see [the Configuration](#configuration-details) section.

| Tool Name | Description | API Endpoint |
|-----------|-------------|------------|
| Get Stats | Retrieve statistics for a given user over a specified time range | [GET {api_path}/users/{user}/stats/{range}](https://wakapi.dev/swagger-ui/swagger-ui/index.html#/wakatime/get-wakatimes-tats) |
| Get Projects | Retrieve and filter the user projects | [GET {api_path}/users/{user}/projects](https://wakapi.dev/swagger-ui/swagger-ui/index.html#/wakatime/get-wakatime-projects) |
| Get User | Retrieve the given user information | [GET {api_path}/users/{user}](https://wakapi.dev/swagger-ui/swagger-ui/index.html#/wakatime/get-wakatime-user) |
| Get Leaders | Retrieve leaderboard information | [GET {api_path}/leaders](https://wakapi.dev/swagger-ui/swagger-ui/index.html#/wakatime/get-wakatime-leaders) |
| Get All Time Since Today | Retrieve all time information since today | [GET {api_path}/users/{user}/all_time_since_today](https://wakapi.dev/swagger-ui/swagger-ui/index.html#/wakatime/get-all-time) |
| Get Project Detail | Retrieve detailed information about a specific project | [GET {api_path}/users/{user}/projects/{id}](https://wakapi.dev/swagger-ui/swagger-ui/index.html#/wakatime/get-wakatime-project) |
| Get Recent Logs | Retrieve recent development logs | [GET {api_path}/users/{user}/heartbeats](https://wakapi.dev/swagger-ui/swagger-ui/index.html#/heartbeat/get-heartbeats) |
| Test Connection | Test connection to the Wakapi server | None |

## Configuration Details

### Configuration Files

You can also use configuration files in TOML or JSON format:

**TOML format (config.toml):**

```toml
[wakapi]
url = "http://your-wakapi-server:3000"
api_key = "your_actual_api_key_here"
api_path = "/compat/wakatime/v1"
timeout = 30
retry_count = 3

[server]
host = "0.0.0.0"
port = 8000

[logging]
level = "INFO"
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

**JSON format (config.json):**

```json
{
  "wakapi": {
    "url": "http://your-wakapi-server:3000",
    "api_key": "your_actual_api_key_here",
    "api_path": "/compat/wakatime/v1",
    "timeout": 30,
    "retry_count": 3
  },
  "server": {
    "host": "0.0.0.0",
    "port": 8000
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

## For Developers

### Setup Development Environment

#### Using Nix Environment (Recommended)

This project provides a reproducible development environment using Nix flakes:

```bash
# Start the development environment
nix develop

# Or start a shell
nix-shell
```

#### Manual Installation

1. Clone this repository
2. Install dependencies using uv:

   ```bash
   uv sync
   ```

### Starting the MCP Server from python command

```bash
# Set environment variables
export WAKAPI_URL="http://localhost:3000"
export WAKAPI_API_KEY="your_actual_api_key_here"
export WAKAPI_API_PATH="/compat/wakatime/v1"

# Start the server in STDIO mode (default)
python main.py --transport stdio

# Start the server in SSE (HTTP) mode
python main.py --transport sse --port 8001

# Start with a configuration file
python main.py --config /path/to/config.toml
```

**Authentication Method**: The API key is automatically base64-encoded and sent as a Bearer token.

- `--transport stdio`: Uses STDIO transport (default). Can be used directly with MCP clients like opencode
- `--transport sse --port 8001`: Uses SSE (HTTP) transport. Accessible via browser or HTTP

### Testing

You can test the server using pytest:

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_mcp_server.py -v
```

## License

Apache License 2.0

## Contributing

Issues and Pull Requests are welcome.
