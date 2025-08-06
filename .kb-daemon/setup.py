#!/usr/bin/env python3
"""
KB Daemon Setup Script - One-click installation
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("="*60)
    print("KB DAEMON INSTALLATION")
    print("="*60)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        sys.exit(1)
    
    print("✓ Python version OK")
    
    # Install required packages
    print("\n📦 Installing required packages...")
    packages = [
        'pyyaml',
        'watchdog'
    ]
    
    for package in packages:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                         check=True, capture_output=True)
            print(f"  ✓ {package} installed")
        except subprocess.CalledProcessError:
            print(f"  ❌ Failed to install {package}")
            print("  Try: pip install", package)
    
    # Create symlink in user's bin directory
    kb_daemon_path = Path(__file__).parent / 'kb_daemon.py'
    
    # Create kb-daemon command
    user_bin = Path.home() / '.local' / 'bin'
    user_bin.mkdir(parents=True, exist_ok=True)
    
    kb_command = user_bin / 'kb-daemon'
    kb_command.write_text(f'''#!/bin/bash
python3 {kb_daemon_path} "$@"
''')
    kb_command.chmod(0o755)
    
    print(f"\n✓ Created command: kb-daemon")
    
    # Install git hooks
    print("\n🔧 Installing git hooks...")
    from capture.git_hooks import GitHooks
    git_hooks = GitHooks(None, {})
    git_hooks.install_hooks()
    
    # Install shell integration
    shell_installer = Path.home() / '.kb-daemon' / 'install_shell.sh'
    if shell_installer.exists():
        print("\n🐚 Shell integration ready!")
        print(f"Run: {shell_installer}")
    
    # Test database
    print("\n💾 Testing database...")
    from storage.db_manager import DatabaseManager
    db = DatabaseManager(Path.home() / '.kb-daemon' / 'storage' / 'kb_store.db')
    stats = db.get_statistics()
    print(f"  ✓ Database initialized")
    
    print("\n" + "="*60)
    print("✅ INSTALLATION COMPLETE!")
    print("="*60)
    
    print("\n📋 Next steps:")
    print("1. Add to PATH: export PATH=$PATH:~/.local/bin")
    print("2. Install shell integration: ~/.kb-daemon/install_shell.sh")
    print("3. Start daemon: kb-daemon start")
    print("4. Test: kb-daemon test")
    print("5. Daily review: kb-daemon review")
    
    print("\n💡 Quick test:")
    print("   kb-daemon test")

if __name__ == "__main__":
    # Change to script directory
    os.chdir(Path(__file__).parent)
    main()
