#!/bin/bash

# Unified Dashboard for Qwen Orchestrator using Panes
# Single interface for all dashboard functionality with intuitive UX
# Uses panes with 3 panes on left and chat pane on right

set -e

# Colors for better visualization
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Global variables
SESSION_NAME="qwen-unified-dashboard"
PROJECT_SESSION=""

# Function to print colored output
print_status() {
    echo -e "${BLUE}[DASHBOARD]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "========================================"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

# Function to check if session exists
session_exists() {
    local session_name=$1
    tmux has-session -t "$session_name" 2>/dev/null
}

# Function to get project sessions
get_project_sessions() {
    tmux list-sessions 2>/dev/null | grep "^project-" | cut -d: -f1 || true
}

# Function to create unified dashboard with panes
create_unified_dashboard() {
    local project_session=${1:-}
    
    print_status "Creating unified dashboard with panes..."
    
    # Kill existing dashboard session if it exists
    if session_exists "$SESSION_NAME"; then
        print_warning "Killing existing dashboard session..."
        tmux kill-session -t "$SESSION_NAME" 2>/dev/null
        sleep 1
    fi
    
    # Create new session with detached state
    print_status "Creating new dashboard session..."
    
    # Check if dashboard session already exists
    if session_exists "$SESSION_NAME"; then
        print_warning "Dashboard session already exists. Attaching to existing session."
        attach_dashboard
        return 0
    fi

    print_status "Attempting to create tmux session: $SESSION_NAME"
    if ! tmux new-session -d -s "$SESSION_NAME" -n "Main" 2> /tmp/tmux_new_session_error.log; then
        print_error "Failed to create dashboard session. Check /tmp/tmux_new_session_error.log for details."
        cat /tmp/tmux_new_session_error.log
        return 1
    else
        print_success "Dashboard session created successfully"
    fi
    
    # Create the pane layout:
    # ---------------------
    # | Resources |       |
    # |-----------|       |
    # | Tasks     | Chat  |
    # |-----------|       |
    # | Control   |       |
    # ---------------------
    
    # Split the main window horizontally to create left and right columns
    tmux split-window -t "${SESSION_NAME}:Main" -h
    
    # Split the left column twice vertically to create three panes
    tmux split-window -t "${SESSION_NAME}:Main.0" -v
    tmux split-window -t "${SESSION_NAME}:Main.0" -v
    
    # Rename the panes for clarity
    # Pane 0: Resources (top-left)
    # Pane 1: Tasks (middle-left)
    # Pane 2: Control (bottom-left)
    # Pane 3: Chat (right full-height)
    
    # Set up the Resources pane (pane 0)
    tmux send-keys -t "${SESSION_NAME}:Main.0" \
        "echo -e '${BLUE}=== RESOURCE MONITOR ===${NC}'; \
         echo -e '${CYAN}Monitoring system resources...${NC}'; \
         echo ''; \
         watch -n 2 './readable_monitor.sh'" C-m
    
    # Set up the Tasks pane (pane 1)
    tmux send-keys -t "${SESSION_NAME}:Main.1" \
        "echo -e '${BLUE}=== TASK TRACKING ===${NC}'; \
         echo -e '${CYAN}Monitoring project tasks and git commits...${NC}'; \
         echo ''; \
         watch -n 30 'python3 task_tracker.py'" C-m
    
    # Set up the Control pane (pane 2)
    create_control_script
    local control_script="/tmp/qwen_dashboard_control.sh"
    chmod +x "$control_script"
    tmux send-keys -t "${SESSION_NAME}:Main.2" "$control_script" C-m
    
    # Set up the Chat pane (pane 3)
    tmux send-keys -t "${SESSION_NAME}:Main.3" \
        "echo -e '${BLUE}=== AGENT CHAT HISTORY ===${NC}'; \
         echo -e '${CYAN}Monitoring agent communications in chat room format...${NC}'; \
         echo ''; \
         watch -n 10 'python3 display_chat_history.py'" C-m
    
    # Resize panes to make them more balanced
    # Make the right pane (chat) wider
    tmux resize-pane -t "${SESSION_NAME}:Main.3" -x 70%
    
    print_success "Unified dashboard with panes created successfully!"
    return 0
}

# Function to create control script
create_control_script() {
    local control_script="/tmp/qwen_dashboard_control.sh"
    
    cat > "$control_script" << 'EOF'
#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}=== QWEN ORCHESTRATOR CONTROL PANEL ===${NC}"
    echo -e "${CYAN}Interactive commands for orchestrator management${NC}"
    echo
}

print_commands() {
    echo -e "${YELLOW}Available Commands:${NC}"
    echo "  status     - Show system status"
    echo "  list       - List all agents"
    echo "  sessions   - Show tmux sessions"
    echo "  create     - Create new agent (create <type> <session> <window>)"
    echo "  message    - Send message to agent (message <agent_id> <message>)"
    echo "  archive    - Archive/Delete agent (archive <agent_id>)"
    echo "  projects   - List project sessions"
    echo "  killproj   - Kill project session (killproj <session_name>)"
    echo "  resources  - Show system resource usage"
    echo "  help       - Show this help"
    echo "  quit       - Exit control panel"
    echo "  exit       - Exit control panel"
    echo
}

print_header
print_commands

while true; do
    read -p "dashboard> " cmd args
    
    case $cmd in
        "status")
            python3 qwen_control.py status detailed
            ;;
        "list")
            python3 qwen_control.py list
            ;;
        "sessions")
            tmux list-sessions
            ;;
        "create")
            if [ -n "$args" ]; then
                python3 qwen_control.py create $args
            else
                echo "Usage: create <type> <session> <window>"
            fi
            ;;
        "message")
            if [ -n "$args" ]; then
                ./send-qwen-message.sh $args
            else
                echo "Usage: message <agent_id> <message>"
            fi
            ;;
        "archive")
            if [ -n "$args" ]; then
                python3 qwen_control.py archive $args
            else
                echo "Usage: archive <agent_id>"
            fi
            ;;
        "projects")
            echo "Project Sessions:"
            tmux list-sessions 2>/dev/null | grep "^project-" | cut -d: -f1 || echo "No project sessions found"
            ;;
        "killproj")
            if [ -n "$args" ]; then
                tmux kill-session -t "$args" 2>/dev/null && echo "Killed project session: $args" || echo "Failed to kill project session: $args"
            else
                echo "Usage: killproj <session_name>"
            fi
            ;;
        "help")
            print_commands
            ;;
        "resources")
            # Show system resource usage
            ./monitor_agents.sh --interval 1
            ;;
        "quit"|"exit")
            break
            ;;
        "")
            # Empty command, just show prompt again
            ;;
        *)
            echo "Unknown command. Type 'help' for available commands."
            ;;
    esac
    
    echo
done

echo "Exiting control panel..."
EOF
}

# Function to attach to dashboard
attach_dashboard() {
    if session_exists "$SESSION_NAME"; then
        print_status "Attaching to dashboard session..."
        echo
        echo -e "${YELLOW}Dashboard Controls:${NC}"
        echo "  • Ctrl+B, Arrow Keys - Navigate between panes"
        echo "  • Ctrl+B, D - Detach from dashboard"
        echo
        echo -e "${CYAN}Dashboard Panes:${NC}"
        echo "  • Pane 0: Resources (top-left)"
        echo "  • Pane 1: Tasks (middle-left)"
        echo "  • Pane 2: Control (bottom-left)"
        echo "  • Pane 3: Chat (right full-height)"
        echo
        sleep 2
        tmux attach-session -t "$SESSION_NAME"
    else
        print_error "Dashboard session does not exist. Create it first."
        return 1
    fi
}

# Function to show dashboard status
show_status() {
    if session_exists "$SESSION_NAME"; then
        echo -e "${GREEN}Dashboard session is running${NC}"
        echo "Active windows:"
        tmux list-windows -t "$SESSION_NAME" 2>/dev/null | while read line; do
            echo "  $line"
        done
    else
        echo -e "${RED}Dashboard session is not running${NC}"
    fi
}

# Function to kill dashboard
kill_dashboard() {
    if session_exists "$SESSION_NAME"; then
        print_warning "Killing dashboard session..."
        tmux kill-session -t "$SESSION_NAME"
        if [ $? -eq 0 ]; then
            print_success "Dashboard session killed successfully"
        else
            print_error "Failed to kill dashboard session"
        fi
    else
        print_warning "Dashboard session is not running"
    fi
}

# Function to show project sessions
show_project_sessions() {
    print_status "Available project sessions:"
    echo "=============================="
    
    if tmux list-sessions >/dev/null 2>&1; then
        tmux list-sessions 2>/dev/null | while read line; do
            if [ -n "$line" ]; then
                session_name=$(echo "$line" | cut -d: -f1)
                # Filter for project sessions
                if [[ "$session_name" == project-* ]]; then
                    echo "  🖥️  $session_name"
                fi
            fi
        done
    else
        print_warning "No tmux sessions found"
    fi
    echo "  • Resource usage monitoring (CPU, Memory, GPU, VRAM)"
    echo "  • Agent output monitoring"
    echo "  • Automatic cleanup on detach"
}

# Function to show help
show_help() {
    echo -e "${BLUE}=== QWEN ORCHESTRATOR UNIFIED DASHBOARD (Panes Version) ===${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  ./unified_dashboard_panes.sh [command] [options]"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "  start [project]    Create and start the unified dashboard"
    echo "  attach             Attach to the running dashboard session"
    echo "  status             Show dashboard status"
    echo "  kill               Kill the dashboard session"
    echo "  projects           List available project sessions"
    echo "  help               Show this help message"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./unified_dashboard_panes.sh start"
    echo "  ./unified_dashboard_panes.sh start project-interactivedemo"
    echo "  ./unified_dashboard_panes.sh attach"
    echo "  ./unified_dashboard_panes.sh projects"
    echo ""
    echo -e "${YELLOW}Features:${NC}"
    echo "  • Single unified interface using panes (3 left panes + 1 right chat pane)"
    echo "  • Real-time system monitoring and agent status"
    echo "  • Interactive control panel with CRUD operations"
    echo "  • Project-specific monitoring when specified"
    echo "  • Resource usage monitoring (CPU, Memory, GPU, VRAM)"
    echo "  • Agent output monitoring"
    echo "  • Execution tracking and gap identification"
    echo "  • Automatic cleanup on detach"
}

# Main execution
case "$1" in
    start)
        create_unified_dashboard "$2"
        if [ $? -eq 0 ]; then
            attach_dashboard
        fi
        ;;
    attach)
        attach_dashboard
        ;;
    status)
        show_status
        ;;
    kill)
        kill_dashboard
        ;;
    projects)
        show_project_sessions
        ;;
    help|"")
        show_help
        ;;
    *)
        echo -e "${RED}Invalid command: $1${NC}"
        show_help
        exit 1
        ;;
esac