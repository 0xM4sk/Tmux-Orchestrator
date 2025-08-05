#!/bin/bash

# Show Tmux Sessions - Interactive visibility for tmux orchestration
# Shows users what tmux sessions are being created and allows easy attachment

set -e

# Colors for better visualization
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[TMUX VIEWER]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

# Function to show current tmux sessions
show_sessions() {
    print_status "Current tmux sessions:"
    echo "========================"
    
    if tmux list-sessions >/dev/null 2>&1; then
        tmux list-sessions 2>/dev/null | while read line; do
            if [ -n "$line" ]; then
                session_name=$(echo "$line" | cut -d: -f1)
                echo "  🖥️  $session_name"
                
                # Show windows in session
                if tmux list-windows -t "$session_name" >/dev/null 2>&1; then
                    tmux list-windows -t "$session_name" 2>/dev/null | while read window_line; do
                        if [ -n "$window_line" ]; then
                            window_name=$(echo "$window_line" | awk '{print $2}' | sed 's/*$//' | sed 's/-$//')
                            if [ -n "$window_name" ] && [ "$window_name" != "windows" ]; then
                                echo "    🪟 $window_name"
                            fi
                        fi
                    done
                fi
                echo
            fi
        done
    else
        print_warning "No tmux sessions found"
    fi
}

# Function to attach to a session
attach_session() {
    local session_name=$1
    
    if [ -z "$session_name" ]; then
        print_error "Session name required"
        return 1
    fi
    
    if tmux has-session -t "$session_name" 2>/dev/null; then
        print_info "Attaching to session '$session_name'..."
        echo "💡 To detach later: Press Ctrl+B, then D"
        sleep 2
        tmux attach-session -t "$session_name"
    else
        print_error "Session '$session_name' not found"
        return 1
    fi
}

# Function to create and show a session
create_session() {
    local session_name=$1
    local window_name=${2:-"Main"}
    local command=${3:-""}
    
    if [ -z "$session_name" ]; then
        print_error "Session name required"
        return 1
    fi
    
    print_status "Creating tmux session: $session_name"
    
    # Create session
    if tmux new-session -d -s "$session_name" -n "$window_name" 2>/dev/null; then
        print_success "Created session '$session_name' with window '$window_name'"
        
        # If command provided, send it
        if [ -n "$command" ]; then
            print_info "Executing command in $session_name:$window_name: $command"
            tmux send-keys -t "$session_name:$window_name" "$command" C-m
        fi
        
        show_sessions
        return 0
    else
        print_error "Failed to create session '$session_name'"
        return 1
    fi
}

# Function to show session activity
watch_sessions() {
    local watch_time=${1:-5}
    
    print_status "Watching tmux sessions (updates every ${watch_time}s)..."
    print_info "Press Ctrl+C to stop watching"
    echo
    
    while true; do
        clear
        echo -e "${BLUE}=== TMUX SESSION MONITOR ===${NC}"
        echo -e "${CYAN}Last updated: $(date)${NC}"
        echo
        show_sessions
        echo
        echo -e "${YELLOW}Watching... (Ctrl+C to exit)${NC}"
        sleep "$watch_time"
    done
}

# Function to show help
show_help() {
    echo -e "${BLUE}=== TMUX SESSION VIEWER ===${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  ./show_tmux_sessions.sh [command] [options]"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "  list              Show all current tmux sessions"
    echo "  watch [seconds]   Watch sessions with auto-refresh (default: 5s)"
    echo "  create <name> [window] [command]  Create new session"
    echo "  attach <name>     Attach to a session"
    echo "  help              Show this help message"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./show_tmux_sessions.sh list"
    echo "  ./show_tmux_sessions.sh watch 3"
    echo "  ./show_tmux_sessions.sh create myproject Main 'python3 app.py'"
    echo "  ./show_tmux_sessions.sh attach myproject"
}

# Main execution
case "$1" in
    list|"")
        show_sessions
        ;;
    watch)
        watch_sessions "$2"
        ;;
    create)
        create_session "$2" "$3" "$4"
        ;;
    attach)
        attach_session "$2"
        ;;
    help)
        show_help
        ;;
    *)
        print_error "Invalid command: $1"
        show_help
        exit 1
        ;;
esac