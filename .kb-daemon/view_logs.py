#!/usr/bin/env python3
"""
KB Daemon Log Viewer - Easy way to view captured data
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def view_logs():
    print("\n" + "="*60)
    print("📊 KB DAEMON - LOG VIEWER")
    print("="*60)
    
    # Check both log locations
    kb_logs = Path.home() / "DEV" / "knowledge-base" / ".kb-daemon" / "logs"
    capture_dir = Path.home() / ".kb-daemon" / "capture"
    
    print("\n📁 Log Locations:")
    print(f"  1. Shadow logs: {kb_logs}")
    print(f"  2. Capture dir: {capture_dir}")
    
    # Show shadow logs
    if kb_logs.exists():
        shadow_files = sorted(kb_logs.glob("shadow_*.json"), reverse=True)
        if shadow_files:
            print(f"\n🌙 Shadow Mode Logs ({len(shadow_files)} files):")
            for i, f in enumerate(shadow_files[:5], 1):
                size = f.stat().st_size
                print(f"  {i}. {f.name} ({size} bytes)")
            
            # Show latest
            latest = shadow_files[0]
            print(f"\n📋 Latest Shadow Log: {latest.name}")
            with open(latest) as f:
                events = json.load(f)
            
            print(f"  Events captured: {len(events)}")
            
            # Summarize by category
            categories = {}
            for event in events:
                cat = event.get('category', 'unknown')
                categories[cat] = categories.get(cat, 0) + 1
            
            print("\n  By Category:")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"    - {cat}: {count}")
            
            # Show recent activity
            print("\n  Recent Activity (last 5):")
            for event in events[-5:]:
                timestamp = event.get('timestamp', 'unknown')
                category = event.get('category', 'unknown')
                importance = event.get('importance', 0)
                
                # Extract description
                if event.get('type') == 'file_change':
                    desc = f"Modified: {event.get('key_info', {}).get('file', 'unknown')}"
                elif event.get('type') == 'pattern_detected':
                    desc = f"Pattern: {event.get('data', {}).get('pattern', 'unknown')}"
                else:
                    desc = event.get('type', 'unknown')
                
                print(f"    • [{importance}/10] {category}: {desc}")
    
    # Show shell events
    shell_events = capture_dir / "shell_events.jsonl"
    if shell_events.exists():
        print(f"\n🐚 Shell Events:")
        with open(shell_events) as f:
            lines = f.readlines()
        print(f"  Total events: {len(lines)}")
        
        if lines:
            print("  Recent commands:")
            for line in lines[-5:]:
                try:
                    event = json.loads(line)
                    if event['type'] == 'dir_change':
                        print(f"    • Changed to: {event['data']['to']}")
                    elif event['type'] == 'shell_command':
                        print(f"    • Command: {event['data'].get('command', 'unknown')}")
                except:
                    pass
    
    # Show git events
    git_events = capture_dir / "git_events.jsonl"
    if git_events.exists():
        print(f"\n🔧 Git Events:")
        with open(git_events) as f:
            lines = f.readlines()
        print(f"  Total events: {len(lines)}")
    
    print("\n" + "="*60)
    print("💡 To review and approve entries:")
    print("   python3 interface/cli.py review")
    print("="*60)

if __name__ == "__main__":
    view_logs()
