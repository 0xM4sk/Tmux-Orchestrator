#!/bin/bash

# Unified Dashboard for Qwen Orchestrator
# Single interface for all dashboard functionality with intuitive UX
# Maintains modularity while constraining user interaction to a single panel

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

# Function to get session windows
get_session_windows() {
    local session_name=$1
    if session_exists "$session_name"; then
        tmux list-windows -t "$session_name" 2>/dev/null | awk '{print $2}' | sed 's/*$//' | sed 's/-$//' | grep -v "^windows$"
    fi
}

# Function to create unified dashboard
create_unified_dashboard() {
    local project_session=${1:-}
    
    print_status "Creating unified dashboard..."
    
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
    if ! tmux new-session -d -s "$SESSION_NAME" -n "Overview" 2> /tmp/tmux_new_session_error.log; then
        print_error "Failed to create dashboard session. Check /tmp/tmux_new_session_error.log for details."
        cat /tmp/tmux_new_session_error.log
        return 1
    else
        print_success "Dashboard session created successfully"
    fi
    
    # Set up the main overview window with system monitoring
    tmux send-keys -t "${SESSION_NAME}:Overview" \
        "echo -e '${BLUE}=== QWEN ORCHESTRATOR UNIFIED DASHBOARD ===${NC}'; \
         echo -e '${YELLOW}Session: $SESSION_NAME${NC}'; \
         echo -e '${CYAN}Monitoring system status and active agents...${NC}'; \
         echo ''; \
         watch -n 5 'python3 qwen_control.py status detailed'" C-m
    
    # Create Agent Output window
    tmux new-window -t "$SESSION_NAME" -n "AgentOutput"
    tmux send-keys -t "${SESSION_NAME}:AgentOutput" \
        "echo -e '${BLUE}=== AGENT OUTPUT ===${NC}'; \
         echo -e '${CYAN}Monitoring agent activities and outputs...${NC}'; \
         echo ''; \
         watch -n 10 './extract_dashboard_info.sh AgentOutput'" C-m
    
    # Create Execution Tracking window
    tmux new-window -t "$SESSION_NAME" -n "Execution"
    tmux send-keys -t "${SESSION_NAME}:Execution" \
        "echo -e '${BLUE}=== EXECUTION TRACKING ===${NC}'; \
         echo -e '${CYAN}Monitoring execution flow and identifying gaps...${NC}'; \
         echo ''; \
         watch -n 30 'python3 -c \"
import json
from agentic_capabilities import AgenticExecutor
executor = AgenticExecutor()
summary = executor.get_execution_summary()
print(\"Total Actions: {0}\".format(summary[\"total_actions\"]))
print(\"Identified Gaps: {0}\".format(summary[\"identified_gaps\"]))
if summary[\"gaps\"] and len(summary[\"gaps\"]) > 0:
    print(\"Gaps Details:\")
    for gap in summary[\"gaps\"]:
        print(\"  Agent {0} had a {1:.0f}s gap\".format(gap[\"agent_id\"], gap[\"duration_seconds\"]))
\"'" C-m
    
    # Create Projects window if project session specified
    if [ -n "$project_session" ]; then
        tmux new-window -t "$SESSION_NAME" -n "Project"
        # Wait a moment for the window to be created
        sleep 1
        local project_monitor_script="/tmp/qwen_project_monitor.py"
        cat > "$project_monitor_script" << EOT
import subprocess
import time
from datetime import datetime

def get_session_info(session_name):
    try:
        result = subprocess.run(['tmux', 'list-windows', '-t', session_name], capture_output=True, text=True)
        print("Session: " + session_name)
        print("=" * 40)
        for line in result.stdout.strip().split('\\n'):
            if line and ':' in line:
                parts = line.split()
                if len(parts) > 1:
                    window_name = parts[1].replace('*', '').replace('-', '')
                    if window_name and window_name != "windows":
                        print("  Window: " + window_name)
        print()
    except Exception as e:
        print("Error: " + str(e))
        
get_session_info('$project_session')
print("Last Updated: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
EOT
        chmod +x "$project_monitor_script"
        tmux send-keys -t "${SESSION_NAME}:Project" \
            "echo -e '${BLUE}=== PROJECT MONITORING: $project_session ===${NC}'; \
             echo -e '${CYAN}Monitoring project windows and agent activity...${NC}'; \
             echo ''; \
             watch -n 3 'python3 $project_monitor_script'" C-m
        # Send the monitoring command to the Project window
        tmux send-keys -t "${SESSION_NAME}:Project" \
            "echo -e '${BLUE}=== PROJECT MONITORING: $project_session ===${NC}'; \
             echo -e '${CYAN}Monitoring project windows and agent activity...${NC}'; \
             echo ''; \
             watch -n 3 'python3 $project_monitor_script'" C-m
    fi
    
    # Create Logs window
    tmux new-window -t "$SESSION_NAME" -n "Logs"
    tmux send-keys -t "${SESSION_NAME}:Logs" \
        "echo -e '${BLUE}=== SYSTEM LOGS ===${NC}'; \
         echo -e '${CYAN}Monitoring system activity and agent communications...${NC}'; \
         echo ''; \
         tail -f ~/.qwen_orchestrator/logs/system.log 2>/dev/null || echo 'No logs available yet'" C-m
    
    # Create Interactive Control window
    tmux new-window -t "$SESSION_NAME" -n "Control"
    create_control_script
    
    # Create Resource Monitor window
    tmux new-window -t "$SESSION_NAME" -n "Resources"
    tmux send-keys -t "${SESSION_NAME}:Resources" \
        "echo -e '${BLUE}=== RESOURCE MONITOR ===${NC}'; \
         echo -e '${CYAN}Monitoring system resources...${NC}'; \
         echo ''; \
         watch -n 2 './readable_monitor.sh'" C-m
    
    # Create Chat History window
    tmux new-window -t "$SESSION_NAME" -n "Chat"
    tmux send-keys -t "${SESSION_NAME}:Chat" \
        "echo -e '${BLUE}=== AGENT CHAT HISTORY ===${NC}'; \
         echo -e '${CYAN}Monitoring agent communications in chat room format...${NC}'; \
         echo ''; \
         watch -n 10 'python3 display_chat_history.py'" C-m
    
    # Create Task Tracking window
    tmux new-window -t "$SESSION_NAME" -n "Tasks"
    tmux send-keys -t "${SESSION_NAME}:Tasks" \
        "echo -e '${BLUE}=== TASK TRACKING ===${NC}'; \
         echo -e '${CYAN}Monitoring project tasks and git commits...${NC}'; \
         echo ''; \
         watch -n 30 'python3 task_tracker.py'" C-m
    
    print_success "Unified dashboard created successfully!"
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

    chmod +x "$control_script"
    tmux send-keys -t "${SESSION_NAME}:Control" "$control_script" C-m
}

# Function to attach to dashboard
attach_dashboard() {
    if session_exists "$SESSION_NAME"; then
        print_status "Attaching to dashboard session..."
        echo
        echo -e "${YELLOW}Dashboard Controls:${NC}"
        echo "  • Ctrl+B, N - Next window"
        echo "  • Ctrl+B, P - Previous window"  
        echo "  • Ctrl+B, [number] - Switch to window"
        echo "  • Ctrl+B, D - Detach from dashboard"
        echo
        echo -e "${CYAN}Dashboard Windows:${NC}"
        tmux list-windows -t "$SESSION_NAME" 2>/dev/null | while read line; do
            if [ -n "$line" ]; then
                window_num=$(echo "$line" | cut -d: -f1)
                window_name=$(echo "$line" | awk '{print $2}' | sed 's/*$//' | sed 's/-$//')
                echo "  Window $window_num: $window_name"
            fi
        done
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
    echo -e "${BLUE}=== QWEN ORCHESTRATOR UNIFIED DASHBOARD ===${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  ./unified_dashboard.sh [command] [options]"
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
    echo "  ./unified_dashboard.sh start"
    echo "  ./unified_dashboard.sh start project-interactivedemo"
    echo "  ./unified_dashboard.sh attach"
    echo "  ./unified_dashboard.sh projects"
    echo ""
    echo -e "${YELLOW}Features:${NC}"
    echo "  • Single unified interface for all dashboard functionality"
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