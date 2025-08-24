#!/usr/bin/env python3
"""
Debug KB Daemon PID issues
"""

import os
import subprocess
from pathlib import Path

print("🔍 Debugging KB Daemon Process")
print("=" * 60)

# Check for PID file
pid_file = Path("/Users/fathindosunmu/DEV/knowledge-base/.kb-daemon/daemon.pid")
print(f"\n📁 PID file location: {pid_file}")
print(f"   Exists: {pid_file.exists()}")

if pid_file.exists():
    print(f"   Content: {pid_file.read_text().strip()}")

# Check for running processes
print("\n🔄 Running KB processes:")
result = subprocess.run(['pgrep', '-fl', 'kb_daemon.py'], capture_output=True, text=True)
if result.stdout:
    print(result.stdout)
else:
    print("   No processes found with pgrep")

# Check with ps
print("\n📊 PS output:")
result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
for line in result.stdout.split('\n'):
    if 'kb_daemon' in line and 'grep' not in line:
        print(f"   {line[:120]}...")

# Check different possible PID file locations
possible_locations = [
    Path("/Users/fathindosunmu/DEV/knowledge-base/.kb-daemon/daemon.pid"),
    Path("/Users/fathindosunmu/.kb-daemon/daemon.pid"),
    Path.home() / ".kb-daemon" / "daemon.pid",
    Path.cwd() / "daemon.pid"
]

print("\n📍 Checking possible PID file locations:")
for loc in possible_locations:
    if loc.exists():
        print(f"   ✅ Found at: {loc}")
        print(f"      Content: {loc.read_text().strip()}")
    else:
        print(f"   ❌ Not at: {loc}")

print("\n" + "=" * 60)
