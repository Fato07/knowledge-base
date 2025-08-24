#!/usr/bin/env python3
"""
Process Manager - Handle daemon start/stop with PID file
"""

import os
import sys
import signal
import psutil
from pathlib import Path
from typing import Optional

class ProcessManager:
    """Manage daemon process lifecycle"""
    
    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path(__file__).parent.parent
        self.pid_file = self.base_path / "daemon.pid"
    
    def start_daemon(self) -> bool:
        """Start the daemon and save PID"""
        # Check if already running
        if self.is_running():
            pid = self.get_pid()
            print(f"⚠️  KB Daemon already running (PID: {pid})")
            return False
        
        # Save current process PID
        pid = os.getpid()
        self.save_pid(pid)
        print(f"✅ KB Daemon started (PID: {pid})")
        return True
    
    def stop_daemon(self) -> bool:
        """Stop the running daemon"""
        if not self.is_running():
            print("○ KB Daemon is not running")
            # Clean up stale PID file if exists
            if self.pid_file.exists():
                self.pid_file.unlink()
            return False
        
        pid = self.get_pid()
        if not pid:
            print("⚠️  PID file exists but is empty")
            self.pid_file.unlink()
            return False
        
        try:
            # Try graceful termination first
            print(f"🛑 Stopping KB Daemon (PID: {pid})...")
            process = psutil.Process(pid)
            
            # Send SIGTERM for graceful shutdown
            process.terminate()
            
            # Wait up to 5 seconds for process to terminate
            try:
                process.wait(timeout=5)
                print("✅ KB Daemon stopped gracefully")
            except psutil.TimeoutExpired:
                # Force kill if not terminated
                print("⚠️  Graceful shutdown timed out, forcing stop...")
                process.kill()
                process.wait(timeout=2)
                print("✅ KB Daemon force stopped")
            
            # Clean up PID file
            self.pid_file.unlink()
            return True
            
        except psutil.NoSuchProcess:
            print(f"⚠️  Process {pid} not found (already terminated)")
            # Clean up stale PID file
            self.pid_file.unlink()
            return False
        except psutil.AccessDenied:
            print(f"❌ Access denied to stop process {pid}")
            print("   Try: sudo kb stop")
            return False
        except Exception as e:
            print(f"❌ Error stopping daemon: {e}")
            return False
    
    def is_running(self) -> bool:
        """Check if daemon is currently running"""
        pid = self.get_pid()
        if not pid:
            return False
        
        try:
            # Check if process exists and is our daemon
            process = psutil.Process(pid)
            
            # Verify it's actually our KB daemon
            cmdline = ' '.join(process.cmdline())
            if 'kb_daemon.py' in cmdline:
                return True
            else:
                # PID exists but it's not our daemon
                print(f"⚠️  PID {pid} exists but is not KB daemon")
                self.pid_file.unlink()
                return False
                
        except psutil.NoSuchProcess:
            # Process doesn't exist
            if self.pid_file.exists():
                self.pid_file.unlink()
            return False
        except psutil.AccessDenied:
            # Can't access process info, assume it's running
            return True
    
    def get_pid(self) -> Optional[int]:
        """Get PID from file"""
        if not self.pid_file.exists():
            return None
        
        try:
            pid_text = self.pid_file.read_text().strip()
            return int(pid_text) if pid_text else None
        except (ValueError, IOError):
            return None
    
    def save_pid(self, pid: int):
        """Save PID to file"""
        self.pid_file.write_text(str(pid))
    
    def cleanup(self):
        """Clean up PID file on exit"""
        if self.pid_file.exists():
            current_pid = os.getpid()
            saved_pid = self.get_pid()
            
            # Only remove if it's our PID
            if current_pid == saved_pid:
                self.pid_file.unlink()
    
    def get_status(self) -> dict:
        """Get detailed daemon status"""
        is_running = self.is_running()
        pid = self.get_pid()
        
        status = {
            'running': is_running,
            'pid': pid,
            'pid_file': str(self.pid_file),
            'uptime': None,
            'memory_usage': None,
            'cpu_percent': None
        }
        
        if is_running and pid:
            try:
                process = psutil.Process(pid)
                status['uptime'] = process.create_time()
                status['memory_usage'] = process.memory_info().rss / 1024 / 1024  # MB
                status['cpu_percent'] = process.cpu_percent(interval=0.1)
            except:
                pass
        
        return status


# Daemon stop function using subprocess (for external calls)
def stop_daemon_external():
    """Stop daemon from external command"""
    import subprocess
    
    # First try using psutil/PID file
    manager = ProcessManager()
    if manager.stop_daemon():
        return True
    
    # Fallback to pkill if PID method fails
    try:
        # Try to find and kill using pgrep/pkill
        result = subprocess.run(
            ['pgrep', '-f', 'kb_daemon.py.*start'],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    subprocess.run(['kill', '-TERM', pid], check=True)
                    print(f"✅ Stopped process {pid}")
                except:
                    subprocess.run(['kill', '-9', pid], check=False)
            return True
        else:
            print("○ No KB daemon process found")
            return False
            
    except Exception as e:
        print(f"❌ Error stopping daemon: {e}")
        return False


if __name__ == "__main__":
    # Test the process manager
    manager = ProcessManager()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'stop':
            manager.stop_daemon()
        elif sys.argv[1] == 'status':
            status = manager.get_status()
            print(f"Status: {status}")
        elif sys.argv[1] == 'start':
            manager.start_daemon()
