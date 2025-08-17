#!/bin/bash
# KB Daemon Shell Integration Installer

echo "Installing KB Daemon shell integration..."

# Add to appropriate shell config
if [ -n "$BASH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
else
    echo "Unsupported shell"
    exit 1
fi

# Check if already installed
if ! grep -q "kb-daemon/shell_wrapper.sh" "$SHELL_CONFIG" 2>/dev/null; then
    echo "" >> "$SHELL_CONFIG"
    echo "# KB Daemon Shell Integration" >> "$SHELL_CONFIG"
    echo "[ -f ~/.kb-daemon/shell_wrapper.sh ] && source ~/.kb-daemon/shell_wrapper.sh" >> "$SHELL_CONFIG"
    echo "Shell integration added to $SHELL_CONFIG"
    echo "Please restart your shell or run: source $SHELL_CONFIG"
else
    echo "Shell integration already installed"
fi
