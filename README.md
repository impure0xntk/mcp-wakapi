# Wakapi MCP Server

This is an MCP (Model Context Protocol) server. It provides development time tracking tools by collecting logs from Wakapi REST API.

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

### Get Stats

Retrieve statistics for a given user over a specified time range.

Parameters:

- `user`: User ID to fetch data for (or 'current')
- `range`: Range interval identifier
- `project` (optional): Project to filter by
- `language` (optional): Language to filter by
- `editor` (optional): Editor to filter by
- `operating_system` (optional): OS to filter by
- `machine` (optional): Machine to filter by
- `label` (optional): Project label to filter by

### Get Projects

Retrieve and filter the user projects.

Parameters:

- `user`: User ID to fetch data for (or 'current')
- `q` (optional): Query to filter projects by

### Get User

Retrieve the given user information.

Parameters:

- `user`: User ID to fetch (or 'current')

### Get Leaders

Retrieve leaderboard information.

Parameters:

- `user`: User ID to fetch data for (or 'current')
- `range`: Range interval identifier
- `language` (optional): Language to filter by

### Get All Time Since Today

Retrieve all time information since today.

Parameters:

- `user`: User ID to fetch data for (or 'current')

### Get Project Detail

Retrieve detailed information about a specific project.

Parameters:

- `user`: User ID to fetch data for (or 'current')
- `project`: Project name to fetch details for

### Get Recent Logs

Retrieve recent development logs.

Parameters:

- `user`: User ID to fetch data for (or 'current')
- `limit` (optional): Number of logs to return (default: 100)

### Test Connection

Test connection to the Wakapi server.

No parameters required.

## Installation

### Prerequisites

- Python 3.11 or higher
- Wakapi server with API access

### Using Nix Environment (Recommended)

This project provides a reproducible development environment using Nix flakes:

```bash
# Start the development environment
nix develop

# Or start a shell
nix-shell
```

### Manual Installation

1. Clone this repository
2. Install dependencies using uv:
   ```bash
   uv sync
   ```

## Configuration

This server can be configured using several methods:

### Environment Variables

The most common way to configure the server is through environment variables:

```bash
export WAKAPI_URL="http://your-wakapi-server:3000"
export WAKAPI_API_KEY="your_actual_api_key_here"
export WAKAPI_API_PATH="/compat/wakatime/v1"
```

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


## Usage

### Starting the MCP Server

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

## Testing

You can test the server using pytest:

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_mcp_server.py -v
```

## License

MIT License

## Contributing

Issues and Pull Requests are welcome.
