#!/bin/bash
# Clean up test and unnecessary files from knowledge base

echo "======================================"
echo "🧹 KB CLEANUP - Remove Test Files"
echo "======================================"

cd /Users/fathindosunmu/DEV/knowledge-base

# Create backup directory
BACKUP_DIR=".kb-daemon/cleanup_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo ""
echo "📦 Creating backup in $BACKUP_DIR"

# Files to remove (test/temporary files)
FILES_TO_REMOVE=(
    # Test files from Basic Memory setup
    "BASIC_MEMORY_TESTS.md"
    "test-basic-memory.sh"
    
    # Obsidian untitled canvases
    "Untitled.canvas"
    "Untitled 1.canvas"
    "Untitled 2.canvas"
    
    # Test markdown
    "2025-08-06.md"  # This looks like a test file
    
    # Duplicate reference files (keep only one)
    "KB_QUICK_REFERENCE.txt"  # Keep QUICK_REFERENCE.md instead
)

# KB Daemon cleanup files to remove
KB_DAEMON_FILES=(
    ".kb-daemon/safe_cleanup.sh"
    ".kb-daemon/cleanup.py"
    ".kb-daemon/debug_kb.sh"
    ".kb-daemon/reinstall_kb.sh"
    ".kb-daemon/backup_*"  # Old backup directories
)

echo ""
echo "Files to be removed:"
for file in "${FILES_TO_REMOVE[@]}"; do
    if [ -f "$file" ]; then
        echo "  • $file"
        cp "$file" "$BACKUP_DIR/" 2>/dev/null
    fi
done

echo ""
echo "Clean up test files? [y/N]"
read -r CONFIRM

if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
    # Remove main test files
    for file in "${FILES_TO_REMOVE[@]}"; do
        if [ -f "$file" ]; then
            rm "$file"
            echo "  ✓ Removed: $file"
        fi
    done
    
    # Clean up KB daemon redundant files
    echo ""
    echo "Cleaning KB daemon files..."
    cd .kb-daemon
    rm -f safe_cleanup.sh cleanup.py debug_kb.sh reinstall_kb.sh 2>/dev/null
    rm -rf backup_* 2>/dev/null
    echo "  ✓ Cleaned up redundant daemon files"
    
    echo ""
    echo "✅ Cleanup complete!"
    echo "   Backup saved in: $BACKUP_DIR"
else
    echo "❌ Cleanup cancelled"
fi

echo ""
echo "📋 Files kept:"
echo "  • README.md (main documentation)"
echo "  • QUICK_REFERENCE.md (command reference)"
echo "  • basic-memory.toml (Basic Memory config)"
echo "  • .gitignore (git configuration)"
echo "  • All KB entries in daily/, projects/, learning/, etc."
