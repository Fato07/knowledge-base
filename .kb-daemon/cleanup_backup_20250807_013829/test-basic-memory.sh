#!/bin/bash
# Make this file executable: chmod +x test-basic-memory.sh

# Test Basic Memory MCP Server Connection
echo "Testing Basic Memory MCP Server..."
echo "=================================="

# Check if basic-memory is installed
if command -v uvx &> /dev/null; then
    echo "✓ uvx is installed"
    
    # Try to run basic-memory
    echo -e "\nAttempting to start Basic Memory MCP server..."
    echo "Command: uvx basic-memory mcp --base-path ~/DEV/knowledge-base"
    echo -e "\nPress Ctrl+C to stop the test server after verification\n"
    
    # Start the MCP server in test mode
    uvx basic-memory mcp --base-path ~/DEV/knowledge-base
else
    echo "✗ uvx not found. Please install uv tools first."
    exit 1
fi
