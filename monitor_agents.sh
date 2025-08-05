#!/bin/bash

# Monitor Agents and Resource Usage
# Shows real-time information about agents and system resources

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
    echo -e "${BLUE}[MONITOR]${NC} $1"
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

# Function to get system resource usage
get_system_resources() {
    echo -e "${BLUE}=== SYSTEM RESOURCES ===${NC}"
    
    # CPU usage
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    echo "CPU Usage: ${cpu_usage}%"
    
    # Memory usage
    mem_info=$(free -m | grep "Mem:")
    mem_total=$(echo $mem_info | awk '{print $2}')
    mem_used=$(echo $mem_info | awk '{print $3}')
    mem_percent=$(awk "BEGIN {printf \"%.1f\", ($mem_used/$mem_total)*100}")
    echo "Memory Usage: ${mem_used}MB / ${mem_total}MB (${mem_percent}%)"
    
    # GPU and VRAM usage if available
    if command -v nvidia-smi &> /dev/null; then
        gpu_info=$(nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits 2>/dev/null)
        if [ -n "$gpu_info" ]; then
            vram_used=$(echo $gpu_info | cut -d',' -f1 | tr -d ' ')
            vram_total=$(echo $gpu_info | cut -d',' -f2 | tr -d ' ')
            gpu_util=$(echo $gpu_info | cut -d',' -f3 | tr -d ' ')
            vram_percent=$(awk "BEGIN {printf \"%.1f\", ($vram_used/$vram_total)*100}")
            echo "GPU Usage: ${gpu_util}%"
            echo "VRAM Usage: ${vram_used}MB / ${vram_total}MB (${vram_percent}%)"
        fi
    fi
    
    echo
}

# Function to get agent information
get_agent_info() {
    echo -e "${BLUE}=== AGENT INFORMATION ===${NC}"
    
    # Check if qwen_control.py exists
    if [ ! -f "qwen_control.py" ]; then
        print_error "qwen_control.py not found"
        return 1
    fi
    
    # Get agent status
    python3 qwen_control.py status summary 2>/dev/null || print_error "Failed to get agent status"
    
    echo
}

# Function to get agent activity
get_agent_activity() {
    echo -e "${BLUE}=== AGENT ACTIVITY ===${NC}"
    
    # Check if qwen_tmux_integration.py exists
    if [ ! -f "qwen_tmux_integration.py" ]; then
        print_error "qwen_tmux_integration.py not found"
        return 1
    fi
    
    # Get agent activity summary
    python3 -c "
import sys
sys.path.append('.')
from qwen_tmux_integration import QwenTmuxOrchestrator
import json

try:
    orchestrator = QwenTmuxOrchestrator()
    activity = orchestrator.get_agent_activity_summary()
    if 'error' in activity:
        print(f'Error: {activity[\"error\"]}')
        sys.exit(1)
    
    for agent in activity.get('agents', []):
        print(f'Agent: {agent[\"agent_id\"]} ({agent[\"type\"]})')
        print(f'  Session: {agent[\"session\"]}')
        if agent[\"status\"]:
            print(f'  Status: {agent[\"status\"].get(\"status\", \"Unknown\")}')
        print('  Recent Output:')
        output_lines = agent[\"recent_output\"].split('\n')
        for line in output_lines[-5:]:  # Show last 5 lines
            if line.strip():
                print(f'    {line}')
        print()
except Exception as e:
    print(f'Error getting agent activity: {e}')
    sys.exit(1)
" 2>/dev/null || print_error "Failed to get agent activity"
    
    echo
}

# Function to get Ollama model information
get_ollama_info() {
    echo -e "${BLUE}=== OLLAMA INFORMATION ===${NC}"
    
    # Check if Ollama is running
    if command -v ollama &> /dev/null; then
        if ollama list &> /dev/null; then
            echo "Ollama Server: ${GREEN}Running${NC}"
            
            # Get loaded models
            models=$(ollama ps 2>/dev/null)
            if [ -n "$models" ]; then
                echo "Loaded Models:"
                echo "$models" | while read line; do
                    if [[ $line == *"NAME"* ]]; then
                        continue
                    fi
                    echo "  $line"
                done
            else
                echo "No models currently loaded"
            fi
        else
            echo "Ollama Server: ${RED}Not Running${NC}"
        fi
    else
        echo "Ollama Server: ${RED}Not Installed${NC}"
    fi
    
    echo
}

# Function to monitor in real-time
monitor_real_time() {
    local interval=${1:-5}
    
    print_status "Monitoring agents and resources (updates every ${interval}s)..."
    print_info "Press Ctrl+C to stop monitoring"
    echo
    
    while true; do
        clear
        echo -e "${BLUE}=== QWEN ORCHESTRATOR MONITOR ===${NC}"
        echo -e "${CYAN}Last updated: $(date)${NC}"
        echo
        
        get_system_resources
        get_agent_info
        get_agent_activity
        get_ollama_info
        
        echo -e "${YELLOW}Monitoring... (Ctrl+C to exit)${NC}"
        sleep "$interval"
    done
}

# Function to show help
show_help() {
    echo -e "${BLUE}=== QWEN ORCHESTRATOR MONITOR ===${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  ./monitor_agents.sh [options]"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  -i, --interval <seconds>  Set update interval (default: 5)"
    echo "  -h, --help               Show this help message"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./monitor_agents.sh"
    echo "  ./monitor_agents.sh -i 3"
    echo ""
    echo -e "${YELLOW}Features:${NC}"
    echo "  • Real-time system resource monitoring (CPU, Memory, GPU, VRAM)"
    echo "  • Agent status and activity monitoring"
    echo "  • Ollama model loading status"
    echo "  • Automatic updates at specified intervals"
}

# Main execution
main() {
    local interval=5
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -i|--interval)
                interval="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Validate interval
    if ! [[ "$interval" =~ ^[0-9]+$ ]] || [ "$interval" -lt 1 ]; then
        print_error "Interval must be a positive integer"
        exit 1
    fi
    
    # Start monitoring
    monitor_real_time "$interval"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi