from fastmcp import FastMCP

mcp = FastMCP("AddressServer", "Returns dummy addresses")

@mcp.tool()
def get_address(name: str) -> str:
    return f"{name} lives at 123 Main Street, Springfield"

if __name__ == "__main__":
    # Run in Streamable HTTP mode
    mcp.run(transport="http", host="0.0.0.0", port=8000)
