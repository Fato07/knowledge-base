#!/usr/bin/env python3
"""
Intelligent Categorizer - Learns from user behavior
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

class IntelligentCategorizer:
    """
    Hybrid categorizer that learns from user behavior
    while maintaining rule-based foundation
    """
    
    def __init__(self, rules_path: Path, learning_db: Path = None):
        self.rules_path = rules_path
        self.learning_db = learning_db or Path.home() / ".kb-daemon" / "learning.db"
        self.rules = self._load_rules()
        self.user_patterns = self._load_user_patterns()
        self._init_learning_db()
    
    def _init_learning_db(self):
        """Initialize learning database"""
        self.learning_db.parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.learning_db)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS categorization_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                event_pattern TEXT,
                assigned_category TEXT,
                assigned_importance INTEGER,
                user_category TEXT,
                user_importance INTEGER,
                feedback_date TIMESTAMP,
                project_name TEXT,
                project_type TEXT
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pattern_performance (
                pattern TEXT PRIMARY KEY,
                matches INTEGER DEFAULT 0,
                correct INTEGER DEFAULT 0,
                accuracy REAL DEFAULT 0.0,
                last_updated TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    def categorize(self, event: Dict) -> Dict:
        """
        Categorize event using hybrid approach
        """
        # 1. Start with rule-based categorization
        rule_result = self._apply_rules(event)
        
        # 2. Check if we have learned patterns for this event type
        learned_result = self._apply_learned_patterns(event)
        
        # 3. Combine results with confidence weighting
        if learned_result and learned_result['confidence'] > 0.7:
            # Trust learned pattern more
            final_category = learned_result['category']
            final_importance = learned_result['importance']
            method = 'learned'
        else:
            # Use rules as fallback
            final_category = rule_result['category']
            final_importance = rule_result['importance']
            method = 'rules'
        
        # 4. Add metadata for learning
        event['categorization'] = {
            'category': final_category,
            'importance': final_importance,
            'method': method,
            'rule_confidence': rule_result.get('confidence', 0.5),
            'learned_confidence': learned_result.get('confidence', 0) if learned_result else 0
        }
        
        # 5. Track for performance monitoring
        self._track_categorization(event)
        
        return event
    
    def _apply_rules(self, event: Dict) -> Dict:
        """Apply rule-based categorization"""
        # Your existing rule logic here
        # For now, simple pattern matching
        
        event_type = event.get('type', '')
        event_data = event.get('data', {})
        
        # Default values
        category = 'general'
        importance = 5
        confidence = 0.5
        
        # Git commits
        if event_type == 'git_commit':
            message = event_data.get('message', '').lower()
            if 'fix' in message or 'bug' in message:
                category = 'bugfix'
                importance = 7
                confidence = 0.8
            elif 'feat' in message or 'feature' in message:
                category = 'feature'
                importance = 8
                confidence = 0.8
            elif 'refactor' in message:
                category = 'refactor'
                importance = 6
                confidence = 0.9
            elif 'test' in message:
                category = 'testing'
                importance = 6
                confidence = 0.9
            elif 'docs' in message:
                category = 'documentation'
                importance = 5
                confidence = 0.9
        
        # Shell commands
        elif event_type == 'shell_command':
            command = event_data.get('command', '')
            if command in ['pytest', 'jest', 'cargo test', 'go test']:
                category = 'testing'
                importance = 6
                confidence = 0.95
            elif command in ['npm install', 'pip install', 'cargo add']:
                category = 'dependency'
                importance = 4
                confidence = 0.9
        
        return {
            'category': category,
            'importance': importance,
            'confidence': confidence
        }
    
    def _apply_learned_patterns(self, event: Dict) -> Optional[Dict]:
        """Apply patterns learned from user feedback"""
        
        conn = sqlite3.connect(self.learning_db)
        cursor = conn.cursor()
        
        # Create event signature for matching
        event_type = event.get('type', '')
        project_type = event.get('project', {}).get('type', '')
        
        # Look for similar categorized events
        cursor.execute("""
            SELECT user_category, user_importance, COUNT(*) as count
            FROM categorization_feedback
            WHERE event_type = ? 
            AND (project_type = ? OR project_type IS NULL)
            AND feedback_date > date('now', '-30 days')
            GROUP BY user_category, user_importance
            ORDER BY count DESC
            LIMIT 1
        """, (event_type, project_type))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[2] >= 3:  # At least 3 similar corrections
            return {
                'category': result[0],
                'importance': result[1],
                'confidence': min(0.5 + (result[2] * 0.1), 0.95)  # Confidence grows with examples
            }
        
        return None
    
    def learn_from_feedback(self, event: Dict, user_category: str, user_importance: int):
        """
        Learn from user's review decisions
        Called when user approves/modifies during review
        """
        
        conn = sqlite3.connect(self.learning_db)
        cursor = conn.cursor()
        
        # Store feedback
        cursor.execute("""
            INSERT INTO categorization_feedback 
            (event_type, event_pattern, assigned_category, assigned_importance,
             user_category, user_importance, feedback_date, project_name, project_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.get('type'),
            self._create_event_pattern(event),
            event.get('categorization', {}).get('category'),
            event.get('categorization', {}).get('importance'),
            user_category,
            user_importance,
            datetime.now().isoformat(),
            event.get('project', {}).get('name'),
            event.get('project', {}).get('type')
        ))
        
        # Update pattern performance
        if event.get('categorization', {}).get('category') == user_category:
            cursor.execute("""
                INSERT INTO pattern_performance (pattern, matches, correct, accuracy, last_updated)
                VALUES (?, 1, 1, 1.0, ?)
                ON CONFLICT(pattern) DO UPDATE SET
                    matches = matches + 1,
                    correct = correct + 1,
                    accuracy = CAST(correct + 1 AS REAL) / CAST(matches + 1 AS REAL),
                    last_updated = ?
            """, (
                self._create_event_pattern(event),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
        else:
            cursor.execute("""
                INSERT INTO pattern_performance (pattern, matches, correct, accuracy, last_updated)
                VALUES (?, 1, 0, 0.0, ?)
                ON CONFLICT(pattern) DO UPDATE SET
                    matches = matches + 1,
                    accuracy = CAST(correct AS REAL) / CAST(matches + 1 AS REAL),
                    last_updated = ?
            """, (
                self._create_event_pattern(event),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def _create_event_pattern(self, event: Dict) -> str:
        """Create a pattern signature for the event"""
        event_type = event.get('type', 'unknown')
        project_type = event.get('project', {}).get('type', 'unknown')
        
        # Add more pattern details based on event type
        if event_type == 'git_commit':
            # Include keywords from commit message
            message = event.get('data', {}).get('message', '')
            keywords = self._extract_keywords(message)
            return f"{event_type}:{project_type}:{','.join(keywords)}"
        
        return f"{event_type}:{project_type}"
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        keywords = []
        keyword_patterns = ['fix', 'feat', 'bug', 'refactor', 'test', 'docs', 'style', 'perf']
        
        text_lower = text.lower()
        for pattern in keyword_patterns:
            if pattern in text_lower:
                keywords.append(pattern)
        
        return keywords[:3]  # Limit to 3 keywords
    
    def _track_categorization(self, event: Dict):
        """Track categorization for monitoring"""
        # This could write to a log file or metrics system
        pass
    
    def get_learning_stats(self) -> Dict:
        """Get statistics about learning performance"""
        
        conn = sqlite3.connect(self.learning_db)
        cursor = conn.cursor()
        
        # Overall accuracy
        cursor.execute("""
            SELECT 
                COUNT(*) as total_feedback,
                SUM(CASE WHEN assigned_category = user_category THEN 1 ELSE 0 END) as correct,
                AVG(CASE WHEN assigned_category = user_category THEN 1.0 ELSE 0.0 END) as accuracy
            FROM categorization_feedback
            WHERE feedback_date > date('now', '-30 days')
        """)
        
        overall = cursor.fetchone()
        
        # Per-category performance
        cursor.execute("""
            SELECT 
                assigned_category,
                COUNT(*) as attempts,
                SUM(CASE WHEN assigned_category = user_category THEN 1 ELSE 0 END) as correct,
                AVG(CASE WHEN assigned_category = user_category THEN 1.0 ELSE 0.0 END) as accuracy
            FROM categorization_feedback
            WHERE feedback_date > date('now', '-30 days')
            GROUP BY assigned_category
        """)
        
        categories = cursor.fetchall()
        conn.close()
        
        return {
            'total_feedback': overall[0] or 0,
            'overall_accuracy': overall[2] or 0,
            'categories': {
                cat[0]: {
                    'attempts': cat[1],
                    'correct': cat[2],
                    'accuracy': cat[3]
                }
                for cat in categories
            }
        }
    
    def _load_rules(self) -> Dict:
        """Load rules from YAML file"""
        # Your existing rule loading logic
        return {}
    
    def _load_user_patterns(self) -> Dict:
        """Load learned user patterns from database"""
        # Load frequently corrected patterns
        return {}


# Test the intelligent categorizer
if __name__ == "__main__":
    categorizer = IntelligentCategorizer(
        Path.home() / ".kb-daemon" / "config" / "patterns.yml"
    )
    
    # Test event
    test_event = {
        'type': 'git_commit',
        'data': {
            'message': 'fix: resolve memory leak in user service'
        },
        'project': {
            'name': 'my-app',
            'type': 'node'
        }
    }
    
    result = categorizer.categorize(test_event)
    print("Categorized:", result['categorization'])
    
    # Simulate user feedback
    categorizer.learn_from_feedback(test_event, 'bugfix', 8)
    
    # Check learning stats
    stats = categorizer.get_learning_stats()
    print("Learning Stats:", json.dumps(stats, indent=2))
