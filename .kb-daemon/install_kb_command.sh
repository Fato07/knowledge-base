#!/bin/bash
# Install kb command system-wide

echo "======================================"
echo "📦 Installing 'kb' command"
echo "======================================"

KB_SCRIPT="/Users/fathindosunmu/DEV/knowledge-base/.kb-daemon/kb"

# Make the script executable
chmod +x "$KB_SCRIPT"

# Check if we can write to /usr/local/bin
if [ -w "/usr/local/bin" ]; then
    # Direct copy
    cp "$KB_SCRIPT" /usr/local/bin/kb
    echo "✅ Installed to /usr/local/bin/kb"
else
    # Need sudo
    echo "🔐 Need admin access to install to /usr/local/bin"
    echo "Run: sudo cp $KB_SCRIPT /usr/local/bin/kb"
    echo ""
    echo "Or install to user directory:"
    USER_BIN="$HOME/.local/bin"
    mkdir -p "$USER_BIN"
    cp "$KB_SCRIPT" "$USER_BIN/kb"
    chmod +x "$USER_BIN/kb"
    echo "✅ Installed to $USER_BIN/kb"
    echo ""
    echo "Add to PATH in ~/.bashrc or ~/.zshrc:"
    echo "  export PATH=\$PATH:$USER_BIN"
fi

echo ""
echo "======================================"
echo "✅ Installation complete!"
echo "======================================"
echo ""
echo "Available commands:"
echo "  kb review    - Run daily review"
echo "  kb start     - Start daemon"
echo "  kb status    - Check status"
echo "  kb log       - View logs"
echo "  kb help      - Show all commands"
echo ""
echo "Try it now:"
echo "  kb status"
