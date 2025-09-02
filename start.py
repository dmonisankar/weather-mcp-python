import os

def main():
    """
    Startup script that can handle both SSE server mode (for Code Engine)
    and stdio mode (for local MCP development).
    """
    
    if os.environ.get('CE_SERVICES') or os.environ.get('CODE_ENGINE'):
        # Running in IBM Code Engine - start SSE server with health endpoints
        print("Starting Weather MCP server in SSE mode for Code Engine")
        from sse_server import run_server
        run_server()
    else:
        # Running locally - use stdio mode for MCP protocol
        print("Starting Weather MCP server in stdio mode")
        from weather import mcp
        mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
