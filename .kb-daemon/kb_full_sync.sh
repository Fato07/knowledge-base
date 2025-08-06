#!/bin/bash
# KB Full Sync - Review captured events AND sync to graph

echo "======================================"
echo "🔄 KB FULL SYNC - Review + Graph Update"
echo "======================================"

# Step 1: Run daily review
echo ""
echo "📊 Step 1: Running daily review..."
cd /Users/fathindosunmu/DEV/knowledge-base/.kb-daemon
python3 interface/cli.py review

# Step 2: Sync to Basic Memory graph
echo ""
echo "📈 Step 2: Syncing to knowledge graph..."

# Check if basic-memory is available via uvx
if command -v uvx &> /dev/null; then
    echo "Found uvx, syncing to Basic Memory..."
    cd /Users/fathindosunmu/DEV/knowledge-base
    
    # Sync markdown files to graph
    uvx basic-memory sync
    
    echo ""
    echo "✅ Graph updated!"
    echo ""
    echo "📊 You can now:"
    echo "  - Query with: uvx basic-memory query 'what did I learn today'"
    echo "  - View graph: uvx basic-memory graph"
    echo "  - Or use Claude with MCP to query your knowledge"
else
    echo "⚠️  uvx not found - Basic Memory not available"
    echo "To install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "Then: uv tool install basic-memory"
fi

echo ""
echo "======================================"
echo "✅ Full sync complete!"
echo "======================================"
