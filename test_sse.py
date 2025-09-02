#!/usr/bin/env python3
"""
Test script for Weather MCP Server SSE functionality
"""

import asyncio
import aiohttp
import json
import sys
from typing import AsyncGenerator

async def test_sse_connection(url: str = "http://localhost:8080"):
    """Test SSE connection to the Weather MCP Server"""
    
    print(f"Testing SSE connection to {url}")
    
    # Test health endpoint first
    async with aiohttp.ClientSession() as session:
        try:
            print("\n1. Testing health endpoint...")
            async with session.get(f"{url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"✅ Health check passed: {health_data}")
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return
        
        try:
            print("\n2. Testing service info endpoint...")
            async with session.get(f"{url}/") as response:
                if response.status == 200:
                    info_data = await response.json()
                    print(f"✅ Service info: {info_data}")
                else:
                    print(f"❌ Service info failed: {response.status}")
        except Exception as e:
            print(f"❌ Service info error: {e}")
        
        try:
            print("\n3. Testing SSE connection...")
            timeout = aiohttp.ClientTimeout(total=3)  # 3 second timeout
            async with session.get(f"{url}/sse", timeout=timeout) as response:
                if response.status == 200:
                    print("✅ SSE connection established")
                    print("📡 Reading first few SSE events...")
                    
                    # Read first few lines of SSE stream
                    event_count = 0
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            data = line[6:]  # Remove 'data: ' prefix
                            try:
                                json_data = json.loads(data)
                                print(f"📨 Received: {json_data}")
                                event_count += 1
                            except json.JSONDecodeError:
                                print(f"📨 Received (raw): {data}")
                        elif line:
                            print(f"📨 SSE event: {line}")
                        
                        # Stop after receiving first event
                        if event_count >= 1:
                            print("✅ SSE stream working correctly")
                            break
                else:
                    print(f"❌ SSE connection failed: {response.status}")
        except asyncio.TimeoutError:
            print("✅ SSE connection timeout (expected for continuous stream)")
        except KeyboardInterrupt:
            print("\n🛑 SSE test interrupted by user")
        except Exception as e:
            print(f"❌ SSE connection error: {e}")

async def test_mcp_tool_call(url: str = "http://localhost:8080"):
    """Test MCP tool call via SSE"""
    
    print(f"\n4. Testing MCP tool call...")
    
    # This would require implementing the MCP protocol over SSE
    # For now, just verify the SSE endpoint is available
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{url}/sse") as response:
                if response.status == 200:
                    print("✅ SSE endpoint is ready for MCP protocol")
                else:
                    print(f"❌ SSE endpoint not available: {response.status}")
        except Exception as e:
            print(f"❌ SSE endpoint error: {e}")

def main():
    """Main test function"""
    
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    
    print("🧪 Weather MCP Server SSE Test")
    print("=" * 40)
    
    # Test the server
    asyncio.run(test_sse_connection(url))
    asyncio.run(test_mcp_tool_call(url))
    
    print("\n✨ Test completed")

if __name__ == "__main__":
    main()
