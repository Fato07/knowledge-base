#!/usr/bin/env python3
"""
Import shadow logs into database for review
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from storage.db_manager import DatabaseManager
from process.categorizer import ActivityCategorizer
from process.summarizer import Summarizer

def import_shadow_logs():
    """Import shadow logs into the database"""
    print("\n📥 Importing shadow logs into database...")
    
    # Initialize components
    db = DatabaseManager(Path.home() / ".kb-daemon" / "storage" / "kb_store.db")
    
    # Find shadow logs
    logs_dir = Path(__file__).parent / "logs"
    shadow_files = sorted(logs_dir.glob("shadow_*.json"), reverse=True)
    
    if not shadow_files:
        print("❌ No shadow logs found")
        return False
    
    total_imported = 0
    
    for shadow_file in shadow_files[:5]:  # Import last 5 shadow logs
        print(f"\n📄 Processing: {shadow_file.name}")
        
        with open(shadow_file) as f:
            events = json.load(f)
        
        # Filter for important events (importance >= 3)
        important_events = [e for e in events if e.get('importance', 0) >= 3]
        
        print(f"  Found {len(important_events)} important events")
        
        # Store each event in database
        for event in important_events:
            try:
                db.store_event(event)
                total_imported += 1
            except Exception as e:
                print(f"  ⚠️  Error storing event: {e}")
    
    print(f"\n✅ Imported {total_imported} events into database")
    
    # Show statistics
    stats = db.get_statistics()
    print(f"\n📊 Database Statistics:")
    print(f"  Total events: {stats['total_events']}")
    print(f"  Categories: {', '.join(stats['events_by_category'].keys())}")
    
    return True

def main():
    """Main entry point"""
    import_shadow_logs()
    
    print("\n" + "="*60)
    print("✅ Shadow logs imported!")
    print("="*60)
    print("\n🎯 Now you can run the review:")
    print("   kb review")
    print("\nOr directly:")
    print("   python3 interface/cli.py review")

if __name__ == "__main__":
    main()
