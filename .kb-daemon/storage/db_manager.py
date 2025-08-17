#!/usr/bin/env python3
"""
Database Manager - Manages storage of KB events with review tracking
"""

import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

class DatabaseManager:
    """Manages the KB daemon database"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        self._upgrade_schema()  # Upgrade after init
        
    def _init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    type TEXT NOT NULL,
                    category TEXT,
                    importance INTEGER,
                    data TEXT,
                    key_info TEXT,
                    session TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Summaries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_count INTEGER,
                    time_range TEXT,
                    text TEXT,
                    full_data TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # KB entries table (for approved entries)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS kb_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    category TEXT,
                    title TEXT,
                    content TEXT,
                    tags TEXT,
                    relations TEXT,
                    approved BOOLEAN DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Review sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS review_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    review_date TEXT NOT NULL,
                    events_reviewed INTEGER,
                    entries_created INTEGER,
                    entries_approved INTEGER,
                    entries_skipped INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes (basic ones first)
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_category ON events(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_importance ON events(importance)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_kb_entries_category ON kb_entries(category)')
            # Note: idx_events_reviewed will be created in _upgrade_schema if needed
            
            conn.commit()
            
    def _upgrade_schema(self):
        """Upgrade schema for existing databases"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if reviewed column exists
            cursor.execute("PRAGMA table_info(events)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'reviewed' not in columns:
                cursor.execute('ALTER TABLE events ADD COLUMN reviewed BOOLEAN DEFAULT 0')
                cursor.execute('ALTER TABLE events ADD COLUMN review_date TEXT')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_reviewed ON events(reviewed)')
                conn.commit()
                print("✓ Database schema upgraded with review tracking")
            
    def store_event(self, event: Dict):
        """Store a single event"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if reviewed column exists
            cursor.execute("PRAGMA table_info(events)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'reviewed' in columns:
                cursor.execute('''
                    INSERT INTO events (timestamp, type, category, importance, data, key_info, session, reviewed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.get('timestamp'),
                    event.get('type'),
                    event.get('category'),
                    event.get('importance'),
                    json.dumps(event.get('data', {})),
                    json.dumps(event.get('key_info', {})),
                    json.dumps(event.get('session', {})) if event.get('session') else None,
                    0  # Not reviewed by default
                ))
            else:
                cursor.execute('''
                    INSERT INTO events (timestamp, type, category, importance, data, key_info, session)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.get('timestamp'),
                    event.get('type'),
                    event.get('category'),
                    event.get('importance'),
                    json.dumps(event.get('data', {})),
                    json.dumps(event.get('key_info', {})),
                    json.dumps(event.get('session', {})) if event.get('session') else None
                ))
            
            conn.commit()
            
    def get_unreviewed_events(self, min_importance: int = 3) -> List[Dict]:
        """Get events that haven't been reviewed yet"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM events 
                WHERE reviewed = 0 AND importance >= ?
                ORDER BY timestamp DESC
            ''', (min_importance,))
            
            rows = cursor.fetchall()
            
            events = []
            for row in rows:
                event = {
                    'id': row[0],
                    'timestamp': row[1],
                    'type': row[2],
                    'category': row[3],
                    'importance': row[4],
                    'data': json.loads(row[5]) if row[5] else {},
                    'key_info': json.loads(row[6]) if row[6] else {},
                    'session': json.loads(row[7]) if row[7] else None
                }
                events.append(event)
                
            return events
            
    def mark_events_reviewed(self, event_ids: List[int]):
        """Mark events as reviewed"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            review_date = datetime.now(timezone.utc).isoformat()
            
            for event_id in event_ids:
                cursor.execute('''
                    UPDATE events 
                    SET reviewed = 1, review_date = ?
                    WHERE id = ?
                ''', (review_date, event_id))
            
            conn.commit()
            
    def create_review_session(self, stats: Dict) -> int:
        """Create a review session record"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO review_sessions 
                (review_date, events_reviewed, entries_created, entries_approved, entries_skipped)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now(timezone.utc).isoformat(),
                stats.get('events_reviewed', 0),
                stats.get('entries_created', 0),
                stats.get('entries_approved', 0),
                stats.get('entries_skipped', 0)
            ))
            
            conn.commit()
            return cursor.lastrowid
            
    def get_recent_events(self, hours: int = 24, min_importance: int = 0) -> List[Dict]:
        """Get recent events (for backward compatibility)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            from datetime import timedelta
            threshold = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
            
            cursor.execute('''
                SELECT * FROM events 
                WHERE timestamp > ? AND importance >= ?
                ORDER BY timestamp DESC
            ''', (threshold, min_importance))
            
            rows = cursor.fetchall()
            
            events = []
            for row in rows:
                event = {
                    'id': row[0],
                    'timestamp': row[1],
                    'type': row[2],
                    'category': row[3],
                    'importance': row[4],
                    'data': json.loads(row[5]) if row[5] else {},
                    'key_info': json.loads(row[6]) if row[6] else {},
                    'session': json.loads(row[7]) if row[7] else None
                }
                events.append(event)
                
            return events
            
    def get_review_history(self, days: int = 30) -> List[Dict]:
        """Get review session history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            from datetime import timedelta
            threshold = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            
            cursor.execute('''
                SELECT * FROM review_sessions 
                WHERE review_date > ?
                ORDER BY review_date DESC
            ''', (threshold,))
            
            rows = cursor.fetchall()
            
            sessions = []
            for row in rows:
                session = {
                    'id': row[0],
                    'review_date': row[1],
                    'events_reviewed': row[2],
                    'entries_created': row[3],
                    'entries_approved': row[4],
                    'entries_skipped': row[5]
                }
                sessions.append(session)
                
            return sessions
            
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Total events
            cursor.execute('SELECT COUNT(*) FROM events')
            stats['total_events'] = cursor.fetchone()[0]
            
            # Unreviewed events
            cursor.execute('SELECT COUNT(*) FROM events WHERE reviewed = 0 AND importance >= 3')
            stats['unreviewed_events'] = cursor.fetchone()[0]
            
            # Events by category
            cursor.execute('''
                SELECT category, COUNT(*) 
                FROM events 
                GROUP BY category
            ''')
            stats['events_by_category'] = dict(cursor.fetchall())
            
            # Average importance
            cursor.execute('SELECT AVG(importance) FROM events WHERE importance IS NOT NULL')
            avg = cursor.fetchone()[0]
            stats['average_importance'] = round(avg, 2) if avg else 0
            
            # Total summaries
            cursor.execute('SELECT COUNT(*) FROM summaries')
            stats['total_summaries'] = cursor.fetchone()[0]
            
            # Pending KB entries
            cursor.execute('SELECT COUNT(*) FROM kb_entries WHERE approved = 0')
            stats['pending_entries'] = cursor.fetchone()[0]
            
            # Review sessions (if table exists)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='review_sessions'")
            if cursor.fetchone():
                cursor.execute('SELECT COUNT(*) FROM review_sessions')
                result = cursor.fetchone()
                stats['total_reviews'] = result[0] if result else 0
            else:
                stats['total_reviews'] = 0
            
            return stats
            
    def store_summary(self, summary: Dict):
        """Store a summary"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO summaries (timestamp, event_count, time_range, text, full_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                summary.get('timestamp'),
                summary.get('event_count'),
                json.dumps(summary.get('time_range', {})),
                summary.get('text'),
                json.dumps(summary)
            ))
            
            conn.commit()
            
    def get_recent_summaries(self, days: int = 7) -> List[Dict]:
        """Get recent summaries"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            from datetime import timedelta
            threshold = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            
            cursor.execute('''
                SELECT * FROM summaries 
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            ''', (threshold,))
            
            rows = cursor.fetchall()
            
            summaries = []
            for row in rows:
                summary = {
                    'id': row[0],
                    'timestamp': row[1],
                    'event_count': row[2],
                    'time_range': json.loads(row[3]) if row[3] else {},
                    'text': row[4],
                    'full_data': json.loads(row[5]) if row[5] else {}
                }
                summaries.append(summary)
                
            return summaries
            
    def create_kb_entry(self, entry: Dict) -> int:
        """Create a KB entry for review"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO kb_entries (timestamp, category, title, content, tags, relations, approved)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry.get('timestamp', datetime.now(timezone.utc).isoformat()),
                entry.get('category'),
                entry.get('title'),
                entry.get('content'),
                json.dumps(entry.get('tags', [])),
                json.dumps(entry.get('relations', [])),
                entry.get('approved', False)
            ))
            
            conn.commit()
            return cursor.lastrowid
            
    def get_pending_kb_entries(self) -> List[Dict]:
        """Get KB entries pending approval"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM kb_entries 
                WHERE approved = 0
                ORDER BY timestamp DESC
            ''')
            
            rows = cursor.fetchall()
            
            entries = []
            for row in rows:
                entry = {
                    'id': row[0],
                    'timestamp': row[1],
                    'category': row[2],
                    'title': row[3],
                    'content': row[4],
                    'tags': json.loads(row[5]) if row[5] else [],
                    'relations': json.loads(row[6]) if row[6] else [],
                    'approved': bool(row[7])
                }
                entries.append(entry)
                
            return entries
            
    def approve_kb_entry(self, entry_id: int):
        """Approve a KB entry"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE kb_entries 
                SET approved = 1
                WHERE id = ?
            ''', (entry_id,))
            
            conn.commit()
            
    def delete_kb_entry(self, entry_id: int):
        """Delete a KB entry"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM kb_entries WHERE id = ?', (entry_id,))
            conn.commit()
