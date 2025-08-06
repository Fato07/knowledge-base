#!/bin/bash
# Run the daily review with fixed code

echo "======================================"
echo "📊 KB DAEMON - DAILY REVIEW"
echo "======================================"

cd /Users/fathindosunmu/DEV/knowledge-base/.kb-daemon

# Run the review (data already imported)
python3 interface/cli.py review
