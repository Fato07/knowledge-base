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
        self.git_hooks = GitHooks(self.capture_queue, self.config['git'])
        self.shell_monitor = ShellMonitor(self.capture_queue, self.config['capture'])
        self.file_watcher = FileWatcher(self.capture_queue, self.config['capture'])
        
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
    parser.add_argument('command', choices=['start', 'stop', 'status', 'review', 'test'],
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
        # TODO: Check if daemon is running
        print("Status command not yet implemented")
    elif args.command == 'review':
        cli = CLI()
        cli.daily_review()
    elif args.command == 'test':
        print("Testing KB Daemon configuration...")
        daemon = KBDaemon(args.config)
        print("✓ Configuration loaded successfully")
        print("✓ Database initialized")
        print("✓ All modules loaded")
        print("\nKB Daemon is ready to start!")

if __name__ == "__main__":
    main()
