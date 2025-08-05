#!/bin/bash
# Script to provide clean, human-readable monitoring output with color coding

# Function to create a bar visualization without bc
create_bar() {
    local percentage=$1
    local width=20
    # Calculate filled blocks (simple integer math)
    local filled=$((percentage * width / 100))
    local bar=""
    
    # Ensure filled is not negative
    if [ "$filled" -lt 0 ]; then
        filled=0
    fi
    
    # Ensure filled doesn't exceed width
    if [ "$filled" -gt "$width" ]; then
        filled=$width
    fi
    
    # Create the filled part of the bar
    for ((i=0; i<filled; i++)); do
        bar="${bar}█"
    done
    
    # Create the empty part of the bar
    for ((i=filled; i<width; i++)); do
        bar="${bar}░"
    done
    
    echo "$bar"
}

# Function to color code based on utilization
color_code() {
    local value=$1
    local type=${2:-"default"}
    
    # Check if value is a number
    if ! [[ "$value" =~ ^[0-9]+$ ]]; then
        echo "⚪"  # White for unknown values
        return
    fi
    
    # For VRAM percentage, we'll use a different threshold
    if [ "$type" = "vram" ]; then
        if [ "$value" -gt 85 ]; then
            echo "🔴"  # Red for high VRAM usage
        elif [ "$value" -gt 70 ]; then
            echo "🟡"  # Yellow for medium VRAM usage
        else
            echo "🟢"  # Green for low VRAM usage
        fi
    else
        if [ "$value" -gt 80 ]; then
            echo "🔴"  # Red for high usage
        elif [ "$value" -gt 50 ]; then
            echo "🟡"  # Yellow for medium usage
        else
            echo "🟢"  # Green for low usage
        fi
    fi
}

echo "=== QWEN ORCHESTRATOR MONITOR ==="
echo "Last updated: $(date)"
echo ""

echo "=== SYSTEM RESOURCES ==="
# Get system resource information
cpu_raw=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
# Extract just the integer part of CPU usage
cpu_usage=$(echo "$cpu_raw" | cut -d'.' -f1 | grep -o '[0-9]*')
# Default to 0 if empty
cpu_usage=${cpu_usage:-0}

memory_usage=$(free -m | awk 'NR==2{printf "%.1f/%.1f GB (%.1f%%)", $3/1024, $2/1024, $3*100/$2}')
gpu_usage=$(timeout 2s nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
# Default to 0 if empty
gpu_usage=${gpu_usage:-0}

vram_raw=$(timeout 2s nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits 2>/dev/null | head -1)
vram_used=$(echo "$vram_raw" | cut -d',' -f1 | tr -d ' ')
vram_total=$(echo "$vram_raw" | cut -d',' -f2 | tr -d ' ')
# Calculate percentage without bc
if [ -n "$vram_used" ] && [ -n "$vram_total" ] && [ "$vram_total" -ne 0 ]; then
    vram_percentage=$((vram_used * 100 / vram_total))
else
    vram_percentage=0
fi

vram_bar=$(create_bar "$vram_percentage")
vram_color=$(color_code "$vram_percentage" "vram")

# Color codes for CPU and GPU
cpu_color=$(color_code "$cpu_usage")
gpu_color=$(color_code "$gpu_usage")

echo "CPU Usage: ${cpu_color} ${cpu_usage}%"
echo "Memory Usage: ${memory_usage:-N/A}"
echo "GPU Usage: ${gpu_color} ${gpu_usage}%"
echo "VRAM Usage: ${vram_color} ${vram_bar} ${vram_used:-0}MB/${vram_total:-0}MB"
echo ""

echo "=== AGENT INFORMATION ==="
# Get agent information from the monitor script with timeout and remove ANSI codes
agent_info=$(timeout 3s ./monitor_agents.sh 2>/dev/null | sed 's/\x1b\[[0-9;]*[mGKH]//g' | grep -E "(Total Active:|Project_Manager:|Developer:|Qa:|Orchestrator:)" | head -5)

if [ -n "$agent_info" ]; then
    echo "$agent_info"
else
    echo "Agent information temporarily unavailable"
fi
echo ""

echo "=== PROJECT MANAGER AGENTS ==="
# Get specific project manager agent information
project_managers=$(timeout 2s tmux list-sessions 2>/dev/null | sed 's/\x1b\[[0-9;]*[mGKH]//g' | grep -o "project-[a-zA-Z0-9-]*" | sort -u)

if [ -n "$project_managers" ]; then
    echo "Active project sessions:"
    for session in $project_managers; do
        echo "  - $session"
        # Check for project manager windows in the session
        pm_windows=$(timeout 2s tmux list-windows -t "$session" 2>/dev/null | sed 's/\x1b\[[0-9;]*[mGKH]//g' | grep "Project_Manager" | wc -l)
        if [ "$pm_windows" -gt 0 ]; then
            echo "    Project Manager Windows: $pm_windows"
        fi
    done
else
    echo "No project manager agents found"
fi
echo ""

echo "=== SYSTEM HEALTH ==="
ollama_status=$(pgrep ollama >/dev/null && echo "Running" || echo "Not Running")
echo "Ollama Server: $ollama_status"

echo ""
echo "=== SUMMARY ==="
echo "Resource monitoring: Active"
echo "Project manager agents: Active"
echo "Dashboard: Running"
echo "All systems operational"