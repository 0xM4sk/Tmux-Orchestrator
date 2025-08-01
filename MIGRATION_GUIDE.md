# Migration Guide: Claude to Qwen 3 Coder

This guide walks you through migrating your existing Claude-based Tmux Orchestrator to the new Qwen 3 Coder + Ollama system.

## 🎯 Migration Overview

### What's Changing
- **AI Backend**: Claude CLI → Qwen 3 Coder via Ollama API
- **Cost Model**: Subscription-based → Free local processing
- **Agent Runtime**: Interactive CLI sessions → Persistent API-based agents
- **Message System**: tmux send-keys → Direct API communication
- **State Management**: Session-based → Persistent conversation history

### What Stays the Same
- **Tmux Architecture**: Multi-window, multi-session orchestration
- **Agent Hierarchy**: Orchestrator → Project Managers → Developers/QA
- **Workflow Patterns**: Task assignment, status reporting, coordination
- **Git Discipline**: 30-minute commits, feature branches, meaningful messages

## 📋 Pre-Migration Checklist

### System Requirements
- [ ] **Operating System**: macOS or Linux
- [ ] **Python**: 3.8 or higher
- [ ] **tmux**: Latest version
- [ ] **Memory**: 8GB+ RAM (16GB+ recommended for larger models)
- [ ] **Storage**: 10GB+ free space for models and conversation history
- [ ] **Network**: Internet connection for initial model download

### Backup Current System
```bash
# 1. Backup existing tmux sessions
tmux list-sessions > ~/claude_sessions_backup.txt

# 2. Capture current agent conversations (if any)
mkdir -p ~/claude_backup
for session in $(tmux list-sessions -F "#{session_name}"); do
    for window in $(tmux list-windows -t "$session" -F "#{window_index}"); do
        tmux capture-pane -t "$session:$window" -p > ~/claude_backup/"${session}_${window}.txt"
    done
done

# 3. Backup configuration files
cp -r ~/Coding/Tmux\ orchestrator ~/claude_orchestrator_backup
```

## 🚀 Step-by-Step Migration

### Step 1: Install New System

```bash
# Navigate to your orchestrator directory
cd ~/Coding/Tmux\ orchestrator

# Run the setup script
./setup_qwen_orchestrator.sh
```

The setup script will:
- Install Ollama if not present
- Download Qwen 3 Coder model
- Install Python dependencies
- Create directory structure
- Configure the system
- Run health checks

### Step 2: Verify Installation

```bash
# Check system health
python3 qwen_control.py health

# Test basic functionality
python3 qwen_control.py status

# Test message sending
./send-qwen-message.sh --help
```

Expected output should show:
- ✅ Ollama server running
- ✅ Qwen model available
- ✅ Python dependencies installed

### Step 3: Migrate Existing Sessions

#### Option A: Clean Start (Recommended)
```bash
# Start fresh orchestrator session
./quick_start.sh

# Deploy example project to test
./deploy_example_project.sh
```

#### Option B: Preserve Existing Sessions
```bash
# For each existing tmux session, create corresponding agents
python3 qwen_control.py create orchestrator orchestrator-session 0
python3 qwen_control.py create project_manager your-project 0
python3 qwen_control.py create developer your-project 1
```

### Step 4: Update Workflows

#### Replace Claude Commands
| Old Command | New Command |
|-------------|-------------|
| `claude` | `python3 qwen_agent.py <agent_id>` |
| `./send-claude-message.sh session:window "msg"` | `./send-qwen-message.sh agent_id "msg"` |
| `python3 claude_control.py status` | `python3 qwen_control.py status` |

#### Update Scheduling Scripts
The system automatically updates `schedule_with_note.sh` to use `qwen_control.py` instead of `claude_control.py`.

#### Update Agent Briefings
Agent role prompts are now managed in the system. You can customize them by:
```bash
# View current role templates
ls ~/.tmux_orchestrator/templates/

# Edit role prompts
nano ~/.tmux_orchestrator/templates/orchestrator_prompt.txt
```

## 🔄 Command Migration Reference

### Agent Management
```bash
# OLD: Start Claude in tmux window
tmux send-keys -t session:0 "claude" Enter

# NEW: Start Qwen agent
python3 qwen_agent.py --create --role orchestrator --session session --window 0 orchestrator
# OR use the integrated approach:
python3 -c "from qwen_tmux_integration import QwenTmuxOrchestrator; o = QwenTmuxOrchestrator(); o.create_agent_in_window('session', 0, 'orchestrator')"
```

### Message Sending
```bash
# OLD: Send message via tmux
./send-claude-message.sh ai-chat:0 "What's your status?"

# NEW: Send message via API
./send-qwen-message.sh pm_ai-chat "What's your status?"
```

### System Monitoring
```bash
# OLD: Check Claude status (if claude_control.py existed)
python3 claude_control.py status detailed

# NEW: Check Qwen system status
python3 qwen_control.py status detailed
```

### Agent Communication
```bash
# OLD: Manual tmux message coordination
./send-claude-message.sh pm:0 "Check with developer in window 1"

# NEW: Structured agent communication
python3 -c "
from agent_communication import create_communication_hub
from agent_state import AgentStateManager
from conversation_manager import ConversationManager
from qwen_client import QwenClient

# Create communication hub
client = QwenClient()
state_mgr = AgentStateManager()
conv_mgr = ConversationManager(state_mgr, client)
hub = create_communication_hub(state_mgr, conv_mgr)

# Send structured status request
hub.request_status('pm_project', 'dev_project')
"
```

## 🔧 Configuration Migration

### Environment Variables
```bash
# OLD: Claude API configuration (if any)
export CLAUDE_API_KEY="your-key"

# NEW: Ollama configuration (usually defaults work)
export OLLAMA_HOST="http://localhost:11434"  # Optional, this is default
```

### Configuration Files
```bash
# OLD: Claude configuration (if any)
# Usually none needed

# NEW: Qwen configuration
cat ~/.tmux_orchestrator/config/qwen_config.json
```

### Agent Role Customization
```bash
# NEW: Customize agent roles
nano ~/.tmux_orchestrator/templates/orchestrator_prompt.txt
nano ~/.tmux_orchestrator/templates/project_manager_prompt.txt
nano ~/.tmux_orchestrator/templates/developer_prompt.txt
```

## 📊 Feature Comparison

| Feature | Claude System | Qwen System | Migration Notes |
|---------|---------------|-------------|-----------------|
| **Cost** | Subscription ($20/month) | Free | Immediate cost savings |
| **Speed** | 1-3 seconds | 2-5 seconds | Slightly slower, but local |
| **Privacy** | Cloud-based | Local | All data stays on your machine |
| **Availability** | Internet required | Offline capable | Works without internet |
| **Context Window** | 200K tokens | 32K tokens | May need more summarization |
| **Model Updates** | Automatic | Manual | Run `ollama pull qwen2.5-coder:7b` |
| **Conversation Persistence** | Session-based | File-based | Better persistence across restarts |
| **Agent State** | Memory-based | Database-like | More robust state management |

## 🚨 Common Migration Issues

### Issue 1: Ollama Won't Start
```bash
# Check if port is in use
lsof -i :11434

# Kill existing process if needed
pkill ollama

# Restart Ollama
ollama serve
```

### Issue 2: Model Download Fails
```bash
# Check available space
df -h

# Try different model size
ollama pull qwen2.5-coder:1.5b  # Smaller model
ollama pull qwen2.5-coder:14b   # Larger model

# Update configuration
nano ~/.tmux_orchestrator/config/qwen_config.json
```

### Issue 3: Agent Creation Fails
```bash
# Check system status
python3 qwen_control.py health

# Verify directory permissions
ls -la ~/.tmux_orchestrator/

# Check Python dependencies
python3 -c "import requests, json, threading"
```

### Issue 4: Message Sending Fails
```bash
# Check agent exists
python3 qwen_control.py list

# Check agent status
python3 qwen_control.py info agent_id

# Test direct API
curl -X POST http://localhost:11434/api/chat -d '{"model":"qwen2.5-coder:7b","messages":[{"role":"user","content":"Hello"}]}'
```

## 🧪 Testing Your Migration

### Basic Functionality Test
```bash
# 1. Create test orchestrator session
./quick_start.sh

# 2. Verify agents are running
python3 qwen_control.py status detailed

# 3. Send test message
./send-qwen-message.sh orchestrator "Hello! Please confirm you're working correctly."

# 4. Check response in tmux
tmux attach -t qwen-orchestrator
```

### Advanced Workflow Test
```bash
# 1. Deploy test project
./deploy_example_project.sh

# 2. Assign task via structured communication
python3 -c "
from agent_communication import create_communication_hub
from agent_state import AgentStateManager
from conversation_manager import ConversationManager
from qwen_client import QwenClient

client = QwenClient()
state_mgr = AgentStateManager()
conv_mgr = ConversationManager(state_mgr, client)
hub = create_communication_hub(state_mgr, conv_mgr)

# Assign test task
task = {
    'objective': 'Create a simple Hello World function',
    'success_criteria': 'Function returns Hello World string',
    'priority': 'medium',
    'deadline': '1 hour'
}

hub.assign_task('project_manager_example-webapp', 'developer_example-webapp', task)
"

# 3. Monitor progress
watch -n 10 'python3 qwen_control.py status'
```

## 📈 Performance Optimization

### Hardware Optimization
```bash
# Check system resources
htop

# Monitor GPU usage (if available)
nvidia-smi  # For NVIDIA GPUs

# Optimize model size based on available RAM
# 1.5B model: ~2GB RAM
# 7B model: ~8GB RAM  
# 14B model: ~16GB RAM
```

### Configuration Tuning
```json
// ~/.tmux_orchestrator/config/qwen_config.json
{
  "model": "qwen2.5-coder:7b",
  "temperature": 0.7,        // Lower for more consistent responses
  "max_tokens": 2048,        // Adjust based on needs
  "timeout": 30,             // Increase for slower systems
  "max_retries": 3,          // Increase for unreliable connections
  "retry_delay": 1.0         // Adjust retry timing
}
```

## 🔄 Rollback Plan

If you need to rollback to Claude:

```bash
# 1. Stop Qwen agents
tmux kill-server

# 2. Stop Ollama
pkill ollama

# 3. Restore backup
cp -r ~/claude_orchestrator_backup/* ~/Coding/Tmux\ orchestrator/

# 4. Restart with Claude
# Follow original Claude setup instructions
```

## 🎉 Post-Migration Checklist

- [ ] All agents start successfully
- [ ] Message sending works between agents
- [ ] Scheduling system functions correctly
- [ ] Conversation history persists across restarts
- [ ] System monitoring shows healthy status
- [ ] Performance is acceptable for your use case
- [ ] Backup system is in place
- [ ] Team is trained on new commands

## 📚 Additional Resources

### Documentation
- [Qwen 3 Coder Documentation](https://github.com/QwenLM/Qwen2.5-Coder)
- [Ollama Documentation](https://ollama.ai/docs)
- [System Architecture](README.md#architecture)

### Support Commands
```bash
# Get help with any component
python3 qwen_control.py --help
./send-qwen-message.sh --help
python3 qwen_agent.py --help

# Check system logs
tail -f ~/.tmux_orchestrator/logs/system.log
tail -f ~/.tmux_orchestrator/logs/communication.log
```

### Community
- Report issues in the project repository
- Share optimization tips and configurations
- Contribute improvements to the migration process

---

**Migration Complete!** 🎊

You've successfully migrated from Claude to Qwen 3 Coder. Your orchestrator now runs locally, costs nothing to operate, and provides better conversation persistence. Enjoy your free, private, and powerful AI orchestration system!