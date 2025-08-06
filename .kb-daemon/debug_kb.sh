#!/bin/bash
# Debug kb command issue

echo "🔍 Debugging KB Command..."
echo "=========================="

# Check which kb is being used
echo "1. Which kb is being executed:"
which kb

# Check the content of system kb
echo ""
echo "2. First lines of /usr/local/bin/kb:"
head -20 /usr/local/bin/kb | grep -E "(commit|sync-git|help)" || echo "Pattern not found"

# Check our source file
echo ""
echo "3. First lines of source kb:"
head -20 /Users/fathindosunmu/DEV/knowledge-base/.kb-daemon/kb | grep -E "(commit|sync-git|help)" || echo "Pattern not found"

# Check if they're different
echo ""
echo "4. File comparison:"
if diff /usr/local/bin/kb /Users/fathindosunmu/DEV/knowledge-base/.kb-daemon/kb > /dev/null; then
    echo "Files are identical"
else
    echo "Files are DIFFERENT!"
    echo "Showing differences (first 10):"
    diff /usr/local/bin/kb /Users/fathindosunmu/DEV/knowledge-base/.kb-daemon/kb | head -10
fi

# Check file sizes
echo ""
echo "5. File sizes:"
ls -la /usr/local/bin/kb
ls -la /Users/fathindosunmu/DEV/knowledge-base/.kb-daemon/kb

# Try direct execution
echo ""
echo "6. Testing direct execution:"
/Users/fathindosunmu/DEV/knowledge-base/.kb-daemon/kb help | grep commit || echo "commit not in help"
