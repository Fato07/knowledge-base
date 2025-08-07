#!/bin/bash
# Remove all KB daemon hooks from claude command

echo "======================================"
echo "🧹 REMOVING CLAUDE HOOKS"
echo "======================================"
echo ""

# Detect shell config
if [ "$SHELL" = "/bin/zsh" ] || [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
else
    SHELL_RC="$HOME/.bashrc"
fi

echo "Cleaning up $SHELL_RC..."

# Create backup
cp "$SHELL_RC" "$SHELL_RC.backup_$(date +%Y%m%d_%H%M%S)"
echo "✅ Created backup: $SHELL_RC.backup_*"

# Remove all KB daemon related claude configurations
echo ""
echo "Removing KB daemon hooks..."

# Remove function source line
sed -i '' '/editor_functions.sh/d' "$SHELL_RC" 2>/dev/null
sed -i '' '/claude_function.sh/d' "$SHELL_RC" 2>/dev/null

# Remove claude alias with kb start
sed -i '' '/alias claude.*kb start/d' "$SHELL_RC" 2>/dev/null
sed -i '' '/alias claude.*kb_daemon/d' "$SHELL_RC" 2>/dev/null

# Remove KB Daemon comment lines related to claude
sed -i '' '/# KB Daemon.*claude/d' "$SHELL_RC" 2>/dev/null
sed -i '' '/# Claude.*KB Daemon/d' "$SHELL_RC" 2>/dev/null
sed -i '' '/# KB Daemon - Auto-start with claude/d' "$SHELL_RC" 2>/dev/null
sed -i '' '/# KB Daemon - Simple auto-start with claude/d' "$SHELL_RC" 2>/dev/null

# Remove shell auto-start if present
sed -i '' '/kb_auto_start/d' "$SHELL_RC" 2>/dev/null
sed -i '' '/shell_auto_start.sh/d' "$SHELL_RC" 2>/dev/null

echo "✅ Removed all KB daemon claude hooks"

echo ""
echo "======================================"
echo "✅ CLEANUP COMPLETE!"
echo "======================================"
echo ""
echo "Now you need to:"
echo ""
echo "1. Restart your terminal OR run:"
echo "   unfunction claude 2>/dev/null"
echo "   unalias claude 2>/dev/null"
echo "   source $SHELL_RC"
echo ""
echo "2. Set up your original claude command"
echo "   (whatever you used before)"
echo ""
echo "To start KB daemon manually:"
echo "   kb start    # Start daemon"
echo "   kb status   # Check status"
echo "   kb stop     # Stop daemon"
echo ""
echo "Your KB system is still fully functional,"
echo "just without automatic startup."
