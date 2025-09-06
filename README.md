
# Weather MCP Server

A Model Context Protocol (MCP) server providing weather data from the National Weather Service API.

## Features

- **Weather Alerts**: Get active alerts for any US state
- **Weather Forecasts**: Get detailed forecasts by coordinates
- MCP-compatible for AI assistant integration
- Server-Sent Events (SSE) transport mode
- Production-ready deployment on IBM Cloud Code Engine

## Quick Start

### Prerequisites
- Python 3.11+
- `uv` package manager

### Installation
```bash
git clone https://github.com/dmonisankar/weather-mcp-python.git
cd weather-mcp-python

# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Run Locally
```bash
# Run the MCP server (SSE transport)
uv run weather.py
```

The server will start on port 8000 with SSE transport and provide:
- SSE endpoint at `/sse` for MCP protocol communication

## Available Tools

### get_alerts
Get active weather alerts for a US state.
- **Parameter**: `state` (string) - Two-letter state code (e.g., "CA", "NY")

### get_forecast  
Get weather forecast for specific coordinates.
- **Parameters**: 
  - `latitude` (float) - Location latitude
  - `longitude` (float) - Location longitude

## Deployment

### IBM Cloud Code Engine
Deploy to production using IBM Cloud Code Engine with Docker containers and SSE transport.

**Quick Deploy:**
```bash
# Build and push container
docker build -t us.icr.io/YOUR_NAMESPACE/weather-mcp-python:latest .
docker push us.icr.io/YOUR_NAMESPACE/weather-mcp-python:latest

# Deploy to Code Engine
ibmcloud ce app create \
  --name weather-mcp-server \
  --image us.icr.io/YOUR_NAMESPACE/weather-mcp-python:latest \
  --port 8000
```

See `DEPLOYMENT.md` for complete step-by-step instructions.

## Testing

Use [MCP Inspector](https://github.com/modelcontextprotocol/inspector) to test:
```bash
npm install -g @modelcontextprotocol/inspector
mcp-inspector
```

Connect to your deployed server's SSE endpoint: `https://your-app-url/sse`

## Architecture

- **Framework**: FastMCP for simplified MCP server development
- **API**: National Weather Service REST API
- **Transport**: Server-Sent Events (SSE) only
- **Deployment**: Containerized with Docker, hosted on IBM Cloud Code Engine



### Transport Modes

- **SSE**: For production deployment on Code Engine and web-based access

## API Reference

The application uses the [National Weather Service API](https://www.weather.gov/documentation/services-web-api) to fetch weather data.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements

- National Weather Service for providing the weather data API
- MCP framework for enabling AI tool integration
- Documentation on Model context protocol: https://modelcontextprotocol.io/quickstart/server#test-with-commands
- Original code taken from https://github.com/jpan8866/mcp-weather.git 
