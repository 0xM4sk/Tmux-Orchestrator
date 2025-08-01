#!/bin/bash

# Send message to Qwen agent via API
# Usage: send-qwen-message.sh <agent_id> <message>
# Replaces send-claude-message.sh with API-based communication

if [ $# -lt 2 ]; then
    echo "Usage: $0 <agent_id> <message>"
    echo "Example: $0 pm_ai-chat 'What is the current status of the authentication system?'"
    echo ""
    echo "Available agent discovery:"
    echo "  List all agents: python3 qwen_control.py list"
    echo "  Agent info: python3 qwen_control.py info <agent_id>"
    exit 1
fi

AGENT_ID="$1"
shift  # Remove first argument, rest is the message
MESSAGE="$*"

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH="${SCRIPT_DIR}"
LOG_FILE="${HOME}/.tmux_orchestrator/logs/message_log.txt"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Function to check if agent exists
check_agent_exists() {
    local agent_id="$1"
    
    # Use qwen_control.py to check if agent exists
    if ! python3 "${PYTHON_PATH}/qwen_control.py" info "$agent_id" >/dev/null 2>&1; then
        return 1
    fi
    return 0
}

# Function to send message via API
send_api_message() {
    local agent_id="$1"
    local message="$2"
    
    # Use enhanced qwen_control.py to send the message
    local response
    response=$(python3 "${PYTHON_PATH}/qwen_control.py" message "$agent_id" "$message" 2>&1)
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo "✅ Message sent to $agent_id"
        log_message "SUCCESS: Message sent to $agent_id: $message"
        
        # Display response if available
        if [ -n "$response" ] && [ "$response" != "null" ]; then
            echo ""
            echo "🤖 Response from $agent_id:"
            echo "────────────────────────────────────────"
            echo "$response"
            echo "────────────────────────────────────────"
        fi
        return 0
    else
        echo "❌ Failed to send message to $agent_id"
        echo "Error: $response"
        log_message "ERROR: Failed to send message to $agent_id: $response"
        return 1
    fi
}

# Function to find agent by session:window format (backward compatibility)
find_agent_by_session_window() {
    local session_window="$1"
    
    # Check if it's in session:window format
    if [[ "$session_window" =~ ^([^:]+):([0-9]+)$ ]]; then
        local session="${BASH_REMATCH[1]}"
        local window="${BASH_REMATCH[2]}"
        
        # Try to find agent in that session and window
        local agents_output
        agents_output=$(python3 "${PYTHON_PATH}/qwen_control.py" list --session "$session" 2>/dev/null)
        
        if [ $? -eq 0 ]; then
            # Parse the output to find agent in the specific window
            local agent_id
            agent_id=$(echo "$agents_output" | grep -E "- ${session}:${window} -" | awk '{print $1}')
            
            if [ -n "$agent_id" ]; then
                echo "$agent_id"
                return 0
            fi
        fi
    fi
    
    return 1
}

# Function to suggest similar agent IDs
suggest_agents() {
    local input_id="$1"
    
    echo ""
    echo "🔍 Available agents:"
    python3 "${PYTHON_PATH}/qwen_control.py" list 2>/dev/null | head -10
    
    echo ""
    echo "💡 Tips:"
    echo "  - Use 'python3 qwen_control.py list' to see all agents"
    echo "  - Use 'python3 qwen_control.py list --session <session>' to filter by session"
    echo "  - Agent IDs are typically in format: <type>_<session> (e.g., pm_ai-chat, dev_frontend)"
}

# Main execution
main() {
    log_message "Attempting to send message to $AGENT_ID: $MESSAGE"
    
    # First, try direct agent ID lookup
    if check_agent_exists "$AGENT_ID"; then
        send_api_message "$AGENT_ID" "$MESSAGE"
        exit $?
    fi
    
    # If not found, try session:window format (backward compatibility)
    echo "⚠️  Agent '$AGENT_ID' not found, checking session:window format..."
    
    local resolved_agent
    resolved_agent=$(find_agent_by_session_window "$AGENT_ID")
    
    if [ $? -eq 0 ] && [ -n "$resolved_agent" ]; then
        echo "✅ Found agent: $resolved_agent"
        send_api_message "$resolved_agent" "$MESSAGE"
        exit $?
    fi
    
    # Agent not found
    echo "❌ Agent '$AGENT_ID' not found"
    log_message "ERROR: Agent $AGENT_ID not found"
    
    suggest_agents "$AGENT_ID"
    exit 1
}

# Health check function
health_check() {
    echo "🏥 Qwen Orchestrator Health Check"
    echo "=================================="
    
    # Check if Python dependencies are available
    if ! python3 -c "import qwen_client, agent_state, conversation_manager" 2>/dev/null; then
        echo "❌ Python dependencies not found"
        echo "   Make sure qwen_client.py, agent_state.py, and conversation_manager.py are in the same directory"
        return 1
    fi
    
    # Check system status
    python3 "${PYTHON_PATH}/qwen_control.py" health 2>/dev/null
    local health_exit=$?
    
    if [ $health_exit -eq 0 ]; then
        echo "✅ System health check passed"
        return 0
    else
        echo "❌ System health check failed"
        return 1
    fi
}

# Handle special commands
case "$AGENT_ID" in
    "--help"|"-h")
        echo "Send message to Qwen agent via API"
        echo ""
        echo "Usage: $0 <agent_id> <message>"
        echo ""
        echo "Examples:"
        echo "  $0 orchestrator 'Show me the status of all projects'"
        echo "  $0 pm_ai-chat 'What is the current progress on authentication?'"
        echo "  $0 dev_frontend 'Please implement the login form component'"
        echo ""
        echo "Agent Management:"
        echo "  List agents:     python3 qwen_control.py list"
        echo "  Agent info:      python3 qwen_control.py info <agent_id>"
        echo "  System status:   python3 qwen_control.py status"
        echo ""
        echo "Backward Compatibility:"
        echo "  You can still use session:window format (e.g., ai-chat:0)"
        echo "  The script will try to resolve it to the actual agent ID"
        exit 0
        ;;
    "--health")
        health_check
        exit $?
        ;;
    "--version")
        echo "send-qwen-message.sh v2.0 - Qwen API Edition"
        echo "Replaces Claude CLI with Qwen 3 Coder API communication"
        exit 0
        ;;
esac

# Validate inputs
if [ -z "$AGENT_ID" ]; then
    echo "❌ Agent ID cannot be empty"
    exit 1
fi

if [ -z "$MESSAGE" ]; then
    echo "❌ Message cannot be empty"
    exit 1
fi

# Run main function
main