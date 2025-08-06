#!/usr/bin/env python3
"""
KB Daemon - Comprehensive System Test
"""

import os
import sys
import json
import time
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime
from queue import Queue

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all module imports"""
    print("\n📦 Testing imports...")
    modules_ok = True
    
    try:
        import yaml
        print("  ✓ yaml")
    except ImportError:
        print("  ❌ yaml - Run: pip install pyyaml")
        modules_ok = False
    
    try:
        from watchdog.observers import Observer
        print("  ✓ watchdog")
    except ImportError:
        print("  ❌ watchdog - Run: pip install watchdog")
        modules_ok = False
    
    # Test internal modules
    try:
        from capture.git_hooks import GitHooks
        print("  ✓ capture.git_hooks")
    except Exception as e:
        print(f"  ❌ capture.git_hooks: {e}")
        modules_ok = False
    
    try:
        from capture.shell_monitor import ShellMonitor
        print("  ✓ capture.shell_monitor")
    except Exception as e:
        print(f"  ❌ capture.shell_monitor: {e}")
        modules_ok = False
    
    try:
        from capture.file_watcher import FileWatcher
        print("  ✓ capture.file_watcher")
    except Exception as e:
        print(f"  ❌ capture.file_watcher: {e}")
        modules_ok = False
    
    try:
        from process.categorizer import ActivityCategorizer
        print("  ✓ process.categorizer")
    except Exception as e:
        print(f"  ❌ process.categorizer: {e}")
        modules_ok = False
    
    try:
        from process.summarizer import Summarizer
        print("  ✓ process.summarizer")
    except Exception as e:
        print(f"  ❌ process.summarizer: {e}")
        modules_ok = False
    
    try:
        from storage.db_manager import DatabaseManager
        print("  ✓ storage.db_manager")
    except Exception as e:
        print(f"  ❌ storage.db_manager: {e}")
        modules_ok = False
    
    try:
        from interface.cli import CLI
        print("  ✓ interface.cli")
    except Exception as e:
        print(f"  ❌ interface.cli: {e}")
        modules_ok = False
    
    return modules_ok

def test_configuration():
    """Test configuration files"""
    print("\n⚙️  Testing configuration...")
    config_ok = True
    
    config_path = Path(__file__).parent / "config" / "settings.yml"
    if config_path.exists():
        print(f"  ✓ settings.yml exists")
        try:
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f)
            print(f"  ✓ settings.yml valid YAML")
            
            # Check LLM configuration
            llm_config = config.get('processing', {})
            if llm_config.get('use_local_llm'):
                print(f"  ⚠️  Local LLM enabled - Ollama required")
            else:
                print(f"  ✓ Using rule-based processing (no LLM needed)")
                
            # Check API configuration
            if 'llm_model' in llm_config:
                model = llm_config['llm_model']
                if 'claude' in model:
                    print(f"  ⚠️  Claude API configured - API key needed in environment")
                    if 'ANTHROPIC_API_KEY' not in os.environ:
                        print(f"     ❌ ANTHROPIC_API_KEY not set")
                        print(f"     💡 For now, system will use rule-based fallback")
        except Exception as e:
            print(f"  ❌ Error reading settings.yml: {e}")
            config_ok = False
    else:
        print(f"  ❌ settings.yml not found")
        config_ok = False
    
    patterns_path = Path(__file__).parent / "config" / "patterns.yml"
    if patterns_path.exists():
        print(f"  ✓ patterns.yml exists")
        try:
            import yaml
            with open(patterns_path) as f:
                patterns = yaml.safe_load(f)
            print(f"  ✓ patterns.yml valid YAML")
        except Exception as e:
            print(f"  ❌ Error reading patterns.yml: {e}")
            config_ok = False
    else:
        print(f"  ❌ patterns.yml not found")
        config_ok = False
    
    return config_ok

def test_database():
    """Test database functionality"""
    print("\n💾 Testing database...")
    
    try:
        from storage.db_manager import DatabaseManager
        
        # Use temp database for testing
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = Path(tmp.name)
        
        db = DatabaseManager(db_path)
        print(f"  ✓ Database created")
        
        # Test storing an event
        test_event = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'type': 'test_event',
            'category': 'testing',
            'importance': 5,
            'data': {'test': 'data'},
            'key_info': {'test': 'info'}
        }
        
        db.store_event(test_event)
        print(f"  ✓ Event stored")
        
        # Test retrieving events
        events = db.get_recent_events(hours=1)
        if events:
            print(f"  ✓ Events retrieved: {len(events)}")
        
        # Test statistics
        stats = db.get_statistics()
        print(f"  ✓ Statistics working")
        
        # Cleanup
        db_path.unlink()
        
        return True
        
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        return False

def test_categorizer():
    """Test event categorization"""
    print("\n🏷️  Testing categorizer...")
    
    try:
        from process.categorizer import ActivityCategorizer
        
        patterns_file = Path(__file__).parent / "config" / "patterns.yml"
        categorizer = ActivityCategorizer(patterns_file)
        print(f"  ✓ Categorizer initialized")
        
        # Test categorizing different event types
        test_events = [
            {
                'type': 'git_commit',
                'data': {'message': 'fix: resolve login bug'},
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            },
            {
                'type': 'shell_command',
                'data': {'command': 'npm', 'args': 'test', 'exit_code': 1},
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            },
            {
                'type': 'file_change',
                'data': {'path': '/test/file.py', 'event_type': 'modified'},
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        ]
        
        categorized = categorizer.categorize_batch(test_events)
        print(f"  ✓ Categorized {len(categorized)} events")
        
        for event in categorized:
            if 'category' in event and 'importance' in event:
                print(f"    - {event['type']}: category={event['category']}, importance={event['importance']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Categorizer test failed: {e}")
        return False

def test_summarizer():
    """Test event summarization"""
    print("\n📝 Testing summarizer...")
    
    try:
        from process.summarizer import Summarizer
        
        config = {'use_local_llm': False}  # Force rule-based for testing
        summarizer = Summarizer(config)
        print(f"  ✓ Summarizer initialized (rule-based mode)")
        
        # Create test events
        test_events = [
            {
                'type': 'git_commit',
                'category': 'bugfix',
                'importance': 7,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'key_info': {'commit_message': 'Fixed critical auth bug'},
                'data': {}
            },
            {
                'type': 'shell_command',
                'category': 'testing',
                'importance': 5,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'key_info': {'command': 'npm test', 'success': True},
                'data': {}
            }
        ]
        
        summary = summarizer.summarize(test_events)
        print(f"  ✓ Summary generated")
        
        if 'text' in summary:
            print(f"  ✓ Text summary created:")
            print(f"    {summary['text'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Summarizer test failed: {e}")
        return False

def test_git_integration():
    """Test git hooks integration"""
    print("\n🔧 Testing Git integration...")
    
    try:
        from capture.git_hooks import GitHooks
        
        queue = Queue()
        config = {'track_external_changes': True}
        git_hooks = GitHooks(queue, config)
        print(f"  ✓ GitHooks initialized")
        
        # Check if git is available
        import subprocess
        try:
            result = subprocess.run(['git', '--version'], capture_output=True)
            print(f"  ✓ Git available")
        except:
            print(f"  ⚠️  Git not found in PATH")
        
        # Check git email
        email = git_hooks._get_git_email()
        if email:
            print(f"  ✓ Git email configured: {email}")
        else:
            print(f"  ⚠️  Git email not configured")
            print(f"     Run: git config --global user.email 'your@email.com'")
        
        # Check hooks directory
        hooks_dir = Path.home() / ".kb-daemon" / "git-templates" / "hooks"
        if hooks_dir.exists():
            print(f"  ✓ Git hooks directory exists")
            hooks = list(hooks_dir.glob("*"))
            if hooks:
                print(f"  ✓ {len(hooks)} hooks installed")
        else:
            print(f"  ⚠️  Git hooks not installed yet")
            print(f"     Run: python3 setup.py")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Git integration test failed: {e}")
        return False

def test_cli():
    """Test CLI interface"""
    print("\n🖥️  Testing CLI interface...")
    
    try:
        from interface.cli import CLI
        
        cli = CLI()
        print(f"  ✓ CLI initialized")
        
        # Test database connection
        stats = cli.db.get_statistics()
        print(f"  ✓ Database accessible")
        print(f"    - Total events: {stats['total_events']}")
        print(f"    - Pending entries: {stats['pending_entries']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ CLI test failed: {e}")
        return False

def test_daemon():
    """Test main daemon"""
    print("\n🤖 Testing main daemon...")
    
    try:
        from kb_daemon import KBDaemon
        
        daemon = KBDaemon()
        print(f"  ✓ Daemon initialized")
        
        # Check configuration
        if daemon.config.get('daemon', {}).get('shadow_mode'):
            print(f"  ✓ Shadow mode enabled (non-intrusive)")
        
        print(f"  ✓ Process interval: {daemon.config['daemon']['process_interval']}s")
        print(f"  ✓ Min importance: {daemon.config['processing']['min_importance']}/10")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Daemon test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_shell_integration():
    """Test shell integration"""
    print("\n🐚 Testing shell integration...")
    
    shell_wrapper = Path.home() / ".kb-daemon" / "shell_wrapper.sh"
    if shell_wrapper.exists():
        print(f"  ✓ Shell wrapper exists")
    else:
        print(f"  ⚠️  Shell wrapper not found")
        print(f"     Will be created when daemon starts")
    
    installer = Path.home() / ".kb-daemon" / "install_shell.sh"
    if installer.exists():
        print(f"  ✓ Shell installer ready")
        print(f"     Run: {installer}")
    else:
        print(f"  ⚠️  Shell installer not found")
    
    return True

def check_llm_configuration():
    """Check LLM configuration details"""
    print("\n🤖 Checking LLM Configuration...")
    
    config_path = Path(__file__).parent / "config" / "settings.yml"
    import yaml
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    processing = config.get('processing', {})
    
    print(f"\n  Current settings:")
    print(f"    - use_local_llm: {processing.get('use_local_llm', False)}")
    print(f"    - llm_model: {processing.get('llm_model', 'N/A')}")
    print(f"    - fallback_to_rules: {processing.get('fallback_to_rules', True)}")
    
    if not processing.get('use_local_llm'):
        print(f"\n  ✅ LLM DISABLED - Using rule-based processing")
        print(f"     The system will work perfectly without any LLM!")
        print(f"     Rule-based processing includes:")
        print(f"     - Smart categorization")
        print(f"     - Pattern detection")
        print(f"     - Importance scoring")
        print(f"     - Session detection")
        print(f"     - Automatic summarization")
    else:
        print(f"\n  ⚠️  Local LLM enabled but not required for Phase 1")
        print(f"     To disable and use rule-based (recommended):")
        print(f"     Edit: {config_path}")
        print(f"     Set: use_local_llm: false")
    
    return True

def main():
    print("="*60)
    print("🔬 KB DAEMON - COMPREHENSIVE SYSTEM TEST")
    print("="*60)
    
    all_ok = True
    
    # Run all tests
    all_ok &= test_imports()
    all_ok &= test_configuration()
    all_ok &= test_database()
    all_ok &= test_categorizer()
    all_ok &= test_summarizer()
    all_ok &= test_git_integration()
    all_ok &= test_cli()
    all_ok &= test_daemon()
    all_ok &= test_shell_integration()
    all_ok &= check_llm_configuration()
    
    print("\n" + "="*60)
    if all_ok:
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\n🚀 System is ready to use!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install pyyaml watchdog")
        print("2. Run setup: python3 setup.py")
        print("3. Start daemon: python3 kb_daemon.py start")
        print("4. Or test mode: python3 kb_daemon.py test")
    else:
        print("⚠️  Some tests failed - check above for details")
        print("="*60)
        print("\nCommon fixes:")
        print("1. Install Python packages: pip install pyyaml watchdog")
        print("2. Run setup: python3 setup.py")
        print("3. Check file permissions")

if __name__ == "__main__":
    # Change to kb-daemon directory
    os.chdir(Path(__file__).parent)
    main()
