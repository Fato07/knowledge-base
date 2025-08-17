#!/bin/bash
# KB Full Sync - Review + Graph Update

echo "======================================"
echo "🔄 KB FULL SYNC - Review + Graph Update"
echo "======================================"

# Step 1: Run the review
echo ""
echo "📊 Step 1: Running daily review..."
cd /Users/fathindosunmu/DEV/knowledge-base/.kb-daemon
python3 interface/cli.py review

# Step 2: Sync to Basic Memory graph
echo ""
echo "📈 Step 2: Syncing to knowledge graph..."

# Check if uvx is available (Basic Memory's tool)
if command -v uvx &> /dev/null; then
    echo "Found uvx, syncing with Basic Memory..."
    cd /Users/fathindosunmu/DEV/knowledge-base
    
    # Run Basic Memory sync
    uvx --from basic-memory sync
    
    echo "✅ Graph sync complete!"
    
    # Optional: Show graph stats
    echo ""
    echo "📊 Graph statistics:"
    uvx --from basic-memory stats 2>/dev/null || echo "Stats not available"
else
    echo "⚠️  uvx not found"
    echo "Basic Memory might not be installed."
    echo ""
    echo "To install Basic Memory:"
    echo "  1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  2. Install Basic Memory: uvx basic-memory"
    echo ""
    echo "Graph sync skipped - only markdown files were created"
fi

echo ""
echo "======================================"
echo "✅ Full sync complete!"
echo "======================================"
