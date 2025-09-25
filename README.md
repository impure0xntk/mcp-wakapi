# MCP Server for Wakapi

This is an MCP (Model Context Protocol) server that collects logs using Wakapi's REST API.

## Features

- Collects development time logs via the Wakapi API
- Provides multiple MCP tools (log retrieval, statistics retrieval, project/language list retrieval)
- Fast processing using FastMCP
- Reproducible development environment with Nix flakes
- Modular tool architecture
- Improved testability through dependency injection
- Design based on the single responsibility principle

## Functions

### Provided Tools

1. **get_logs** - Retrieve log data from Wakapi
2. **get_stats** - Retrieve statistics
3. **get_projects** - Retrieve list of available projects
4. **get_languages** - Retrieve list of available languages
5. **get_recent_logs** - Retrieve recent logs
6. **test_connection** - Test connection to Wakapi server

## Environment Setup

### Required Environment Variables

Copy `.env.example` to `.env` and enter the required settings.

```bash
cp .env.example .env
# Edit .env to set actual values
# WAKAPI_URL=http://your-wakapi-server:3000
# WAKAPI_API_KEY=your_actual_api_key_here
```

**Note**: The API key is used as a Base64-encoded Bearer token. Set the Wakapi API key directly.

### Development Environment Setup

1. Clone this repository
2. Start the development environment using Nix flakes

```bash
# Start the development environment
nix develop

# Or start a shell
nix-shell
```

### Dependency Installation

When the development environment is started, the following dependencies are automatically installed:

- httpx - HTTP client
- fastmcp - MCP server framework
- pydantic - Data validation
- python-dotenv - Environment variable management

## Usage

### Starting the MCP Server

```bash
# Set environment variables
export WAKAPI_URL="http://localhost:3000"
export WAKAPI_API_KEY="your_actual_api_key_here"

# Start the server in STDIO mode (default)
python main.py --transport stdio

# Start the server in SSE (HTTP) mode
python main.py --transport sse --port 8001
```

**Authentication Method**: The API key is automatically Base64-encoded and sent as a Bearer token.

- `--transport stdio`: Uses STDIO transport (default). Can be used directly with MCP clients like opencode.
- `--transport sse --port 8001`: Uses SSE (HTTP) transport. Accessible via browser or HTTP clients (e.g., <http://localhost:8001>).

### Usage Examples for Each Tool

#### Output Format

All tools return data in JSON-compatible object array format. In case of errors, an object containing error information is returned.

#### 1. Retrieving Logs

```python
# Retrieve logs for the last 7 days (object array format)
logs = await get_recent_logs(days=7, limit=100)
# Return value: [{"id": "...", "project": "...", "language": "...", "editor": "...", ...}, ...]

# Retrieve logs for a specific period
logs = await get_logs(
    start_date="2024-01-01T00:00:00",
    end_date="2024-01-31T23:59:59",
    project_name="my-project"
)
# Return value: Array of log objects
```

#### 2. Retrieving Statistics

```python
# Today's statistics (single object format)
stats = await get_stats(time_range="daily")
# Return value: {"total_time": 3600, "total_count": 100, "languages": {...}, ...}

# Weekly statistics for a specific project
stats = await get_stats(
    project_name="my-project",
    time_range="weekly"
)
# Return value: Statistics object
```

#### 3. Retrieving Project List

```python
# Project list (object array format)
projects = await get_projects()
print("Available projects:", projects)
# Return value: [{"name": "project1", ...}, {"name": "project2", ...}, ...]
```

#### 4. Retrieving Language List

```python
# Language list (object array format)
languages = await get_languages()
print("Available languages:", languages)
# Return value: [{"name": "Python", ...}, {"name": "JavaScript", ...}, ...]
```

### Verifying Operation with MCP Inspector

You can verify the server's operation using MCP Inspector.

#### 1. Start in SSE Mode

```bash
# Start the server in SSE mode
python main.py --transport sse --port 8001
```

#### 2. Start MCP Inspector

```bash
# Install MCP Inspector (if not installed)
npm install -g @modelcontextprotocol/inspector

# Connect to the server with MCP Inspector
mcp-inspector --transport sse http://localhost:8001
```

#### 3. Verification Steps

1. Once MCP Inspector starts, check the tool list
2. Select each tool and set parameters
3. Click the execute button to check the results
4. Confirm that the response is returned in the correct format (object array)

#### 4. Connection Test Example

```bash
# Use the connection test tool
mcp-inspector --transport sse http://localhost:8001 --tool test_connection

# Test retrieving project list
mcp-inspector --transport sse http://localhost:8001 --tool get_projects
```

MCP Inspector allows interactive testing of all tools and inspection of request/response details.

## API Endpoints

### Wakapi API Specifications

This server uses the following Wakapi API endpoints:

- `GET /api/users/current/data` - Retrieve log data
- `GET /api/users/current/stats` - Retrieve statistics
- `GET /api/users/current/projects` - Retrieve project list
- `GET /api/users/current/languages` - Retrieve language list

## Structure

```
mcp-wakapi/
├── src/
│   ├── __init__.py
│   ├── wakapi_client.py        # Wakapi API client
│   └── mcp_server.py           # MCP server main
├── mcp_wakapi/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration management class
│   │   ├── exceptions.py       # Exception classes
│   │   └── models.py           # Data models
│   └── tools/
│       ├── __init__.py         # Tool module exports
│       ├── base.py             # Base tool class
│       ├── dependency_injection.py # Dependency injection system
│       ├── registry.py         # Tool registry
│       ├── logs.py             # Log retrieval tool
│       ├── stats.py            # Statistics retrieval tool
│       ├── projects.py         # Project retrieval tool
│       ├── languages.py        # Language retrieval tool
│       ├── recent_logs.py      # Recent log retrieval tool
│       └── connection.py       # Connection test tool
├── tests/
│   ├── test_mcp_server.py      # MCP server tests
│   ├── test_tools.py           # Tool class tests
│   ├── test_dependency_injection.py # DI tests
│   ├── test_tool_registry.py   # Tool registry tests
│   └── test_wakapi_client.py   # Wakapi client tests
├── main.py                     # Entry point
├── pyproject.toml             # Python project settings
├── flake.nix                 # Nix flakes settings
├── .env.example              # Environment variable sample
└── README.md                 # This file
```

## Development

### Local Execution

```bash
# Start the development environment
nix develop

# Start the server
python main.py
```

### Testing

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_tools.py -v
pytest tests/test_dependency_injection.py -v
pytest tests/test_tool_registry.py -v
```

### New Architecture

The new modular architecture implemented in Stage 2:

1. **Base Tool Class** (`mcp_wakapi/tools/base.py`) - Base class for all tools
2. **Dependency Injection System** (`mcp_wakapi/tools/dependency_injection.py`) - Injection of configuration and client
3. **Tool Registry** (`mcp_wakapi/tools/registry.py`) - Tool registration and management
4. **Individual Tool Modules** - Independent classes for each function

#### Benefits

- **Testability**: Each tool class can be tested independently
- **Single Responsibility Principle**: Each class has a single responsibility
- **Dependency Injection**: Dependencies for configuration and client are injected externally
- **Extensibility**: Easy to add new tools
- **Backward Compatibility**: Introduces new architecture while maintaining existing APIs

## Stage 3: Unified Error Handling

In Stage 3, the error handling system was significantly improved.

### Main Improvements

1. **Extended Exception Classes**
   - `WakapiError`: Base exception class (supports error codes, HTTP status, details)
   - `ConfigurationError`: Configuration-related errors (HTTP 400)
   - `AuthenticationError`: Authentication errors (HTTP 401)
   - `ApiError`: API call errors (HTTP 400)
   - `ValidationError`: Data validation errors (HTTP 400)
   - `NetworkError`: Network errors (HTTP 503)
   - `ToolExecutionError`: Tool execution errors (HTTP 400)
   - `NotFoundError`: Resource not found errors (HTTP 404)
   - `PermissionError`: Permission errors (HTTP 403)

2. **Global Exception Handler**
   - Unified error handling via FastMCP middleware
   - All exceptions returned as unified JSON responses
   - Automatic HTTP status code setting

3. **Structured Logging**
   - JSON-formatted structured logs using `structlog`
   - Logs detailed information (error codes, context, stack traces) on errors
   - Standardized log output for success and errors

4. **Unified Error Response Format**

    ```json
    {
      "error": true,
      "message": "Error message",
      "code": 1300,
      "http_status": 400,
      "timestamp": "2024-01-15T10:30:00Z",
      "details": {
        "field": "invalid_value",
        "context": "additional_info"
      }
    }
    ```

### Benefits of Error Handling

- **Consistency**: All errors are handled in the same format
- **Ease of Debugging**: Easy problem identification with structured logs
- **Client Compatibility**: Easy client-side implementation with unified JSON responses
- **Extensibility**: Easy to add new error types
- **Monitoring Support**: Easy integration with log analysis tools via structured logs

### Testing

In Stage 3, comprehensive test cases were also added:

```bash
# Run error handling tests
pytest tests/test_error_handling.py -v
```

These tests verify the following:

- Operation of each exception class
- Operation of the logging system
- Error handling for each tool
- Operation of the global exception handler
- Uniformity of error response format

## License

MIT License

## Contributing

Issues and Pull Requests are welcome.

## Dependencies

### Production Dependencies (pyproject.toml)

- fastmcp >=0.1.0 - MCP server framework
- httpx >=0.25.0 - HTTP client
- pydantic >=2.0.0 - Data validation and configuration management
- python-dotenv >=1.0.0 - Environment variable management
- toml >=0.10.0 - TOML configuration file parsing
- structlog >=24.2.0 - Structured logging

### Development Dependencies (pyproject.toml optional-dependencies.dev)

- pytest >=7.0.0 - Test framework
- pytest-asyncio >=0.21.0 - Async test support
- black >=23.0.0 - Code formatter
- ruff >=0.1.0 - Linter and formatter

### Nix Environment (flake.nix)

The Nix development environment automatically includes the above Python packages and can be used in conjunction with uv for dependency management.

## Stage 4: Dependency Organization

In Stage 4, dependencies in pyproject.toml and flake.nix were integrated and organized.

### Main Changes

- **Duplicate Dependency Integration**: Resolved duplicates for httpx, pydantic, python-dotenv, toml, pytest, pytest-asyncio
- **Removal of Unnecessary Dependencies**: Removed pip from flake.nix
- **Structlog Organization**: Removed development duplicates and unified as production dependency
- **Unified Version Constraints**: Specified all minimum versions in pyproject.toml
- **Clear Separation of Production/Development**: Separated production and development dependencies

### Setup Methods

1. **Using Nix Environment**:

    ```bash
    nix develop
    ```

2. **Using uv**:

    ```bash
    uv sync
    ```

3. **Running Tests**:

    ```bash
    pytest
    ```

This simplifies dependency maintenance, improving reproducibility and consistency.

## Related Projects

- [Wakapi](https://wakapi.xyz/) - Time tracking tool
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) - Communication protocol between AI models and tools
