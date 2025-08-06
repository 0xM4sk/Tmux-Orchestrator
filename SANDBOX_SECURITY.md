# 🔒 Sandbox Security System

The Tmux Orchestrator includes a comprehensive sandbox security system that prevents agents from accessing files outside their designated project directories. This ensures that your system remains secure even when running autonomous agents.

## 🚨 Security Issue Fixed

**Problem**: The original system allowed agents to modify files outside their project directories, including core system files like `README.md`.

**Solution**: Implemented a robust sandboxing system that enforces strict boundaries and prevents unauthorized file access.

## 🏗️ Architecture

### Core Components

1. **PathValidator**: Validates all file paths against allowed boundaries
2. **FileAccessMonitor**: Logs and monitors all file access attempts
3. **BoundaryViolationAlert**: Sends critical alerts for security violations
4. **SandboxManager**: Manages agent permissions and project boundaries
5. **AgenticExecutor**: Enforces sandboxing during file and command operations

### Security Features

- ✅ **File Creation Protection**: Agents cannot create files outside their project directory
- ✅ **Command Execution Security**: Commands accessing restricted paths are blocked
- ✅ **Path Validation**: All file operations validated against sandbox boundaries
- ✅ **Access Logging**: Complete audit trail of all file access attempts
- ✅ **Violation Alerts**: Critical alerts for security boundary violations
- ✅ **Project Isolation**: Each project has its own isolated sandbox

## 🚀 Quick Setup

### 1. Run the Setup Script

```bash
python3 setup_sandbox.py
```

This script will:
- Detect your installation directory
- Create environment configuration
- Set up sample project structure
- Test the sandbox configuration

### 2. Configure Environment

Add to your shell profile (`.bashrc`, `.zshrc`, etc.):

```bash
export ORCHESTRATOR_ROOT="/path/to/your/tmux-orchestrator"
```

Or source the generated `.env` file:

```bash
source .env
```

### 3. Test Security

```bash
python3 test_sandbox_security.py
```

## 📁 Configuration

### Environment Variables

- `ORCHESTRATOR_ROOT`: Path to your Tmux Orchestrator installation
- Defaults to current working directory if not set

### Configuration Files

#### `agent_sandbox_config.json`
Main configuration file with environment variable substitution:

```json
{
  "sandbox_config": {
    "default_boundaries": {
      "root_directory": "${ORCHESTRATOR_ROOT}",
      "restricted_paths": [
        "${ORCHESTRATOR_ROOT}/core",
        "${ORCHESTRATOR_ROOT}/services",
        "${ORCHESTRATOR_ROOT}/qwen_control.py"
      ]
    },
    "project_sandboxes": {
      "my-project": {
        "allowed_base_path": "${ORCHESTRATOR_ROOT}/projects/my-project",
        "allowed_subdirectories": ["src", "tests", "docs"],
        "restricted_paths": ["${ORCHESTRATOR_ROOT}/core"]
      }
    }
  }
}
```

#### `user_sandbox_config.json`
User-specific configuration (created by setup script):

```json
{
  "user_sandbox_config": {
    "additional_restricted_paths": ["/etc/passwd", "/home/user/private"],
    "additional_projects": {
      "my-custom-project": {
        "allowed_base_path": "${ORCHESTRATOR_ROOT}/projects/my-custom-project"
      }
    }
  }
}
```

## 🔧 Usage

### Creating Sandboxed Agents

```python
from agentic_capabilities import AgenticExecutor

# Create executor with project sandboxing
executor = AgenticExecutor(
    working_directory=".",
    agent_id="my_agent",
    project_name="my-project"  # This restricts the agent to projects/my-project/
)

# All operations are now sandboxed
executor.create_file("src/main.py", "# My code")  # ✅ Allowed
executor.create_file("/etc/passwd", "hack")       # ❌ Blocked
```

### Using Sandbox Manager

```python
from sandbox_manager import SandboxManager

# Initialize sandbox manager
sandbox_manager = SandboxManager()

# Create sandbox enforcer for an agent
enforcer = sandbox_manager.enforce_sandbox(
    agent_id="my_agent",
    agent_type="developer",
    project_name="my-project"
)

# Validate operations
if enforcer.validate_operation("create_file", "/path/to/file"):
    print("Operation allowed")
else:
    print("Operation blocked")
```

## 🧪 Testing

### Run Security Tests

```bash
python3 test_sandbox_security.py
```

### Test Results

```
🎉 ALL TESTS PASSED! Sandbox security is working correctly.
- Configuration Tests: ✅ PASSED
- Security Tests: ✅ PASSED
```

### Manual Testing

1. **Test File Creation**:
   ```bash
   # Should be blocked
   python3 -c "
   from agentic_capabilities import AgenticExecutor
   executor = AgenticExecutor(agent_id='test', project_name='test-project')
   executor.create_file('/etc/test', 'test')
   "
   ```

2. **Test Command Execution**:
   ```bash
   # Should be blocked
   python3 -c "
   from agentic_capabilities import AgenticExecutor
   executor = AgenticExecutor(agent_id='test', project_name='test-project')
   executor.execute_command('ls /etc')
   "
   ```

## 📊 Monitoring

### Security Logs

All file access attempts are logged to:
```
~/.tmux_orchestrator/agentic_execution.log
```

### Security Reports

Generate security compliance reports:

```python
from sandbox_manager import SandboxManager

sandbox_manager = SandboxManager()
report = sandbox_manager.get_security_report()

print(f"Compliance Rate: {report['compliance_rate']}%")
print(f"Total Violations: {report['security_violations']}")
```

### Log Format

```
[2025-08-05 20:07:13] [agent_id] ALLOWED create_file on /path/to/allowed/file
[2025-08-05 20:07:13] [agent_id] DENIED create_file on /path/to/restricted/file
```

## 🛡️ Security Best Practices

### 1. Regular Auditing

- Monitor security logs regularly
- Review violation alerts
- Update restricted paths as needed

### 2. Project Isolation

- Keep projects in separate directories
- Use descriptive project names
- Avoid sharing sensitive data between projects

### 3. Environment Configuration

- Set `ORCHESTRATOR_ROOT` environment variable
- Use absolute paths in configuration
- Test configuration after changes

### 4. Agent Permissions

- Use appropriate agent types (developer, qa, project_manager)
- Restrict operations based on agent role
- Monitor agent behavior

## 🔍 Troubleshooting

### Common Issues

1. **"ORCHESTRATOR_ROOT not set"**
   - Set the environment variable: `export ORCHESTRATOR_ROOT="/path/to/orchestrator"`
   - Or run the setup script: `python3 setup_sandbox.py`

2. **"Permission denied" errors**
   - Check if the path is in restricted_paths
   - Verify agent has appropriate permissions
   - Review sandbox configuration

3. **Tests failing**
   - Ensure environment variables are set
   - Check file permissions
   - Verify configuration file syntax

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Configuration Validation

```python
from sandbox_manager import SandboxManager

sandbox_manager = SandboxManager()
config = sandbox_manager.config
print("Configuration loaded:", bool(config))
```

## 📚 API Reference

### AgenticExecutor

```python
class AgenticExecutor:
    def __init__(self, working_directory=".", agent_id=None, project_name=None):
        """
        Initialize sandboxed executor
        
        Args:
            working_directory: Base working directory
            agent_id: Unique agent identifier
            project_name: Project name for sandboxing
        """
    
    def create_file(self, file_path: str, content: str, project_name: str = None) -> bool:
        """Create file with sandbox validation"""
    
    def execute_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute command with sandbox validation"""
```

### SandboxManager

```python
class SandboxManager:
    def __init__(self, config_file: str = "agent_sandbox_config.json"):
        """Initialize sandbox manager"""
    
    def enforce_sandbox(self, agent_id: str, agent_type: str, project_name: str = None) -> SandboxEnforcer:
        """Create sandbox enforcer for agent"""
    
    def get_security_report(self) -> Dict[str, Any]:
        """Generate security compliance report"""
```

## 🤝 Contributing

When contributing to the sandbox security system:

1. **Test thoroughly**: Run `python3 test_sandbox_security.py`
2. **Follow security principles**: Never bypass sandboxing
3. **Document changes**: Update this README
4. **Use environment variables**: Avoid hardcoded paths

## 📄 License

This sandbox security system is part of the Tmux Orchestrator project and follows the same license terms.

---

**🔒 Your system is now protected by enterprise-grade sandbox security!** 