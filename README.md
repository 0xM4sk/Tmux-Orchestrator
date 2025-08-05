# Qwen Orchestrator Framework

A modular, extensible framework for orchestrating AI agents with tmux integration and intelligent autoscaling capabilities.

## Overview

The Qwen Orchestrator Framework is a comprehensive system for managing and coordinating multiple AI agents in a tmux-based environment. It provides a robust architecture for agent lifecycle management, communication, execution tracking, and monitoring with intelligent autoscaling based on resource detection capabilities.

## Architecture

The framework is organized into several distinct components with clear separation of concerns:

### Core Modules

1. **Agent Management**
   - `agent_state_manager.py`: Manages agent states and lifecycle
   - `agent_factory.py`: Factory pattern implementation for creating agents
   - `agent_registry.py`: Central registry for all active agents

2. **Communication System**
   - `message_router.py`: Routes messages between agents and services
   - `protocol_enforcer.py`: Ensures message format and protocol compliance
   - `conversation_manager.py`: Manages multi-agent conversations

3. **Execution Tracking**
   - `execution_monitor.py`: Monitors agent task execution
   - `gap_detector.py`: Detects execution gaps and inconsistencies
   - `recovery_manager.py`: Manages recovery from execution failures

4. **Dashboard Monitoring**
   - `dashboard_manager.py`: Manages system dashboards and layouts
   - `metrics_collector.py`: Collects system metrics for visualization
   - `alert_system.py`: Handles system alerts and notifications

5. **Data Management**
   - `data_store.py`: Persistent storage for system data
   - `data_processor.py`: Processes and transforms data
   - `data_validator.py`: Validates data integrity and format

### Template Modules

Reusable boilerplate code templates for common functionality:

1. **Authentication**: Auth templates and boilerplate
2. **Notification**: Notification templates and boilerplate
3. **Testing**: Testing templates and boilerplate
4. **API**: API templates and boilerplate
5. **AWS**: AWS integration templates and boilerplate

### Demo Applications

Separate demo applications demonstrating framework capabilities:

1. **Strangers Calendar App**: Complete calendar application demo

### Knowledge Management

1. **Cache**: Consolidated knowledge and lessons learned
2. **Users**: User content including diagrams, examples, and rulesets

## Key Features

- **Modular Design**: Clean separation of concerns with well-defined interfaces
- **Agent Orchestration**: Comprehensive agent lifecycle management
- **Communication Framework**: Structured messaging with protocol enforcement
- **Execution Monitoring**: Real-time tracking of agent tasks and performance
- **Dashboard System**: Customizable dashboards for system monitoring
- **Data Management**: Robust data storage, processing, and validation
- **Recovery Mechanisms**: Automated recovery from failures and gaps
- **Extensible Architecture**: Easy to extend with new modules and services
- **Intelligent Autoscaling**: Dynamic agent parallelism based on resource detection
- **Knowledge Management**: Systematic learning from failures and successes

## Intelligent Autoscaling

The framework implements intelligent autoscaling capabilities that dynamically adjust agent parallelism and context windows based on real-time resource detection:

### Resource Detection
- Continuous monitoring of CPU, memory, and I/O utilization
- Detection of system bottlenecks and performance constraints
- Analysis of task queue depths and execution patterns

### Dynamic Scaling
- **Horizontal Scaling**: Automatic creation of additional agent instances during high-demand periods
- **Vertical Scaling**: Dynamic adjustment of context windows and resource allocation per agent
- **Load Balancing**: Intelligent distribution of tasks across available agents
- **Graceful Degradation**: Reduction of parallelism during resource constraints

### Scaling Policies
- **Performance-Based**: Scaling decisions based on execution metrics and response times
- **Predictive**: Anticipatory scaling based on historical usage patterns
- **Conservative**: Resource-conscious scaling to prevent over-allocation
- **Adaptive**: Continuous optimization of scaling parameters based on outcomes

## Repository Structure

```
/home/baseline/Tmux-Orchestrator/
├── core/                          # Core orchestrator system
├── modules/                       # Template boilerplate code modules
├── demos/                         # Demo applications
├── users/                         # User content and documentation
├── cache/                         # Consolidated knowledge and lessons
├── docs/                          # Core documentation
├── tests/                         # Core system tests
└── requirements.txt               # Python dependencies
```

## Hardware Requirements

### Minimum Requirements
- **CPU**: 2 cores (x86_64 architecture)
- **Memory**: 4 GB RAM
- **Storage**: 10 GB available disk space
- **Operating System**: Linux (Ubuntu 20.04+, CentOS 8+, or equivalent)
- **Additional**: tmux 3.0+

### Recommended Requirements
- **CPU**: 4+ cores
- **Memory**: 8+ GB RAM
- **Storage**: 50+ GB available disk space (SSD recommended)
- **Operating System**: Linux with kernel 5.4+
- **Additional**: tmux 3.2+, Python 3.9+

### For Production Deployments
- **CPU**: 8+ cores (16+ recommended)
- **Memory**: 16+ GB RAM
- **Storage**: 100+ GB available disk space (NVMe SSD recommended)
- **Network**: Gigabit Ethernet
- **Additional**: tmux 3.3+, Python 3.10+

## Software Requirements

- Python 3.8+
- tmux 3.0+
- Required Python packages (see `requirements.txt`)
- Systemd (for service management, optional)

## Deployment

The framework includes a blue/green deployment script (`blue_green_deploy.sh`) for seamless updates without disrupting running agents.

### Quick Start

1. Ensure all hardware and software requirements are met
2. Clone the repository
3. Install dependencies: `pip install -r requirements.txt`
4. Run the integration tests to verify the framework is working correctly
5. Start the orchestrator: `python app.py`

### Production Deployment

1. Set up the environment according to hardware requirements
2. Configure system services for automatic startup
3. Implement monitoring and alerting
4. Set up log rotation and backup procedures
5. Use the blue/green deployment script for updates

## Testing

Integration tests are provided in `test_framework_integration.py` to verify that all modules work together properly. Additional tests can be found in the `tests/` directory.

## Usage

### System Management

The orchestrator can be managed using the `qwen_control.py` script:

```bash
# Check system status
python3 qwen_control.py status

# List all active agents
python3 qwen_control.py list

# Get detailed information about a specific agent
python3 qwen_control.py info agent_id

# Send a message to an agent
python3 qwen_control.py message agent_id "Your message here"

# Create a new agent
python3 qwen_control.py create agent_type session_name window_index

# Archive an agent
python3 qwen_control.py archive agent_id
```

### Unified Dashboard

The orchestrator includes a unified dashboard that provides real-time monitoring and control through a tmux interface. The dashboard has been streamlined to focus on the most essential windows:

#### Dashboard Windows

1. **Control** - Interactive command interface for orchestrator management
2. **Chat** - Real-time chat history between agents displayed in a chat room format
3. **Tasks** - Task tracking with git commit metadata and project progress

#### Starting the Dashboard

```bash
# Start the unified dashboard
./unified_dashboard.sh start

# Start the dashboard for a specific project
./unified_dashboard.sh start project-strangers-calendar-app

# Attach to an existing dashboard session
./unified_dashboard.sh attach

# Show dashboard status
./unified_dashboard.sh status

# Kill the dashboard session
./unified_dashboard.sh kill
```

#### Using the Control Window

The Control window provides an interactive command-line interface for managing the orchestrator:

```bash
# Show system status
dashboard> status

# List all agents
dashboard> list

# Show tmux sessions
dashboard> sessions

# Create a new agent
dashboard> create <type> <session> <window>

# Send message to agent
dashboard> message <agent_id> <message>

# Archive/Delete agent
dashboard> archive <agent_id>

# List project sessions
dashboard> projects

# Kill project session
dashboard> killproj <session_name>

# Show system resource usage
dashboard> resources

# Show available commands
dashboard> help
```

#### Using the Chat Window

The Chat window displays real-time conversations between agents in an easy-to-read chat room format:

- Shows messages from all active agents
- Color-coded agent types (👑 PM, 👨‍💻 Dev, 🕵️ QA, 🤖 Agent)
- Timestamped messages for tracking conversation flow
- Automatic updates every 10 seconds

#### Using the Tasks Window

The Tasks window provides real-time task tracking with git commit metadata:

- Displays project tasks with status indicators (⏳ pending, ✅ completed, 🔄 in progress)
- Shows recent git commits with author and timestamp information
- Tracks agent activities and progress
- Automatic updates every 30 seconds

#### Dashboard Navigation

Once attached to the dashboard session, you can navigate between windows using tmux shortcuts:

- `Ctrl+B, N` - Next window
- `Ctrl+B, P` - Previous window
- `Ctrl+B, [number]` - Switch to specific window
- `Ctrl+B, D` - Detach from dashboard

### Interaction Examples

Here are examples of how to interact with the orchestrator using natural language commands:

#### Project Management Commands

```bash
# Get a status update from a project's PM and assign a new task
python3 qwen_control.py message project_manager_strangers-calendar "Get a status update from the Strangers Calendar App project about OAuth implementation and tell the development team to implement Google and Apple authentication endpoints"

# Request progress report and next steps
python3 qwen_control.py message project_manager_strangers-calendar "What's the current status of the Strangers Calendar App project? Please provide a progress report and outline the next steps for the development team."

# Coordinate between team members
python3 qwen_control.py message project_manager_strangers-calendar "Coordinate with the QA team to test the calendar creation functionality and have the developers implement the sharing feature next."
```

#### Agent Management Commands

```bash
# Create a new project team
python3 qwen_control.py message orchestrator "Create a project team for the Strangers Calendar App with 1 project manager, 2 developers, and 1 QA engineer"

# Assign specific tasks to team members
python3 qwen_control.py message dev_strangers-calendar_1 "Implement the backend API for calendar creation and sharing functionality"

# Request status updates
python3 qwen_control.py message qa_strangers-calendar "Test the OAuth authentication flow and report any issues to the development team"
```

#### System Administration Commands

```bash
# Check system health and resource usage
python3 qwen_control.py message orchestrator "Perform a health check and report on system resource usage and agent performance"

# Clean up inactive agents
python3 qwen_control.py message orchestrator "Clean up any inactive agents and archive completed project sessions"

# Scale system resources
python3 qwen_control.py message orchestrator "Analyze current workload and scale agent parallelism based on resource availability"
```

### Message Sending Script

You can also use the `send-qwen-message.sh` script for sending messages:

```bash
# Send a message to a specific agent
./send-qwen-message.sh agent_id "Your message here"

# Send a message to the orchestrator
./send-qwen-message.sh orchestrator "Get a status update from the Strangers Calendar App project's PM about OAuth implementation and tell the PM to assign the Google and Apple authentication tasks to the development team"
```

## Contributing

This framework is designed to be extended and customized. New modules can be added following the existing patterns and interfaces. Please follow these guidelines:

1. Maintain the modular architecture
2. Follow existing code patterns and documentation standards
3. Add appropriate tests for new functionality
4. Update documentation when making changes
5. Contribute improvements back to the template modules for reuse

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on the GitHub repository or contact the maintainers.
