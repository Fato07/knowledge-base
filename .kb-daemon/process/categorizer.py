#!/usr/bin/env python3
"""
Activity Categorizer - Categorizes and scores captured events
"""

import yaml
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class ActivityCategorizer:
    """Categorizes activities based on patterns"""
    
    def __init__(self, patterns_file: Path):
        self.patterns = self._load_patterns(patterns_file)
        self.context_window = []  # Recent events for context
        
    def _load_patterns(self, patterns_file: Path) -> Dict:
        """Load patterns from YAML file"""
        with open(patterns_file, 'r') as f:
            return yaml.safe_load(f)
            
    def categorize_batch(self, events: List[Dict]) -> List[Dict]:
        """Categorize a batch of events"""
        categorized = []
        
        for event in events:
            # Add to context window
            self.context_window.append(event)
            if len(self.context_window) > 50:
                self.context_window.pop(0)
                
            # Categorize individual event
            categorized_event = self.categorize_event(event)
            
            # Check for session patterns
            session = self._detect_session()
            if session:
                categorized_event['session'] = session
                
            categorized.append(categorized_event)
            
        return categorized
        
    def categorize_event(self, event: Dict) -> Dict:
        """Categorize a single event"""
        event_type = event.get('type', '')
        
        # If already categorized, enhance it
        if 'category' in event:
            event = self._enhance_category(event)
        else:
            # Determine category
            event['category'] = self._determine_category(event)
            
        # Calculate importance if not set
        if 'importance' not in event:
            event['importance'] = self._calculate_importance(event)
            
        # Extract key information
        event['key_info'] = self._extract_key_info(event)
        
        return event
        
    def _determine_category(self, event: Dict) -> str:
        """Determine the category of an event"""
        event_type = event.get('type', '')
        data = event.get('data', {})
        
        # Check against patterns
        for category, pattern_def in self.patterns['detection_patterns'].items():
            if self._matches_pattern(event, pattern_def):
                return category
                
        # Default categories by type
        if event_type == 'git_commit':
            return 'development'
        elif event_type == 'shell_command':
            command = data.get('command', '')
            if command in ['npm', 'yarn', 'pip', 'cargo']:
                return 'dependency_management'
            elif command in ['pytest', 'jest', 'test']:
                return 'testing'
            elif command == 'docker':
                return 'containerization'
                
        return 'general'
        
    def _matches_pattern(self, event: Dict, pattern_def: Dict) -> bool:
        """Check if event matches a pattern definition"""
        indicators = pattern_def.get('indicators', [])
        keywords = pattern_def.get('keywords', [])
        
        event_str = str(event).lower()
        
        # Check keywords
        for keyword in keywords:
            if keyword.lower() in event_str:
                return True
                
        # Check indicators
        data = event.get('data', {})
        for indicator in indicators:
            if indicator == 'error_in_output' and data.get('exit_code', 0) != 0:
                return True
            elif indicator == 'multiple_test_runs':
                # Check context window for multiple test runs
                test_runs = [e for e in self.context_window[-5:] 
                           if 'test' in str(e).lower()]
                if len(test_runs) >= 2:
                    return True
                    
        return False
        
    def _enhance_category(self, event: Dict) -> Dict:
        """Enhance an already categorized event"""
        category = event.get('category', '')
        
        # Add subcategory based on patterns
        if category == 'testing':
            if event.get('is_error'):
                event['subcategory'] = 'test_failure'
            elif event.get('fixes_error'):
                event['subcategory'] = 'test_fix'
                
        elif category == 'git_commit':
            message = event.get('data', {}).get('message', '')
            if 'WIP' in message:
                event['subcategory'] = 'work_in_progress'
                event['importance'] = max(event.get('importance', 5) - 2, 1)
                
        return event
        
    def _calculate_importance(self, event: Dict) -> int:
        """Calculate importance score for an event"""
        category = event.get('category', '')
        event_type = event.get('type', '')
        
        # Get base importance from patterns
        importance_factors = self.patterns.get('importance_scoring', {}).get('factors', {})
        
        # Start with category-based importance
        base_importance = importance_factors.get(category, 5)
        
        # Adjust based on specific factors
        data = event.get('data', {})
        
        # Breaking changes are always important
        if 'breaking' in str(event).lower():
            base_importance = max(base_importance, 9)
            
        # Errors are important
        if event.get('is_error'):
            base_importance = min(base_importance + 2, 10)
            
        # External changes are important to track
        if event.get('external_commits'):
            base_importance = max(base_importance, 7)
            
        # Long duration indicates importance
        duration = data.get('duration', 0)
        if duration > 60:
            base_importance = min(base_importance + 1, 10)
            
        return base_importance
        
    def _extract_key_info(self, event: Dict) -> Dict:
        """Extract key information from an event"""
        key_info = {}
        event_type = event.get('type', '')
        data = event.get('data', {})
        
        if event_type == 'git_commit':
            key_info['commit_message'] = data.get('message', '')[:100]
            key_info['files_changed'] = len(data.get('files_changed', '').split())
            
        elif event_type == 'shell_command':
            key_info['command'] = f"{data.get('command')} {data.get('args', '')}".strip()
            key_info['duration'] = data.get('duration', 0)
            key_info['success'] = data.get('exit_code', 0) == 0
            
        elif event_type == 'file_change':
            path = Path(data.get('path', ''))
            key_info['file'] = path.name
            key_info['file_type'] = path.suffix
            
        return key_info
        
    def _detect_session(self) -> Optional[Dict]:
        """Detect if current events form a session"""
        if len(self.context_window) < 3:
            return None
            
        recent = self.context_window[-10:]
        
        # Debugging session detection
        errors = [e for e in recent if e.get('is_error')]
        fixes = [e for e in recent if e.get('fixes_error')]
        
        if errors and fixes:
            return {
                'type': 'debugging',
                'duration': self._calculate_session_duration(recent),
                'errors_encountered': len(errors),
                'fixed': len(fixes) > 0
            }
            
        # Feature development session
        feature_indicators = [
            e for e in recent 
            if e.get('category') in ['feature_start', 'code_created', 'test_created']
        ]
        
        if len(feature_indicators) >= 3:
            return {
                'type': 'feature_development',
                'duration': self._calculate_session_duration(recent),
                'files_created': len([e for e in recent if 'created' in e.get('category', '')])
            }
            
        # Learning session
        learning_indicators = [
            e for e in recent
            if 'documentation' in str(e).lower() or 'README' in str(e)
        ]
        
        if len(learning_indicators) >= 2:
            return {
                'type': 'learning',
                'duration': self._calculate_session_duration(recent)
            }
            
        return None
        
    def _calculate_session_duration(self, events: List[Dict]) -> int:
        """Calculate duration of a session in seconds"""
        if not events:
            return 0
            
        timestamps = []
        for event in events:
            ts_str = event.get('timestamp', '')
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str.rstrip('Z'))
                    timestamps.append(ts)
                except:
                    continue
                    
        if len(timestamps) >= 2:
            duration = (max(timestamps) - min(timestamps)).seconds
            return duration
            
        return 0
