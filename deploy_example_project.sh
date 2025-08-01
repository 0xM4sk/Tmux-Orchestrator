#!/bin/bash
# Deploy example project with Qwen agents

echo "🏗️  Deploying example project"

python3 -c "
from qwen_tmux_integration import deploy_simple_project
orchestrator = deploy_simple_project('example-webapp', include_qa=True)
print('✅ Example project deployed')
print('📋 Use: tmux attach -t project-example-webapp')
"
