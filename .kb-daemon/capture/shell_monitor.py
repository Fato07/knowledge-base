#!/usr/bin/env python3
"""
Shell Monitor - Captures and analyzes shell command execution
"""

import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from queue import Queue
import subprocess
import re

class ShellMonitor:
    """Monitors shell commands and captures important activities"""
    
    def __init__(self, capture_queue: Queue, config: Dict, base_path=None):
        self.capture_queue = capture_queue
        self.config = config
        self.running = False
        self.base_path = base_path or Path.home()
        self.events_file = self.base_path / "capture" / "shell_events.jsonl"
        self.events_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Track command patterns
        self.track_commands = config.get('track_commands', [])
        self.command_history = []  # Keep recent commands for pattern detection
        self.last_error = None
        
    def start(self):
        """Start monitoring shell commands"""
        self.running = True
        
        # Install shell integration
        self._install_shell_integration()
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitor_events, daemon=True)
        monitor_thread.start()
        
    def stop(self):
        """Stop monitoring"""
        self.running = False
        
    def _install_shell_integration(self):
        """Install shell integration for command capture"""
        # Create the command wrapper script
        wrapper_script = self.base_path / "shell_wrapper.sh"
        capture_dir = self.base_path / "capture"
        
        wrapper_content = f'''#!/bin/bash
# KB Daemon Shell Wrapper

# Set capture directory
export KB_CAPTURE_DIR="{capture_dir}"

kb_capture_command() {{
    local cmd="$1"
    shift
    local args="$@"
    local start_time=$(date +%s)
    local working_dir=$(pwd)
    
    # Run the actual command
    command "$cmd" "$args"
    local exit_code=$?
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Capture the output (last 100 lines)
    local output_file="/tmp/kb_cmd_output_$$"
    
    # Create event JSON
    cat > /tmp/kb_event_$$.json <<EOF
{{
    "type": "shell_command",
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "data": {{
        "command": "$cmd",
        "args": "$args",
        "exit_code": $exit_code,
        "duration": $duration,
        "working_dir": "$working_dir"
    }}
}}
EOF
    
    # Append to events file
    cat /tmp/kb_event_$$.json >> "$KB_CAPTURE_DIR/shell_events.jsonl"
    rm /tmp/kb_event_$$.json
    
    return $exit_code
}}

# Alias tracked commands
KB_TRACK_COMMANDS=(npm yarn pnpm cargo pytest python node docker kubectl terraform ansible make)

for cmd in "${{KB_TRACK_COMMANDS[@]}}"; do
    if command -v "$cmd" > /dev/null 2>&1; then
        alias $cmd="kb_capture_command $cmd"
    fi
done

# Enhanced prompt command for context
kb_prompt_command() {{
    # Capture directory changes
    if [ "$PWD" != "$OLDPWD" ]; then
        echo '{{"type":"dir_change","timestamp":"'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'","data":{{"from":"'$OLDPWD'","to":"'$PWD'"}}}}' >> "$KB_CAPTURE_DIR/shell_events.jsonl"
    fi
}}

# Add to PROMPT_COMMAND
export PROMPT_COMMAND="${{PROMPT_COMMAND:+$PROMPT_COMMAND; }}kb_prompt_command"
'''
        
        wrapper_script.write_text(wrapper_content)
        wrapper_script.chmod(0o755)
        
        # Create shell integration installer
        installer = self.base_path / "install_shell.sh"
        installer_content = f'''#!/bin/bash
# KB Daemon Shell Integration Installer

echo "Installing KB Daemon shell integration..."

# Add to appropriate shell config
if [ -n "$BASH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
else
    echo "Unsupported shell"
    exit 1
fi

# Check if already installed
if ! grep -q "kb-daemon/shell_wrapper.sh" "$SHELL_CONFIG" 2>/dev/null; then
    echo "" >> "$SHELL_CONFIG"
    echo "# KB Daemon Shell Integration" >> "$SHELL_CONFIG"
    echo "[ -f ~/.kb-daemon/shell_wrapper.sh ] && source ~/.kb-daemon/shell_wrapper.sh" >> "$SHELL_CONFIG"
    echo "Shell integration added to $SHELL_CONFIG"
    echo "Please restart your shell or run: source $SHELL_CONFIG"
else
    echo "Shell integration already installed"
fi
'''
        
        installer.write_text(installer_content)
        installer.chmod(0o755)
        
        print(f"Shell integration prepared. Run: {installer}")
        
    def _monitor_events(self):
        """Monitor shell events file for new events"""
        if not self.events_file.exists():
            self.events_file.touch()
            
        # Track file position
        last_position = 0
        
        while self.running:
            try:
                if self.events_file.exists():
                    with open(self.events_file, 'r') as f:
                        f.seek(last_position)
                        new_lines = f.readlines()
                        last_position = f.tell()
                        
                        for line in new_lines:
                            if line.strip():
                                try:
                                    event = json.loads(line)
                                    processed_event = self._process_shell_event(event)
                                    if processed_event:
                                        self.capture_queue.put(processed_event)
                                except json.JSONDecodeError:
                                    continue
                                    
            except Exception as e:
                print(f"Error monitoring shell events: {e}")
                
            time.sleep(1)  # Check every second
            
    def _process_shell_event(self, event: Dict) -> Optional[Dict]:
        """Process and enrich shell events"""
        event_type = event.get('type', '')
        
        if event_type == 'shell_command':
            return self._process_command(event)
        elif event_type == 'dir_change':
            return self._process_dir_change(event)
            
        return None
        
    def _process_command(self, event: Dict) -> Optional[Dict]:
        """Process command execution event"""
        data = event.get('data', {})
        command = data.get('command', '')
        
        # Check if command should be tracked
        if command not in self.track_commands and not self._is_important_command(data):
            return None
            
        # Add to command history
        self.command_history.append(event)
        if len(self.command_history) > 100:
            self.command_history.pop(0)
            
        # Categorize the command
        category = self._categorize_command(command, data)
        importance = self._calculate_command_importance(command, data)
        
        # Detect patterns
        patterns = self._detect_patterns()
        
        # Enrich event
        event['category'] = category
        event['importance'] = importance
        event['patterns'] = patterns
        
        # Track errors
        if data.get('exit_code', 0) != 0:
            self.last_error = event
            event['is_error'] = True
            event['importance'] = min(importance + 2, 10)
            
            # Check if this is a fix for previous error
            if self._is_error_fix(event):
                event['fixes_error'] = True
                event['importance'] = 8
                
        return event
        
    def _process_dir_change(self, event: Dict) -> Optional[Dict]:
        """Process directory change event"""
        data = event.get('data', {})
        to_dir = data.get('to', '')
        
        # Detect project switch
        if '/DEV/' in to_dir or '/Projects/' in to_dir:
            project_name = self._extract_project_name(to_dir)
            if project_name:
                event['category'] = 'project_switch'
                event['project'] = project_name
                event['importance'] = 4
                return event
                
        return None
        
    def _is_important_command(self, data: Dict) -> bool:
        """Check if a command is important enough to track"""
        command = data.get('command', '')
        args = data.get('args', '')
        
        # Important patterns
        important_patterns = [
            r'install', r'add', r'remove', r'update', r'upgrade',
            r'build', r'test', r'deploy', r'push', r'pull',
            r'merge', r'rebase', r'commit'
        ]
        
        full_command = f"{command} {args}"
        for pattern in important_patterns:
            if re.search(pattern, full_command, re.IGNORECASE):
                return True
                
        # Long-running commands are usually important
        if data.get('duration', 0) > 5:
            return True
            
        return False
        
    def _categorize_command(self, command: str, data: Dict) -> str:
        """Categorize a command"""
        args = data.get('args', '')
        full_command = f"{command} {args}"
        
        # Package management
        if command in ['npm', 'yarn', 'pnpm', 'pip', 'cargo']:
            if any(x in args for x in ['install', 'add']):
                return 'dependency_add'
            elif any(x in args for x in ['remove', 'uninstall']):
                return 'dependency_remove'
            elif 'test' in args:
                return 'testing'
            elif 'build' in args:
                return 'building'
                
        # Testing
        elif command in ['pytest', 'jest', 'mocha'] or 'test' in full_command:
            return 'testing'
            
        # Docker
        elif command == 'docker':
            if 'build' in args:
                return 'docker_build'
            elif 'run' in args:
                return 'docker_run'
            elif 'compose' in args:
                return 'docker_compose'
                
        # Git
        elif command == 'git':
            git_subcmd = args.split()[0] if args else ''
            return f'git_{git_subcmd}' if git_subcmd else 'git'
            
        # Kubernetes
        elif command == 'kubectl':
            if 'apply' in args:
                return 'deploy'
            elif 'get' in args:
                return 'inspect'
                
        return 'shell_command'
        
    def _calculate_command_importance(self, command: str, data: Dict) -> int:
        """Calculate importance score for a command"""
        args = data.get('args', '')
        duration = data.get('duration', 0)
        
        # Base importance from config
        importance = 5
        
        # High importance commands
        high_importance = ['deploy', 'apply', 'push', 'merge', 'install']
        if any(x in f"{command} {args}" for x in high_importance):
            importance = 8
            
        # Medium importance
        medium_importance = ['test', 'build', 'commit']
        if any(x in f"{command} {args}" for x in medium_importance):
            importance = 6
            
        # Adjust for duration
        if duration > 30:
            importance += 1
        if duration > 60:
            importance += 1
            
        return min(importance, 10)
        
    def _detect_patterns(self) -> List[str]:
        """Detect patterns in recent command history"""
        patterns = []
        
        if len(self.command_history) < 3:
            return patterns
            
        recent = self.command_history[-10:]
        
        # Detect debugging pattern (repeated test runs)
        test_commands = [c for c in recent if c.get('category') == 'testing']
        if len(test_commands) >= 3:
            # Check for failures followed by success
            failures = [c for c in test_commands if c.get('data', {}).get('exit_code', 0) != 0]
            if failures:
                patterns.append('debugging_session')
                
        # Detect dependency installation pattern
        dep_commands = [c for c in recent if 'dependency' in c.get('category', '')]
        if len(dep_commands) >= 2:
            patterns.append('dependency_management')
            
        # Detect build-test cycle
        build_cmds = [c for c in recent if c.get('category') == 'building']
        test_cmds = [c for c in recent if c.get('category') == 'testing']
        if build_cmds and test_cmds:
            patterns.append('build_test_cycle')
            
        return patterns
        
    def _is_error_fix(self, event: Dict) -> bool:
        """Check if this command fixes a previous error"""
        if not self.last_error:
            return False
            
        # Same command succeeding after failure
        if (event.get('data', {}).get('command') == 
            self.last_error.get('data', {}).get('command') and
            event.get('data', {}).get('exit_code') == 0):
            return True
            
        return False
        
    def _extract_project_name(self, path: str) -> Optional[str]:
        """Extract project name from path"""
        parts = Path(path).parts
        
        # Look for common project indicators
        for i, part in enumerate(parts):
            if part in ['DEV', 'Projects', 'MyProjects', 'src']:
                if i + 1 < len(parts):
                    return parts[i + 1]
                    
        # Use last directory name as fallback
        return Path(path).name if Path(path).name else None
