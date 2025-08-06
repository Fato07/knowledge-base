#!/bin/bash
# Safe cleanup with backup

echo "======================================"
echo "🧹 KB DAEMON - SAFE CLEANUP"
echo "======================================"

cd /Users/fathindosunmu/DEV/knowledge-base/.kb-daemon

# Create backup directory
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo ""
echo "📦 Creating backup in $BACKUP_DIR..."

# Files to remove (redundant)
FILES_TO_REMOVE=(
    "fix_and_review.sh"
    "run_review.sh"
    "make_executable.sh"
    "make_kb_executable.sh"
    "make_view_executable.sh"
    "update_commands.sh"
    "init_and_test.py"
    "kb_universal"
    "cleanup.py"  # Remove itself after use
)

# Backup and remove
for file in "${FILES_TO_REMOVE[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/" 2>/dev/null
        rm "$file"
        echo "  ✓ Removed: $file"
    fi
done

echo ""
echo "📋 Essential files kept:"
echo "  • kb_daemon.py         (main daemon)"
echo "  • kb                   (unified command)"
echo "  • setup.py             (installation)"
echo "  • view_logs.py         (log viewer)"
echo "  • view.sh              (quick view)"
echo "  • test_system.py       (comprehensive test)"
echo "  • manual_test.py       (quick test)"
echo "  • quick_start.sh       (getting started)"
echo "  • kb_full_sync.sh      (full sync)"
echo "  • import_shadow.py     (shadow importer)"
echo "  • install_kb_command.sh (command installer)"

echo ""
echo "✅ Cleanup complete!"
echo "   Backup saved in: $BACKUP_DIR"
echo ""
echo "🧪 Test that everything works:"
echo "   kb status"
echo "   kb help"
