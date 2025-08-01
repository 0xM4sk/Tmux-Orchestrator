![Orchestrator Hero](/Orchestrator.png)

**Run AI agents 24/7 while you sleep** - The Tmux Orchestrator enables Qwen 3 Coder agents to work autonomously, schedule their own check-ins, and coordinate across multiple projects without human intervention. Now completely free and running locally with Ollama!

## 🤖 Key Capabilities & Autonomous Features

- **Self-trigger** - Agents schedule their own check-ins and continue work autonomously
- **Coordinate** - Project managers assign tasks to engineers across multiple codebases
- **Persist** - Work continues even when you close your laptop with persistent conversation history
- **Scale** - Run multiple teams working on different projects simultaneously
- **Cost-Free** - No API costs! Runs completely locally with Ollama
- **Private** - All conversations and data stay on your machine
- **Offline** - Works without internet connection after initial setup

## 🆓 Why Qwen 3 Coder + Ollama?

### Cost Benefits
- **$0/month** vs Claude's $20/month subscription
- **No token limits** - unlimited conversations and code generation
- **No usage tracking** - work as much as you want

### Privacy & Control
- **Local processing** - your code never leaves your machine
- **No data collection** - complete privacy for sensitive projects
- **Custom models** - fine-tune for your specific needs
- **Offline capable** - work anywhere, anytime

### Performance
- **2-5 second responses** - competitive with cloud services
- **32K context window** - handles large codebases effectively
- **Specialized for coding** - optimized for development tasks
- **Multiple concurrent agents** - true parallel processing

## 🏗️ Architecture

The Tmux Orchestrator uses a three-tier hierarchy with persistent API-based agents:

```
┌─────────────┐
│ Orchestrator│ ← You interact here
└──────┬──────┘
       │ Monitors & coordinates
       ▼
┌─────────────┐     ┌─────────────┐
│  Project    │     │  Project    │
│  Manager 1  │     │  Manager 2  │ ← Assign tasks, enforce specs
└──────┬──────┘     └──────┬──────┘
       │                   │
       ▼                   ▼
┌─────────────┐     ┌─────────────┐
│ Engineer 1  │     │ Engineer 2  │ ← Write code, fix bugs
└─────────────┘     └─────────────┘
```

### Why Separate Agents?
- **Limited context windows** - Each agent stays focused on its role
- **Specialized expertise** - PMs manage, engineers code
- **Parallel work** - Multiple engineers can work simultaneously
- **Better memory** - Smaller contexts mean better recall

## 📸 Examples in Action

### Project Manager Coordination
![Initiate Project Manager](Examples/Initiate%20Project%20Manager.png)
*The orchestrator creating and briefing a new project manager agent*

### Status Reports & Monitoring
![Status Reports](Examples/Status%20reports.png)
*Real-time status updates from multiple agents working in parallel*

### Tmux Communication
![Reading TMUX Windows and Sending Messages](Examples/Reading%20TMUX%20Windows%20and%20Sending%20Messages.png)
*How agents communicate across tmux windows and sessions*

### Project Completion
![Project Completed](Examples/Project%20Completed.png)
*Successful project completion with all tasks verified and committed*

## 🎯 Quick Start

### Option 1: Basic Setup (Single Project)

```bash
# 1. Create a project spec
cat > project_spec.md << 'EOF'
PROJECT: My Web App
GOAL: Add user authentication system
CONSTRAINTS:
- Use existing database schema
- Follow current code patterns  
- Commit every 30 minutes
- Write tests for new features

DELIVERABLES:
1. Login/logout endpoints
2. User session management
3. Protected route middleware
EOF

# 2. Start tmux session
tmux new-session -s my-project

# 3. Start project manager in window 0
python3 qwen_agent.py --create --role project_manager --session my-project --window 0 pm_my-project

# 4. The PM will automatically receive the spec and can coordinate with engineers
./send-qwen-message.sh pm_my-project "Read project_spec.md and coordinate implementation. Create developer agent if needed."

# 5. Schedule orchestrator check-in
./schedule_with_note.sh 30 "Check PM progress on auth system"
```

### Option 2: Full Orchestrator Setup

```bash
# Start the orchestrator using the quick start script
./quick_start.sh

# Or manually create orchestrator session
python3 -c "
from qwen_tmux_integration import create_orchestrator_session
create_orchestrator_session('orchestrator')
"

# Deploy projects using the integrated system
python3 -c "
from qwen_tmux_integration import deploy_simple_project
deploy_simple_project('frontend-dashboard', include_qa=True)
deploy_simple_project('backend-optimization', include_qa=True)
"
```

## ✨ Key Features

### 🔄 Self-Scheduling Agents
Agents can schedule their own check-ins using:
```bash
./schedule_with_note.sh 30 "Continue dashboard implementation"
```

### 👥 Multi-Agent Coordination
- Project managers communicate with engineers
- Orchestrator monitors all project managers
- Cross-project knowledge sharing

### 💾 Automatic Git Backups
- Commits every 30 minutes of work
- Tags stable versions
- Creates feature branches for experiments

### 📊 Real-Time Monitoring
- See what every agent is doing
- Intervene when needed
- Review progress across all projects

## 📋 Best Practices

### Writing Effective Specifications

```markdown
PROJECT: E-commerce Checkout
GOAL: Implement multi-step checkout process

CONSTRAINTS:
- Use existing cart state management
- Follow current design system
- Maximum 3 API endpoints
- Commit after each step completion

DELIVERABLES:
1. Shipping address form with validation
2. Payment method selection (Stripe integration)
3. Order review and confirmation page
4. Success/failure handling

SUCCESS CRITERIA:
- All forms validate properly
- Payment processes without errors  
- Order data persists to database
- Emails send on completion
```

### Git Safety Rules

1. **Before Starting Any Task**
   ```bash
   git checkout -b feature/[task-name]
   git status  # Ensure clean state
   ```

2. **Every 30 Minutes**
   ```bash
   git add -A
   git commit -m "Progress: [what was accomplished]"
   ```

3. **When Task Completes**
   ```bash
   git tag stable-[feature]-[date]
   git checkout main
   git merge feature/[task-name]
   ```

## 🚨 Common Pitfalls & Solutions

| Pitfall | Consequence | Solution |
|---------|-------------|----------|
| Vague instructions | Agent drift, wasted compute | Write clear, specific specs |
| No git commits | Lost work, frustrated devs | Enforce 30-minute commit rule |
| Too many tasks | Context overload, confusion | One task per agent at a time |
| No specifications | Unpredictable results | Always start with written spec |
| Missing checkpoints | Agents stop working | Schedule regular check-ins |

## 🛠️ How It Works

### The Magic of Tmux
Tmux (terminal multiplexer) is the key enabler because:
- It persists terminal sessions even when disconnected
- Allows multiple windows/panes in one session
- Claude runs in the terminal, so it can control other Claude instances
- Commands can be sent programmatically to any window

### 💬 Simplified Agent Communication

We now use the `send-qwen-message.sh` script for all agent communication:

```bash
# Send message to any Qwen agent
./send-qwen-message.sh agent_id "Your message here"

# Examples:
./send-qwen-message.sh dev_frontend "What's your progress on the login form?"
./send-qwen-message.sh dev_backend "The API endpoint /api/users is returning 404"
./send-qwen-message.sh pm_project "Please coordinate with the QA team"
```

The script handles API communication automatically, making agent interaction reliable and efficient.

### Scheduling Check-ins
```bash
# Schedule with specific, actionable notes
./schedule_with_note.sh 30 "Review auth implementation, assign next task"
./schedule_with_note.sh 60 "Check test coverage, merge if passing"
./schedule_with_note.sh 120 "Full system check, rotate tasks if needed"
```

**Important**: The orchestrator needs to know which tmux window it's running in to schedule its own check-ins correctly. If scheduling isn't working, verify the orchestrator knows its current window with:
```bash
echo "Current window: $(tmux display-message -p "#{session_name}:#{window_index}")"
```

## 🎓 Advanced Usage

### Multi-Project Orchestration
```bash
# Start orchestrator
tmux new-session -s orchestrator

# Create project managers for each project
tmux new-window -n frontend-pm
tmux new-window -n backend-pm  
tmux new-window -n mobile-pm

# Each PM manages their own engineers
# Orchestrator coordinates between PMs
```

### Cross-Project Intelligence
The orchestrator can share insights between projects:
- "Frontend is using /api/v2/users, update backend accordingly"
- "Authentication is working in Project A, use same pattern in Project B"
- "Performance issue found in shared library, fix across all projects"

## 📚 Core Files

- `send-qwen-message.sh` - Agent communication via API
- `qwen_control.py` - System management and monitoring
- `qwen_agent.py` - Agent runtime for tmux windows
- `setup_qwen_orchestrator.sh` - Complete system setup
- `qwen_tmux_integration.py` - Advanced orchestration features
- `QWEN.md` - Agent behavior instructions and best practices
- `MIGRATION_GUIDE.md` - Guide for migrating from Claude
- `LEARNINGS.md` - Accumulated knowledge base

## 🤝 Contributing & Optimization

The orchestrator evolves through community discoveries and optimizations. When contributing:

1. Document new tmux commands and patterns in CLAUDE.md
2. Share novel use cases and agent coordination strategies
3. Submit optimizations for claudes synchronization
4. Keep command reference up-to-date with latest findings
5. Test improvements across multiple sessions and scenarios

Key areas for enhancement:
- Agent communication patterns
- Cross-project coordination
- Novel automation workflows

## 📄 License

MIT License - Use freely but wisely. Remember: with great automation comes great responsibility.

---

*"The tools we build today will program themselves tomorrow"* - Alan Kay, 1971