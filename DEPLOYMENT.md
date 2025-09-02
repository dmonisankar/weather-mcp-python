# IBM Cloud Code Engine Deployment Guide

This comprehensive guide provides detailed step-by-step instructions for deploying the Weather MCP Server to IBM Cloud Code Engine.

## Prerequisites

Before starting the deployment, ensure you have:

1. **IBM Cloud Account**: [Sign up here](https://cloud.ibm.com/registration) if you don't have one
2. **Docker Desktop**: [Download here](https://www.docker.com/products/docker-desktop/)
3. **IBM Cloud CLI**: Will be installed in Step 1
4. **Local development environment** with:
   - Python 3.11+
   - Git
   - A terminal/command prompt

## Step 1: Install IBM Cloud CLI

### macOS/Linux
```bash
curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
```

### Windows (PowerShell as Administrator)
```powershell
iex(New-Object Net.WebClient).DownloadString('https://clis.cloud.ibm.com/install/powershell')
```

### Verify Installation
```bash
ibmcloud --version
```

## Step 2: Install Required Plugins

```bash
# Install Code Engine plugin
ibmcloud plugin install code-engine

# Install Container Registry plugin  
ibmcloud plugin install container-registry
```

Verify the plugins are installed:
```bash
ibmcloud plugin list
```

## Step 3: Login to IBM Cloud

### Interactive Login
```bash
ibmcloud login
```

### API Key Login (Recommended for Automation)
```bash
ibmcloud login --apikey YOUR_API_KEY
```

To create an API key:
1. Go to [IBM Cloud Console](https://cloud.ibm.com)
2. Click on "Manage" → "Access (IAM)"
3. Select "API keys" → "Create an IBM Cloud API key"

## Step 4: Set Target Region and Resource Group

List available regions:
```bash
ibmcloud regions
```

Set your target region (e.g., us-south, eu-gb):
```bash
ibmcloud target -r us-south
```

List available resource groups:
```bash
ibmcloud resource groups
```

Set your resource group:
```bash
ibmcloud target -g YOUR_RESOURCE_GROUP
```

## Step 5: Configure IBM Cloud Container Registry

### 5.1 Login to Container Registry
```bash
ibmcloud cr login
```

### 5.2 Create a Namespace
```bash
# List existing namespaces
ibmcloud cr namespaces

# Create a new namespace (replace with a unique name)
ibmcloud cr namespace-add YOUR_NAMESPACE
```

Example:
```bash
ibmcloud cr namespace-add weather-mcp-dev
```

### 5.3 Get Registry Endpoint
```bash
ibmcloud cr region
```

Note the registry endpoint (e.g., `us.icr.io` for US South).

## Step 6: Update Deployment Configuration

### 6.1 Edit deploy.sh
Open `deploy.sh` in your editor and locate line 11:
```bash
REGISTRY_NAMESPACE="your-registry-namespace"
```

Replace with your actual namespace:
```bash
REGISTRY_NAMESPACE="weather-mcp-dev"  # Use your namespace from Step 5.2
```

### 6.2 Make Script Executable
```bash
chmod +x deploy.sh
```

## Step 7: Deploy the Application

### Option A: Automated Deployment (Recommended)

Run the deployment script:
```bash
./deploy.sh
```

The script will automatically:
1. Create/select a Code Engine project named `weather-mcp-project`
2. Build the Docker image locally
3. Push the image to IBM Cloud Container Registry
4. Deploy the application to Code Engine
5. Display the application URL

Expected output:
```
🚀 Deploying Weather MCP Server to IBM Cloud Code Engine
📋 Current resource group: Default
🏗️  Setting up Code Engine project...
📦 Building Docker image...
📤 Pushing image to IBM Cloud Container Registry...
🚀 Deploying application to Code Engine...
✅ Deployment completed successfully!
🌐 Application URL: https://weather-mcp-server.xxxxx.us-south.codeengine.appdomain.cloud
```

### Option B: Manual Deployment

If you prefer to deploy manually or the script fails:

#### 7.1 Create Code Engine Project
```bash
# Create a new project
ibmcloud ce project create --name weather-mcp-project

# Select the project
ibmcloud ce project select --name weather-mcp-project
```

#### 7.2 Build Docker Image
```bash
# Get your registry endpoint
REGISTRY=$(ibmcloud cr region | grep -oE '[a-z]+\.icr\.io')
NAMESPACE="YOUR_NAMESPACE"  # Replace with your namespace

# Build the image
docker build -t ${REGISTRY}/${NAMESPACE}/weather-mcp-python:latest .
```

#### 7.3 Push Image to Registry
```bash
docker push ${REGISTRY}/${NAMESPACE}/weather-mcp-python:latest
```

#### 7.4 Deploy to Code Engine
```bash
ibmcloud ce app create \
  --name weather-mcp-server \
  --image ${REGISTRY}/${NAMESPACE}/weather-mcp-python:latest \
  --port 8000 \
  --env CODE_ENGINE=true \
  --cpu 0.25 \
  --memory 0.5G \
  --min-scale 0 \
  --max-scale 10
```

## Step 8: Verify Deployment

### 8.1 Get Application URL
```bash
ibmcloud ce app get --name weather-mcp-server --output json | jq -r '.status.url'
```

If you don't have `jq` installed:
```bash
ibmcloud ce app get --name weather-mcp-server
# Look for the URL in the output
```

### 8.2 Test the Endpoints

Test health endpoint:
```bash
curl https://YOUR_APP_URL/health
```

Expected response:
```json
{"status": "healthy", "service": "weather-mcp"}
```

Test info endpoint:
```bash
curl https://YOUR_APP_URL/
```

Expected response:
```json
{
  "name": "Weather MCP Server",
  "version": "0.1.0",
  "description": "MCP server providing weather information via NWS API",
  "transport": "sse",
  "endpoints": {
    "health": "/health",
    "info": "/",
    "sse": "/sse"
  }
}
```

### 8.3 View Application Logs
```bash
ibmcloud ce app logs --name weather-mcp-server --follow
```

## Monitoring and Management

### Check Application Status
```bash
ibmcloud ce app get --name weather-mcp-server
```

### View Logs
```bash
ibmcloud ce app logs --name weather-mcp-server
```

### Update Application
```bash
# After making changes, rebuild and update
./deploy.sh
```

### Scale Application
```bash
ibmcloud ce app update --name weather-mcp-server --min-scale 1 --max-scale 20
```

### Delete Application
```bash
ibmcloud ce app delete --name weather-mcp-server
```

## Testing the Deployment

Once deployed, you can test the application:

1. **Health Check**: Visit `https://your-app-url/health`
2. **Service Info**: Visit `https://your-app-url/` for service details
3. **SSE Connection**: Connect to `https://your-app-url/sse` for MCP protocol over SSE

## API Usage

The deployed service provides the following endpoints:

- `GET /` - Service information and available endpoints
- `GET /health` - Health check
- `GET /sse` - Server-Sent Events endpoint for MCP protocol
- MCP Tools via SSE: `get_alerts`, `get_forecast`

Example SSE connection:
```javascript
const eventSource = new EventSource('https://your-app-url/sse');
eventSource.onmessage = function(event) {
    console.log('Received:', event.data);
};
```

## Troubleshooting Guide

### Issue 1: Docker push fails with authentication error
**Error Message:** `unauthorized: authentication required`

**Solution:**
```bash
# Re-login to container registry
ibmcloud cr login

# Verify Docker is configured correctly
docker pull hello-world

# If still failing, check your registry endpoint
ibmcloud cr region
```

### Issue 2: "Namespace not found" error
**Error Message:** `The specified namespace was not found`

**Solution:**
```bash
# List your namespaces
ibmcloud cr namespaces

# Create namespace if it doesn't exist
ibmcloud cr namespace-add YOUR_NAMESPACE
```

### Issue 3: Application fails to start
**Symptoms:** Application shows as "Failed" or keeps restarting

**Solution:**
```bash
# Check application logs
ibmcloud ce app logs --name weather-mcp-server --all

# Check events for errors
ibmcloud ce app events --name weather-mcp-server

# Common fixes:
# 1. Verify port is set to 8000
# 2. Check CODE_ENGINE environment variable is set
# 3. Ensure image was pushed successfully
```

### Issue 4: Cannot access application URL
**Symptoms:** URL returns 404 or connection refused

**Solution:**
```bash
# Verify app is running
ibmcloud ce app list

# Check if URL is assigned
ibmcloud ce app get --name weather-mcp-server

# If min-scale is 0, the app might be scaled down
# Force at least one instance to run:
ibmcloud ce app update --name weather-mcp-server --min-scale 1
```

### Issue 5: "Project not found" error
**Error Message:** `Project 'weather-mcp-project' not found`

**Solution:**
```bash
# List all projects
ibmcloud ce project list

# Create the project if it doesn't exist
ibmcloud ce project create --name weather-mcp-project

# Select the project
ibmcloud ce project select --name weather-mcp-project
```

### Issue 6: Build fails on M1/M2 Mac
**Symptoms:** Docker build fails with platform errors

**Solution:**
```bash
# Build with platform flag
docker buildx build --platform linux/amd64 \
  -t ${REGISTRY}/${NAMESPACE}/weather-mcp-python:latest .

# Push the image
docker push ${REGISTRY}/${NAMESPACE}/weather-mcp-python:latest
```

### Resource Limits

If you encounter resource limits:
- Increase CPU/memory allocations
- Adjust scaling parameters
- Check your IBM Cloud service plan limits

## Cost Optimization

- Use `min-scale 0` for automatic scale-to-zero when not in use
- Monitor usage with IBM Cloud monitoring
- Set appropriate CPU/memory limits
- Consider using reserved capacity for predictable workloads

## Security Considerations

- The application only accesses public NWS APIs
- No sensitive data is stored
- HTTPS is enforced by Code Engine
- Consider adding authentication for production use

## Next Steps

- Add monitoring and alerting
- Implement caching for better performance
- Add rate limiting
- Set up CI/CD pipeline for automatic deployments
- Add custom domain if needed
