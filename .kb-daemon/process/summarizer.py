#!/usr/bin/env python3
"""
Summarizer - Summarizes events using AI or rule-based approaches
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict

class Summarizer:
    """Summarizes captured events intelligently"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.use_llm = False  # Force rule-based for Phase 1
        # LLM support will be added in Phase 2
            
    def _init_llm(self):
        """Initialize LLM connection"""
        # TODO: Implement Ollama or Claude API integration
        pass
        
    def summarize(self, events: List[Dict]) -> Dict:
        """Summarize a batch of events"""
        if self.use_llm and hasattr(self, 'llm'):
            return self._llm_summarize(events)
        else:
            return self._rule_based_summarize(events)
            
    def _rule_based_summarize(self, events: List[Dict]) -> Dict:
        """Rule-based summarization"""
        summary = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event_count': len(events),
            'time_range': self._get_time_range(events),
            'categories': defaultdict(list),
            'key_activities': [],
            'decisions': [],
            'problems_solved': [],
            'external_changes': [],
            'learning': []
        }
        
        # Group by category
        for event in events:
            category = event.get('category', 'general')
            summary['categories'][category].append(event)
            
        # Extract key activities
        summary['key_activities'] = self._extract_key_activities(events)
        
        # Extract decisions
        summary['decisions'] = self._extract_decisions(events)
        
        # Extract problems solved
        summary['problems_solved'] = self._extract_problems_solved(events)
        
        # Extract external changes
        summary['external_changes'] = self._extract_external_changes(events)
        
        # Extract learning
        summary['learning'] = self._extract_learning(events)
        
        # Generate natural language summary
        summary['text'] = self._generate_text_summary(summary)
        
        return summary
        
    def _get_time_range(self, events: List[Dict]) -> Dict:
        """Get time range of events"""
        timestamps = []
        for event in events:
            ts_str = event.get('timestamp', '')
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str.rstrip('Z'))
                    timestamps.append(ts)
                except:
                    continue
                    
        if timestamps:
            return {
                'start': min(timestamps).isoformat() + 'Z',
                'end': max(timestamps).isoformat() + 'Z',
                'duration_minutes': int((max(timestamps) - min(timestamps)).seconds / 60)
            }
            
        return {}
        
    def _extract_key_activities(self, events: List[Dict]) -> List[Dict]:
        """Extract key activities from events"""
        activities = []
        
        # High importance events are key activities
        for event in events:
            if event.get('importance', 0) >= 7:
                activity = {
                    'description': self._describe_event(event),
                    'category': event.get('category'),
                    'timestamp': event.get('timestamp')
                }
                activities.append(activity)
                
        # Sessions are key activities
        seen_sessions = set()
        for event in events:
            session = event.get('session')
            if session:
                session_key = f"{session.get('type')}_{session.get('duration')}"
                if session_key not in seen_sessions:
                    seen_sessions.add(session_key)
                    activities.append({
                        'description': f"{session['type'].replace('_', ' ').title()} session ({session.get('duration', 0) // 60} minutes)",
                        'category': 'session',
                        'timestamp': event.get('timestamp')
                    })
                    
        return activities[:10]  # Top 10 activities
        
    def _extract_decisions(self, events: List[Dict]) -> List[str]:
        """Extract decisions made"""
        decisions = []
        
        for event in events:
            category = event.get('category', '')
            key_info = event.get('key_info', {})
            
            # Dependencies added are decisions
            if category == 'dependency_add':
                command = key_info.get('command', '')
                decisions.append(f"Added dependency: {command}")
                
            # Breaking changes are decisions
            if event.get('breaking_change'):
                decisions.append(f"Breaking change: {key_info.get('commit_message', 'Unknown')}")
                
            # Architecture/config changes are decisions
            if category == 'config_change':
                decisions.append(f"Configuration change: {key_info.get('file', 'Unknown')}")
                
        return decisions[:5]  # Top 5 decisions
        
    def _extract_problems_solved(self, events: List[Dict]) -> List[Dict]:
        """Extract problems that were solved"""
        problems = []
        
        # Look for error -> fix patterns
        errors = [e for e in events if e.get('is_error')]
        fixes = [e for e in events if e.get('fixes_error')]
        
        for fix in fixes:
            # Find corresponding error
            fix_command = fix.get('data', {}).get('command', '')
            for error in errors:
                if error.get('data', {}).get('command', '') == fix_command:
                    problems.append({
                        'problem': f"Error in: {fix_command}",
                        'solution': "Fixed after debugging",
                        'time_to_fix': self._calculate_time_diff(error, fix)
                    })
                    break
                    
        # Debugging sessions that ended
        for event in events:
            session = event.get('session')
            if session and session.get('type') == 'debugging' and session.get('fixed'):
                problems.append({
                    'problem': f"Debugging session with {session.get('errors_encountered', 0)} errors",
                    'solution': "Resolved",
                    'duration_minutes': session.get('duration', 0) // 60
                })
                
        return problems[:5]
        
    def _extract_external_changes(self, events: List[Dict]) -> List[Dict]:
        """Extract external changes integrated"""
        external = []
        
        for event in events:
            if event.get('external_commits'):
                external_analysis = event.get('external_changes', {})
                external.append({
                    'type': 'commits_merged',
                    'count': len(event['external_commits']),
                    'authors': external_analysis.get('authors', []),
                    'breaking_changes': external_analysis.get('potential_breaking_changes', [])
                })
                
        return external
        
    def _extract_learning(self, events: List[Dict]) -> List[str]:
        """Extract learning moments"""
        learning = []
        
        for event in events:
            category = event.get('category', '')
            
            # Documentation reading is learning
            if category == 'documentation':
                learning.append(f"Reviewed documentation: {event.get('key_info', {}).get('file', 'Unknown')}")
                
            # Learning sessions
            session = event.get('session')
            if session and session.get('type') == 'learning':
                learning.append(f"Learning session ({session.get('duration', 0) // 60} minutes)")
                
            # New patterns from external code
            external_changes = event.get('external_changes')
            if external_changes and external_changes.get('patterns_introduced'):
                learning.append("New patterns introduced from team code")
                
        return learning[:5]
        
    def _describe_event(self, event: Dict) -> str:
        """Generate a description for an event"""
        event_type = event.get('type', '')
        category = event.get('category', '')
        key_info = event.get('key_info', {})
        
        if event_type == 'git_commit':
            return f"Commit: {key_info.get('commit_message', 'Unknown')}"
        elif event_type == 'shell_command':
            return f"Command: {key_info.get('command', 'Unknown')}"
        elif event_type == 'file_change':
            return f"File {event.get('data', {}).get('event_type', 'changed')}: {key_info.get('file', 'Unknown')}"
        elif event_type == 'pattern_detected':
            return f"Pattern: {event.get('data', {}).get('pattern', 'Unknown')}"
        else:
            return f"{category.replace('_', ' ').title()}"
            
    def _calculate_time_diff(self, event1: Dict, event2: Dict) -> int:
        """Calculate time difference between two events in minutes"""
        try:
            ts1 = datetime.fromisoformat(event1.get('timestamp', '').rstrip('Z'))
            ts2 = datetime.fromisoformat(event2.get('timestamp', '').rstrip('Z'))
            return int(abs((ts2 - ts1).seconds) / 60)
        except:
            return 0
            
    def _generate_text_summary(self, summary: Dict) -> str:
        """Generate natural language summary"""
        lines = []
        
        # Time range
        time_range = summary.get('time_range', {})
        if time_range and time_range.get('duration_minutes'):
            lines.append(f"Activity period: {time_range.get('duration_minutes', 0)} minutes")
            
        # Main activities
        activities = summary.get('key_activities', [])
        if activities:
            lines.append(f"\nKey activities ({len(activities)}):")
            for act in activities[:3]:
                desc = act.get('description', 'Unknown activity')
                lines.append(f"  • {desc}")
                
        # Decisions
        decisions = summary.get('decisions', [])
        if decisions:
            lines.append(f"\nDecisions made ({len(decisions)}):")
            for dec in decisions[:3]:
                lines.append(f"  • {dec}")
                
        # Problems solved
        problems = summary.get('problems_solved', [])
        if problems:
            lines.append(f"\nProblems solved ({len(problems)}):")
            for prob in problems[:2]:
                problem_desc = prob.get('problem', 'Unknown')
                solution_desc = prob.get('solution', 'Resolved')
                lines.append(f"  • {problem_desc} → {solution_desc}")
                
        # External changes
        external = summary.get('external_changes', [])
        if external:
            total_commits = sum(e.get('count', 0) for e in external)
            lines.append(f"\nIntegrated {total_commits} external commits")
            
        # Learning
        learning = summary.get('learning', [])
        if learning:
            lines.append(f"\nLearning moments:")
            for learn in learning[:2]:
                lines.append(f"  • {learn}")
                
        return '\n'.join(lines) if lines else "No summary available"
        
    def _llm_summarize(self, events: List[Dict]) -> Dict:
        """Use LLM to summarize events"""
        # TODO: Implement LLM-based summarization
        # For now, fall back to rule-based
        return self._rule_based_summarize(events)
