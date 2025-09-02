#!/bin/bash

# IBM Cloud Code Engine Deployment Script for Weather MCP Server

set -e

# Configuration
PROJECT_NAME="weather-mcp-project"
APP_NAME="weather-mcp-server"
IMAGE_NAME="weather-mcp-python"
REGISTRY_NAMESPACE="your-registry-namespace"  # Update this with your container registry namespace

echo "🚀 Deploying Weather MCP Server to IBM Cloud Code Engine"

# Check if IBM Cloud CLI is installed
if ! command -v ibmcloud &> /dev/null; then
    echo "❌ IBM Cloud CLI is not installed. Please install it first:"
    echo "curl -fsSL https://clis.cloud.ibm.com/install/linux | sh"
    exit 1
fi

# Check if Code Engine plugin is installed
if ! ibmcloud plugin list | grep -q "code-engine"; then
    echo "📦 Installing Code Engine plugin..."
    ibmcloud plugin install code-engine
fi

# Login check
echo "🔐 Checking IBM Cloud login status..."
if ! ibmcloud target; then
    echo "Please log in to IBM Cloud:"
    ibmcloud login
fi

# Select resource group (optional - will use default if not specified)
echo "📋 Current resource group:"
ibmcloud target

# Create or select Code Engine project
echo "🏗️  Setting up Code Engine project..."
if ibmcloud ce project get --name "$PROJECT_NAME" &> /dev/null; then
    echo "✅ Project '$PROJECT_NAME' already exists. Selecting it..."
    ibmcloud ce project select --name "$PROJECT_NAME"
else
    echo "📁 Creating new project '$PROJECT_NAME'..."
    ibmcloud ce project create --name "$PROJECT_NAME"
    ibmcloud ce project select --name "$PROJECT_NAME"
fi

# Build and push image to IBM Cloud Container Registry
echo "🔨 Building and pushing container image..."

# Get the registry endpoint for your region
REGISTRY_ENDPOINT=$(ibmcloud cr region)
FULL_IMAGE_NAME="${REGISTRY_ENDPOINT}/${REGISTRY_NAMESPACE}/${IMAGE_NAME}:latest"

echo "📦 Building Docker image..."
docker build -t "$FULL_IMAGE_NAME" .

echo "📤 Pushing image to IBM Cloud Container Registry..."
docker push "$FULL_IMAGE_NAME"

# Deploy the application
echo "🚀 Deploying application to Code Engine..."
if ibmcloud ce app get --name "$APP_NAME" &> /dev/null; then
    echo "🔄 Updating existing application..."
    ibmcloud ce app update \
        --name "$APP_NAME" \
        --image "$FULL_IMAGE_NAME" \
        --port 8000 \
        --env CODE_ENGINE=true \
        --cpu 0.25 \
        --memory 0.5G \
        --min-scale 0 \
        --max-scale 10
else
    echo "✨ Creating new application..."
    ibmcloud ce app create \
        --name "$APP_NAME" \
        --image "$FULL_IMAGE_NAME" \
        --port 8000 \
        --env CODE_ENGINE=true \
        --cpu 0.25 \
        --memory 0.5G \
        --min-scale 0 \
        --max-scale 10
fi

# Get the application URL
echo "🌐 Getting application URL..."
APP_URL=$(ibmcloud ce app get --name "$APP_NAME" --output json | jq -r '.status.url')

echo ""
echo "✅ Deployment completed successfully!"
echo "🌐 Application URL: $APP_URL"
echo "🏥 Health Check: $APP_URL/health"
echo ""
echo "📊 To monitor your application:"
echo "   ibmcloud ce app get --name $APP_NAME"
echo "   ibmcloud ce app logs --name $APP_NAME"
echo ""
echo "🔧 To update your application:"
echo "   ./deploy.sh"
echo ""
echo "🗑️  To delete your application:"
echo "   ibmcloud ce app delete --name $APP_NAME"
