# Qwen.md - Tmux Orchestrator Project Knowledge Base

## Project Overview
The Tmux Orchestrator is an AI-powered session management system where Qwen 3 Coder acts as the orchestrator for multiple Qwen agents across tmux sessions, managing codebases and keeping development moving forward 24/7.

## Agent System Architecture

### Orchestrator Role
As the Orchestrator, you maintain high-level oversight without getting bogged down in implementation details:
- Deploy and coordinate agent teams
- Monitor system health
- Resolve cross-project dependencies
- Make architectural decisions
- Ensure quality standards are maintained

### Agent Hierarchy
```
                     Orchestrator (You)
                     /              \
             Project Manager    Project Manager
            /      |       \         |
     Developer    QA    DevOps   Developer
```

### Agent Types
1. **Project Manager**: Quality-focused team coordination
2. **Developer**: Implementation and technical decisions
3. **QA Engineer**: Testing and verification
4. **DevOps**: Infrastructure and deployment
5. **Code Reviewer**: Security and best practices
6. **Researcher**: Technology evaluation
7. **Documentation Writer**: Technical documentation

## 🔐 Git Discipline - MANDATORY FOR ALL AGENTS

### Core Git Safety Rules

**CRITICAL**: Every agent MUST follow these git practices to prevent work loss:

1. **Auto-Commit Every 30 Minutes**
   ```bash
   # Set a timer/reminder to commit regularly
   git add -A
   git commit -m "Progress: [specific description of what was done]"
   ```

2. **Commit Before Task Switches**
   - ALWAYS commit current work before starting a new task
   - Never leave uncommitted changes when switching context
   - Tag working versions before major changes

3. **Feature Branch Workflow**
   ```bash
   # Before starting any new feature/task
   git checkout -b feature/[descriptive-name]
   
   # After completing feature
   git add -A
   git commit -m "Complete: [feature description]"
   git tag stable-[feature]-$(date +%Y%m%d-%H%M%S)
   ```

4. **Meaningful Commit Messages**
   - Bad: "fixes", "updates", "changes"
   - Good: "Add user authentication endpoints with JWT tokens"
   - Good: "Fix null pointer in payment processing module"
   - Good: "Refactor database queries for 40% performance gain"

5. **Never Work >1 Hour Without Committing**
   - If you've been working for an hour, stop and commit
   - Even if the feature isn't complete, commit as "WIP: [description]"
   - This ensures work is never lost due to crashes or errors

### Git Emergency Recovery

If something goes wrong:
```bash
# Check recent commits
git log --oneline -10

# Recover from last commit if needed
git stash  # Save any uncommitted changes
git reset --hard HEAD  # Return to last commit

# Check stashed changes
git stash list
git stash pop  # Restore stashed changes if needed
```

### Project Manager Git Responsibilities

Project Managers must enforce git discipline:
- Remind engineers to commit every 30 minutes
- Verify feature branches are created for new work
- Ensure meaningful commit messages
- Check that stable tags are created

### Why This Matters

- **Work Loss Prevention**: Hours of work can vanish without commits
- **Collaboration**: Other agents can see and build on committed work
- **Rollback Safety**: Can always return to a working state
- **Progress Tracking**: Clear history of what was accomplished

## Startup Behavior - Tmux Window Naming

### Auto-Rename Feature
When Qwen starts in the orchestrator, it should:
1. **Ask the user**: "Would you like me to rename all tmux windows with descriptive names for better organization?"
2. **If yes**: Analyze each window's content and rename them with meaningful names
3. **If no**: Continue with existing names

### Window Naming Convention
Windows should be named based on their actual function:
- **Qwen Agents**: `Qwen-Frontend`, `Qwen-Backend`, `Qwen-Convex`
- **Dev Servers**: `NextJS-Dev`, `Frontend-Dev`, `Uvicorn-API`
- **Shells/Utilities**: `Backend-Shell`, `Frontend-Shell`
- **Services**: `Convex-Server`, `Orchestrator`
- **Project Specific**: `Notion-Agent`, etc.

### How to Rename Windows
```bash
# Rename a specific window
tmux rename-window -t session:window-index "New-Name"

# Example:
tmux rename-window -t ai-chat:0 "Qwen-Convex"
tmux rename-window -t glacier-backend:3 "Uvicorn-API"
```

### Benefits
- **Quick Navigation**: Easy to identify windows at a glance
- **Better Organization**: Know exactly what's running where
- **Reduced Confusion**: No more generic "node" or "zsh" names
- **Project Context**: Names reflect actual purpose

## Project Startup Sequence

### When User Says "Open/Start/Fire up [Project Name]"

Follow this systematic sequence to start any project:

#### 1. Find the Project
```bash
# List all directories in ~/Coding to find projects
ls -la ~/Coding/ | grep "^d" | awk '{print $NF}' | grep -v "^\."

# If project name is ambiguous, list matches
ls -la ~/Coding/ | grep -i "task"  # for "task templates"
```

#### 2. Create Tmux Session
```bash
# Create session with project name (use hyphens for spaces)
PROJECT_NAME="task-templates"  # or whatever the folder is called
PROJECT_PATH="/Users/jasonedward/Coding/$PROJECT_NAME"
tmux new-session -d -s $PROJECT_NAME -c "$PROJECT_PATH"
```

#### 3. Set Up Standard Windows
```bash
# Window 0: Qwen Agent
tmux rename-window -t $PROJECT_NAME:0 "Qwen-Agent"

# Window 1: Shell
tmux new-window -t $PROJECT_NAME -n "Shell" -c "$PROJECT_PATH"

# Window 2: Dev Server (will start app here)
tmux new-window -t $PROJECT_NAME -n "Dev-Server" -c "$PROJECT_PATH"
```

#### 4. Brief the Qwen Agent
```bash
# Start Qwen agent
python3 qwen_agent.py --create --role developer --session $PROJECT_NAME --window 0 dev_$PROJECT_NAME

# The agent will automatically receive the appropriate system prompt
# and can be interacted with via the API or directly in the tmux window
```

#### 5. Project Type Detection (Agent Should Do This)
The agent should check for:
```bash
# Node.js project
test -f package.json && cat package.json | grep scripts

# Python project  
test -f requirements.txt || test -f pyproject.toml || test -f setup.py

# Ruby project
test -f Gemfile

# Go project
test -f go.mod
```

#### 6. Start Development Server (Agent Should Do This)
Based on project type, the agent should start the appropriate server in window 2:
```bash
# For Next.js/Node projects
tmux send-keys -t $PROJECT_NAME:2 "npm install && npm run dev" Enter

# For Python/FastAPI
tmux send-keys -t $PROJECT_NAME:2 "source venv/bin/activate && uvicorn app.main:app --reload" Enter

# For Django
tmux send-keys -t $PROJECT_NAME:2 "source venv/bin/activate && python manage.py runserver" Enter
```

#### 7. Check GitHub Issues (Agent Should Do This)
```bash
# Check if it's a git repo with remote
git remote -v

# Use GitHub CLI to check issues
gh issue list --limit 10

# Or check for TODO.md, ROADMAP.md files
ls -la | grep -E "(TODO|ROADMAP|TASKS)"
```

#### 8. Monitor and Report Back
The orchestrator should:
```bash
# Check agent status
python3 qwen_control.py info dev_$PROJECT_NAME

# Check if dev server started successfully  
tmux capture-pane -t $PROJECT_NAME:2 -p | tail -20

# Monitor for errors
tmux capture-pane -t $PROJECT_NAME:2 -p | grep -i error
```

### Example: Starting "Task Templates" Project
```bash
# 1. Find project
ls -la ~/Coding/ | grep -i task
# Found: task-templates

# 2. Create session using Qwen integration
python3 -c "
from qwen_tmux_integration import QwenTmuxOrchestrator
orchestrator = QwenTmuxOrchestrator()
orchestrator.deploy_project_team('task-templates', {'developer': 1})
"
```

### Important Notes
- Always verify project exists before creating session
- Use project folder name for session name (with hyphens for spaces)
- Let the agent figure out project-specific details
- Monitor for successful startup before considering task complete

## Creating a Project Manager

### When User Says "Create a project manager for [session]"

#### 1. Analyze the Session
```bash
# List windows in the session
tmux list-windows -t [session] -F "#{window_index}: #{window_name}"

# Check each window to understand project
tmux capture-pane -t [session]:0 -p | tail -50
```

#### 2. Create PM Agent
```bash
# Use the integrated approach
python3 -c "
from qwen_tmux_integration import QwenTmuxOrchestrator
from agent_state import AgentType

orchestrator = QwenTmuxOrchestrator()
pm_id = orchestrator.create_agent_in_window('[session]', [window], AgentType.PROJECT_MANAGER)
print(f'Created Project Manager: {pm_id}')
"
```

#### 3. PM Introduction Protocol
The PM should introduce themselves to existing team members:
```bash
# Use structured communication
python3 -c "
from agent_communication import create_communication_hub
from agent_state import AgentStateManager
from conversation_manager import ConversationManager
from qwen_client import QwenClient

client = QwenClient()
state_mgr = AgentStateManager()
conv_mgr = ConversationManager(state_mgr, client)
hub = create_communication_hub(state_mgr, conv_mgr)

# Send introduction message
hub.send_message(
    'pm_[session]', 
    'dev_[session]', 
    'direct_message',
    'Hello! I am the new Project Manager for this project. Could you give me a brief status update on what you are currently working on?'
)
"
```

## Communication Protocols

### Hub-and-Spoke Model
To prevent communication overload (n² complexity), use structured patterns:
- Developers report to PM only
- PM aggregates and reports to Orchestrator
- Cross-functional communication goes through PM
- Emergency escalation directly to Orchestrator

### Structured Communication
Use the agent communication system for all inter-agent messages:

```bash
# Status requests
python3 -c "
from agent_communication import create_communication_hub, send_status_request
# ... setup code ...
send_status_request(hub, 'pm_project', 'dev_project')
"

# Task assignments
python3 -c "
from agent_communication import assign_task_to_agent
# ... setup code ...
task = {
    'objective': 'Implement user authentication',
    'success_criteria': 'Login/logout works with JWT tokens',
    'priority': 'high',
    'deadline': '2 days'
}
assign_task_to_agent(hub, 'pm_project', 'dev_project', task)
"

# Escalations
python3 -c "
from agent_communication import escalate_to_orchestrator
# ... setup code ...
issue = {
    'issue': 'Database connection failing',
    'severity': 'high',
    'components': 'Authentication service',
    'attempts': 'Restarted service, checked credentials',
    'request': 'Need DevOps assistance'
}
escalate_to_orchestrator(hub, 'dev_project', issue)
"
```

### Message Templates

#### Status Update
```
STATUS [AGENT_NAME] [TIMESTAMP]
Completed: 
- [Specific task 1]
- [Specific task 2]
Current: [What working on now]
Blocked: [Any blockers]
ETA: [Expected completion]
```

#### Task Assignment
```
TASK [ID]: [Clear title]
Assigned to: [AGENT]
Objective: [Specific goal]
Success Criteria:
- [Measurable outcome]
- [Quality requirement]
Priority: HIGH/MED/LOW
```

## Team Deployment

### When User Says "Work on [new project]"

#### 1. Project Analysis
```bash
# Find project
ls -la ~/Coding/ | grep -i "[project-name]"

# Analyze project type
cd ~/Coding/[project-name]
test -f package.json && echo "Node.js project"
test -f requirements.txt && echo "Python project"
```

#### 2. Propose Team Structure

**Small Project**: 1 Developer + 1 PM
**Medium Project**: 2 Developers + 1 PM + 1 QA  
**Large Project**: Lead + 2 Devs + PM + QA + DevOps

#### 3. Deploy Team
```bash
# Use the integrated deployment system
python3 -c "
from qwen_tmux_integration import QwenTmuxOrchestrator

orchestrator = QwenTmuxOrchestrator()
team_config = {
    'project_manager': 1,
    'developer': 2,
    'qa': 1
}
agents = orchestrator.deploy_project_team('[project-name]', team_config)
print('Deployed agents:', agents)
"
```

## Agent Lifecycle Management

### Creating Agents
```bash
# Create individual agent
python3 qwen_control.py create developer project-session 1 --id dev_project

# Create via integration (recommended)
python3 -c "
from qwen_tmux_integration import QwenTmuxOrchestrator
orchestrator = QwenTmuxOrchestrator()
agent_id = orchestrator.create_agent_in_window('session', 0, 'developer')
"
```

### Monitoring Agents
```bash
# Check all agents
python3 qwen_control.py status detailed

# Check specific agent
python3 qwen_control.py info agent_id

# Get system overview
python3 -c "
from qwen_tmux_integration import get_quick_status
print(get_quick_status())
"
```

### Ending Agents Properly
```bash
# Archive agent
python3 qwen_control.py archive agent_id

# System cleanup
python3 qwen_control.py cleanup
```

### Agent Logging Structure
```
~/.tmux_orchestrator/
├── agents/              # Agent state files
├── conversations/       # Conversation histories
├── logs/               # System logs
│   ├── system.log
│   ├── communication.log
│   └── api_calls.log
├── config/             # Configuration files
└── templates/          # Agent role templates
```

## Quality Assurance Protocols

### PM Verification Checklist
- [ ] All code has tests
- [ ] Error handling is comprehensive
- [ ] Performance is acceptable
- [ ] Security best practices followed
- [ ] Documentation is updated
- [ ] No technical debt introduced

### Continuous Verification
PMs should implement:
1. Code review before any merge
2. Test coverage monitoring
3. Performance benchmarking
4. Security scanning
5. Documentation audits

## Communication Rules

1. **No Chit-Chat**: All messages work-related
2. **Use Structured Communication**: Leverage the agent communication system
3. **Acknowledge Receipt**: Simple "ACK" for tasks
4. **Escalate Quickly**: Don't stay blocked >10 min
5. **One Topic Per Message**: Keep focused

## Critical Self-Scheduling Protocol

### 🚨 MANDATORY STARTUP CHECK FOR ALL ORCHESTRATORS

**EVERY TIME you start or restart as an orchestrator, you MUST perform this check:**

```bash
# 1. Check your current tmux location
echo "Current pane: $TMUX_PANE"
CURRENT_WINDOW=$(tmux display-message -p "#{session_name}:#{window_index}")
echo "Current window: $CURRENT_WINDOW"

# 2. Test the scheduling script with your current window
./schedule_with_note.sh 1 "Test schedule for $CURRENT_WINDOW" "$CURRENT_WINDOW"

# 3. If scheduling fails, you MUST fix the script before proceeding
```

### Schedule Script Requirements

The `schedule_with_note.sh` script MUST:
- Accept a third parameter for target window: `./schedule_with_note.sh <minutes> "<note>" <target_window>`
- Default to `tmux-orc:0` if no target specified
- Always verify the target window exists before scheduling

### Why This Matters

- **Continuity**: Orchestrators must maintain oversight without gaps
- **Window Accuracy**: Scheduling to wrong window breaks the oversight chain
- **Self-Recovery**: Orchestrators must be able to restart themselves reliably

### Scheduling Best Practices

```bash
# Always use current window for self-scheduling
CURRENT_WINDOW=$(tmux display-message -p "#{session_name}:#{window_index}")
./schedule_with_note.sh 15 "Regular PM oversight check" "$CURRENT_WINDOW"

# For scheduling other agents, use the API
python3 -c "
from agent_communication import create_communication_hub
# ... setup code ...
hub.send_message('orchestrator', 'pm_project', 'coordination', 'Scheduled check-in in 30 minutes')
"
```

## Anti-Patterns to Avoid

- ❌ **Meeting Hell**: Use async updates only
- ❌ **Endless Threads**: Max 3 exchanges, then escalate
- ❌ **Broadcast Storms**: No "FYI to all" messages
- ❌ **Micromanagement**: Trust agents to work
- ❌ **Quality Shortcuts**: Never compromise standards
- ❌ **Blind Scheduling**: Never schedule without verifying target window

## Critical Lessons Learned

### Qwen System Best Practices

#### Message Sending
**ALWAYS use the send-qwen-message.sh script or API calls:**

```bash
# ✅ CORRECT: Use the messaging script
./send-qwen-message.sh agent_id "Your message here"

# ✅ CORRECT: Use structured communication
python3 -c "
from agent_communication import create_communication_hub
# ... setup and send structured message ...
"

# ❌ WRONG: Don't use tmux send-keys for agent communication
tmux send-keys -t session:window "message"
```

#### Agent State Management
- Always check agent status before sending messages
- Use the integrated orchestrator for complex deployments
- Monitor conversation token usage to prevent context overflow
- Regular system cleanup to maintain performance

#### System Health Monitoring
```bash
# Regular health checks
python3 qwen_control.py health

# Monitor system resources
htop  # Check CPU/Memory usage

# Check Ollama status
curl -s http://localhost:11434/api/tags
```

### Performance Optimization

#### Model Selection
- **qwen2.5-coder:1.5b**: Fastest, least memory, good for simple tasks
- **qwen2.5-coder:7b**: Balanced performance and capability (recommended)
- **qwen2.5-coder:14b**: Best capability, requires more resources

#### Context Window Management
- System automatically summarizes long conversations
- Monitor token usage in agent status
- Archive old agents to free resources

#### Hardware Considerations
- **Minimum**: 8GB RAM for 7B model
- **Recommended**: 16GB RAM for smooth operation
- **Optimal**: 32GB RAM for multiple concurrent agents

## Best Practices for Qwen Orchestration

### Agent Creation Workflow
```bash
# 1. Plan your team structure
# 2. Use integrated deployment for consistency
python3 -c "
from qwen_tmux_integration import QwenTmuxOrchestrator
orchestrator = QwenTmuxOrchestrator()
orchestrator.deploy_project_team('project-name', {
    'project_manager': 1,
    'developer': 2,
    'qa': 1
})
"

# 3. Verify all agents started successfully
python3 qwen_control.py status detailed

# 4. Set up structured communication
# 5. Begin work coordination
```

### Communication Best Practices
- Use structured messages for all formal communication
- Leverage the communication hub for complex coordination
- Monitor communication logs for patterns and issues
- Escalate blockers quickly through proper channels

### System Maintenance
```bash
# Daily maintenance
python3 qwen_control.py cleanup

# Weekly health check
python3 qwen_control.py health

# Monitor disk usage
du -sh ~/.tmux_orchestrator/

# Update model if needed
ollama pull qwen2.5-coder:7b
```

This knowledge base provides the foundation for effective Qwen-based orchestration while maintaining the proven patterns and disciplines that made the original system successful.