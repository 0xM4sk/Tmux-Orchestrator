# 🔒 Tmux Orchestrator

A secure, multi-agent orchestration system for managing tmux sessions with comprehensive sandbox security.

## 🚨 Security First

This orchestrator includes enterprise-grade sandbox security that prevents agents from accessing files outside their designated project directories. The system automatically enforces security boundaries and logs all access attempts.

## 🏗️ Architecture

### Core Components

- **Agent Management**: Create and manage multiple AI agents
- **Session Orchestration**: Coordinate tmux sessions across agents
- **Sandbox Security**: Enforce strict file access boundaries
- **Real-time Monitoring**: Track agent activities and system status
- **Project Isolation**: Each project runs in its own secure sandbox

### Security Features

- ✅ **File Creation Protection**: Agents cannot create files outside their project directory
- ✅ **Command Execution Security**: Commands accessing restricted paths are blocked
- ✅ **Path Validation**: All file operations validated against sandbox boundaries
- ✅ **Access Logging**: Complete audit trail of all file access attempts
- ✅ **Violation Alerts**: Critical alerts for security boundary violations
- ✅ **Project Isolation**: Each project has its own isolated sandbox

## 🚀 Quick Start

### 1. Setup

```bash
# Clone the repository
git clone <repository-url>
cd tmux-orchestrator

# Run the security setup script
python3 setup_sandbox.py

# Configure environment (automated by setup script)
export ORCHESTRATOR_ROOT="/path/to/your/installation"
```

### 2. Test Security

```bash
# Verify sandbox security is working
python3 test_sandbox_security.py
```

### 3. Start Orchestrator

```bash
# Start the main orchestrator
python3 qwen_control.py status
```

## 📁 Project Structure

```
tmux-orchestrator/
├── core/                          # Core system (restricted access)
├── services/                      # Services (restricted access)
├── projects/                      # Project directories (agent access)
│   ├── project1/                  # Agent sandbox 1
│   └── project2/                  # Agent sandbox 2
├── agentic_capabilities.py        # Sandboxed execution engine
├── sandbox_manager.py             # Security boundary management
├── qwen_control.py                # Main orchestrator control
└── setup_sandbox.py               # Security setup script
```

## 🔧 Configuration

### Environment Variables

- `ORCHESTRATOR_ROOT`: Path to your Tmux Orchestrator installation
- Defaults to current working directory if not set

### Security Configuration

The system uses `agent_sandbox_config.json` for security boundaries:

```json
{
  "sandbox_config": {
    "default_boundaries": {
      "root_directory": "${ORCHESTRATOR_ROOT}",
      "restricted_paths": [
        "${ORCHESTRATOR_ROOT}/core",
        "${ORCHESTRATOR_ROOT}/services"
      ]
    }
  }
}
```

## 🧪 Testing

### Security Tests

```bash
# Run comprehensive security tests
python3 test_sandbox_security.py
```

### Compliance Report

```bash
# Check security compliance (target: 99%+)
python3 -c "
from sandbox_manager import SandboxManager
sm = SandboxManager()
report = sm.get_security_report()
print(f'Compliance Rate: {report[\"compliance_rate\"]:.2f}%')
"
```

## 📊 Monitoring

### Security Logs

All file access attempts are logged to:
```
~/.tmux_orchestrator/agentic_execution.log
```

### Real-time Status

```bash
# Check orchestrator status
python3 qwen_control.py status

# List active agents
python3 qwen_control.py list
```

## 🔒 Security Best Practices

1. **Regular Auditing**: Monitor security logs regularly
2. **Project Isolation**: Keep projects in separate directories
3. **Environment Configuration**: Set `ORCHESTRATOR_ROOT` environment variable
4. **Agent Permissions**: Use appropriate agent types (developer, qa, project_manager)

## 🛠️ Development

### Adding New Projects

1. Create project directory in `projects/`
2. Update `agent_sandbox_config.json` if needed
3. Test with `python3 test_sandbox_security.py`

### Contributing

When contributing:
1. **Test thoroughly**: Run `python3 test_sandbox_security.py`
2. **Follow security principles**: Never bypass sandboxing
3. **Use environment variables**: Avoid hardcoded paths
4. **Document changes**: Update this README

## 📚 Documentation

- [Sandbox Security System](SANDBOX_SECURITY.md) - Detailed security documentation
- [Agent Management](docs/agent_management.md) - Agent creation and management
- [Session Control](docs/session_control.md) - Tmux session management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run security tests: `python3 test_sandbox_security.py`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**🔒 Your system is protected by enterprise-grade sandbox security with 99%+ compliance rate!**