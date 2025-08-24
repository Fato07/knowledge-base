#!/usr/bin/env python3
"""
KB Daemon Launcher - Properly daemonize the process
"""

import os
import sys
import subprocess
from pathlib import Path

def start_daemon_background():
    """Start KB daemon in background"""
    
    daemon_path = Path(__file__).parent / "kb_daemon.py"
    pid_file = Path(__file__).parent / "daemon.pid"
    
    # Check if already running
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            # Check if process exists
            os.kill(pid, 0)
            print(f"⚠️  KB Daemon already running (PID: {pid})")
            return False
        except (ProcessLookupError, ValueError):
            # Process doesn't exist, remove stale PID file
            pid_file.unlink()
    
    print("🚀 Starting KB Daemon in background...")
    
    # Start daemon in background using subprocess
    process = subprocess.Popen(
        [sys.executable, str(daemon_path), "start"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True  # Detach from terminal
    )
    
    # Save PID
    pid_file.write_text(str(process.pid))
    
    print(f"✅ KB Daemon started (PID: {process.pid})")
    print("   Run 'kb status' to check status")
    print("   Run 'kb stop' to stop the daemon")
    
    return True

if __name__ == "__main__":
    start_daemon_background()
