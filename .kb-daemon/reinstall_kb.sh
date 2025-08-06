#!/bin/bash
# Quick reinstall of kb command

echo "🔄 Reinstalling kb command..."

KB_SCRIPT="/Users/fathindosunmu/DEV/knowledge-base/.kb-daemon/kb"

# Check where kb is currently installed
if [ -f "/usr/local/bin/kb" ]; then
    echo "Found kb in /usr/local/bin"
    if [ -w "/usr/local/bin" ]; then
        cp "$KB_SCRIPT" /usr/local/bin/kb
        echo "✅ Updated /usr/local/bin/kb"
    else
        echo "Need sudo to update /usr/local/bin/kb"
        echo "Run: sudo cp $KB_SCRIPT /usr/local/bin/kb"
    fi
elif [ -f "$HOME/.local/bin/kb" ]; then
    echo "Found kb in ~/.local/bin"
    cp "$KB_SCRIPT" "$HOME/.local/bin/kb"
    chmod +x "$HOME/.local/bin/kb"
    echo "✅ Updated ~/.local/bin/kb"
else
    echo "kb command not found in standard locations"
    echo "Installing to ~/.local/bin..."
    mkdir -p "$HOME/.local/bin"
    cp "$KB_SCRIPT" "$HOME/.local/bin/kb"
    chmod +x "$HOME/.local/bin/kb"
    echo "✅ Installed to ~/.local/bin/kb"
    echo ""
    echo "Add to PATH if needed:"
    echo "  export PATH=\$PATH:~/.local/bin"
fi

echo ""
echo "✅ Done! Try these commands:"
echo "  kb help      # See all commands"
echo "  kb commit    # Git commit"
echo "  kb full      # Full workflow"
