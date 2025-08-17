#!/usr/bin/env python3
"""
Git Hooks Integration - Captures git activity intelligently
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from queue import Queue
import re

class GitHooks:
    """Manages git hook integration for intelligent capture"""
    
    def __init__(self, capture_queue: Queue, config: Dict, base_path=None):
        self.capture_queue = capture_queue
        self.config = config
        self.base_path = base_path or Path.home()
        self.my_email = self._get_git_email()
        
    def _get_git_email(self) -> str:
        """Get the user's git email"""
        try:
            result = subprocess.run(
                ['git', 'config', 'user.email'],
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except:
            return ""
    
    def install_hooks(self):
        """Install git hooks globally"""
        hooks_dir = Path(__file__).parent.parent / "git-templates" / "hooks"
        
        # Create hook scripts
        self._create_post_commit_hook(hooks_dir)
        self._create_post_merge_hook(hooks_dir)
        self._create_post_checkout_hook(hooks_dir)
        self._create_prepare_commit_msg_hook(hooks_dir)
        
        # Set global git config
        subprocess.run([
            'git', 'config', '--global', 'init.templatedir',
            str(hooks_dir.parent)
        ])
        
        print("Git hooks installed globally")
        
    def _create_post_commit_hook(self, hooks_dir: Path):
        """Create post-commit hook"""
        capture_dir = self.base_path / "capture"
        hook_content = f'''#!/bin/bash
# KB Daemon post-commit hook

# Set capture directory
export KB_CAPTURE_DIR="{capture_dir}"

# Get commit information
COMMIT_HASH=$(git rev-parse HEAD)
COMMIT_MSG=$(git log -1 --pretty=%B)
BRANCH=$(git branch --show-current)
CHANGED_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD)

# Detect commit type
COMMIT_TYPE="general"
if [[ "$COMMIT_MSG" =~ ^fix:|^bugfix: ]]; then
    COMMIT_TYPE="bugfix"
elif [[ "$COMMIT_MSG" =~ ^feat:|^feature: ]]; then
    COMMIT_TYPE="feature"
elif [[ "$COMMIT_MSG" =~ ^refactor: ]]; then
    COMMIT_TYPE="refactor"
elif [[ "$COMMIT_MSG" =~ ^docs: ]]; then
    COMMIT_TYPE="documentation"
elif [[ "$COMMIT_MSG" =~ ^test: ]]; then
    COMMIT_TYPE="testing"
fi

# Create event JSON
EVENT_JSON=$(cat <<EOF
{
    "type": "git_commit",
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "data": {
        "hash": "$COMMIT_HASH",
        "message": "$COMMIT_MSG",
        "branch": "$BRANCH",
        "commit_type": "$COMMIT_TYPE",
        "files_changed": "$CHANGED_FILES"
    }
}
EOF
)

# Send to KB daemon  
echo "$EVENT_JSON" >> "$KB_CAPTURE_DIR/git_events.jsonl"
'''
        
        hook_path = hooks_dir / "post-commit"
        hook_path.write_text(hook_content)
        hook_path.chmod(0o755)
        
    def _create_post_merge_hook(self, hooks_dir: Path):
        """Create post-merge hook for tracking external changes"""
        capture_dir = self.base_path / "capture"
        hook_content = f'''#!/bin/bash
# KB Daemon post-merge hook - tracks external changes

# Set capture directory
export KB_CAPTURE_DIR="{capture_dir}"

# Get merge information
BRANCH=$(git branch --show-current)
HEAD_BEFORE=$1
HEAD_AFTER=$(git rev-parse HEAD)

# Get list of commits in the merge
NEW_COMMITS=$(git rev-list $HEAD_BEFORE..$HEAD_AFTER)

# Create event JSON
EVENT_JSON=$(cat <<EOF
{
    "type": "git_merge",
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "data": {
        "branch": "$BRANCH",
        "head_before": "$HEAD_BEFORE",
        "head_after": "$HEAD_AFTER",
        "commits_merged": "$NEW_COMMITS"
    }
}
EOF
)

# Send to KB daemon
echo "$EVENT_JSON" >> "$KB_CAPTURE_DIR/git_events.jsonl"
'''
        
        hook_path = hooks_dir / "post-merge"
        hook_path.write_text(hook_content)
        hook_path.chmod(0o755)
        
    def _create_post_checkout_hook(self, hooks_dir: Path):
        """Create post-checkout hook for branch switches"""
        capture_dir = self.base_path / "capture"
        hook_content = f'''#!/bin/bash
# KB Daemon post-checkout hook

# Set capture directory
export KB_CAPTURE_DIR="{capture_dir}"

PREV_HEAD=$1
NEW_HEAD=$2
BRANCH_CHECKOUT=$3

if [ "$BRANCH_CHECKOUT" = "1" ]; then
    NEW_BRANCH=$(git branch --show-current)
    
    EVENT_JSON=$(cat <<EOF
{
    "type": "git_checkout",
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "data": {
        "prev_head": "$PREV_HEAD",
        "new_head": "$NEW_HEAD",
        "branch": "$NEW_BRANCH"
    }
}
EOF
)
    
    echo "$EVENT_JSON" >> "$KB_CAPTURE_DIR/git_events.jsonl"
fi
'''
        
        hook_path = hooks_dir / "post-checkout"
        hook_path.write_text(hook_content)
        hook_path.chmod(0o755)
        
    def _create_prepare_commit_msg_hook(self, hooks_dir: Path):
        """Create prepare-commit-msg hook for context capture"""
        hook_content = '''#!/bin/bash
# KB Daemon prepare-commit-msg hook

COMMIT_MSG_FILE=$1
COMMIT_SOURCE=$2

# Add context comment (will be stripped from actual commit)
if [ -z "$COMMIT_SOURCE" ]; then
    # Get current context
    CURRENT_DIR=$(pwd)
    CURRENT_TIME=$(date +"%H:%M")
    
    # Check if we're in a debugging session (recent test failures)
    if [ -f .kb_daemon_test_status ]; then
        TEST_STATUS=$(cat .kb_daemon_test_status)
        if [ "$TEST_STATUS" = "failed" ]; then
            echo "# KB: Likely fixing test failures" >> "$COMMIT_MSG_FILE"
        fi
    fi
fi
'''
        
        hook_path = hooks_dir / "prepare-commit-msg"
        hook_path.write_text(hook_content)
        hook_path.chmod(0o755)
    
    def process_git_event(self, event: Dict) -> Dict:
        """Process a git event and enrich with context"""
        event_type = event.get('type', '')
        
        if event_type == 'git_commit':
            return self._process_commit(event)
        elif event_type == 'git_merge':
            return self._process_merge(event)
        elif event_type == 'git_checkout':
            return self._process_checkout(event)
        
        return event
    
    def _process_commit(self, event: Dict) -> Dict:
        """Process commit event"""
        data = event.get('data', {})
        
        # Enrich with additional context
        event['category'] = data.get('commit_type', 'general')
        event['importance'] = self._calculate_commit_importance(data)
        
        # Extract key information from commit message
        message = data.get('message', '')
        if 'BREAKING' in message.upper():
            event['breaking_change'] = True
            event['importance'] = 9
        
        return event
    
    def _process_merge(self, event: Dict) -> Dict:
        """Process merge event - identify external changes"""
        data = event.get('data', {})
        commits = data.get('commits_merged', '').split()
        
        my_commits = []
        external_commits = []
        
        for commit_hash in commits:
            if self._is_my_commit(commit_hash):
                my_commits.append(commit_hash)
            else:
                external_commits.append(commit_hash)
        
        event['my_commits'] = my_commits
        event['external_commits'] = external_commits
        event['category'] = 'integration'
        event['importance'] = 7 if external_commits else 5
        
        # If there are external commits, extract what they changed
        if external_commits:
            event['external_changes'] = self._analyze_external_commits(external_commits)
        
        return event
    
    def _process_checkout(self, event: Dict) -> Dict:
        """Process checkout event"""
        data = event.get('data', {})
        branch = data.get('branch', '')
        
        # Detect branch type
        if branch.startswith('feature/'):
            event['category'] = 'feature_start'
            event['importance'] = 6
        elif branch.startswith('fix/'):
            event['category'] = 'bugfix_start'
            event['importance'] = 6
        else:
            event['category'] = 'branch_switch'
            event['importance'] = 3
        
        return event
    
    def _is_my_commit(self, commit_hash: str) -> bool:
        """Check if a commit is authored by the user"""
        try:
            result = subprocess.run(
                ['git', 'show', '-s', '--format=%ae', commit_hash],
                capture_output=True,
                text=True
            )
            author_email = result.stdout.strip()
            return author_email == self.my_email
        except:
            return False
    
    def _analyze_external_commits(self, commits: List[str]) -> Dict:
        """Analyze external commits to understand what changed"""
        analysis = {
            'count': len(commits),
            'authors': set(),
            'files_changed': set(),
            'patterns_introduced': [],
            'potential_breaking_changes': []
        }
        
        for commit_hash in commits:
            try:
                # Get commit details
                result = subprocess.run(
                    ['git', 'show', '--format=%an|%s', '--name-only', commit_hash],
                    capture_output=True,
                    text=True
                )
                
                lines = result.stdout.strip().split('\n')
                if lines:
                    author, subject = lines[0].split('|', 1)
                    analysis['authors'].add(author)
                    
                    # Check for breaking changes
                    if 'BREAKING' in subject.upper():
                        analysis['potential_breaking_changes'].append({
                            'commit': commit_hash,
                            'message': subject
                        })
                    
                    # Collect changed files
                    for line in lines[2:]:  # Skip empty line after commit info
                        if line:
                            analysis['files_changed'].add(line)
            except:
                continue
        
        # Convert sets to lists for JSON serialization
        analysis['authors'] = list(analysis['authors'])
        analysis['files_changed'] = list(analysis['files_changed'])
        
        return analysis
    
    def _calculate_commit_importance(self, commit_data: Dict) -> int:
        """Calculate importance score for a commit"""
        importance = 5  # Base score
        
        commit_type = commit_data.get('commit_type', '')
        if commit_type == 'bugfix':
            importance = 7
        elif commit_type == 'feature':
            importance = 8
        elif commit_type == 'refactor':
            importance = 6
        elif commit_type == 'documentation':
            importance = 4
        elif commit_type == 'testing':
            importance = 6
        
        # Adjust based on files changed
        files = commit_data.get('files_changed', '').split()
        if len(files) > 10:
            importance += 1
        if any('test' in f for f in files):
            importance += 1
        
        return min(importance, 10)  # Cap at 10
