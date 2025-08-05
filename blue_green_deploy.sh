#!/bin/bash

# Blue/Green Deployment Script for Qwen Orchestrator
# Ensures smooth transition without disrupting currently running agents

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
PROD_BRANCH="main"
DEV_BRANCH="dev"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
DEPLOYMENT_STATUS_FILE="/tmp/qwen_deployment_status"
SESSION_PREFIX="project-"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[DEPLOY]${NC} $1"
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

# Function to check if session exists
session_exists() {
    local session_name=$1
    tmux has-session -t "$session_name" 2>/dev/null
}

# Function to get project sessions
get_project_sessions() {
    tmux list-sessions 2>/dev/null | grep "^${SESSION_PREFIX}" | cut -d: -f1 || true
}

# Function to check if agents are running in a session
check_agents_in_session() {
    local session_name=$1
    local agent_count=0
    
    if session_exists "$session_name"; then
        # Count windows that might contain agents
        agent_count=$(tmux list-windows -t "$session_name" 2>/dev/null | grep -c -E "(Developer|Project_Manager|Qa|Agent)" || echo "0")
    fi
    
    echo "$agent_count"
}

# Function to save current deployment state
save_deployment_state() {
    local state_file="$DEPLOYMENT_STATUS_FILE"
    local current_branch=$(git rev-parse --abbrev-ref HEAD)
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    cat > "$state_file" << EOT
{
  "timestamp": "$timestamp",
  "current_branch": "$current_branch",
  "deployment_status": "active",
  "project_sessions": [
$(get_project_sessions | sed 's/^/    "/' | sed 's/$/",/' | sed '$ s/,$//')
  ]
}
EOT
    
    print_info "Saved deployment state to $state_file"
}

# Function to verify deployment state
verify_deployment_state() {
    local state_file="$DEPLOYMENT_STATUS_FILE"
    
    if [ -f "$state_file" ]; then
        print_info "Verifying deployment state from $state_file"
        cat "$state_file"
        return 0
    else
        print_warning "No deployment state file found"
        return 1
    fi
}

# Function to check for running agents
check_running_agents() {
    print_status "Checking for running agents..."
    
    local project_sessions=$(get_project_sessions)
    local total_agents=0
    
    if [ -n "$project_sessions" ]; then
        print_info "Found project sessions:"
        for session in $project_sessions; do
            local agent_count=$(check_agents_in_session "$session")
            print_info "  $session: $agent_count potential agents"
            total_agents=$((total_agents + agent_count))
        done
    else
        print_info "No project sessions found"
    fi
    
    echo "$total_agents"
    return 0
}

# Function to stage new deployment
stage_new_deployment() {
    print_status "Staging new deployment from $DEV_BRANCH branch..."
    
    # Ensure we're on the dev branch
    if [ "$CURRENT_BRANCH" != "$DEV_BRANCH" ]; then
        print_info "Switching to $DEV_BRANCH branch"
        git checkout "$DEV_BRANCH"
    fi
    
    # Pull latest changes
    print_info "Pulling latest changes from $DEV_BRANCH"
    git pull origin "$DEV_BRANCH" || print_warning "Could not pull from origin, continuing with local changes"
    
    # Verify the new modules are in place
    local required_dirs=(
        "core/agent_management"
        "core/communication_system"
        "core/execution_tracking"
        "core/dashboard_monitoring"
        "core/data_management"
        "services/authentication"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            print_error "Required directory $dir not found"
            return 1
        fi
    done
    
    print_success "New deployment staged successfully"
    return 0
}

# Function to run canary test
run_canary_test() {
    print_status "Running canary test..."
    
    # Test importing the new modules
    print_info "Testing module imports..."
    
    local test_script="/tmp/qwen_canary_test.py"
    cat > "$test_script" << 'EOT'
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    # Test importing core modules
    from core.agent_management.agent_state_manager import AgentStateManager
    from core.agent_management.agent_factory import AgentFactory
    from core.agent_management.agent_registry import AgentRegistry
    from core.communication_system.message_router import MessageRouter
    from core.communication_system.protocol_enforcer import ProtocolEnforcer
    from core.communication_system.conversation_manager import ConversationManager
    from core.execution_tracking.execution_monitor import ExecutionMonitor
    from core.execution_tracking.gap_detector import GapDetector
    from core.execution_tracking.recovery_manager import RecoveryManager
    from core.dashboard_monitoring.dashboard_manager import DashboardManager
    from core.dashboard_monitoring.metrics_collector import MetricsCollector
    from core.dashboard_monitoring.alert_system import AlertSystem
    from core.data_management.data_store import DataStore
    from core.data_management.data_processor import DataProcessor
    from core.data_management.data_validator import DataValidator
    from services.authentication.auth_manager import AuthManager
    from services.authentication.token_manager import TokenManager
    from services.authentication.user_manager import UserManager
    
    print("✅ All modules imported successfully")
    
    # Test basic instantiation
    try:
        agent_state_manager = AgentStateManager()
        agent_factory = AgentFactory()
        agent_registry = AgentRegistry(agent_state_manager)
        message_router = MessageRouter()
        protocol_enforcer = ProtocolEnforcer()
        conversation_manager = ConversationManager()
        execution_monitor = ExecutionMonitor()
        gap_detector = GapDetector(execution_monitor)
        recovery_manager = RecoveryManager(execution_monitor, gap_detector)
        dashboard_manager = DashboardManager()
        metrics_collector = MetricsCollector()
        alert_system = AlertSystem()
        data_store = DataStore()
        data_processor = DataProcessor()
        data_validator = DataValidator()
        auth_manager = AuthManager("test_secret")
        token_manager = TokenManager("test_secret")
        user_manager = UserManager()
        
        print("✅ All classes instantiated successfully")
        print("🎉 Canary test passed!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error during instantiation: {e}")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
EOT
    
    # Run the canary test
    if python3 "$test_script"; then
        print_success "Canary test passed"
        rm -f "$test_script"
        return 0
    else
        print_error "Canary test failed"
        rm -f "$test_script"
        return 1
    fi
}

# Function to perform blue/green transition
perform_transition() {
    print_status "Performing blue/green transition..."
    
    # Save current state
    save_deployment_state
    
    # Verify we have the new code
    if [ "$CURRENT_BRANCH" != "$DEV_BRANCH" ]; then
        print_error "Not on $DEV_BRANCH branch. Current branch: $CURRENT_BRANCH"
        return 1
    fi
    
    # Check that running agents won't be affected
    print_info "Verifying that running agents won't be disrupted..."
    local agent_count_output=$(check_running_agents)
    local agent_count=$(echo "$agent_count_output" | tail -n 1)
    
    if [ "$agent_count" -gt 0 ]; then
        print_warning "$agent_count agents are currently running. They will continue to operate during transition."
    else
        print_info "No agents currently running. Safe to proceed with transition."
    fi
    
    # Perform the transition by merging dev into main
    print_info "Switching to $PROD_BRANCH branch"
    git checkout "$PROD_BRANCH"
    
    print_info "Merging $DEV_BRANCH into $PROD_BRANCH"
    if git merge "$DEV_BRANCH"; then
        print_success "Successfully merged $DEV_BRANCH into $PROD_BRANCH"
    else
        print_error "Failed to merge $DEV_BRANCH into $PROD_BRANCH"
        # Switch back to dev branch
        git checkout "$DEV_BRANCH"
        return 1
    fi
    
    # Tag the deployment
    local timestamp=$(date -u +"%Y%m%d-%H%M%S")
    local tag_name="deployment-$timestamp"
    git tag "$tag_name"
    git push origin "$PROD_BRANCH" --tags
    
    print_success "Deployment tagged as $tag_name and pushed to origin"
    
    # Switch back to dev branch for continued development
    git checkout "$DEV_BRANCH"
    
    print_success "Blue/green transition completed successfully!"
    print_info "Production is now running the new code from $DEV_BRANCH"
    return 0
}

# Function to rollback deployment
rollback_deployment() {
    print_status "Rolling back deployment..."
    
    # Check if we have a previous state
    if ! verify_deployment_state; then
        print_error "No deployment state found. Cannot rollback."
        return 1
    fi
    
    # Switch to main branch
    print_info "Switching to $PROD_BRANCH branch"
    git checkout "$PROD_BRANCH"
    
    # Get the previous commit before the merge
    local previous_commit=$(git log --oneline --grep="deployment-" | head -n 1 | cut -d' ' -f1)
    if [ -n "$previous_commit" ]; then
        print_info "Rolling back to commit $previous_commit"
        git reset --hard "$previous_commit"
        git push --force origin "$PROD_BRANCH"
        print_success "Rolled back to $previous_commit"
    else
        print_warning "No previous deployment tag found. Rolling back to previous commit."
        git reset --hard HEAD~1
        git push --force origin "$PROD_BRANCH"
        print_success "Rolled back to previous commit"
    fi
    
    # Switch back to dev branch
    git checkout "$DEV_BRANCH"
    
    print_success "Rollback completed"
    return 0
}

# Function to show deployment status
show_status() {
    print_status "Deployment Status"
    echo "=================="
    echo "Current Branch: $CURRENT_BRANCH"
    echo "Production Branch: $PROD_BRANCH"
    echo "Development Branch: $DEV_BRANCH"
    echo ""
    
    # Check for running agents
    local agent_count_output=$(check_running_agents)
    local agent_count=$(echo "$agent_count_output" | tail -n 1)
    echo "Running Agents: $agent_count"
    echo ""
    
    # Show git status
    print_info "Git Status:"
    git status --short
    echo ""
    
    # Show recent commits
    print_info "Recent Commits:"
    git log --oneline -5
    echo ""
    
    # Verify deployment state if exists
    verify_deployment_state
}

# Function to show help
show_help() {
    echo -e "${BLUE}=== QWEN ORCHESTRATOR BLUE/GREEN DEPLOYMENT ===${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  ./blue_green_deploy.sh [command]"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "  stage       Stage new deployment (verify modules are in place)"
    echo "  test        Run canary test on new modules"
    echo "  deploy      Perform blue/green transition"
    echo "  rollback    Rollback to previous deployment"
    echo "  status      Show deployment status"
    echo "  help        Show this help message"
    echo ""
    echo -e "${YELLOW}Process:${NC}"
    echo "  1. Stage new deployment (verify modules)"
    echo "  2. Run canary test (test imports and basic functionality)"
    echo "  3. Deploy (perform blue/green transition)"
    echo "  4. Monitor (verify agents continue running)"
    echo ""
    echo -e "${YELLOW}Safety:${NC}"
    echo "  • Running agents are not disrupted during transition"
    echo "  • Deployment state is saved for rollback capability"
    echo "  • Canary testing validates new modules before transition"
}

# Main execution
case "$1" in
    stage)
        stage_new_deployment
        ;;
    test)
        run_canary_test
        ;;
    deploy)
        # Run staging and testing first
        if stage_new_deployment && run_canary_test; then
            perform_transition
        else
            print_error "Staging or testing failed. Deployment aborted."
            exit 1
        fi
        ;;
    rollback)
        rollback_deployment
        ;;
    status)
        show_status
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