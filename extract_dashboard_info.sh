#!/bin/bash
# Script to extract clean information from dashboard windows

WINDOW_NAME=${1:-"Resources"}

# Function to extract key information from tmux window
extract_info() {
    local session_name=$1
    local window_name=$2
    
    # Get the window ID
    window_id=$(tmux list-windows -t "$session_name" 2>/dev/null | grep "$window_name" | head -1 | cut -d: -f1)
    
    if [ -n "$window_id" ]; then
        # Capture the pane content
        content=$(tmux capture-pane -t "${session_name}:${window_id}" -p -S -50 2>/dev/null)
        
        # Extract system resources information
        if [ "$window_name" = "Resources" ]; then
            echo "=== SYSTEM RESOURCES ==="
            echo "$content" | grep -E "(CPU Usage:|Memory Usage:|GPU Usage:|VRAM Usage:)" | sed 's/\x1b\[[0-9;]*[mGKH]//g'
        elif [ "$window_name" = "AgentOutput" ]; then
            echo "=== AGENT OUTPUT ==="
            echo "$content" | grep -A 5 -E "Agent:.*project_manager" | sed 's/\x1b\[[0-9;]*[mGKH]//g'
        else
            echo "=== $window_name WINDOW ==="
            # Just clean the content
            echo "$content" | sed 's/\x1b\[[0-9;]*[mGKH]//g' | head -10
        fi
    else
        echo "Window '$window_name' not found in session '$session_name'"
    fi
}

# Check if unified dashboard session exists
if tmux has-session -t "qwen-unified-dashboard" 2>/dev/null; then
    echo "=== $WINDOW_NAME WINDOW INFORMATION ==="
    extract_info "qwen-unified-dashboard" "$WINDOW_NAME"
else
    echo "Dashboard session not found"
    
    # Try to find any dashboard session
    dashboard_session=$(tmux list-sessions 2>/dev/null | grep -E "(dashboard|Dashboard)" | head -1 | cut -d: -f1)
    
    if [ -n "$dashboard_session" ]; then
        echo "Found dashboard session: $dashboard_session"
        extract_info "$dashboard_session" "$WINDOW_NAME"
    else
        echo "No dashboard session found"
    fi
fi