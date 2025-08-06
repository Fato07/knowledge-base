#!/bin/bash
# KB Daily Workflow - Complete daily knowledge management

echo "======================================"
echo "🌟 KB DAILY WORKFLOW"
echo "======================================"

# Step 1: Review
echo ""
echo "📊 Step 1: Daily Review"
echo "------------------------"
kb review

# Step 2: Sync to graph
echo ""
echo "🕸️ Step 2: Sync to Graph"
echo "------------------------"
kb sync

# Step 3: Commit to git
echo ""
echo "📚 Step 3: Git Commit"
echo "------------------------"
kb commit

echo ""
echo "======================================"
echo "✅ Daily workflow complete!"
echo "======================================"
echo ""
echo "Your knowledge base is now:"
echo "  ✓ Reviewed"
echo "  ✓ Synced to graph"
echo "  ✓ Committed to git"
