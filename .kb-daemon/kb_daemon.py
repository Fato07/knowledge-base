#!/usr/bin/env python3
"""
KB Daemon - Main entry point for the intelligent KB automation system
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
import subprocess
import time
from queue import Queue
from threading import Thread

# Add the kb-daemon directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from capture.git_hooks import GitHooks
from capture.shell_monitor import ShellMonitor
from capture.file_watcher import FileWatcher
from capture.project_detector import ProjectDetector
from process.categorizer import ActivityCategorizer
from process.summarizer import Summarizer
from storage.db_manager import DatabaseManager
from interface.cli import CLI

class KBDaemon:
    """Main daemon orchestrator for KB intelligence system"""
    
    def __init__(self, config_path: str = None):
        self.base_path = Path(__file__).parent
        self.config_path = config_path or self.base_path / "config" / "settings.yml"
        self.config = self._load_config()
        
        # Initialize logging
        self._setup_logging()
        
        # Initialize components
        self.capture_queue = Queue()
        self.db = DatabaseManager(self.base_path / "storage" / "kb_store.db")
        self.categorizer = ActivityCategorizer(self.base_path / "config" / "patterns.yml")
        self.summarizer = Summarizer(self.config['processing'])
        
        # Initialize capture modules
        self.git_hooks = GitHooks(self.capture_queue, self.config['git'], self.base_path)
        self.shell_monitor = ShellMonitor(self.capture_queue, self.config['capture'], self.base_path)
        self.file_watcher = FileWatcher(self.capture_queue, self.config['capture'], self.base_path)
        
        # Initialize project detector
        self.project_detector = ProjectDetector(self.base_path)
        self.current_project = None
        
        self.running = False
        
    def _load_config(self) -> Dict:
        """Load configuration from YAML file"""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = self.base_path / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"kb_daemon_{datetime.now():%Y%m%d}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def start(self):
        """Start the daemon"""
        self.logger.info("Starting KB Daemon...")
        self.running = True
        
        # Start capture threads
        threads = [
            Thread(target=self.shell_monitor.start, daemon=True),
            Thread(target=self.file_watcher.start, daemon=True),
            Thread(target=self.process_queue, daemon=True),
        ]
        
        for t in threads:
            t.start()
            
        self.logger.info("KB Daemon started successfully")
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the daemon"""
        self.logger.info("Stopping KB Daemon...")
        self.running = False
        self.shell_monitor.stop()
        self.file_watcher.stop()
        self.logger.info("KB Daemon stopped")
        
    def process_queue(self):
        """Process captured events periodically"""
        events_buffer = []
        last_process_time = time.time()
        
        while self.running:
            # Check if it's time to process
            current_time = time.time()
            should_process = (
                current_time - last_process_time >= self.config['daemon']['process_interval']
                or len(events_buffer) >= self.config['processing']['batch_size']
            )
            
            # Collect events from queue
            while not self.capture_queue.empty() and len(events_buffer) < 1000:
                try:
                    event = self.capture_queue.get_nowait()
                    events_buffer.append(event)
                except:
                    break
            
            # Process if we should
            if should_process and events_buffer:
                self._process_events(events_buffer)
                events_buffer = []
                last_process_time = current_time
            
            time.sleep(1)  # Small delay to prevent CPU spinning
            
    def _process_events(self, events: List[Dict]):
        """Process a batch of events"""
        self.logger.info(f"Processing {len(events)} events")
        
        # Add project context to each event
        for event in events:
            # Detect project from event path if available
            event_path = event.get('data', {}).get('working_dir') or event.get('data', {}).get('path')
            if event_path:
                project = self.project_detector.detect_project(Path(event_path))
            else:
                project = self.project_detector.detect_project()
            
            # Add project context
            event['project'] = {
                'name': project['name'],
                'type': project['type'],
                'path': project['path']
            }
            
            # Track project switches
            if self.current_project and self.current_project['name'] != project['name']:
                switch_event = self.project_detector.track_project_switch(
                    self.current_project, project
                )
                events.append(switch_event)
            
            self.current_project = project
        
        # Categorize events
        categorized = self.categorizer.categorize_batch(events)
        
        # Filter by importance
        important_events = [
            e for e in categorized 
            if e.get('importance', 0) >= self.config['processing']['min_importance']
        ]
        
        if not important_events:
            self.logger.info("No important events to process")
            return
        
        # Summarize if needed
        if len(important_events) > 5:
            summary = self.summarizer.summarize(important_events)
            self.db.store_summary(summary)
        else:
            # Store individual events
            for event in important_events:
                self.db.store_event(event)
        
        self.logger.info(f"Processed and stored {len(important_events)} important events")
        
        # If in shadow mode, just log what would be captured
        if self.config['daemon'].get('shadow_mode', False):
            self._log_shadow_mode_capture(important_events)
    
    def _log_shadow_mode_capture(self, events: List[Dict]):
        """Log what would be captured in shadow mode"""
        shadow_log = self.base_path / "logs" / f"shadow_{datetime.now():%Y%m%d_%H%M%S}.json"
        with open(shadow_log, 'w') as f:
            json.dump(events, f, indent=2, default=str)
        self.logger.info(f"Shadow mode: Would capture {len(events)} events. See {shadow_log}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="KB Daemon - Intelligent Knowledge Base Automation")
    parser.add_argument('command', choices=['start', 'stop', 'status', 'review', 'test', 'full'],
                       help='Command to execute')
    parser.add_argument('--config', help='Path to config file')
    
    args = parser.parse_args()
    
    if args.command == 'start':
        daemon = KBDaemon(args.config)
        daemon.start()
    elif args.command == 'stop':
        # TODO: Implement proper daemon stop via PID file
        print("Stop command not yet implemented")
    elif args.command == 'status':
        # Check if daemon is running
        daemon_running = False
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['cmdline'] and 'kb_daemon.py' in ' '.join(proc.info['cmdline']) and 'start' in ' '.join(proc.info['cmdline']):
                    daemon_running = True
                    break
        except ImportError:
            # If psutil not installed, use subprocess
            result = subprocess.run(['pgrep', '-f', 'kb_daemon.py'], capture_output=True, text=True)
            daemon_running = bool(result.stdout.strip())
        except Exception:
            # Fallback to subprocess if psutil fails
            result = subprocess.run(['pgrep', '-f', 'kb_daemon.py'], capture_output=True, text=True)
            daemon_running = bool(result.stdout.strip())
        
        # Get database statistics
        base_path = Path(__file__).parent
        db = DatabaseManager(base_path / "storage" / "kb_store.db")
        stats = db.get_statistics()
        
        # Display status
        print("📈 KB Daemon Status")
        if daemon_running:
            print("✅ Daemon is running")
        else:
            print("○ Daemon is not running")
        
        # Show recent captures from shadow logs
        logs_dir = base_path / "logs"
        shadow_logs = list(logs_dir.glob("shadow_*.json"))
        recent_events = 0
        if shadow_logs:
            for log_file in shadow_logs:
                try:
                    with open(log_file) as f:
                        events = json.load(f)
                        recent_events += len(events)
                except:
                    pass
        
        print(f"\nRecent captures: {recent_events} events")
        
        if stats:
            print(f"\n📊 Database Statistics:")
            print(f"  Total events: {stats.get('total_events', 0)}")
            print(f"  Average importance: {stats.get('average_importance', 0):.2f}/10")
            pending = stats.get('pending_entries', 0)
            if pending > 0:
                print(f"  Pending reviews: {pending}")
                print(f"\n💡 Run 'kb review' to process pending events")
    elif args.command == 'review':
        # Determine base_path
        if args.config:
            daemon = KBDaemon(args.config)
            base_path = daemon.base_path
        else:
            base_path = Path(__file__).parent
        
        cli = CLI(base_path)
        cli.daily_review()
    elif args.command == 'test':
        print("Testing KB Daemon configuration...")
        daemon = KBDaemon(args.config)
        print("✓ Configuration loaded successfully")
        print("✓ Database initialized")
        print("✓ All modules loaded")
        print("\nKB Daemon is ready to start!")
    elif args.command == 'full':
        # Full sync: Review + Basic Memory sync
        print("🔄 KB Full Sync - Review + Graph Update")
        print("=" * 60)
        
        # Step 1: Run review
        print("\n📊 Step 1: Running daily review...")
        base_path = Path(__file__).parent
        cli = CLI(base_path)
        cli.daily_review()
        
        # Step 2: Sync to Basic Memory
        print("\n📈 Step 2: Syncing to knowledge graph...")
        import subprocess
        kb_path = Path.home() / "DEV" / "knowledge-base"
        
        # Check if uvx is available
        try:
            subprocess.run(["which", "uvx"], check=True, capture_output=True)
            print("Found uvx, syncing with Basic Memory...")
            
            # Change to knowledge-base directory and run sync
            result = subprocess.run(
                ["uvx", "--from", "basic-memory", "sync"],
                cwd=kb_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Graph sync complete!")
            else:
                print(f"⚠️  Graph sync failed: {result.stderr}")
        except subprocess.CalledProcessError:
            print("⚠️  uvx not found")
            print("Basic Memory might not be installed.")
            print("")
            print("To install Basic Memory:")
            print("  1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh")
            print("  2. Run: uvx --from basic-memory sync")
            print("")
            print("Graph sync skipped - only markdown files were created")
        
        print("\n" + "=" * 60)
        print("✅ Full sync complete!")
        print("=" * 60)

if __name__ == "__main__":
    main()
