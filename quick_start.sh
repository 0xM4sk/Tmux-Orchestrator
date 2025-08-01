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
