#!/bin/bash
# Script to clean ANSI escape codes from dashboard window outputs

WINDOW_NAME=${1:-"Resources"}

# Comprehensive function to remove all ANSI escape codes
remove_ansi_codes() {
    sed 's/\x1b\[[0-9;]*[mGKH]//g' | \
    sed 's/\x1b\[?25[lh]//g' | \
    sed 's/\x1b\[?1049[h]//g' | \
    sed 's/\x1b\[2J//g' | \
    sed 's/\x1b\[H//g' | \
    sed 's/\x1b\[3J//g' | \
    sed 's/\^[[:digit:]:]*;//g' | \
    sed 's/\\033\[[0-9;]*[mGKH]//g' | \
    sed 's/\\e\[[0-9;]*[mGKH]//g' | \
    tr -d '\000-\037\177-\237'
}

# Function to clean tmux window output
clean_tmux_output() {
    local session_name=$1
    local window_name=$2
    
    # Get the window ID
    window_id=$(tmux list-windows -t "$session_name" 2>/dev/null | grep "$window_name" | head -1 | cut -d: -f1)
    
    if [ -n "$window_id" ]; then
        # Capture and clean the pane content
        tmux capture-pane -t "${session_name}:${window_id}" -p -S -50 2>/dev/null | remove_ansi_codes
    else
        echo "Window '$window_name' not found in session '$session_name'"
    fi
}

# Check if unified dashboard session exists
if tmux has-session -t "qwen-unified-dashboard" 2>/dev/null; then
    echo "=== $WINDOW_NAME WINDOW OUTPUT ==="
    clean_tmux_output "qwen-unified-dashboard" "$WINDOW_NAME"
else
    echo "Dashboard session not found"
    
    # Try to find any dashboard session
    dashboard_session=$(tmux list-sessions 2>/dev/null | grep -E "(dashboard|Dashboard)" | head -1 | cut -d: -f1)
    
    if [ -n "$dashboard_session" ]; then
        echo "Found dashboard session: $dashboard_session"
        clean_tmux_output "$dashboard_session" "$WINDOW_NAME"
    else
        echo "No dashboard session found"
    fi
fi