#!/usr/bin/env python3
"""
File Watcher - Monitors file system changes for intelligent capture
"""

import os
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional
from queue import Queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

class FileWatcher:
    """Watches file system for relevant changes"""
    
    def __init__(self, capture_queue: Queue, config: Dict, base_path=None):
        self.capture_queue = capture_queue
        self.config = config
        self.running = False
        self.observer = None
        
        # Paths to watch
        self.watch_paths = self._get_watch_paths()
        
        # Ignore patterns
        self.ignore_patterns = set([
            '.git', '__pycache__', 'node_modules', '.venv', 'venv',
            '.env', '*.pyc', '*.log', '.DS_Store', '*.swp', '*.swo',
            'dist', 'build', 'coverage', '.pytest_cache'
        ])
        
        # Track recent changes to detect patterns
        self.recent_changes = []
        
    def _get_watch_paths(self) -> List[Path]:
        """Get list of paths to watch"""
        paths = []
        
        # Default to watching current projects
        dev_path = Path.home() / "DEV"
        if dev_path.exists():
            # Only watch specific project directories, not all
            for project in dev_path.iterdir():
                if project.is_dir() and not project.name.startswith('.'):
                    paths.append(project)
                    
        return paths[:5]  # Limit to 5 most recent projects to avoid overwhelming
        
    def start(self):
        """Start watching file system"""
        if not self.watch_paths:
            print("No paths to watch")
            return
            
        self.running = True
        self.observer = Observer()
        
        event_handler = KBFileEventHandler(self)
        
        for path in self.watch_paths:
            if path.exists():
                self.observer.schedule(event_handler, str(path), recursive=True)
                print(f"Watching: {path}")
                
        self.observer.start()
        
        # Start pattern detection thread
        pattern_thread = threading.Thread(target=self._detect_patterns, daemon=True)
        pattern_thread.start()
        
    def stop(self):
        """Stop watching"""
        self.running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
            
    def should_ignore(self, path: str) -> bool:
        """Check if a path should be ignored"""
        path_obj = Path(path)
        
        # Check each part of the path
        for part in path_obj.parts:
            for pattern in self.ignore_patterns:
                if pattern.startswith('*'):
                    if part.endswith(pattern[1:]):
                        return True
                elif part == pattern:
                    return True
                    
        return False
        
    def process_file_event(self, event: FileSystemEvent):
        """Process a file system event"""
        if self.should_ignore(event.src_path):
            return
            
        # Create event data
        event_data = {
            'type': 'file_change',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'data': {
                'path': event.src_path,
                'event_type': event.event_type,
                'is_directory': event.is_directory
            }
        }
        
        # Categorize the event
        category = self._categorize_file_event(event)
        if not category:
            return  # Skip unimportant events
            
        event_data['category'] = category
        event_data['importance'] = self._calculate_file_importance(event, category)
        
        # Track for pattern detection
        self.recent_changes.append(event_data)
        if len(self.recent_changes) > 100:
            self.recent_changes.pop(0)
            
        # Add to queue if important enough
        if event_data['importance'] >= 3:
            self.capture_queue.put(event_data)
            
    def _categorize_file_event(self, event: FileSystemEvent) -> Optional[str]:
        """Categorize a file event"""
        path = Path(event.src_path)
        name = path.name
        suffix = path.suffix
        
        # Test files
        if 'test' in name.lower() or 'spec' in name.lower():
            if event.event_type == 'created':
                return 'test_created'
            elif event.event_type == 'modified':
                return 'test_modified'
                
        # Configuration files
        elif name in ['package.json', 'Cargo.toml', 'pyproject.toml', 'docker-compose.yml']:
            return 'config_change'
            
        # Documentation
        elif suffix in ['.md', '.rst', '.txt'] and 'README' in name.upper():
            return 'documentation'
            
        # Source code
        elif suffix in ['.py', '.js', '.ts', '.jsx', '.tsx', '.rs', '.go', '.java']:
            if event.event_type == 'created':
                return 'code_created'
            elif event.event_type == 'modified':
                return 'code_modified'
                
        # Skip other events
        return None
        
    def _calculate_file_importance(self, event: FileSystemEvent, category: str) -> int:
        """Calculate importance of a file event"""
        importance = 3  # Base
        
        # Higher importance for certain categories
        if category in ['test_created', 'config_change']:
            importance = 6
        elif category == 'documentation':
            importance = 5
        elif category == 'code_created':
            importance = 5
        elif category == 'code_modified':
            importance = 4
            
        # Boost for certain files
        path = Path(event.src_path)
        if path.name in ['package.json', 'requirements.txt', 'Cargo.toml']:
            importance += 2
            
        return min(importance, 10)
        
    def _detect_patterns(self):
        """Detect patterns in file changes"""
        while self.running:
            time.sleep(30)  # Check every 30 seconds
            
            if len(self.recent_changes) < 5:
                continue
                
            # Detect refactoring (many files changed in short time)
            recent_window = [
                c for c in self.recent_changes[-20:]
                if (datetime.utcnow() - datetime.fromisoformat(c['timestamp'].rstrip('Z'))).seconds < 300
            ]
            
            if len(recent_window) > 10:
                # Many files changed recently
                pattern_event = {
                    'type': 'pattern_detected',
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'category': 'refactoring_session',
                    'importance': 7,
                    'data': {
                        'files_changed': len(recent_window),
                        'pattern': 'refactoring'
                    }
                }
                self.capture_queue.put(pattern_event)
                
            # Detect test-driven development (test file changes followed by code changes)
            test_changes = [c for c in recent_window if 'test' in c.get('category', '')]
            code_changes = [c for c in recent_window if 'code' in c.get('category', '')]
            
            if test_changes and code_changes:
                if test_changes[0]['timestamp'] < code_changes[0]['timestamp']:
                    pattern_event = {
                        'type': 'pattern_detected',
                        'timestamp': datetime.utcnow().isoformat() + 'Z',
                        'category': 'tdd_session',
                        'importance': 6,
                        'data': {
                            'pattern': 'test_driven_development'
                        }
                    }
                    self.capture_queue.put(pattern_event)


class KBFileEventHandler(FileSystemEventHandler):
    """Handles file system events for KB daemon"""
    
    def __init__(self, watcher: FileWatcher):
        self.watcher = watcher
        
    def on_created(self, event):
        self.watcher.process_file_event(event)
        
    def on_modified(self, event):
        self.watcher.process_file_event(event)
        
    def on_deleted(self, event):
        # Generally less important
        pass
        
    def on_moved(self, event):
        # Could indicate refactoring
        if not self.watcher.should_ignore(event.dest_path):
            self.watcher.process_file_event(event)
