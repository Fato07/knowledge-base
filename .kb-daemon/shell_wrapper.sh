#!/bin/bash
# KB Daemon Shell Wrapper

# Set capture directory
export KB_CAPTURE_DIR="/Users/fathindosunmu/DEV/knowledge-base/.kb-daemon/capture"

kb_capture_command() {
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
{
    "type": "shell_command",
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "data": {
        "command": "$cmd",
        "args": "$args",
        "exit_code": $exit_code,
        "duration": $duration,
        "working_dir": "$working_dir"
    }
}
EOF
    
    # Append to events file
    cat /tmp/kb_event_$$.json >> "$KB_CAPTURE_DIR/shell_events.jsonl"
    rm /tmp/kb_event_$$.json
    
    return $exit_code
}

# Alias tracked commands
KB_TRACK_COMMANDS=(npm yarn pnpm cargo pytest python node docker kubectl terraform ansible make)

for cmd in "${KB_TRACK_COMMANDS[@]}"; do
    if command -v "$cmd" > /dev/null 2>&1; then
        alias $cmd="kb_capture_command $cmd"
    fi
done

# Enhanced prompt command for context
kb_prompt_command() {
    # Capture directory changes
    if [ "$PWD" != "$OLDPWD" ]; then
        echo '{"type":"dir_change","timestamp":"'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'","data":{"from":"'$OLDPWD'","to":"'$PWD'"}}' >> "$KB_CAPTURE_DIR/shell_events.jsonl"
    fi
}

# Add to PROMPT_COMMAND
export PROMPT_COMMAND="${PROMPT_COMMAND:+$PROMPT_COMMAND; }kb_prompt_command"
