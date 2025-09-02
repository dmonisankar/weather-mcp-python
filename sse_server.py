"""
SSE Server wrapper for Weather MCP with health and info endpoints
"""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from weather import mcp
import asyncio
from typing import AsyncGenerator

# Create FastAPI app
app = FastAPI(title="Weather MCP Server")

@app.get("/health")
async def health():
    """Health check endpoint"""
    return JSONResponse({"status": "healthy", "service": "weather-mcp"})

@app.get("/")
async def info():
    """Service info endpoint"""
    return JSONResponse({
        "name": "Weather MCP Server",
        "version": "0.1.0",
        "description": "MCP server providing weather information via NWS API",
        "transport": "sse",
        "endpoints": {
            "health": "/health",
            "info": "/",
            "sse": "/sse"
        }
    })

@app.get("/sse")
async def sse_endpoint():
    """SSE endpoint for MCP protocol"""
    async def event_generator() -> AsyncGenerator[str, None]:
        # Send initial connection message
        yield f"data: {{\"type\": \"connection\", \"status\": \"connected\"}}\n\n"
        
        # Keep connection alive with heartbeat
        while True:
            await asyncio.sleep(30)
            yield f"data: {{\"type\": \"heartbeat\"}}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )

# Mount the MCP app if it has ASGI interface
# Note: This requires FastMCP to expose an ASGI app when in SSE mode
# If FastMCP doesn't provide this, we'll need a different approach

def run_server():
    """Run the SSE server"""
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Starting Weather MCP SSE server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_server()