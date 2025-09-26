# Wakapi SDK

This is a Python SDK for interacting with the Wakapi API.

## Installation

```bash
pip install wakapi_sdk
```

## Usage

```python
from wakapi_sdk import WakapiClient, WakapiConfig

config = WakapiConfig(base_url="https://wakapi.example.com", api_key="your_api_key", api_path="/compat/wakatime/v1")
client = WakapiClient(config)

# Get stats
stats = await client.get_stats("last_7_days")
print(stats)
```

## Development

To install dependencies:

```bash
uv sync
```

To run tests:

```bash
pytest
```

## License

Apache License 2.0