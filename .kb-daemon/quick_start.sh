#!/bin/bash
# KB Daemon Quick Start Script

echo "======================================"
echo "KB DAEMON - QUICK START"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "kb_daemon.py" ]; then
    echo "❌ Error: Run this from the .kb-daemon directory"
    exit 1
fi

# Install Python dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install pyyaml watchdog 2>/dev/null || {
    echo "⚠️  Could not install automatically"
    echo "Run manually:"
    echo "  pip3 install pyyaml watchdog"
}

# Run manual test
echo ""
echo "🧪 Running system test..."
python3 manual_test.py

# Check if test passed
if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "✅ SYSTEM READY!"
    echo "======================================"
    echo ""
    echo "Choose an option:"
    echo "1) Start daemon in shadow mode (recommended)"
    echo "2) Run daily review interface"
    echo "3) Test daemon without starting"
    echo "4) Exit"
    echo ""
    read -p "Enter choice [1-4]: " choice

    case $choice in
        1)
            echo "Starting daemon in shadow mode..."
            python3 kb_daemon.py start
            ;;
        2)
            echo "Opening daily review..."
            python3 interface/cli.py review
            ;;
        3)
            echo "Testing daemon..."
            python3 kb_daemon.py test
            ;;
        4)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice"
            ;;
    esac
else
    echo ""
    echo "❌ Tests failed. Please fix issues above."
fi
