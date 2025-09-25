from fastmcp.client import Client


class MCPTestClient:
    """Test wrapper for MCP ClientSession to simplify tool calls."""

    def __init__(self, uri):
        """Initialize the test client."""
        self.uri = uri

    async def __aenter__(self):
        """Enter the async context."""
        self.session = Client(self.uri)
        await self.session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context."""
        await self.session.__aexit__(exc_type, exc_val, exc_tb)

    async def call_tool(self, name, args):
        """Simplified tool call."""
        result = await self.session.call_tool(name, arguments=args)
        return result

    async def list_tools(self):
        """List available tools."""
        return await self.session.list_tools()
