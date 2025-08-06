#!/bin/bash
# KB Daemon - View captured logs

echo "======================================"
echo "📊 KB DAEMON - CAPTURED DATA"
echo "======================================"

KB_LOGS="$HOME/DEV/knowledge-base/.kb-daemon/logs"
CAPTURE_DIR="$HOME/.kb-daemon/capture"

# Show shadow logs
echo ""
echo "🌙 Shadow Mode Logs:"
if [ -d "$KB_LOGS" ]; then
    LATEST=$(ls -t "$KB_LOGS"/shadow_*.json 2>/dev/null | head -1)
    if [ -n "$LATEST" ]; then
        echo "  Latest: $(basename $LATEST)"
        echo "  Events captured: $(grep -c '{' "$LATEST")"
        echo ""
        echo "  Last 5 activities:"
        tail -5 "$LATEST" | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        event = json.loads(line.strip().rstrip(','))
        cat = event.get('category', 'unknown')
        imp = event.get('importance', 0)
        if 'key_info' in event:
            file = event['key_info'].get('file', '')
            if file:
                print(f'    • [{imp}/10] {cat}: {file}')
        elif 'data' in event and 'pattern' in event['data']:
            print(f'    • [{imp}/10] {cat}: {event[\"data\"][\"pattern\"]}')
    except: pass
" 2>/dev/null
    else
        echo "  No shadow logs found"
    fi
else
    echo "  Log directory not found"
fi

# Show shell events
echo ""
echo "🐚 Shell Events:"
if [ -f "$CAPTURE_DIR/shell_events.jsonl" ]; then
    COUNT=$(wc -l < "$CAPTURE_DIR/shell_events.jsonl")
    echo "  Total: $COUNT events"
    echo "  Recent activity:"
    tail -3 "$CAPTURE_DIR/shell_events.jsonl" | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        event = json.loads(line)
        if event['type'] == 'dir_change':
            print(f'    • Moved to: {event[\"data\"][\"to\"]}')
        elif event['type'] == 'shell_command':
            cmd = event['data'].get('command', 'unknown')
            print(f'    • Command: {cmd}')
    except: pass
" 2>/dev/null
else
    echo "  No shell events captured yet"
fi

# Show git events
echo ""
echo "🔧 Git Events:"
if [ -f "$CAPTURE_DIR/git_events.jsonl" ]; then
    COUNT=$(wc -l < "$CAPTURE_DIR/git_events.jsonl")
    echo "  Total: $COUNT events"
else
    echo "  No git events captured yet"
fi

echo ""
echo "======================================"
echo "📋 Actions:"
echo "  • View full log: cat $LATEST"
echo "  • Run daily review: python3 interface/cli.py review"
echo "  • Check daemon status: ps aux | grep kb_daemon"
echo "======================================"
