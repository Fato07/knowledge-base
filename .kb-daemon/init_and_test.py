#!/usr/bin/env python3
"""
KB Daemon Initialization and Test Script
Run this to set up and test the KB Daemon
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Add the kb-daemon directory to Python path
KB_DAEMON_PATH = Path(__file__).parent
sys.path.insert(0, str(KB_DAEMON_PATH))

def test_imports():
    """Test all module imports"""
    print("Testing imports...")
    try:
        from capture.git_hooks import GitHooks
        print("  ✓ Git hooks module")
        
        from capture.shell_monitor import ShellMonitor
        print("  ✓ Shell monitor module")
        
        from capture.file_watcher import FileWatcher
        print("  ✓ File watcher module")
        
        from process.categorizer import ActivityCategorizer
        print("  ✓ Categorizer module")
        
        from process.summarizer import Summarizer
        print("  ✓ Summarizer module")
        
        from storage.db_manager import DatabaseManager
        print("  ✓ Database module")
        
        from interface.cli import CLI
        print("  ✓ CLI module")
        
        return True
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False

def setup_local_directories():
    """Set up directories within the KB daemon path"""
    print("\nSetting up local directories...")
    
    # Create necessary directories
    dirs = [
        KB_DAEMON_PATH / "runtime" / "capture",
        KB_DAEMON_PATH / "runtime" / "storage",
        KB_DAEMON_PATH / "runtime" / "logs",
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created {dir_path.relative_to(KB_DAEMON_PATH)}")
    
    return True

def test_database():
    """Test database initialization"""
    print("\nTesting database...")
    
    try:
        from storage.db_manager import DatabaseManager
        
        # Use local database path
        db_path = KB_DAEMON_PATH / "runtime" / "storage" / "kb_store.db"
        db = DatabaseManager(db_path)
        
        # Test operations
        test_event = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'type': 'test',
            'category': 'testing',
            'importance': 5,
            'data': {'test': True},
            'key_info': {'message': 'Test event'}
        }
        
        db.store_event(test_event)
        stats = db.get_statistics()
        
        print(f"  ✓ Database working")
        print(f"  ✓ Total events: {stats['total_events']}")
        
        return True
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return False

def test_categorizer():
    """Test the categorizer"""
    print("\nTesting categorizer...")
    
    try:
        from process.categorizer import ActivityCategorizer
        
        patterns_file = KB_DAEMON_PATH / "config" / "patterns.yml"
        categorizer = ActivityCategorizer(patterns_file)
        
        # Test event categorization
        test_events = [
            {
                'type': 'git_commit',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'data': {
                    'message': 'fix: resolve authentication bug',
                    'files_changed': 'auth.js tests/auth.test.js'
                }
            },
            {
                'type': 'shell_command',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'data': {
                    'command': 'npm',
                    'args': 'test',
                    'exit_code': 0,
                    'duration': 15
                }
            }
        ]
        
        categorized = categorizer.categorize_batch(test_events)
        
        print(f"  ✓ Categorized {len(categorized)} events")
        for event in categorized:
            print(f"    - {event.get('category')}: importance {event.get('importance')}/10")
        
        return True
    except Exception as e:
        print(f"  ❌ Categorizer error: {e}")
        return False

def test_summarizer():
    """Test the summarizer"""
    print("\nTesting summarizer...")
    
    try:
        from process.summarizer import Summarizer
        
        config = {'use_local_llm': False}
        summarizer = Summarizer(config)
        
        # Create test events
        test_events = [
            {
                'type': 'git_commit',
                'category': 'bugfix',
                'importance': 7,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'key_info': {
                    'commit_message': 'Fixed authentication bug',
                    'files_changed': 3
                }
            }
        ]
        
        summary = summarizer.summarize(test_events)
        
        print(f"  ✓ Generated summary")
        print(f"    Events: {summary.get('event_count')}")
        if summary.get('text'):
            print(f"    Preview: {summary['text'][:100]}...")
        
        return True
    except Exception as e:
        print(f"  ❌ Summarizer error: {e}")
        return False

def create_shell_integration():
    """Create shell integration scripts in the local directory"""
    print("\nCreating shell integration...")
    
    # Create wrapper script
    wrapper_path = KB_DAEMON_PATH / "shell_wrapper.sh"
    wrapper_content = '''#!/bin/bash
# KB Daemon Shell Wrapper - Local Version

KB_DAEMON_DIR="''' + str(KB_DAEMON_PATH) + '''"
KB_CAPTURE_FILE="$KB_DAEMON_DIR/runtime/capture/shell_events.jsonl"

kb_capture_command() {
    local cmd="$1"
    shift
    local args="$@"
    local start_time=$(date +%s)
    local working_dir=$(pwd)
    
    # Run the actual command
    command "$cmd" "$args"
    local exit_code=$?
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Create event JSON
    cat >> "$KB_CAPTURE_FILE" <<EOF
{"type":"shell_command","timestamp":"$(date -u +"%Y-%m-%dT%H:%M:%SZ")","data":{"command":"$cmd","args":"$args","exit_code":$exit_code,"duration":$duration,"working_dir":"$working_dir"}}
EOF
    
    return $exit_code
}

# Alias tracked commands (optional - uncomment to use)
# alias npm="kb_capture_command npm"
# alias git="kb_capture_command git"
# alias python="kb_capture_command python"

echo "KB Daemon shell integration loaded (local version)"
'''
    
    wrapper_path.write_text(wrapper_content)
    wrapper_path.chmod(0o755)
    print(f"  ✓ Created {wrapper_path.name}")
    
    # Create installer script
    installer_path = KB_DAEMON_PATH / "install_shell_integration.sh"
    installer_content = f'''#!/bin/bash
# Install KB Daemon Shell Integration

echo "Installing KB Daemon shell integration..."

KB_DAEMON_DIR="{KB_DAEMON_PATH}"

# Detect shell
if [ -n "$BASH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
else
    echo "Unsupported shell"
    exit 1
fi

# Add to shell config
if ! grep -q "kb-daemon/shell_wrapper.sh" "$SHELL_CONFIG" 2>/dev/null; then
    echo "" >> "$SHELL_CONFIG"
    echo "# KB Daemon Shell Integration" >> "$SHELL_CONFIG"
    echo "[ -f $KB_DAEMON_DIR/shell_wrapper.sh ] && source $KB_DAEMON_DIR/shell_wrapper.sh" >> "$SHELL_CONFIG"
    echo "✓ Added to $SHELL_CONFIG"
    echo "Please run: source $SHELL_CONFIG"
else
    echo "Already installed in $SHELL_CONFIG"
fi
'''
    
    installer_path.write_text(installer_content)
    installer_path.chmod(0o755)
    print(f"  ✓ Created {installer_path.name}")
    
    return True

def create_git_hooks():
    """Create git hooks in local directory"""
    print("\nCreating git hooks...")
    
    hooks_dir = KB_DAEMON_PATH / "git-hooks"
    hooks_dir.mkdir(exist_ok=True)
    
    # Post-commit hook
    post_commit = hooks_dir / "post-commit"
    post_commit_content = f'''#!/bin/bash
# KB Daemon post-commit hook

KB_DAEMON_DIR="{KB_DAEMON_PATH}"
KB_CAPTURE_FILE="$KB_DAEMON_DIR/runtime/capture/git_events.jsonl"

COMMIT_HASH=$(git rev-parse HEAD)
COMMIT_MSG=$(git log -1 --pretty=%B)
BRANCH=$(git branch --show-current)
CHANGED_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD | tr '\\n' ' ')

cat >> "$KB_CAPTURE_FILE" <<EOF
{{"type":"git_commit","timestamp":"$(date -u +"%Y-%m-%dT%H:%M:%SZ")","data":{{"hash":"$COMMIT_HASH","message":"$COMMIT_MSG","branch":"$BRANCH","files_changed":"$CHANGED_FILES"}}}}
EOF

echo "KB Daemon: Captured commit"
'''
    
    post_commit.write_text(post_commit_content)
    post_commit.chmod(0o755)
    print(f"  ✓ Created post-commit hook")
    
    # Instructions for installing hooks
    instructions = hooks_dir / "INSTALL.md"
    instructions_content = f'''# Installing Git Hooks

## For a specific repository:
```bash
cp {hooks_dir}/post-commit .git/hooks/
chmod +x .git/hooks/post-commit
```

## For all new repositories (global):
```bash
git config --global init.templatedir {hooks_dir}
```

## Test the hook:
```bash
git commit --allow-empty -m "test: KB daemon hook"
```
'''
    
    instructions.write_text(instructions_content)
    print(f"  ✓ Created installation instructions")
    
    return True

def test_cli():
    """Test CLI interface"""
    print("\nTesting CLI interface...")
    
    try:
        from interface.cli import CLI
        
        # Override database path for testing
        import interface.cli as cli_module
        original_init = cli_module.CLI.__init__
        
        def patched_init(self):
            from storage.db_manager import DatabaseManager
            self.db = DatabaseManager(
                KB_DAEMON_PATH / "runtime" / "storage" / "kb_store.db"
            )
            from process.summarizer import Summarizer
            self.summarizer = Summarizer({'use_local_llm': False})
        
        cli_module.CLI.__init__ = patched_init
        
        cli_obj = CLI()
        stats = cli_obj.db.get_statistics()
        
        print(f"  ✓ CLI initialized")
        print(f"    Database has {stats['total_events']} events")
        
        return True
    except Exception as e:
        print(f"  ❌ CLI error: {e}")
        return False

def main():
    """Main test and setup function"""
    print("="*60)
    print("KB DAEMON - INITIALIZATION & TEST")
    print("="*60)
    
    all_good = True
    
    # Run tests
    all_good &= test_imports()
    all_good &= setup_local_directories()
    all_good &= test_database()
    all_good &= test_categorizer()
    all_good &= test_summarizer()
    all_good &= create_shell_integration()
    all_good &= create_git_hooks()
    all_good &= test_cli()
    
    print("\n" + "="*60)
    
    if all_good:
        print("✅ ALL TESTS PASSED!")
        print("\n📋 Next Steps:")
        print(f"1. Install shell integration:")
        print(f"   bash {KB_DAEMON_PATH}/install_shell_integration.sh")
        print(f"   source ~/.bashrc  # or ~/.zshrc")
        print(f"\n2. Install git hooks (for current repo):")
        print(f"   cp {KB_DAEMON_PATH}/git-hooks/post-commit .git/hooks/")
        print(f"\n3. Start the daemon:")
        print(f"   python3 {KB_DAEMON_PATH}/kb_daemon.py start")
        print(f"\n4. Run daily review:")
        print(f"   python3 {KB_DAEMON_PATH}/interface/cli.py review")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nCommon fixes:")
        print("1. Install missing packages: pip install pyyaml watchdog")
        print("2. Check Python version: python3 --version (need 3.7+)")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
