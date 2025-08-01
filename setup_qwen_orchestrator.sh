#!/bin/bash

# Setup script for Qwen Orchestrator
# Replaces Claude-based system with Qwen 3 Coder + Ollama

set -e  # Exit on any error

echo "🚀 Setting up Qwen Orchestrator"
echo "================================"

# Configuration
QWEN_MODEL="qwen2.5-coder:7b"
BASE_DIR="$HOME/.tmux_orchestrator"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on supported system
check_system() {
    print_status "Checking system compatibility..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    if ! command -v tmux &> /dev/null; then
        print_error "tmux is required but not installed"
        exit 1
    fi
    
    print_success "System compatibility check passed"
}

# Install Ollama if not present
install_ollama() {
    print_status "Checking Ollama installation..."
    
    if command -v ollama &> /dev/null; then
        print_success "Ollama is already installed"
        return 0
    fi
    
    print_status "Installing Ollama..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install ollama
        else
            curl -fsSL https://ollama.ai/install.sh | sh
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        print_error "Unsupported operating system: $OSTYPE"
        print_error "Please install Ollama manually from https://ollama.ai"
        exit 1
    fi
    
    print_success "Ollama installed successfully"
}

# Start Ollama service
start_ollama() {
    print_status "Starting Ollama service..."
    
    # Check if Ollama is already running
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        print_success "Ollama service is already running"
        return 0
    fi
    
    # Start Ollama in background
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - use launchctl or background process
        nohup ollama serve > /dev/null 2>&1 &
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux - try systemctl first, then background process
        if systemctl is-active --quiet ollama 2>/dev/null; then
            systemctl start ollama
        else
            nohup ollama serve > /dev/null 2>&1 &
        fi
    fi
    
    # Wait for service to start
    print_status "Waiting for Ollama service to start..."
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
            print_success "Ollama service started successfully"
            return 0
        fi
        sleep 1
    done
    
    print_error "Failed to start Ollama service"
    exit 1
}

# Download Qwen model
download_qwen_model() {
    print_status "Checking Qwen model availability..."
    
    # Check if model is already available
    if ollama list | grep -q "$QWEN_MODEL"; then
        print_success "Qwen model $QWEN_MODEL is already available"
        return 0
    fi
    
    print_status "Downloading Qwen model: $QWEN_MODEL"
    print_warning "This may take several minutes depending on your internet connection..."
    
    if ollama pull "$QWEN_MODEL"; then
        print_success "Qwen model downloaded successfully"
    else
        print_error "Failed to download Qwen model"
        print_error "You can try manually: ollama pull $QWEN_MODEL"
        exit 1
    fi
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Check if pip is available
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is required but not installed"
        exit 1
    fi
    
    # Install required packages
    pip3 install --user requests aiohttp
    
    print_success "Python dependencies installed"
}

# Create directory structure
create_directories() {
    print_status "Creating directory structure..."
    
    mkdir -p "$BASE_DIR"/{agents,conversations,templates,config,logs}
    
    # Create subdirectories for conversations
    mkdir -p "$BASE_DIR/conversations"/{orchestrator,project_manager,developer,qa,devops,code_reviewer,researcher,documentation,temporary}
    
    print_success "Directory structure created at $BASE_DIR"
}

# Copy configuration files
setup_configuration() {
    print_status "Setting up configuration..."
    
    # Copy Qwen configuration
    if [ -f "$SCRIPT_DIR/qwen_config.json" ]; then
        cp "$SCRIPT_DIR/qwen_config.json" "$BASE_DIR/config/"
        print_success "Qwen configuration copied"
    else
        # Create default configuration
        cat > "$BASE_DIR/config/qwen_config.json" << EOF
{
  "base_url": "http://localhost:11434",
  "model": "$QWEN_MODEL",
  "temperature": 0.7,
  "max_tokens": 2048,
  "timeout": 30,
  "max_retries": 3,
  "retry_delay": 1.0
}
EOF
        print_success "Default Qwen configuration created"
    fi
}

# Test the installation
test_installation() {
    print_status "Testing installation..."
    
    # Test Ollama connection
    if ! curl -s http://localhost:11434/api/tags >/dev/null; then
        print_error "Cannot connect to Ollama service"
        return 1
    fi
    
    # Test Python modules
    if ! python3 -c "import requests, json, threading, subprocess" 2>/dev/null; then
        print_error "Python dependencies not properly installed"
        return 1
    fi
    
    # Test Qwen model
    if ! ollama list | grep -q "$QWEN_MODEL"; then
        print_error "Qwen model not available"
        return 1
    fi
    
    # Test our Python scripts
    cd "$SCRIPT_DIR"
    if python3 -c "import qwen_client; client = qwen_client.QwenClient(); health = client.health_check(); print('Health check:', health['server_running'] and health['model_available']); client.close()" 2>/dev/null | grep -q "True"; then
        print_success "All tests passed!"
        return 0
    else
        print_error "System test failed"
        return 1
    fi
}

# Create example scripts
create_examples() {
    print_status "Creating example scripts..."
    
    # Quick start script
    cat > "$SCRIPT_DIR/quick_start.sh" << 'EOF'
#!/bin/bash
# Quick start script for Qwen Orchestrator

echo "🚀 Starting Qwen Orchestrator"

# Create orchestrator session
python3 -c "
from qwen_tmux_integration import create_orchestrator_session
orchestrator = create_orchestrator_session('qwen-orchestrator')
print('✅ Orchestrator session created: qwen-orchestrator')
print('📋 Use: tmux attach -t qwen-orchestrator')
"
EOF

    chmod +x "$SCRIPT_DIR/quick_start.sh"
    
    # Example project deployment
    cat > "$SCRIPT_DIR/deploy_example_project.sh" << 'EOF'
#!/bin/bash
# Deploy example project with Qwen agents

echo "🏗️  Deploying example project"

python3 -c "
from qwen_tmux_integration import deploy_simple_project
orchestrator = deploy_simple_project('example-webapp', include_qa=True)
print('✅ Example project deployed')
print('📋 Use: tmux attach -t project-example-webapp')
"
EOF

    chmod +x "$SCRIPT_DIR/deploy_example_project.sh"
    
    print_success "Example scripts created"
}

# Main installation process
main() {
    echo ""
    print_status "Starting Qwen Orchestrator setup..."
    echo ""
    
    check_system
    install_ollama
    start_ollama
    download_qwen_model
    install_python_deps
    create_directories
    setup_configuration
    create_examples
    
    echo ""
    print_status "Running installation tests..."
    if test_installation; then
        echo ""
        print_success "🎉 Qwen Orchestrator setup completed successfully!"
        echo ""
        echo "Next steps:"
        echo "1. Start the orchestrator: ./quick_start.sh"
        echo "2. Deploy a test project: ./deploy_example_project.sh"
        echo "3. Check system status: python3 qwen_control.py status"
        echo "4. Send a message: ./send-qwen-message.sh orchestrator 'Hello!'"
        echo ""
        echo "Documentation:"
        echo "- Agent management: python3 qwen_control.py --help"
        echo "- Message sending: ./send-qwen-message.sh --help"
        echo "- Configuration: $BASE_DIR/config/qwen_config.json"
        echo ""
    else
        echo ""
        print_error "❌ Installation test failed"
        echo ""
        echo "Troubleshooting:"
        echo "1. Check Ollama service: curl http://localhost:11434/api/tags"
        echo "2. Check model: ollama list"
        echo "3. Check Python: python3 -c 'import requests'"
        echo "4. Check logs: $BASE_DIR/logs/"
        echo ""
        exit 1
    fi
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Qwen Orchestrator Setup Script"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --model MODEL  Specify Qwen model (default: $QWEN_MODEL)"
        echo "  --test-only    Only run tests, don't install"
        echo ""
        exit 0
        ;;
    --model)
        QWEN_MODEL="$2"
        shift 2
        ;;
    --test-only)
        test_installation
        exit $?
        ;;
esac

# Run main installation
main "$@"