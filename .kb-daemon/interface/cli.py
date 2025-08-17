#!/usr/bin/env python3
"""
CLI Interface - Command line interface for KB daemon with smart review tracking
"""

import os
import sys
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.db_manager import DatabaseManager
from process.summarizer import Summarizer

class CLI:
    """Command line interface for KB daemon"""
    
    def __init__(self, base_path=None):
        # Use project database path if available, fallback to global
        if base_path:
            db_path = base_path / "storage" / "kb_store.db"
        else:
            # Try to detect if we're in a project directory
            current_dir = Path.cwd()
            if (current_dir / "storage" / "kb_store.db").exists():
                db_path = current_dir / "storage" / "kb_store.db"
            elif (current_dir.parent / "storage" / "kb_store.db").exists():
                db_path = current_dir.parent / "storage" / "kb_store.db"
            else:
                # Fallback to global path
                db_path = Path.home() / ".kb-daemon" / "storage" / "kb_store.db"
        
        self.db = DatabaseManager(db_path)
        print(f"📊 Using database: {db_path}")
        self.summarizer = Summarizer({'use_local_llm': False})
        
    def daily_review(self):
        """Run daily review interface - only shows unreviewed events"""
        print("\n" + "="*60)
        print("📊 KB DAEMON - DAILY REVIEW")
        print("="*60)
        
        # Get only unreviewed events
        events = self.db.get_unreviewed_events(min_importance=3)
        
        if not events:
            print("\n✨ No new events to review!")
            
            # Show statistics
            stats = self.db.get_statistics()
            if stats['total_events'] > 0:
                print(f"\n📈 Overall Statistics:")
                print(f"  Total events captured: {stats['total_events']}")
                print(f"  Average importance: {stats['average_importance']}/10")
                
                # Show last review
                history = self.db.get_review_history(days=7)
                if history:
                    last_review = history[0]
                    print(f"\n  Last review: {last_review['review_date'][:10]}")
                    print(f"  Events reviewed: {last_review['events_reviewed']}")
                    print(f"  Entries created: {last_review['entries_approved']}")
            
            return
            
        print(f"\n📈 Found {len(events)} new events to review")
        
        # Generate summary
        summary = self.summarizer.summarize(events)
        
        # Display summary
        print("\n" + "-"*40)
        print("SUMMARY")
        print("-"*40)
        print(summary.get('text', 'No summary available'))
        
        # Generate KB entries
        kb_entries = self._generate_kb_entries(events, summary)
        
        if not kb_entries:
            print("\n✅ No significant KB entries to create")
            # Mark events as reviewed anyway
            event_ids = [e['id'] for e in events]
            self.db.mark_events_reviewed(event_ids)
            return
            
        print("\n" + "-"*40)
        print(f"SUGGESTED KB ENTRIES ({len(kb_entries)})")
        print("-"*40)
        
        # Track review statistics
        review_stats = {
            'events_reviewed': len(events),
            'entries_created': len(kb_entries),
            'entries_approved': 0,
            'entries_skipped': 0
        }
        
        # Review each entry
        for i, entry in enumerate(kb_entries, 1):
            action = self._review_entry(i, entry, len(kb_entries))
            if action == 'approved':
                review_stats['entries_approved'] += 1
            elif action == 'skipped':
                review_stats['entries_skipped'] += 1
        
        # Mark all events as reviewed
        event_ids = [e['id'] for e in events]
        self.db.mark_events_reviewed(event_ids)
        
        # Save review session
        self.db.create_review_session(review_stats)
        
        # Show review summary
        print("\n" + "="*60)
        print("📊 REVIEW SUMMARY")
        print("="*60)
        print(f"Events reviewed: {review_stats['events_reviewed']}")
        print(f"Entries approved: {review_stats['entries_approved']}")
        print(f"Entries skipped: {review_stats['entries_skipped']}")
        
        # Show statistics
        self._show_statistics()
        
        print("\n✅ Daily review complete!")
        print("   Events have been marked as reviewed.")
        print("   Run 'kb review' again to see only new events.")
        
    def _generate_kb_entries(self, events: List[Dict], summary: Dict) -> List[Dict]:
        """Generate KB entries from events"""
        entries = []
        
        # Create entries for key activities
        for activity in summary.get('key_activities', [])[:5]:
            entry = {
                'title': activity['description'][:100],
                'category': activity.get('category', 'general'),
                'content': self._format_activity_content(activity),
                'tags': self._extract_tags(activity),
                'timestamp': activity.get('timestamp')
            }
            entries.append(entry)
            
        # Create entries for decisions
        for decision in summary.get('decisions', []):
            entry = {
                'title': decision[:100],
                'category': 'decision',
                'content': decision,
                'tags': ['decision'] + self._extract_tags({'description': decision}),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            entries.append(entry)
            
        # Create entries for problems solved
        for problem in summary.get('problems_solved', []):
            entry = {
                'title': f"Solved: {problem['problem'][:80]}",
                'category': 'problem_solved',
                'content': f"**Problem:** {problem['problem']}\n\n**Solution:** {problem['solution']}",
                'tags': ['problem', 'solution', 'debugging'],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            entries.append(entry)
            
        # Create entry for external changes if any
        if summary.get('external_changes'):
            total_commits = sum(e.get('count', 0) for e in summary['external_changes'])
            entry = {
                'title': f"Integrated {total_commits} external commits",
                'category': 'integration',
                'content': self._format_external_changes(summary['external_changes']),
                'tags': ['integration', 'team', 'external'],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            entries.append(entry)
            
        return entries
        
    def _format_activity_content(self, activity: Dict) -> str:
        """Format activity content for KB entry"""
        content = activity['description']
        
        if activity.get('category'):
            content += f"\n\n**Category:** {activity['category']}"
            
        if activity.get('timestamp'):
            content += f"\n**Time:** {activity['timestamp']}"
            
        return content
        
    def _format_external_changes(self, external_changes: List[Dict]) -> str:
        """Format external changes for KB entry"""
        lines = []
        
        for change in external_changes:
            lines.append(f"**{change.get('type', 'Changes')}:**")
            lines.append(f"  - Commits: {change.get('count', 0)}")
            
            authors = change.get('authors', [])
            if authors:
                lines.append(f"  - Authors: {', '.join(authors)}")
                
            breaking = change.get('breaking_changes', [])
            if breaking:
                lines.append("  - ⚠️ Potential breaking changes detected")
                
        return '\n'.join(lines)
        
    def _extract_tags(self, data: Dict) -> List[str]:
        """Extract tags from data"""
        tags = []
        
        text = str(data).lower()
        
        # Common tags
        tag_keywords = {
            'test': ['test', 'testing', 'pytest', 'jest'],
            'bug': ['bug', 'fix', 'error', 'issue'],
            'feature': ['feature', 'feat', 'new'],
            'refactor': ['refactor', 'cleanup', 'optimize'],
            'config': ['config', 'configuration', 'setup'],
            'docker': ['docker', 'container', 'compose'],
            'api': ['api', 'endpoint', 'rest', 'graphql'],
            'database': ['database', 'db', 'sql', 'mongo'],
            'frontend': ['frontend', 'ui', 'react', 'vue'],
            'backend': ['backend', 'server', 'node', 'python']
        }
        
        for tag, keywords in tag_keywords.items():
            if any(kw in text for kw in keywords):
                tags.append(tag)
                
        return list(set(tags))[:5]  # Max 5 tags
        
    def _review_entry(self, index: int, entry: Dict, total: int) -> str:
        """Review a single KB entry and return action taken"""
        print(f"\n[{index}/{total}] {entry['title']}")
        print("-" * 40)
        print(f"Category: {entry['category']}")
        print(f"Tags: {', '.join(entry['tags'])}")
        print(f"\nContent:\n{entry['content'][:300]}...")
        
        while True:
            action = input("\n[A]pprove, [E]dit, [S]kip, [Q]uit? ").lower()
            
            if action == 'a':
                # Store in database
                entry_id = self.db.create_kb_entry(entry)
                self.db.approve_kb_entry(entry_id)
                
                # Also create markdown file
                self._create_markdown_entry(entry)
                print("✅ Entry approved and saved")
                return 'approved'
                
            elif action == 'e':
                edited_entry = self._edit_entry(entry)
                if edited_entry:
                    entry_id = self.db.create_kb_entry(edited_entry)
                    self.db.approve_kb_entry(entry_id)
                    self._create_markdown_entry(edited_entry)
                    print("✅ Entry edited and saved")
                return 'approved'
                
            elif action == 's':
                print("⏭️  Entry skipped")
                return 'skipped'
                
            elif action == 'q':
                print("Exiting review...")
                sys.exit(0)
                
    def _edit_entry(self, entry: Dict) -> Optional[Dict]:
        """Edit a KB entry"""
        print("\nEditing entry...")
        
        # Simple text-based editing
        new_title = input(f"Title [{entry['title']}]: ").strip()
        if new_title:
            entry['title'] = new_title
            
        new_category = input(f"Category [{entry['category']}]: ").strip()
        if new_category:
            entry['category'] = new_category
            
        new_tags = input(f"Tags [{', '.join(entry['tags'])}]: ").strip()
        if new_tags:
            entry['tags'] = [t.strip() for t in new_tags.split(',')]
            
        print("\nContent (press Enter to keep current):")
        print(entry['content'])
        print("\n[Press Enter to keep, or type new content]")
        
        new_content = input()
        if new_content:
            entry['content'] = new_content
            
        return entry
        
    def _create_markdown_entry(self, entry: Dict):
        """Create markdown file for KB entry"""
        # Determine directory
        kb_path = Path.home() / "DEV" / "knowledge-base"
        
        category_map = {
            'decision': 'architecture',
            'problem_solved': 'learning',
            'integration': 'projects',
            'feature': 'projects',
            'bugfix': 'learning',
            'testing': 'tools',
            'documentation': 'projects',
            'refactoring_session': 'learning',
            'code_created': 'projects',
            'code_modified': 'daily'
        }
        
        subdir = category_map.get(entry['category'], 'daily')
        entry_dir = kb_path / subdir
        entry_dir.mkdir(exist_ok=True)
        
        # Generate filename
        date_str = datetime.now().strftime('%Y%m%d')
        safe_title = "".join(c for c in entry['title'] if c.isalnum() or c in ' -_')[:50]
        filename = f"{date_str}_{safe_title.replace(' ', '_')}.md"
        filepath = entry_dir / filename
        
        # Write content
        content = f"# {entry['title']}\n\n"
        content += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        content += f"**Category:** {entry['category']}\n"
        content += f"**Tags:** {', '.join(entry['tags'])}\n\n"
        content += "---\n\n"
        content += entry['content']
        content += "\n\n---\n"
        content += f"*Generated by KB Daemon*\n"
        
        filepath.write_text(content)
        print(f"📝 Saved to: {filepath}")
        
    def _show_statistics(self):
        """Show KB daemon statistics"""
        stats = self.db.get_statistics()
        
        print("\n" + "="*60)
        print("📊 STATISTICS")
        print("="*60)
        
        print(f"Total Events Captured: {stats['total_events']}")
        print(f"Unreviewed Events: {stats.get('unreviewed_events', 0)}")
        print(f"Average Importance: {stats['average_importance']}/10")
        print(f"Total Reviews: {stats.get('total_reviews', 0)}")
        
        if stats.get('events_by_category'):
            print("\nEvents by Category:")
            for category, count in sorted(stats['events_by_category'].items(), 
                                        key=lambda x: x[1], reverse=True)[:5]:
                print(f"  - {category}: {count}")


def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="KB Daemon CLI")
    parser.add_argument('command', choices=['review', 'stats', 'export'],
                       help='Command to execute')
    
    args = parser.parse_args()
    
    cli = CLI()
    
    if args.command == 'review':
        cli.daily_review()
    elif args.command == 'stats':
        cli._show_statistics()
    elif args.command == 'export':
        print("Export not yet implemented")


if __name__ == "__main__":
    main()
