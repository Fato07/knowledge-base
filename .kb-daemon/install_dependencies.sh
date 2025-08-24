#!/bin/bash
# Install required dependencies for KB Daemon

echo "📦 Installing KB Daemon dependencies..."

# Check if pip3 is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found. Please install Python 3 first."
    exit 1
fi

# Install psutil for process management
echo "Installing psutil..."
pip3 install psutil --user --quiet

# Check if installation was successful
if python3 -c "import psutil" 2>/dev/null; then
    echo "✅ psutil installed successfully"
else
    echo "⚠️  psutil installation may have failed"
    echo "   The daemon will use fallback methods"
fi

# Optional: Install other useful packages
echo ""
echo "Optional packages (not required):"
echo "  - toml: For better config parsing"
echo "  - pyyaml: For YAML config files"
echo ""
echo "Install optional packages? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    pip3 install toml pyyaml --user --quiet
    echo "✅ Optional packages installed"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Test the stop command:"
echo "  kb start  # Start the daemon"
echo "  kb status # Check if running"
echo "  kb stop   # Stop the daemon"
