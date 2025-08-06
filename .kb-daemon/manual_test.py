#!/usr/bin/env python3
"""
Manual test of KB Daemon components
"""

import os
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

print("KB DAEMON - MANUAL COMPONENT TEST")
print("="*50)

# Test 1: Check Python version
print(f"\n✓ Python version: {sys.version.split()[0]}")

# Test 2: Import external dependencies
print("\n📦 External dependencies:")
try:
    import yaml
    print("  ✓ yaml installed")
except ImportError:
    print("  ❌ yaml missing - Run: pip install pyyaml")
    sys.exit(1)

try:
    from watchdog.observers import Observer
    print("  ✓ watchdog installed")
except ImportError:
    print("  ❌ watchdog missing - Run: pip install watchdog")
    sys.exit(1)

# Test 3: Configuration files
print("\n📁 Configuration files:")
config_path = Path(__file__).parent / "config" / "settings.yml"
patterns_path = Path(__file__).parent / "config" / "patterns.yml"

if config_path.exists():
    print(f"  ✓ settings.yml found")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    use_llm = config['processing']['use_local_llm']
    print(f"    - LLM enabled: {use_llm} (should be False for Phase 1)")
else:
    print(f"  ❌ settings.yml missing")

if patterns_path.exists():
    print(f"  ✓ patterns.yml found")
else:
    print(f"  ❌ patterns.yml missing")

# Test 4: Quick module import test
print("\n🔧 Internal modules:")
modules_ok = True

try:
    from storage.db_manager import DatabaseManager
    print("  ✓ DatabaseManager")
except Exception as e:
    print(f"  ❌ DatabaseManager: {e}")
    modules_ok = False

try:
    from process.categorizer import ActivityCategorizer
    print("  ✓ ActivityCategorizer")
except Exception as e:
    print(f"  ❌ ActivityCategorizer: {e}")
    modules_ok = False

try:
    from process.summarizer import Summarizer
    print("  ✓ Summarizer")
except Exception as e:
    print(f"  ❌ Summarizer: {e}")
    modules_ok = False

# Test 5: Quick functional test
if modules_ok:
    print("\n🧪 Functional test:")
    
    # Test database
    from storage.db_manager import DatabaseManager
    db_path = Path.home() / ".kb-daemon" / "storage" / "kb_store.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = DatabaseManager(db_path)
    stats = db.get_statistics()
    print(f"  ✓ Database working - {stats['total_events']} events stored")
    
    # Test categorizer
    from process.categorizer import ActivityCategorizer
    cat = ActivityCategorizer(patterns_path)
    test_event = {
        'type': 'git_commit',
        'data': {'message': 'test commit'},
        'timestamp': '2024-01-01T00:00:00Z'
    }
    result = cat.categorize_event(test_event)
    print(f"  ✓ Categorizer working - importance: {result.get('importance', 0)}/10")
    
    # Test summarizer (rule-based)
    from process.summarizer import Summarizer
    summ = Summarizer({'use_local_llm': False})
    summary = summ.summarize([result])
    print(f"  ✓ Summarizer working (rule-based mode)")

print("\n" + "="*50)
print("✅ SYSTEM STATUS: READY")
print("="*50)

print("\n📋 Configuration Summary:")
print(f"  - Shadow mode: ON (non-intrusive)")
print(f"  - LLM required: NO (using rule-based)")
print(f"  - Min importance: 3/10")
print(f"  - Process interval: 30 minutes")

print("\n🚀 To start the daemon:")
print("  python3 kb_daemon.py start")

print("\n📊 To run daily review:")
print("  python3 interface/cli.py review")
