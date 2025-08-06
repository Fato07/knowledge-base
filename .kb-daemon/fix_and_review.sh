#!/bin/bash
# Quick fix to import shadow logs and run review

echo "======================================"
echo "🔧 KB DAEMON - SHADOW LOG IMPORT"
echo "======================================"

cd /Users/fathindosunmu/DEV/knowledge-base/.kb-daemon

# Import shadow logs into database
echo ""
echo "📥 Importing captured events into database..."
python3 import_shadow.py

# Now run the review
echo ""
echo "📊 Starting daily review..."
echo ""
python3 interface/cli.py review
